from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.auth import aauthenticate, alogin, alogout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import User
from accounts.schemas import LoginSchema, RegisterSchema
from core.pydantic import FormError, parse_form


@require_http_methods(['GET', 'POST'])
async def register(request):
    user = await request.auser()
    if user.is_authenticated:
        return redirect('documents:library')

    errors = {}
    form_data = {}
    if request.method == 'POST':
        form_data = request.POST.dict()
        try:
            payload = parse_form(RegisterSchema, request.POST)
        except FormError as exc:
            errors = exc.errors
        else:
            if await User.objects.filter(username=payload.username).aexists():
                errors['username'] = 'That username is already taken.'
            elif await User.objects.filter(email=payload.email).aexists():
                errors['email'] = 'That email is already registered.'
            else:
                new_user = await sync_to_async(User.objects.create_user)(
                    username=payload.username,
                    email=payload.email,
                    password=payload.password,
                )
                await alogin(request, new_user)
                messages.success(request, 'Welcome aboard. Upload a document to start asking questions.')
                return redirect('documents:library')

    return render(request, 'accounts/register.html', {
        'errors': errors,
        'form_data': form_data,
    })


@require_http_methods(['GET', 'POST'])
async def login_view(request):
    user = await request.auser()
    if user.is_authenticated:
        return redirect('documents:library')

    errors = {}
    form_data = {}
    if request.method == 'POST':
        form_data = request.POST.dict()
        try:
            payload = parse_form(LoginSchema, request.POST)
        except FormError as exc:
            errors = exc.errors
        else:
            authenticated = await aauthenticate(
                request,
                username=payload.username,
                password=payload.password,
            )
            if authenticated is None:
                errors['form'] = 'Invalid username or password.'
            elif not authenticated.is_active:
                errors['form'] = 'This account is disabled.'
            else:
                await alogin(request, authenticated)
                return redirect('documents:library')

    return render(request, 'accounts/login.html', {
        'errors': errors,
        'form_data': form_data,
    })


@require_http_methods(['POST'])
async def logout_view(request):
    await alogout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('accounts:login')
