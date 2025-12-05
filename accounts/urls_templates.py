# accounts/urls_templates.py - DESCOMENTAR DASHBOARD
from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard e perfil
    path('dashboard/', views.dashboard, name='dashboard'),  # ← DESCOMENTAR
    # path('profile/', views.profile_view, name='profile'),
    
    # Gestão (apenas mestres)
    # path('manage/', views.user_management, name='user-management'),
]