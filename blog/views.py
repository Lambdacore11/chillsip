from django.shortcuts import get_object_or_404,redirect
from django.urls import reverse_lazy
from .models import *
from django.views import View
from django.views.generic import ListView,DetailView,CreateView,TemplateView
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator


class PostListView(ListView):
    queryset = Post.objects.filter(is_published = True).order_by('-created')
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'
    paginate_by = 3
    extra_context = {
        'site_section':'post_list'
    }


class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'
    success_url = reverse_lazy('blog:post_done')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
        

class PostCreateDoneView(LoginRequiredMixin,TemplateView):
    template_name = 'blog/post_done.html'


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'
    extra_context = {

        'form':CommentForm(),
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.all()
        paginator = Paginator(comments,5)
        page = self.request.GET.get('page')
        context['comments'] = paginator.get_page(page)
        return context


class CommentCreateView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
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


class CommentDeleteView(LoginRequiredMixin,View):
    def post(self,request,id,*args,**kwargs):
        comment = get_object_or_404(Comment,id=id,user=request.user)
        post = get_object_or_404(Post,id = comment.post_id)
        comment.delete()

        return redirect(post.get_absolute_url())





    