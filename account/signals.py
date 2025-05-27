from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from account.models import Tokens
import random

User = get_user_model()


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
	if created:
		try:
			auth_token = str(random.randint(100000, 999999))
			existing_token = Tokens.objects.get(user=instance)
			if existing_token:
				existing_token.token = auth_token
				existing_token.save()
			else:
				Tokens.objects.create(user=instance, token=auth_token)

			context = {
				'user': instance,
				'token': auth_token,
			}

			html_message = render_to_string('emails/verify.html', context)
			subject = "Verify your Weplay account"
			from_email = settings.DEFAULT_FROM_EMAIL
			to_email = instance.email

			send_mail(
				subject=subject,
				message="",
				html_message=html_message,
				from_email=from_email,
				recipient_list=[to_email],
				fail_silently=False,
			)
		except Exception as e:
			print("Error sending verification email:", e)
			pass
