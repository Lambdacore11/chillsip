from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group as DefaultGroup
from django.core.validators import MinValueValidator,MaxValueValidator
from autoslug import AutoSlugField 


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
    
    def __str__(self):
        return f'{self.username} {self.email}'  


class Group(DefaultGroup):

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        proxy = True


