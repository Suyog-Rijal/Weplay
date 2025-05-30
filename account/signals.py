import threading
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import send_verification_email_async, generate_token

User = get_user_model()


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
	if created:
		try:
			threading.Thread(target=send_verification_email_async, args=(instance, generate_token(instance))).start()
		except Exception as e:
			print("Error preparing verification email:", e)
