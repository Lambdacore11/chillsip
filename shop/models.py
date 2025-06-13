from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4
from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator,MaxValueValidator


class Street(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name='UUID',
    )
    name = models.CharField(max_length=150,
        unique=True,
        verbose_name='Название улицы'
    )

    class Meta:
        
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

        verbose_name = 'Улица'
        verbose_name_plural = 'Улицы'
    
    def __str__(self):
        return self.name


class Category(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name='UUID',
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Название',
    )
    slug = AutoSlugField(
        populate_from='name',
        max_length=200,
        unique=True,
        always_update=True,
        verbose_name='Slug',
    )
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',args=[self.slug])


class Product(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name='UUID',
    )
    category = models.ForeignKey(
        Category,related_name='products',
        on_delete=models.CASCADE,
        verbose_name='Категория',
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Название',
    )
    slug = AutoSlugField(
        populate_from='name',
        max_length=200,
        unique=True,
        always_update=True,
        verbose_name='Slug',
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена',
    )
    count = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Количество',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Изменен',
    )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail',args=[self.slug])
    
    def get_average_rating_url(self):
        average = self.feedback.aggregate(avg=models.Avg('rating'))['avg'] or 0
        rounded = (Decimal(average) * 2).quantize(Decimal('1'), rounding=ROUND_HALF_UP) / 2
        return f'images/rating/{rounded}.png'
    
    
class Cart(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name='UUID',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователи',
    )
    product = models.ForeignKey(
        Product,
        related_name='carts',
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена',
    )
    count = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=1,
        verbose_name='Количество',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

    def __str__(self):
        return str(self.product)

    def get_cost(self):
        return (self.price * self.count)
    

class Order(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name='UUID',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    street = models.ForeignKey(
        Street,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Улица',
    )
    is_private = models.BooleanField(
        verbose_name= 'Частный дом'
    )
    building = models.CharField(
        max_length= 100,
        verbose_name='Дом',
    )
    apartment = models.CharField(
        max_length=100,
        blank = True,
        null = True,
        verbose_name='Квартира',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )
    is_delivered = models.BooleanField (
        default = False,
        verbose_name= 'Доставлен',
    )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f'{self.id}'




class ProductInOrder(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name='UUID',
    )
    product = models.ForeignKey(
        Product,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена',
    )
    order = models.ForeignKey(
        Order,
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        )
    count = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return str(self.product)


class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='feedback',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    product = models.ForeignKey(
        Product,
        related_name='feedback',
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(5)],
        default= 0,
        verbose_name= 'Рейтинг',
    )
    review = models.TextField(
        blank=True,
        null=True,
        verbose_name= 'Обзор',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'





