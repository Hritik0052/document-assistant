from django.contrib.auth import authenticate
from rest_framework import serializers

from myapp.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'phone', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    fcm_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs


class VerifyOtpSerializer(serializers.Serializer):
    token = serializers.CharField()
    otp = serializers.CharField()


class ResendOtpSerializer(serializers.Serializer):
    token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name']
