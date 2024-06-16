from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.handleSignup, name='register'),
    path('login/', views.handlelogin, name='login'),
    path('logout/', views.handleLogout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/update/', views.profile_update, name='profile_update'),
]
