from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid
from datetime import timedelta
from django.utils.timezone import now


class UserManager(BaseUserManager):
    def create_user(self, email, mobile, first_name, last_name, password=None):
        if not email:
            raise ValueError('Email is required')
        if not mobile:
            raise ValueError('Mobile number is required')

        user = self.model(
            email=self.normalize_email(email),
            mobile=mobile,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile, first_name, last_name, password):
        user = self.create_user(
            email=email,
            mobile=mobile,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=13, unique=True)  # حداکثر طول برای +98xxxxxxxxxx
    first_name = models.CharField(max_length=30, default="")
    last_name = models.CharField(max_length=30, default="")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    verify_code = models.CharField(max_length=6, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(minutes=2)
