from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from myapp.models import Token
from myapp.serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ResendOtpSerializer,
    UpdateUserSerializer,
    UserSerializer,
    VerifyOtpSerializer,
)
from myapp.utils import send_otp


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        fcm_id = serializer.validated_data.get('fcm_id')

        token = Token.create_for_user(user, fcm_id=fcm_id)
        send_otp(user, token.otp)

        return Response({
            'message': 'OTP sent successfully.',
            'token': token.token,
            'otp': token.otp,  # exposed for development/testing only
        }, status=status.HTTP_200_OK)


class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = Token.objects.get(token=serializer.validated_data['token'])
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

        if not token.verify_otp(serializer.validated_data['otp']):
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'OTP verified successfully.',
            'token': token.token,
            'user': UserSerializer(token.user).data,
        }, status=status.HTTP_200_OK)


class ResendOtpView(APIView):
    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = Token.objects.get(token=serializer.validated_data['token'])
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

        otp = token.regenerate_otp()
        send_otp(token.user, otp)

        return Response({'message': 'OTP resent successfully.', 'otp': otp}, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = Token.objects.get(token=serializer.validated_data['token'])
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

        if not token.is_verified:
            return Response({'error': 'Token is not verified.'}, status=status.HTTP_400_BAD_REQUEST)

        token.refresh()
        return Response({'message': 'Token refreshed successfully.', 'token': token.token}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        serializer = UpdateUserSerializer(request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)
