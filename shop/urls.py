from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('about/',about_view,name='about'),

    path('order/recieved/<uuid:id>/',order_recieved_view,name='order_recieved'),
    path('order/create/',order_create_view,name='order_create'),
    path('order/',order_list_view,name='order_list'),

    path('cart/decrement/<uuid:id>/',cart_decrement_view,name='cart_decrement'),
    path('cart/increment/<uuid:id>/',cart_increment_view,name='cart_increment'),
    path('cart/delete/<uuid:id>/',cart_delete_product_view,name='cart_delete'),
    path('cart/add/<uuid:id>/',cart_add_product_view,name='cart_add'),
    path('cart/',cart_view,name='cart'),

    path('review/delete/<id>/',review_delete_view,name='review_delete'),
    path('product/<slug:slug>/',product_detail_view,name='product_detail'),
    path('<slug:category_slug>/',product_list_view,name='product_list_by_category'),
    path('',product_list_view,name='product_list'),
]