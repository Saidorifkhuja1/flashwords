import json, random
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .utils import unhash_token
from django.contrib.auth.hashers import make_password, check_password


class SendVerificationCodeAPIView(APIView):
    @swagger_auto_schema(request_body=SendVerificationCodeSerializer)
    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data['email']
        phone_number = data['phone_number']
        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            return Response({"error": "Bu email allaqachon ro\'yxatdan o\'tgan ."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Bu telefon  allaqachon ro\'yxatdan o\'tgan ."}, status=status.HTTP_400_BAD_REQUEST)
        # Generate verification code
        code = str(random.randint(100000, 999999))

        # Store user details in cache temporarily
        cache_key = f"register-temp-{email}"
        cache.set(cache_key, json.dumps({
            "name": data['name'],
            "last_name": data['last_name'],
            "phone_number": data['phone_number'],
            "password": data['password'],
            "code": code
        }), timeout=300)

        # Send email with verification code
        message = f"Your verification code is: {code}"
        email_msg = EmailMessage("Email Verification", message, to=[email])
        email_msg.send(fail_silently=False)

        return Response({"message": "Tasdiqlash kodi sizning email pochtangizga jo\'natildi ."}, status=status.HTTP_200_OK)



class VerifyCodeAPIView(APIView):
    @swagger_auto_schema(request_body=VerifyCodeSerializer)
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        cached_data = cache.get(f"register-temp-{email}")

        if not cached_data:
            return Response({"error": "Verification code expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

        data = json.loads(cached_data)

        if data['code'] != code:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

        # Check both email and phone_number
        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=data["phone_number"]).exists():
            return Response({"error": "User with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            name=data['name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            email=email,
            role=data.get("role", "student"),
            is_verified=True
        )
        user.set_password(data['password'])
        user.save()

        refresh = RefreshToken.for_user(user)
        cache.delete(f"register-temp-{email}")

        return Response({
            "uid": user.uid,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User account created and logged in successfully."
        }, status=status.HTTP_201_CREATED)


class RetrieveProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uid'

    def get(self, request, *args, **kwargs):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token.get('user_id')

        if not user_id:
            raise NotFound("User not found")

        user = get_object_or_404(User, uid=user_id)
        serializer = self.get_serializer(user)

        return Response(serializer.data)


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uid"

    def get_queryset(self):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token.get('user_id')
        return User.objects.filter(uid=user_id)


class PasswordUpdate(APIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        decoded_token = unhash_token(request.headers)
        user_id = decoded_token.get("user_id")
        if not user_id:
            raise AuthenticationFailed("User ID not found in token")

        user = get_object_or_404(User, uid=user_id)
        if not check_password(serializer.validated_data['old_password'], user.password):
            return Response({"error": "Incorrect old password!"}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


class DeleteProfileAPIView(generics.DestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uid'

    def get_queryset(self):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token.get('user_id')
        return User.objects.filter(uid=user_id)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"message": "User successfully deleted"}, status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        if not User.objects.filter(email=email).exists():
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        code = f"{random.randint(100000, 999999)}"
        cache.set(f"reset-code-{email}", code, timeout=300)

        EmailMessage("Reset your password", f"Your password reset code is: {code}", to=[email]).send()

        return Response({"message": "Verification code sent to your email."})


class PasswordResetConfirmView(APIView):
    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        cached_code = cache.get(f"reset-code-{email}")
        if not cached_code:
            return Response({"error": "Verification code expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

        if code != cached_code:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            cache.delete(f"reset-code-{email}")
            return Response({"message": "Password has been reset successfully."})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
