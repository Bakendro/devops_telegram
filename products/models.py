from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Product(models.Model):
    name= models.CharField(max_length=255)
    description = models.TextField()
    price=models.DecimalField(max_digits=10, decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

# Кастомный менеджер для пользователей
class UserTelegramManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # Используйте метод set_password для хэширования пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)
    
class UserTelegram(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Подключаем кастомный менеджер
    objects = UserTelegramManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']
    
    def __str__(self):
        return self.name
# Create your models here.
