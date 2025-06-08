from django.urls import path
from .views import *

app_name= 'blog'

urlpatterns = [
    path('comment/delete/<id>/',comment_delete_view,name='comment_delete'),
    path('comment/create',comment_create_view,name='comment_create'),
    path('<slug:slug>',PostDetailView.as_view(),name='post_detail'),
    path('',PostListView.as_view(),name='post_list'),
]