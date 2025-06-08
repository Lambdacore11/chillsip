from django.urls import path
from .views import *
from django.urls import reverse_lazy

app_name = 'account'

urlpatterns = [

    path('register/',user_register_view,name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('logout/',UserLogoutView.as_view(),name='logout'),
    
    path('profile/<slug:slug>/',UserUpdateView.as_view(),name='profile'),

    path('money/done/',money_done,name='money_done'),
    path('money/<slug:slug>/',money_update_view,name='money'),

    path('password-change/',UserPasswordChangeView.as_view(),name='password_change'),
    path('password-change/done/',UserPasswordChangeDoneView.as_view(),name='password_change_done'),

    path('password-reset/',UserPasswordResetView.as_view(),name='password_reset'),
    path('password-reset/done/',UserPasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',UserPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',UserPasswordResetCompleteView.as_view(),name='password_reset_complete'),
]