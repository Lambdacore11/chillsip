from django.contrib import admin
from .models import *


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'content',
        'is_published',
        'image',
        'created',
        'updated',
    ]
    list_filter = [
        'is_published',
        'created',
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'content',
        'post',
        'created',
        'updated',
    ]
    list_filter = [
        'user',
        'post',
        'created',
    ]
   
