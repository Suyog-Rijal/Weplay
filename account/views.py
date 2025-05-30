from django.conf import settings
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import threading
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from account.serializers import RegisterSerializer, LoginSerializer, GoogleAuthSerializer, MeSerializer, \
	ForgotPasswordSerializer, VerifySerializer, ResendVerificationSerializer
from django.contrib.auth import get_user_model
from utils import generate_token, send_verification_email_async

User = get_user_model()


class RegisterView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"], request=RegisterSerializer, auth=[])
	def post(self, request):
		print(request.data)
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(status=status.HTTP_201_CREATED)


class LoginView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"], request=LoginSerializer, auth=[])
	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')
		user = authenticate(request, email=email, password=password)
		if user is None:
			return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

		if not user.is_verified:
			threading.Thread(target=send_verification_email_async, args=(user, generate_token(user))).start()
			return Response({"detail": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

		refresh = RefreshToken.for_user(user)
		return Response({
			'email': user.email,
			'full_name': user.full_name,
			'token': str(refresh.access_token),
		}, status=status.HTTP_200_OK)


class GoogleAuthView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"], request=GoogleAuthSerializer, auth=[])
	def post(self, request):
		serializer = GoogleAuthSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		token = serializer.validated_data['token']

		try:
			id_info = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
			email = id_info.get('email')
			full_name = id_info.get('name')
			profile_picture = id_info.get('picture') or None

			user, created = User.objects.get_or_create(
				email=email,
				defaults={
					'full_name': full_name,
					'profile_picture': profile_picture,
					'is_google_account': True
				}
			)

			refresh = RefreshToken.for_user(user)
			return Response({
				'email': user.email,
				'full_name': user.full_name,
				'access': str(refresh.access_token),
			}, status=status.HTTP_200_OK)
		except Exception as e:
			print(f"Error during Google authentication: {e}")
			return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(tags=["Authentication"], responses=MeSerializer)
	def get(self, request):
		try:
			serializer = MeSerializer(request.user)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception as e:
			print(f"Error fetching user data: {e}")
			return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgotPasswordView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"], request=ForgotPasswordSerializer, auth=[])
	def post(self, request):
		serializer = ForgotPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		email = serializer.validated_data['email']
		try:
			user = User.objects.get(email=email)
			token = generate_token(user)
			threading.Thread(target=send_verification_email_async, args=(user, token)).start()
		except Exception as e:
			print("First check point")
			print(f"Error in forgot password: {e}")
			return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"], auth=[], request=VerifySerializer)
	def post(self, request):
		try:
			email = request.data.get('email')
			token_value = request.data.get('token')

			user = User.objects.filter(email=email).first()
			if not user:
				return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

			if user.is_verified:
				return Response({'detail': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

			token_obj = getattr(user, 'token', None)
			if not token_obj:
				return Response({'detail': 'Verification token not found.'}, status=status.HTTP_400_BAD_REQUEST)

			if token_obj.token != token_value:
				return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

			if timezone.now() > token_obj.expiry:
				return Response({'detail': 'Token has expired.'}, status=status.HTTP_400_BAD_REQUEST)

			user.is_verified = True
			user.save()
			token_obj.delete()

			return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)

		except Exception as e:
			print(f"Error in verification: {e}")
			return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["Authentication"], auth=[], request=ResendVerificationSerializer)
class ResendVerificationView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		try:
			serializer = ResendVerificationSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			email = serializer.validated_data['email']
			user = User.objects.filter(email=email).first()
			threading.Thread(target=send_verification_email_async, args=(user, generate_token(user))).start()
			return Response({'detail': 'Verification email sent.'}, status=status.HTTP_200_OK)
		except Exception as e:
			print(f"Error in resend verification: {e}")
			return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
