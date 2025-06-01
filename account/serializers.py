from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from account.models import Tokens

User = get_user_model()


class RegisterSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ('full_name', 'email', 'password')

	def validate_password(self, value):
		validate_password(value)
		return value

	def create(self, validated_data):
		user = User(
			full_name=validated_data['full_name'],
			email=validated_data['email']
		)
		user.set_password(validated_data['password'])
		user.save()
		return user


class LoginSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ('email', 'password')


class GoogleAuthSerializer(Serializer):
	token = serializers.CharField(max_length=500, write_only=True)


class MeSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = "__all__"
		extra_kwargs = {
			'password': {'write_only': True},
			'last_login': {'write_only': True},
			'is_superuser': {'write_only': True},
			'groups': {'write_only': True},
			'user_permissions': {'write_only': True},
			'is_active': {'write_only': True},
			'is_staff': {'write_only': True},
			'is_google_account': {'write_only': True},
		}


class ForgotPasswordSerializer(Serializer):
	email = serializers.EmailField(max_length=255, write_only=True)

	def validate_email(self, value):
		if not User.objects.filter(email=value).exists():
			raise serializers.ValidationError("User with this email does not exist.")
		return value


class VerifySerializer(Serializer):
	email = serializers.EmailField(max_length=255, write_only=True)
	token = serializers.CharField(max_length=6, write_only=True)


class ResendVerificationSerializer(Serializer):
	email = serializers.EmailField(max_length=255, write_only=True)


class VerifyJwtSerializer(Serializer):
	token = serializers.CharField(max_length=500, write_only=True)
