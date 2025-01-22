from django.db import models
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        
        # Ensure that full_name is passed when creating the user instance
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, full_name, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    full_name = models.CharField(max_length=100, null=True, blank=True)  # Ensure full_name is here
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Make sure full_name is in the REQUIRED_FIELDS

    def __str__(self):
        return self.email

# TemporaryUser model to store OTP and registration data temporarily
def get_otp_expiry():
    return now() + timedelta(minutes=5)

class TemporaryUser(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(default=now)
    otp_expiry = models.DateTimeField(default=get_otp_expiry)
    full_name = models.CharField(max_length=100, null=True, blank=True)  # Store full_name temporarily
    password = models.CharField(max_length=128)  # Save hashed password temporarily

    def is_otp_valid(self):
        return self.otp_expiry >= now()
