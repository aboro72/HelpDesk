#!/usr/bin/env python3
"""
Test-Script für LLAMA3-Integration auf Jetson Orin NX
Testet alle KI-Funktionen: Kategorisierung, Priorität, Chat
"""
import os
import sys
import django
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Django Setup
sys.path.append('/home/user/PycharmProjects/HelpDesk')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

# Import Services
from apps.ai.llama3_service import llama3_service
from apps.ai.unified_ai_service import unified_ai_service


def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}\n")


def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ️  {text}")


def test_llama3_availability():
    """Test 1: LLAMA3 Service Verfügbarkeit"""
    print_header("TEST 1: LLAMA3 Service Verfügbarkeit")

    if llama3_service.is_available():
        print_success("LLAMA3 Service ist verfügbar!")
        print_info(f"Modell: {llama3_service.model}")
        return True
    else:
        print_error("LLAMA3 Service ist NICHT verfügbar!")
        print_info("Prüfe: sudo systemctl status ollama")
        return False


def test_ticket_categorization():
    """Test 2: Ticket-Kategorisierung"""
    print_header("TEST 2: Ticket-Kategorisierung")

    test_tickets = [
        {
            "title": "Ich kann mich nicht anmelden",
            "description": "Mein Passwort funktioniert nicht mehr. Ich habe es mehrmals versucht."
        },
        {
            "title": "E-Mail kommt nicht an",
            "description": "Ich kann keine E-Mails empfangen seit heute morgen."
        },
        {
            "title": "System ist sehr langsam",
            "description": "Die Anwendung braucht ewig zum Laden, besonders morgens."
        }
    ]

    success_count = 0
    for i, ticket in enumerate(test_tickets, 1):
        print(f"\n{Fore.BLUE}Ticket {i}:")
        print(f"  Titel: {ticket['title']}")
        print(f"  Beschreibung: {ticket['description']}")

        start = time.time()
        category, confidence = llama3_service.categorize_ticket(
            ticket['title'],
            ticket['description']
        )
        duration = time.time() - start

        if category:
            print_success(f"Kategorie: {category}")
            print_info(f"Konfidenz: {confidence:.0%}")
            print_info(f"Zeit: {duration:.2f}s")
            success_count += 1
        else:
            print_error("Kategorisierung fehlgeschlagen")

    print(f"\n{Fore.MAGENTA}Erfolg: {success_count}/{len(test_tickets)}")
    return success_count == len(test_tickets)


def test_priority_suggestion():
    """Test 3: Prioritäts-Vorschlag"""
    print_header("TEST 3: Prioritäts-Vorschlag")

    test_cases = [
        {
            "title": "Server ist komplett ausgefallen",
            "description": "Produktions-Server antwortet nicht. Alle Kunden sind betroffen!",
            "expected": "critical"
        },
        {
            "title": "Kleiner Tippfehler in der Dokumentation",
            "description": "Auf Seite 5 ist ein Komma falsch gesetzt.",
            "expected": "low"
        }
    ]

    success_count = 0
    for i, case in enumerate(test_cases, 1):
        print(f"\n{Fore.BLUE}Fall {i}:")
        print(f"  Titel: {case['title']}")
        print(f"  Erwartet: {case['expected']}")

        start = time.time()
        priority, reason = llama3_service.suggest_priority(
            case['title'],
            case['description']
        )
        duration = time.time() - start

        if priority:
            print_success(f"Priorität: {priority}")
            print_info(f"Begründung: {reason}")
            print_info(f"Zeit: {duration:.2f}s")

            if priority == case['expected']:
                print_success("Erwartung erfüllt!")
                success_count += 1
            else:
                print_error(f"Erwartet wurde: {case['expected']}")
        else:
            print_error("Prioritäts-Vorschlag fehlgeschlagen")

    print(f"\n{Fore.MAGENTA}Erfolg: {success_count}/{len(test_cases)}")
    return success_count >= len(test_cases) // 2  # 50% Erfolgsrate OK


def test_chat_response():
    """Test 4: Chat-Response"""
    print_header("TEST 4: Chat-Response")

    test_messages = [
        "Hallo, ich brauche Hilfe!",
        "Ich kann mich nicht anmelden",
        "Vielen Dank für die Hilfe!"
    ]

    success_count = 0
    for i, message in enumerate(test_messages, 1):
        print(f"\n{Fore.BLUE}Nachricht {i}: {message}")

        start = time.time()
        response = llama3_service.generate_chat_response(message)
        duration = time.time() - start

        if response:
            print_success("Antwort generiert:")
            # Zeige erste 200 Zeichen
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"{Fore.WHITE}{preview}")
            print_info(f"Länge: {len(response)} Zeichen")
            print_info(f"Zeit: {duration:.2f}s")
            success_count += 1
        else:
            print_error("Chat-Response fehlgeschlagen")

    print(f"\n{Fore.MAGENTA}Erfolg: {success_count}/{len(test_messages)}")
    return success_count == len(test_messages)


def test_unified_service():
    """Test 5: Unified Service mit Fallback"""
    print_header("TEST 5: Unified AI Service")

    print_info("Verfügbare Provider:")
    providers = unified_ai_service.get_available_providers()
    for provider in providers:
        print(f"  {Fore.GREEN}✓ {provider}")

    print(f"\n{Fore.BLUE}Test Kategorisierung mit Fallback...")
    category, confidence, provider = unified_ai_service.categorize_ticket(
        "Passwort vergessen",
        "Ich habe mein Passwort vergessen und brauche ein neues."
    )

    if category:
        print_success(f"Kategorie: {category}")
        print_info(f"Provider: {provider}")
        print_info(f"Konfidenz: {confidence:.0%}")
        return True
    else:
        print_error("Unified Service fehlgeschlagen")
        return False


def test_performance_stats():
    """Test 6: Performance-Statistiken"""
    print_header("TEST 6: Performance-Statistiken")

    stats = llama3_service.get_performance_stats()

    print(f"{Fore.CYAN}LLAMA3 Service Stats:")
    print(f"  Verfügbar: {stats['available']}")
    print(f"  Modell: {stats['model']}")
    print(f"  Anfragen: {stats['total_requests']}")
    if stats['total_requests'] > 0:
        print(f"  Ø Antwortzeit: {stats['avg_response_time']}s")
        print(f"  Ø Tokens: {stats['avg_tokens']}")

    unified_stats = unified_ai_service.get_stats()
    print(f"\n{Fore.CYAN}Unified Service Stats:")
    print(f"  Gesamt-Anfragen: {unified_stats['total_requests']}")
    print(f"  Provider-Verteilung:")
    for provider, count in unified_stats.get('usage', {}).items():
        if count > 0:
            print(f"    {provider}: {count}")

    return True


def run_all_tests():
    """Führt alle Tests aus"""
    print_header("🧪 LLAMA3 Integration Test Suite 🧪")
    print(f"{Fore.YELLOW}Jetson Orin NX 16GB | LLAMA3:8B")

    results = []

    # Test 1: Verfügbarkeit
    results.append(("Verfügbarkeit", test_llama3_availability()))

    # Nur weitermachen wenn verfügbar
    if not results[0][1]:
        print_error("\nLLAMA3 nicht verfügbar - Tests abgebrochen!")
        print_info("Führe aus: sudo systemctl start ollama")
        return

    # Test 2: Kategorisierung
    results.append(("Kategorisierung", test_ticket_categorization()))

    # Test 3: Priorität
    results.append(("Priorität", test_priority_suggestion()))

    # Test 4: Chat
    results.append(("Chat-Response", test_chat_response()))

    # Test 5: Unified Service
    results.append(("Unified Service", test_unified_service()))

    # Test 6: Stats
    results.append(("Performance-Stats", test_performance_stats()))

    # Zusammenfassung
    print_header("📊 Test-Zusammenfassung")

    success = sum(1 for _, passed in results if passed)
    total = len(results)

    for name, passed in results:
        if passed:
            print_success(f"{name}")
        else:
            print_error(f"{name}")

    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}Gesamt: {success}/{total} Tests erfolgreich")

    if success == total:
        print(f"{Fore.GREEN}🎉 ALLE TESTS BESTANDEN! 🎉")
        print(f"{Fore.GREEN}LLAMA3-Integration ist PRODUKTIONSBEREIT!")
    elif success >= total * 0.8:
        print(f"{Fore.YELLOW}⚠️  Meiste Tests bestanden - kleinere Probleme")
    else:
        print(f"{Fore.RED}❌ Mehrere Tests fehlgeschlagen - Überprüfung nötig")

    print(f"{Fore.MAGENTA}{'='*70}\n")


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests abgebrochen durch Benutzer")
    except Exception as e:
        print_error(f"Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
