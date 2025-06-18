from django.urls import path
from .views import *

app_name= 'blog'

urlpatterns = [
    path('comment/delete/<id>/',CommentDeleteView.as_view(),name='comment_delete'),
    path('comment/create/',CommentCreateView.as_view(),name='comment_create'),
    
    path('create/done', PostCreateDoneView.as_view(),name='post_done'),
    path('create/',PostCreateView.as_view(),name='post_create'),
    path('post/<slug:slug>/',PostDetailView.as_view(),name='post_detail'),
    path('',PostListView.as_view(),name='post_list'),
]