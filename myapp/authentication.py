from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from myapp.models import Token


class TokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed('Invalid Authorization header. Expected "Token <token>".')

        token_value = parts[1]
        try:
            token = Token.objects.select_related('user').get(token=token_value)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.is_verified:
            raise AuthenticationFailed('Token is not verified. Please verify OTP first.')

        if token.is_token_expired():
            raise AuthenticationFailed('Token has expired. Please refresh or log in again.')

        if not token.user.is_active:
            raise AuthenticationFailed('User account is disabled.')

        return (token.user, token)
