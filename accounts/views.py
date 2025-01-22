import random
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, TemporaryUser
from django.contrib.auth.hashers import make_password

class RegisterUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        full_name = request.data.get('full_name')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email is already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        otp_expiry = now() + timedelta(minutes=5) 
        temp_user, created = TemporaryUser.objects.update_or_create(
            email=email,
            defaults={
                'otp': otp,
                'otp_created_at': now(),
                'otp_expiry': otp_expiry,
                'full_name': full_name,
                'password': make_password(password),  # Hash the password before storing
            }
        )

        # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp}. It is valid for 5 minutes.',
            'saidheerajgudelli@example.com',
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

# API view to verify OTP and complete user registration
class VerifyRegisterOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the temporary user
        temp_user = get_object_or_404(TemporaryUser, email=email)

        # Check OTP expiration
        if temp_user.otp_expiry < now():
            temp_user.delete()  # Remove expired data
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        if temp_user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Move temporary user data to the main user table
        User.objects.create_user(
            email=temp_user.email,
            full_name=temp_user.full_name,  # Pass full_name correctly here
            password=temp_user.password,  # This is already hashed
        )

        # Remove temporary user data after successful registration
        temp_user.delete()

        return Response({"message": "Email verified successfully and user registered"}, status=status.HTTP_200_OK)

# API view to send OTP for login
class LoginSendOTP(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists in the database
        user = get_object_or_404(User, email=email)

        
        otp = str(random.randint(100000, 999999))
        otp_expiry = now() + timedelta(minutes=5)  
        temp_user, _ = TemporaryUser.objects.update_or_create(
            email=email,
            defaults={'otp': otp, 'otp_created_at': now(), 'otp_expiry': otp_expiry},
        )
        # Send OTP via email
        send_mail(
            'Your OTP Code for Login',
            f'Your OTP is {otp}. It is valid for 5 minutes.',
            'your_email@example.com',
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

# API view to verify OTP for login and complete user login
class VerifyLoginOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the temporary user
        temp_user = get_object_or_404(TemporaryUser, email=email)

        # Check OTP expiration
        if temp_user.otp_expiry < now():
            temp_user.delete()  # Remove expired data
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        if temp_user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email exists in the main User table
        user = get_object_or_404(User, email=email)

        # OTP is valid, and user is found. Now we delete the temporary user data.
        temp_user.delete()

        # Return success message (user is logged in)
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
