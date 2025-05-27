from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

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