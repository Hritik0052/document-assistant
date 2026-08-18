from django.conf import settings


class ThemeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        theme = request.COOKIES.get('theme', settings.DEFAULT_THEME)
        if theme not in settings.THEME_CHOICES:
            theme = settings.DEFAULT_THEME
        request.theme = theme
        return self.get_response(request)
