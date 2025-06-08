from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'count',
        'image',
        'description',
        'price',
        'created',
        'updated',
    ]
    list_filter = ['category']

@admin.register(ProductInCart)
class ProductInCartAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'product',
        'price',
        'count',
        'created'
    ]
    list_filter = ['user','product','created']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'street',
        'is_private',
        'building',
        'apartment',
        'created',
        'is_delivered',
    ]
    list_filter = ['user','street','created','is_delivered']

@admin.register(ProductInOrder)
class ProductInOrderAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'price',
        'order',
        'count',
        'created',
    ]
    list_filter = ['product','order','created']


@admin.register(UsersProducts)
class UsersProductsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'product',
        'rating',
        'review',
        'created',
    ]
    list_filter = ['user','product','rating','created']



