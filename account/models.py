from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group as DefaultGroup,BaseUserManager
from django.core.validators import MinValueValidator,MaxValueValidator
from autoslug import AutoSlugField 


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        if not password:
            raise ValueError("Суперпользователь должен иметь пароль")
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    GENDER_CHOICES = (
        ('m','Мужской'),
        ('f','Женский'),
    )
    id = models.UUIDField(primary_key=True,
        default=uuid4, 
        editable=False,
        verbose_name='UUID',
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": ("Пользователь с такой электронной почтой уже существует"),
        },
    )
    middle_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )
    slug = AutoSlugField(
        populate_from='username',
        max_length=200,
        unique=True,
        verbose_name='Slug',
        error_messages={
            "unique": ("Пользователь с таким именем уже существует"),
        },
    )
    account = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='Баланс',
    )
    foto= models.ImageField(
        upload_to='foto/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Фотография',
    )
    age = models.IntegerField(
        validators=[MinValueValidator(1),MaxValueValidator(150)],
        blank=True,
        null=True,
        verbose_name='Возраст',
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='Пол'
    )
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.username} {self.email}'  

class SuspiciousUser(models.Model):
    id = models.UUIDField(primary_key=True,
        default=uuid4, 
        editable=False,
        verbose_name='UUID',
    )
    user = models.ForeignKey(
        User,
        related_name='suspicions',
        on_delete= models.CASCADE,
        verbose_name= 'Пользователи'
    )
    reason = models.TextField(verbose_name='Причина')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Создан')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Подозрительный пользователь'
        verbose_name_plural = 'Подозрительные пользователи'


class Group(DefaultGroup):
    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        proxy = True


