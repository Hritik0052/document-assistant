from django.conf import settings


def ui(request):
    return {
        'current_theme': getattr(request, 'theme', settings.DEFAULT_THEME),
        'theme_choices': settings.THEME_CHOICES,
        'openai_configured': settings.OPENAI_CONFIGURED,
        'postgres_configured': 'postgresql' in settings.DATABASES['default']['ENGINE'],
        'max_upload_mb': settings.MAX_UPLOAD_MB,
        'allowed_upload_extensions': ', '.join(sorted(settings.ALLOWED_UPLOAD_EXTENSIONS)),
    }
