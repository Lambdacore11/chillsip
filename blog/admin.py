from django.contrib import admin
from .models import *


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'content',
        'image',
        'created',
        'updated'
    ]
    list_filter = [
        'created'
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
   
