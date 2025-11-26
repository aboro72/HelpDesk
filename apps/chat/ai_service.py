import json
import logging
import requests
from django.conf import settings
from django.db.models import Q
from apps.admin_panel.models import SystemSettings
from apps.knowledge.models import KnowledgeArticle

logger = logging.getLogger(__name__)

# Import Unified AI Service für LLAMA3-Integration
try:
    from apps.ai.unified_ai_service import unified_ai_service
    UNIFIED_AI_AVAILABLE = unified_ai_service.is_available()
except ImportError:
    UNIFIED_AI_AVAILABLE = False
    logger.warning("Unified AI Service nicht verfügbar - Fallback auf Legacy-Services")


class AIService:
    """AI service handler for chat responses mit LLAMA3-Integration"""

    def __init__(self):
        self.system_settings = SystemSettings.get_settings()
        self.use_llama3 = getattr(settings, 'USE_LLAMA3', True) and UNIFIED_AI_AVAILABLE
    
    def is_ai_enabled(self):
        """Check if AI is enabled in settings"""
        return self.system_settings.ai_enabled
    
    def get_ai_response(self, message, chat_history=None):
        """
        Get AI response for a chat message with fallback mechanisms

        NEUE PRIORITÄT mit LLAMA3:
        1. LLAMA3 (lokal, kostenlos, schnell) - wenn aktiviert
        2. ChatGPT/Claude (API, konfiguriert)
        3. Rule-based fallback (immer verfügbar)

        Args:
            message (str): User's message
            chat_history (list): Previous chat messages for context

        Returns:
            str or None: AI response or None if error/disabled
        """
        if not self.is_ai_enabled():
            return None

        # PRIORITY 1: LLAMA3 lokale KI (wenn aktiviert und verfügbar)
        if self.use_llama3 and UNIFIED_AI_AVAILABLE:
            try:
                logger.info("Trying LLAMA3 local AI for chat response...")

                # Konvertiere Chat-History zum richtigen Format
                context = []
                if chat_history:
                    for msg in chat_history[-5:]:
                        context.append({
                            'role': 'assistant' if not msg.is_from_visitor else 'user',
                            'content': msg.message,
                            'is_from_visitor': msg.is_from_visitor
                        })

                response, provider = unified_ai_service.generate_chat_response(message, context)
                if response:
                    logger.info(f"LLAMA3 response generated (provider: {provider})")
                    return response
                else:
                    logger.warning("LLAMA3 failed, falling back to cloud APIs")
            except Exception as e:
                logger.error(f"LLAMA3 error: {e}, falling back to cloud APIs")

        # PRIORITY 2: Cloud APIs (ChatGPT/Claude)
        try:
            if self.system_settings.ai_provider == 'chatgpt':
                response = self._get_chatgpt_response(message, chat_history)
                if response:
                    return response
                # Fallback to Claude if ChatGPT fails
                logger.warning("ChatGPT failed, falling back to Claude")
                response = self._get_claude_response(message, chat_history)
                if response:
                    return response
            elif self.system_settings.ai_provider == 'claude':
                response = self._get_claude_response(message, chat_history)
                if response:
                    return response
                # Fallback to ChatGPT if Claude fails
                logger.warning("Claude failed, falling back to ChatGPT")
                response = self._get_chatgpt_response(message, chat_history)
                if response:
                    return response
        except Exception as e:
            logger.error(f"Primary AI service error: {e}")

        # PRIORITY 3: Rule-based fallback (immer verfügbar)
        try:
            logger.info("Using fallback free AI response")
            return self._get_claude_free_response(message, chat_history)
        except Exception as e:
            logger.error(f"Fallback AI service error: {e}")
            return self._get_emergency_response()
    
    def _get_emergency_response(self):
        """Emergency response when all AI services fail"""
        return """🔧 **Technischer Hinweis**
        
Entschuldigung, unser KI-System ist momentan nicht verfügbar.

**Sofortige Unterstützung:**
✅ Ein Support-Agent wird benachrichtigt
✅ Ihr Problem wird prioritär bearbeitet
✅ Alternative Kontaktmöglichkeiten:

📞 **Telefon-Support:** [Nummer]
📧 **E-Mail:** support@unternehmen.de
💬 **Live-Agent wird hinzugezogen**

Bitte beschreiben Sie Ihr Problem weiter - ein menschlicher Agent übernimmt sofort! 🚀"""
    
    def _get_chatgpt_response(self, message, chat_history=None):
        """Get response from OpenAI ChatGPT"""
        if not self.system_settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.system_settings.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]
        
        # Add chat history for context
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = "assistant" if not msg.is_from_visitor else "user"
                messages.append({
                    "role": role,
                    "content": msg.message
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": self.system_settings.ai_max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"ChatGPT API request failed: {e}")
        
        return None
    
    def _get_claude_response(self, message, chat_history=None):
        """Get response from Anthropic Claude"""
        # For Claude, we'll implement a fallback to free version if no API key
        if self.system_settings.anthropic_api_key:
            return self._get_claude_api_response(message, chat_history)
        else:
            # Use a simple rule-based response for free version
            return self._get_claude_free_response(message)
    
    def _get_claude_api_response(self, message, chat_history=None):
        """Get response from Claude API (paid version)"""
        headers = {
            'x-api-key': self.system_settings.anthropic_api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # Build conversation context
        conversation = ""
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = "Assistant" if not msg.is_from_visitor else "Human"
                conversation += f"{role}: {msg.message}\n"
        
        conversation += f"Human: {message}\n\nAssistant:"
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": self.system_settings.ai_max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": f"{self._get_system_prompt()}\n\n{conversation}"
                }
            ]
        }
        
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'content' in result and len(result['content']) > 0:
                    return result['content'][0]['text'].strip()
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
        
        return None
    
    def _get_claude_free_response(self, message, chat_history=None):
        """Free version Claude response with intelligent problem-solving and routing"""
        message_lower = message.lower()
        
        # Analyze chat history to understand conversation context
        context = self._analyze_conversation_context(chat_history) if chat_history else {}
        
        # Smart routing based on problem categorization
        if context.get('problem_type'):
            return self._get_categorized_response(message, context)
        
        # Escalation check - suggest human agent for complex cases
        if context.get('conversation_stage') == 'escalation' or context.get('problem_severity') == 'high':
            return self._get_escalation_response(context)
        
        # Greeting responses
        if any(word in message_lower for word in ['hallo', 'hi', 'hey', 'guten tag']) and len(message.split()) <= 3:
            return """Hallo! 👋 Ich bin Ihr KI-Support-Assistent und helfe Ihnen gerne bei technischen Problemen.

Um Ihnen bestmöglich zu helfen, möchte ich ein paar Informationen sammeln:

🔧 **Womit kann ich Ihnen helfen?**
- Anmelde- oder Passwort-Probleme?
- Software funktioniert nicht korrekt?
- E-Mail- oder Netzwerk-Probleme?
- Performance- oder Geschwindigkeitsprobleme?
- Etwas anderes?

Beschreiben Sie mir bitte Ihr Problem, dann kann ich Ihnen gezielt helfen!"""

        # Password/Login problems - intelligent troubleshooting
        elif any(word in message_lower for word in ['passwort', 'password', 'anmelden', 'login', 'einloggen']):
            if not context.get('asked_browser'):
                return """🔐 **Anmelde-Probleme verstehe ich!** Lassen Sie mich Ihnen systematisch helfen.

**Erste wichtige Frage:** Welchen Browser verwenden Sie?
- Chrome
- Firefox  
- Safari
- Edge
- Andere

**Zusätzlich hilfreich:**
- Wann konnten Sie sich zuletzt erfolgreich anmelden?
- Erhalten Sie eine spezifische Fehlermeldung?
- Funktioniert die Anmeldung auf anderen Geräten?

Mit diesen Informationen kann ich Ihnen gezielt weiterhelfen! 🎯"""
            
            else:
                return """🔧 **Schritt-für-Schritt Lösung für Anmelde-Probleme:**

**Sofort-Hilfe (in dieser Reihenfolge):**
1. **Browser-Cache leeren** (Strg+Shift+Entf)
2. **Cookies für diese Website löschen**
3. **Browser komplett neu starten**
4. **Passwort-Manager deaktivieren** (temporär)
5. **Passwort manuell eingeben**

**Falls das nicht hilft:**
6. **Inkognito-/Privat-Modus** testen
7. **Anderen Browser** ausprobieren
8. **Passwort zurücksetzen**

Funktioniert einer dieser Schritte? Lassen Sie mich wissen, was passiert! 🔍"""

        # Email problems - systematic approach
        elif any(word in message_lower for word in ['email', 'e-mail', 'mail']):
            return """📧 **E-Mail-Probleme lösen wir systematisch!**

**Zuerst brauche ich Details:**
- **Welches Problem genau?** (kann nicht senden/empfangen/anmelden?)
- **Welcher E-Mail-Client?** (Outlook, Thunderbird, Webmail, Handy-App?)
- **Seit wann** tritt das Problem auf?
- **Fehlermeldung** vorhanden?

**Schnell-Check (bitte testen):**
✅ Internetverbindung funktioniert?
✅ Andere Websites erreichbar?
✅ Passwort korrekt?

**Geben Sie mir diese Infos, dann kann ich gezielt helfen!** 🎯"""

        # Performance problems - detailed troubleshooting
        elif any(word in message_lower for word in ['langsam', 'slow', 'performance', 'hängt', 'lahm', 'träge']):
            return """🚀 **Performance-Probleme systematisch lösen:**

**Erste Diagnose - bitte testen:**
1. **Andere Websites** auch langsam? (Internet-Test)
2. **Andere Browser** ausprobieren
3. **Wie viele Tabs** haben Sie offen?
4. **Seit wann** ist es langsam?

**Sofort-Maßnahmen:**
⚡ Browser-Cache leeren (Strg+Shift+Entf)
⚡ Unnötige Tabs schließen
⚡ Browser-Erweiterungen deaktivieren
⚡ Computer neu starten

**System-Check:**
- Welches Betriebssystem nutzen Sie?
- Wie alt ist Ihr Computer?
- Läuft Antivirus-Software?

Teilen Sie mir die Ergebnisse mit - dann entwickeln wir die perfekte Lösung! 🔧"""

        # Error/Bug problems - systematic debugging
        elif any(word in message_lower for word in ['fehler', 'error', 'bug', 'funktioniert nicht', 'geht nicht', 'problem']):
            return """🐛 **Fehler systematisch debuggen:**

**Kritische Informationen benötigt:**
1. **Exakte Fehlermeldung** (Screenshot ideal!)
2. **Wann tritt der Fehler auf?** (beim Start, bei bestimmter Aktion?)
3. **Reproduzierbar?** (passiert immer oder manchmal?)
4. **Was haben Sie zuletzt gemacht** bevor der Fehler auftrat?

**System-Info:**
- Browser + Version
- Betriebssystem  
- Andere Programme geöffnet?

**Erste Lösungsversuche:**
🔄 Seite neu laden (F5)
🔄 Browser neu starten
🔄 Im Inkognito-Modus testen
🔄 Anderen Browser testen

**Je mehr Details Sie mir geben, desto gezielter kann ich helfen!** 🎯"""

        # Thank you responses
        elif any(word in message_lower for word in ['danke', 'dankeschön', 'thanks', 'vielen dank']):
            return """😊 **Sehr gerne!** 

Ich bin weiterhin für Sie da! Falls neue Fragen aufkommen oder Sie zusätzliche Hilfe benötigen:

✅ Beschreiben Sie einfach Ihr Problem
✅ Bei komplexen Fällen kann ich einen Support-Agent hinzuziehen
✅ Ich bleibe so lange, bis alles funktioniert!

**War die Lösung erfolgreich?** Lassen Sie mich wissen, ob alles klappt! 🎯"""

        # Goodbye responses  
        elif any(word in message_lower for word in ['tschüss', 'auf wiedersehen', 'bye', 'ciao']):
            return """👋 **Auf Wiedersehen!**

Falls später Probleme auftreten, bin ich jederzeit für Sie da. 

**Vergessen Sie nicht:**
- Bei dringenden Problemen können Sie sofort einen Chat starten
- Ich helfe bei der Problemanalyse und Lösungsfindung
- Support-Agents stehen für komplexe Fälle bereit

Bis bald! 😊"""

        # Complex/unknown problems - intelligent questioning
        else:
            return """🤔 **Interessante Anfrage!** Lassen Sie mich das systematisch angehen.

**Um Ihnen optimal zu helfen, brauche ich mehr Details:**

📋 **Problem-Analyse:**
- **Was genau** möchten Sie erreichen?
- **Was passiert stattdessen?**
- **Wann** tritt das Problem auf?
- **Welche Schritte** haben Sie bereits versucht?

💻 **System-Info:**
- Welcher Browser/welche Software?
- Betriebssystem (Windows/Mac/Linux)?
- Fehlermeldungen vorhanden?

**Je spezifischer Ihre Beschreibung, desto gezielter kann ich Ihnen helfen!**

Falls es sehr komplex wird, kann ich auch einen erfahrenen Support-Agent für Sie hinzuziehen. 🎯"""
    
    def _get_categorized_response(self, message, context):
        """Generate contextual response based on problem category"""
        problem_type = context.get('problem_type')
        user_level = context.get('user_expertise_level', 'beginner')
        stage = context.get('conversation_stage', 'initial')
        
        if problem_type == 'login':
            if stage == 'troubleshooting':
                return """🔧 **Erweiterte Anmelde-Diagnose:**
                
Basierend auf unserer bisherigen Unterhaltung, versuchen wir diese fortgeschrittenen Schritte:

**Browser-spezifische Lösungen:**
1. **Firefox:** Extras > Einstellungen > Datenschutz > Daten löschen
2. **Chrome:** Einstellungen > Erweitert > Browserdaten löschen  
3. **Edge:** Einstellungen > Datenschutz > Browserdaten löschen

**System-Level Checks:**
- Datum/Uhrzeit des Systems korrekt?
- Antivirus/Firewall blockiert Verbindung?
- VPN aktiv? (falls ja, deaktivieren zum Test)

**Letzte Optionen:**
- Anderen Computer/Smartphone testen
- Administrator/IT-Abteilung kontaktieren
- Passwort-Reset über E-Mail

Welcher Schritt hat funktioniert oder benötigen Sie Unterstützung durch einen Mitarbeiter? 🔍"""
            else:
                return """🔐 **Login-Problem erkannt!** 

**Sofort-Diagnose (bitte beantworten):**
- Welchen Browser verwenden Sie?
- Funktioniert die Anmeldung auf anderen Geräten?
- Erhalten Sie eine spezifische Fehlermeldung?

**Schnelle Lösungsversuche:**
✅ Cache/Cookies löschen (Strg+Shift+Entf)
✅ Inkognito-Modus testen
✅ Passwort korrekt eingeben (Caps Lock prüfen)

Berichten Sie mir die Ergebnisse! 🎯"""
        
        elif problem_type == 'email':
            if user_level == 'advanced':
                return """📧 **E-Mail-Problem (Technische Diagnose):**
                
**Server-Level Checks:**
- SMTP/IMAP-Einstellungen korrekt?
- Port-Konfiguration (587/993/995)?
- SSL/TLS-Verschlüsselung aktiviert?
- Authentifizierung-Methode?

**Logs/Fehlercodes:**
- Genaue Fehlernummer/Message?
- Verbindungs-Timeout oder Auth-Fehler?
- DNS-Auflösung der Mail-Server funktional?

**Erweiterte Tests:**
- Telnet-Test zu Mail-Server (Port 25/587)
- Alternative Ports testen
- Provider-spezifische App-Passwörter?

Teilen Sie technische Details oder Logs mit mir! 🔍"""
            else:
                return """📧 **E-Mail-Unterstützung:**
                
**Grundlegende Informationen benötigt:**
- Welcher E-Mail-Anbieter? (Gmail, Outlook, etc.)
- Welches Programm verwenden Sie?
- Können Sie senden, empfangen oder beides nicht?

**Erste Hilfe-Schritte:**
1. Internet-Verbindung testen
2. E-Mail-App/Browser neu starten  
3. Passwort korrekt eingeben
4. Updates installieren

Beschreiben Sie das genaue Problem! 📬"""
        
        elif problem_type == 'performance':
            return """🚀 **Performance-Optimierung:**
            
**System-Analyse (bitte prüfen):**
- Task-Manager öffnen → Hohe CPU/RAM-Nutzung?
- Festplatte voll? (C:\\ > 85% = Problem)
- Wie viele Programme laufen gleichzeitig?

**Sofort-Optimierung:**
⚡ Unnötige Programme schließen
⚡ Browser-Tabs reduzieren (max. 5-10)
⚡ Temporäre Dateien löschen
⚡ Computer neu starten

**Erweiterte Schritte:**
- Windows-Updates installieren
- Autostart-Programme deaktivieren  
- Festplatte defragmentieren
- RAM-Upgrade erwägen

Welche Werte zeigt Ihr Task-Manager? 📊"""
        
        elif problem_type == 'connection':
            return """🌐 **Netzwerk-Diagnose:**
            
**Verbindungs-Test (Schritt für Schritt):**
1. **Grundtest:** Andere Websites erreichbar?
2. **Router-Test:** Andere Geräte im WLAN funktional?
3. **Kabel-Test:** LAN-Kabel fest verbunden?

**Windows-Netzwerk-Diagnose:**
- Rechtsklick auf WLAN-Symbol → "Problembehandlung"
- CMD öffnen → "ipconfig /release" → "ipconfig /renew"
- DNS leeren: "ipconfig /flushdns"

**Router-Reset:**
- Router 30 Sek. vom Strom trennen
- Verkabelung prüfen (LAN/WAN-Ports)
- WLAN-Passwort korrekt?

Beschreiben Sie das genaue Verhalten! 📡"""
        
        # Default categorized response
        return f"""🔍 **{problem_type.title()}-Problem erkannt!**
        
Ich sehe, dass Sie ein {problem_type}-bezogenes Problem haben. 

**Nächste Schritte:**
1. Bitte beschreiben Sie das Problem detaillierter
2. Welche Schritte haben Sie bereits versucht?
3. Wann trat das Problem zum ersten Mal auf?

**Expertise-Level:** {user_level.title()}
Ich passe meine Antworten an Ihr technisches Niveau an.

Teilen Sie mehr Details mit mir! 🎯"""

    def _get_escalation_response(self, context):
        """Generate escalation response for complex cases"""
        severity = context.get('problem_severity', 'low')
        stage = context.get('conversation_stage', 'initial')
        
        if severity == 'high':
            return """🚨 **Dringende Unterstützung benötigt!**
            
Ich erkenne, dass dies ein dringender Fall ist. 

**Sofortige Optionen:**
✅ Ich fordere einen erfahrenen Support-Agent an
✅ Priorität: HOCH - schnellere Bearbeitung
✅ Alle bisherigen Informationen werden übertragen

**Was passiert jetzt:**
1. Support-Agent wird sofort benachrichtigt
2. Übernahme des Chats in wenigen Minuten
3. Direkte technische Unterstützung

**Falls sehr dringend:**
- Telefon-Support verfügbar: [Nummer einfügen]
- E-Mail: support@unternehmen.de

Bitte warten Sie einen Moment - Hilfe ist unterwegs! 🚀"""
        
        else:
            return """🤝 **Experten-Unterstützung empfohlen**
            
Nach unserer Unterhaltung sehe ich, dass dieses Problem komplexere Expertise benötigt.

**Ich empfehle:**
✅ Übergabe an einen menschlichen Support-Agent
✅ Spezialist für Ihr spezifisches Problem
✅ Alle bisherigen Informationen werden übertragen

**Vorteile der Übergabe:**
- Tiefere technische Analyse
- Remotezugriff möglich (mit Ihrer Erlaubnis)
- Direkte Lösungsimplementierung
- Follow-up-Unterstützung

Soll ich einen Support-Agent für Sie anfordern? 👨‍💻"""
    
    def _analyze_conversation_context(self, chat_history):
        """Analyze previous conversation to understand context and build memory"""
        if not chat_history:
            return {}
        
        context = {
            'asked_browser': False,
            'asked_system': False,
            'provided_steps': False,
            'problem_type': None,
            'user_responses': [],
            'attempted_solutions': [],
            'user_expertise_level': 'beginner',
            'problem_severity': 'low',
            'conversation_stage': 'initial'
        }
        
        user_messages = []
        ai_messages = []
        
        # Categorize messages and analyze patterns
        for msg in chat_history:
            if msg.is_from_visitor:
                user_messages.append(msg.message.lower())
            else:
                ai_messages.append(msg.message.lower())
                # Analyze AI response patterns
                if 'browser' in msg.message.lower():
                    context['asked_browser'] = True
                if 'betriebssystem' in msg.message.lower():
                    context['asked_system'] = True
                if 'schritt' in msg.message.lower():
                    context['provided_steps'] = True
        
        # Analyze user expertise level based on technical language used
        technical_terms = ['api', 'server', 'database', 'log', 'cache', 'cookie', 'ssl', 'dns', 'firewall', 'port']
        technical_score = sum(1 for term in technical_terms if any(term in msg for msg in user_messages))
        
        if technical_score >= 3:
            context['user_expertise_level'] = 'advanced'
        elif technical_score >= 1:
            context['user_expertise_level'] = 'intermediate'
        
        # Determine problem type based on keywords
        problem_keywords = {
            'login': ['passwort', 'password', 'anmelden', 'login', 'einloggen', 'account'],
            'email': ['email', 'e-mail', 'mail', 'outlook', 'thunderbird'],
            'performance': ['langsam', 'slow', 'performance', 'hängt', 'lahm', 'träge', 'loading'],
            'connection': ['verbindung', 'connection', 'internet', 'network', 'wifi', 'wlan'],
            'software': ['software', 'programm', 'application', 'app', 'installation'],
            'hardware': ['hardware', 'computer', 'laptop', 'monitor', 'drucker', 'printer']
        }
        
        for problem_type, keywords in problem_keywords.items():
            if any(keyword in ' '.join(user_messages) for keyword in keywords):
                context['problem_type'] = problem_type
                break
        
        # Determine conversation stage
        if len(user_messages) == 1:
            context['conversation_stage'] = 'initial'
        elif context['provided_steps'] and len(user_messages) > 2:
            context['conversation_stage'] = 'troubleshooting'
        elif len(user_messages) > 3:
            context['conversation_stage'] = 'escalation'
        
        # Analyze problem severity based on user language
        urgent_indicators = ['dringend', 'urgent', 'sofort', 'kritisch', 'critical', 'wichtig', 'important', 'hilfe', 'help']
        if any(indicator in ' '.join(user_messages) for indicator in urgent_indicators):
            context['problem_severity'] = 'high'
        
        # Store user responses for better context
        context['user_responses'] = user_messages[-3:]  # Last 3 user messages
        
        return context
    
    def _get_system_prompt(self):
        """Get the enhanced system prompt for AI responses"""
        return """Du bist ein hochqualifizierter KI-Assistent für einen professionellen Helpdesk-Service. Du spezialisierst dich auf systematische Problemanalyse, intelligente Lösungsfindung und exzellenten Kundenservice.

🔧 ERWEITERTE PROBLEMLÖSUNGSSTRATEGIE:

1. INTELLIGENTE PROBLEMANALYSE:
   - Kategorisiere Probleme automatisch (Login, E-Mail, Performance, Netzwerk, Software, Hardware)
   - Bewerte Benutzer-Expertise-Level (Anfänger/Fortgeschritten/Expert)
   - Bestimme Problem-Schweregrad (Niedrig/Mittel/Hoch/Kritisch)
   - Analysiere Gesprächskontext und bisherige Lösungsversuche

2. ADAPTIVE KOMMUNIKATION:
   - Passe Sprache und Detailgrad an Benutzer-Level an
   - Verwende technische Begriffe nur bei erfahrenen Benutzern
   - Biete Schritt-für-Schritt-Anleitungen für Anfänger
   - Stelle präzise Diagnosefragen für Experten

3. KONTEXTUELLE LÖSUNGSSTRATEGIEN:
   - Berücksichtige vorherige Nachrichten und Lösungsversuche
   - Eskaliere bei wiederholten Problemen automatisch
   - Erkenne Muster in Benutzerantworten
   - Baue auf bereits gesammelten Informationen auf

4. PROAKTIVE UNTERSTÜTZUNG:
   - Antizipiere Follow-up-Fragen
   - Erkläre präventive Maßnahmen
   - Biete verwandte Lösungen an
   - Schlage Optimierungen vor

5. SMART ESCALATION CRITERIA:
   - Kritische Sicherheitsprobleme → Sofortige Weiterleitung
   - Mehr als 3 Nachrichten ohne Lösung → Agent-Empfehlung
   - Administrative Rechte benötigt → Techniker anfordern
   - Benutzer explizit frustriert → Menschliche Unterstützung

6. QUALITÄTSINDIKATOREN:
   - Stelle IMMER Nachfragen bei unklaren Problemen
   - Biete MEHRERE Lösungsoptionen (einfach → komplex)
   - Erkläre das WARUM hinter den Lösungen
   - Bestätige Erfolg oder leite zur nächsten Stufe weiter
   - Dokumentiere wichtige Details für Agent-Übergabe

7. KOMMUNIKATIONSRICHTLINIEN:
   - Freundlich und professionell
   - Empathisch bei Frustrationen
   - Klar strukturierte Antworten mit Emojis
   - Actionable Schritte mit Erfolgs-Indikatoren
   - Zeitschätzungen für Lösungsschritte

SPEZIALISIERUNGEN:
📊 Windows/Mac/Linux Systeme | 🌐 Netzwerk-Diagnose | 📧 E-Mail-Konfiguration | 🔐 Security & Authentication | ⚡ Performance-Optimierung | 💻 Software-Troubleshooting

WICHTIG: Du bist ein proaktiver Problem-Solver mit emotionaler Intelligenz. Dein Ziel ist nicht nur die Lösung, sondern auch die Bildung und Zufriedenheit des Benutzers!"""


def get_ai_response_for_chat(message, chat_session):
    """
    Convenience function to get AI response for a chat message
    
    Args:
        message (str): User's message
        chat_session: ChatSession instance
        
    Returns:
        str or None: AI response or None if error/disabled
    """
    ai_service = AIService()
    
    # Get recent chat history for context
    chat_history = chat_session.messages.order_by('timestamp')[:10]
    
    return ai_service.get_ai_response(message, chat_history)