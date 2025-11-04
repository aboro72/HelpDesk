from apps.admin_panel.models import SystemSettings
from apps.main.forms import AdminSettingsForm
from django.core.files.uploadedfile import SimpleUploadedFile

# Erstelle eine Test-Image-Datei
test_image = SimpleUploadedFile(
    "test_logo.png",
    b"fake image content",
    content_type="image/png"
)

# Teste die Form
settings = SystemSettings.get_settings()
form_data = {
    'app_name': settings.app_name,
    'company_name': settings.company_name,
    'site_url': settings.site_url,
    'smtp_host': settings.smtp_host,
    'smtp_port': settings.smtp_port,
    'smtp_username': settings.smtp_username,
    'smtp_password': settings.smtp_password,
    'smtp_use_tls': settings.smtp_use_tls,
    'send_email_notifications': settings.send_email_notifications,
    'max_upload_size_mb': settings.max_upload_size_mb,
    'chat_enabled': True,
    'widget_color': '#667eea',
    'widget_position': 'bottom-right',
    'welcome_message': 'test',
    'offline_message': 'test',
    'auto_assign': False,
    'ai_enabled': False,
    'ai_provider': 'chatgpt',
    'openai_api_key': '',
    'anthropic_api_key': '',
    'ai_response_delay': 2,
    'ai_max_tokens': 500,
    'theme_variant': 'default',
    'primary_color': '#0066CC',
    'secondary_color': '#00B366',
    'accent_color': '#FF6600',
    'danger_color': '#CC0000',
    'font_family': 'inter',
    'border_radius': 8,
    'enable_dark_mode': False,
}

from apps.chat.models import ChatSettings

chat_settings = ChatSettings.get_settings()

form = AdminSettingsForm(form_data, {'logo': test_image}, system_settings=settings, chat_settings=chat_settings)

if form.is_valid():
    print("✓ Form is valid!")
    form.save()
    print("✓ Form saved!")

    # Check if logo was saved
    settings = SystemSettings.get_settings()
    print(f"Logo: {settings.logo}")
else:
    print("✗ Form is INVALID!")
    print("Errors:", form.errors)