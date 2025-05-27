from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from account.serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"])
	@extend_schema(request=RegisterSerializer, auth=[])
	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(status=status.HTTP_201_CREATED)


class LoginView(APIView):
	permission_classes = [AllowAny]

	@extend_schema(tags=["Authentication"])
	@extend_schema(request=LoginSerializer, auth=[])
	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')
		user = authenticate(request, email=email, password=password)
		if user is None:
			return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

		if not user.is_verified:
			return Response({"detail": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

		refresh = RefreshToken.for_user(user)
		return Response({
			'email': user.email,
			'full_name': user.full_name,
			'access': str(refresh.access_token),
		}, status=status.HTTP_200_OK)

