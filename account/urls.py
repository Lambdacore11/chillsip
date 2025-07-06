from django.urls import path
from .views import *

app_name = 'account'

urlpatterns = [
    path('register/done',UserRegisterDoneView.as_view(),name='register_done'),
    path('register/',UserRegisterView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('logout/',UserLogoutView.as_view(),name='logout'),
    
    path('profile/<slug:slug>/',UserUpdateView.as_view(),name='profile'),

    path('money/done/',MoneyDoneView.as_view(),name='money_done'),
    path('money/update/<slug:slug>/',MoneyUpdateView.as_view(),name='money_update'),

    path('password-change/',UserPasswordChangeView.as_view(),name='password_change'),
    path('password-change/done/',UserPasswordChangeDoneView.as_view(),name='password_change_done'),

    path('password-reset/',UserPasswordResetView.as_view(),name='password_reset'),
    path('password-reset/done/',UserPasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',UserPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',UserPasswordResetCompleteView.as_view(),name='password_reset_complete'),
]