from django.shortcuts import render
from .serialazers import *
from blog.models import Post
from shop.models import Product
from rest_framework.viewsets import ReadOnlyModelViewSet


class PostViewSet(ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_published=True)

class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
