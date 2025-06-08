from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.views.generic import ListView,DetailView
from .forms import CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

class PostListView(ListView):
    queryset = Post.objects.filter(is_published = True)
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'
    extra_context = {
        'site_section':'post_list'
    }

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'
    extra_context = {

        'form':CommentForm(),
    }

@login_required 
@require_POST
def comment_create_view(request):
    form = CommentForm(request.POST)
    post = get_object_or_404(Post,id = request.POST['post_id'])
    if form.is_valid():
        cd = form.cleaned_data
        Comment.objects.create(
            user = request.user,
            post = post,
            content = cd['content'],
        )
        return redirect(post)

@require_POST
def comment_delete_view(request,id):
    comment = get_object_or_404(Comment,id=id)
    post = get_object_or_404(Post,id = comment.post_id)
    comment.delete()
    return redirect(post.get_absolute_url())


    