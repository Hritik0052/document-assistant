from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from django.conf import settings


def set_theme(request):
    theme = request.POST.get('theme') or request.GET.get('theme') or settings.DEFAULT_THEME
    if theme not in settings.THEME_CHOICES:
        theme = settings.DEFAULT_THEME
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    response = redirect(next_url)
    response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response


@require_POST
def toast_clear(request):
    list(get_messages(request))
    return HttpResponse('')


def toast_stack(request):
    html = render_to_string('components/toast_stack.html', request=request)
    return HttpResponse(html)
