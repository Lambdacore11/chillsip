from django.shortcuts import redirect,render,get_object_or_404
from django.urls import reverse, reverse_lazy
from .forms import *
from django.contrib.auth import views
from django.views.generic import UpdateView
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models import F


def user_register_view(request):

    form = UserRegisterForm()

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.set_password(cd['password'])
            new_user.save()
            return render(request,'account/register_done.html')
    
    
    return render (request,'account/register.html',{'form':form})


class UserLoginView(views.LoginView):
    form_class = UserLoginForm
    template_name = 'account/login.html'

class UserLogoutView(views.LogoutView):
    template_name = 'account/logout.html'


class UserPasswordChangeView(views.PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'account/password_change.html'
    success_url = reverse_lazy('account:password_change_done')

class UserPasswordChangeDoneView(views.PasswordChangeDoneView):

    template_name = 'account/password_change_done.html'


class UserPasswordResetView(views.PasswordResetView):

    template_name = 'account/password_reset.html'
    email_template_name = 'account/password_reset_email.html'
    success_url = reverse_lazy('account:password_reset_done')

class UserpasswordResetDoneView(views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class UserPasswordResetConfirmView(views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')

class UserPasswordResetCompleteView(views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserUpdateView(UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'account/profile.html'
    def get_success_url(self):
        return reverse('account:profile', kwargs={'slug': self.request.user.slug})


def money_update_view(request,slug):

    form = MoneyUpdateForm()

    if request.method == 'POST':
        user = get_object_or_404(get_user_model(),slug=slug)
        user.account = F('account') + Decimal(request.POST['account'])
        user.save()
        return redirect('account:money_done')
    
    else:
        return render(request,'account/money.html',{'form':form})


def money_done(request):
    return render(request,'account/money_done.html')
