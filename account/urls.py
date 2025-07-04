from django.urls import path
from account.views import RegisterView, LoginView, GoogleAuthView, MeView, ForgotPasswordView, VerifyView, \
	ResendVerificationView, VerifyJwtView

urlpatterns = [
	path('me/', MeView.as_view(), name='me'),

	path('register/', RegisterView.as_view(), name='register'),
	path('login/', LoginView.as_view(), name='login'),
	path('google-auth/', GoogleAuthView.as_view(), name='google_auth'),
	path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
	path('email-verification/', VerifyView.as_view(), name='verify'),
	path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
	path('jwt-verify/', VerifyJwtView.as_view(), name='verify_jwt'),
]