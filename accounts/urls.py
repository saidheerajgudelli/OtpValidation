from django.urls import path
from .views import RegisterUser, VerifyRegisterOTP, LoginSendOTP,VerifyLoginOTP

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('verify-register-otp/', VerifyRegisterOTP.as_view(), name='verify_register_otp'),
    path('login-send-otp/', LoginSendOTP.as_view(), name='login_send_otp'),
    path('verify-login-otp/', VerifyLoginOTP.as_view(), name='login_through_otp'),
]
