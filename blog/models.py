from django.db import models
from uuid import uuid4
from django.conf import settings
from autoslug import AutoSlugField
from django.urls import reverse


class Post(models.Model):

    id = models.UUIDField(primary_key=True,
        default=uuid4, 
        editable=False,
        verbose_name='UUID',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Название'
    )
    slug = AutoSlugField(
        populate_from='name',
        max_length=200,
        unique=True,
        verbose_name='Slug',
    )
    content = models.TextField(
        verbose_name= 'Содержимое'
    )
    image = models.ImageField(
        upload_to='posts/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликован'
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
            models.Index(fields=['-created']),
            models.Index(fields=['slug'])
        ]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
    
    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.slug
            ]
        )

    def __str__(self):
        return self.name


class Comment(models.Model):

    id = models.UUIDField(primary_key=True,
        default=uuid4, 
        editable=False,
        verbose_name='UUID',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользователь'
    )
    content = models.TextField(
        verbose_name= 'Содержимое'
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
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Комментарии'
    
    def __str__(self):
        return self.content
