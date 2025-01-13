from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import UserManager
from django.contrib.auth import get_user_model
import uuid


# Create your models here.

AUTH_PROVIDERS = {
    "email": "email",
    "google": "google"
}

class User(AbstractBaseUser, PermissionsMixin):

    id = models.BigAutoField(primary_key=True, editable=False)
    email = models.EmailField(max_length=255, verbose_name= _("Email Address"), unique=True)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    profile_picture = models.TextField(null= True, blank= True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get("email"))
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def tokens(self):
        token = RefreshToken.for_user(self)
        return {
            "refresh_token": str(token),
            "access_token": str(token.access_token)
        }
    
    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)


class OneTimePassword(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)


class PasswordResetOtp(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = self.generate_unique_otp()
        super().save(*args, **kwargs)

    def generate_unique_otp(self):
        while True:
            otp = str(uuid.uuid4().int)[:8]
            if not PasswordResetOtp.objects.filter(otp=otp).exists():
                return otp
