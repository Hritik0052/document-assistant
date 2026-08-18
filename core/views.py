from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods


@require_http_methods(['POST'])
def set_theme(request):
    theme = request.POST.get('theme') or settings.DEFAULT_THEME
    if theme not in settings.THEME_CHOICES:
        theme = settings.DEFAULT_THEME
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('accounts:login')
    response = HttpResponseRedirect(next_url)
    response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response
