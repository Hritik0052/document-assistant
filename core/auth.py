from functools import wraps

from core.http import async_redirect


def async_login_required(view):
    @wraps(view)
    async def wrapper(request, *args, **kwargs):
        user = await request.auser()
        if not user.is_authenticated:
            return await async_redirect('accounts:login')
        return await view(request, *args, **kwargs)

    return wrapper
