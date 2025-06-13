from django.urls import path
from .views import *

app_name = 'shop'

urlpatterns = [
    path('about/',AboutTemplateView.as_view(),name='about'),

    path('order/received/<uuid:id>/',OrderReceivedView.as_view(),name='order_received'),
    path('order/create/',OrderCreateView.as_view(),name='order_create'),
    path('order/',OrderListView.as_view(),name='order_list'),

    path('cart/decrement/<uuid:id>/',CartDecrementView.as_view(),name='cart_decrement'),
    path('cart/increment/<uuid:id>/',CartIncrementView.as_view(),name='cart_increment'),
    path('cart/delete/<uuid:id>/',CartDeleteProductView.as_view(),name='cart_delete'),
    path('cart/add/<uuid:id>/',CartAddProductView.as_view(),name='cart_add'),
    path('cart/',CartListView.as_view(),name='cart_list'),

    path('review/delete/<id>/',ReviewDeleteView.as_view(),name='review_delete'),
    path('product/<slug:slug>/',ProductDetailView.as_view(),name='product_detail'),
    path('<slug:category_slug>/',ProductListView.as_view(),name='product_list_by_category'),
    path('',ProductListView.as_view(),name='product_list'),
]