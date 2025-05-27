from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from account.manager import UserManager
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractBaseUser, PermissionsMixin):
	full_name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	profile_picture = models.FileField(upload_to='profile_pictures/', blank=True, null=True)
	is_google_account = models.BooleanField(default=False)

	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_verified = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['full_name']

	objects = UserManager()

	class Meta:
		ordering = ('-created_at',)
		verbose_name = 'User'
		verbose_name_plural = 'Users'

	def __str__(self):
		return self.email


def default_expiry():
	return timezone.now() + timedelta(minutes=10)


class Tokens(models.Model):
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
	token = models.CharField(max_length=6)
	expiry = models.DateTimeField(default=default_expiry)

	created_at = models.DateTimeField(auto_now_add=True)
