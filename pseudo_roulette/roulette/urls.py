from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SpinRouletteView, RouletteParticipantsView, ActiveUsersView, RegisterUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='roulette/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='register'), name='logout'),
    path('spin_roulette/', SpinRouletteView.as_view(), name='spin_roulette'),
    path('roulette-participants/', RouletteParticipantsView.as_view(), name='roulette-participants'),
    path('active-users/', ActiveUsersView.as_view(), name='active-users'),
]
