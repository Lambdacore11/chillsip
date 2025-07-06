from django.shortcuts import redirect
from django.urls import reverse,reverse_lazy
from django.contrib.auth import views,get_user_model
from django.views.generic import UpdateView
from django.db.models import F
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin,AccessMixin
from django.views.generic import TemplateView,FormView,CreateView
from .forms import *
from .models import SuspiciousUser


class UserRegisterView(CreateView):
    model = get_user_model()
    form_class = UserRegisterForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('account:register_done')

class UserRegisterDoneView(TemplateView):
    template_name = 'account/register_done.html'

class UserLoginView(views.LoginView):
    form_class = UserLoginForm
    template_name = 'account/login.html'
    
class UserLogoutView(LoginRequiredMixin,views.LogoutView):
    template_name = 'account/logout.html'


class UserPasswordChangeView(LoginRequiredMixin,views.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'account/password_change.html'
    success_url = reverse_lazy('account:password_change_done')
    
class UserPasswordChangeDoneView(LoginRequiredMixin,views.PasswordChangeDoneView):
    template_name = 'account/password_change_done.html'


class UserPasswordResetView(views.PasswordResetView):
    template_name = 'account/password_reset.html'
    email_template_name = 'account/password_reset_email.html'
    success_url = reverse_lazy('account:password_reset_done')
   
class UserPasswordResetDoneView(views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class UserPasswordResetConfirmView(views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')
   
class UserPasswordResetCompleteView(views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'
    

class UserUpdateView(AccessMixin,UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'account/profile.html'
    
    def get_success_url(self):
        return reverse('account:profile', kwargs={'slug': self.request.user.slug})
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        expected_slug = kwargs.get('slug')

        if request.user.slug != expected_slug:
            SuspiciousUser.objects.create(
                user=request.user,
                reason = f"Пытался получить доступ к профилю пользователя {expected_slug}"
            )
            return redirect(self.get_success_url())
        
        return super().dispatch(request, *args, **kwargs)


class MoneyUpdateView(AccessMixin,FormView):
    model = get_user_model()
    form_class = MoneyUpdateForm
    template_name = 'account/money_update.html'
    success_url = reverse_lazy('account:money_done')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        expected_slug = kwargs.get('slug')
        
        if request.user.slug != expected_slug:
            SuspiciousUser.objects.create(
                user=request.user,
                reason = f"Пытался получить доступ к счету пользователя {expected_slug}"
            )
            return redirect('account:profile',slug=request.user.slug)
        
        return super().dispatch(request, *args, **kwargs)
        
    def form_valid(self, form):
        cd = form.cleaned_data
        self.request.user.account = F('account') + cd['account']
        self.request.user.save(update_fields=['account'])
        self.request.user.refresh_from_db()
        return super().form_valid(form)  

class MoneyDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'account/money_done.html'
