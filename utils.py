import secrets

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from account.models import Tokens, default_expiry

test_emails = [
	"rijalsuyog75@gmail.com",
	"dikshyadevkota59@gmail.com"
]


def send_verification_email_async(user, token):
	try:
		if user.email not in test_emails:
			print(f"Skipping email for {user.email} as it is not in the test emails list.")
			return
		context = {
			'user': user,
			'token': token,
		}
		html_content = render_to_string('emails/verify.html', context)
		subject = "Verify your Weplay account"
		from_email = settings.DEFAULT_FROM_EMAIL
		to_email = user.email

		email = EmailMultiAlternatives(subject, "", from_email, [to_email])
		email.attach_alternative(html_content, "text/html")
		email.send()
	except Exception as e:
		print("Error sending verification email:", e)


def send_password_reset_email_async(user, token):
	try:
		context = {
			'user': user,
			'token': token,
		}
		html_content = render_to_string('emails/reset_password.html', context)
		subject = "Reset your Weplay password"
		from_email = settings.DEFAULT_FROM_EMAIL
		to_email = user.email

		email = EmailMultiAlternatives(subject, "", from_email, [to_email])
		email.attach_alternative(html_content, "text/html")
		email.send()
	except Exception as e:
		print("Error sending password reset email:", e)


def generate_token(user):
	auth_token = ''.join(secrets.choice('0123456789') for _ in range(6))
	existing_token = Tokens.objects.filter(user=user).first()
	if existing_token:
		existing_token.token = auth_token
		existing_token.expiry = default_expiry()
		existing_token.save()
	else:
		Tokens.objects.create(user=user, token=auth_token)
	return auth_token
