from django.contrib import admin
from .models import User, OneTimePassword, UserProfile

# Register your models here.

admin.site.register(User)
admin.site.register(OneTimePassword)
admin.site.register(UserProfile)
