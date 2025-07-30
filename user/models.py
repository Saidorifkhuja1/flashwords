import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models


PHONE_REGEX = RegexValidator(
    regex=r"^\+998([0-9][0-9]|99)\d{7}$",
    message="Please provide a valid phone number",
)

class UserManager(BaseUserManager):
    def create_user(self, phone_number, last_name, name, email, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('User must have a phone number')
        if not name:
            raise ValueError('User must have a name')
        if not last_name:
            raise ValueError('User must have a last name')
        if not email:
            raise ValueError('User must have an email')

        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            name=name,
            last_name=last_name,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, last_name, name, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROlE_CHOICES = [
        ('student', 'STUDENT'),
        ('Teacher', 'TEACHER'),
    ]
    STATUS_CHOICES = [
        ('active', 'ACTIVE'),
        ('pending', 'PENDING'),
        ('disabled', 'DISABLED'),
        ('blocked', 'BLOCKED'),
    ]
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    phone_number = models.CharField(validators=[PHONE_REGEX], max_length=21, unique=True, default="+998931112233", blank=True, null=True)
    email = models.EmailField(unique=True)
    notification_token = models.CharField(max_length=250, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True, null=True)
    mini_avatar = models.ImageField(upload_to='accounts/mini_avatars/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROlE_CHOICES, default='student')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name', 'phone_number']

    def __str__(self):
        return f'{self.name} {self.last_name}'

    @property
    def is_staff(self):
        return self.is_admin








