# accounts/urls_templates.py

from django.urls import path
from . import views
from .views import (
    # Views de Classe que acabamos de adicionar
    UserListView, 
    UserDetailView, 
    UserUpdateView, 
    UserDeleteView
)

urlpatterns = [
    # Autenticação (Funções existentes)
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'), # Garanta que views.dashboard existe
    
    # ------------------ CRUD ADMINISTRATIVO (Mestres) ------------------
    # URL que faltava (user-list)
    path('users/', UserListView.as_view(), name='user-list'), 
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Se precisar de um formulário de criação dedicado:
    # path('users/create/', UserCreateView.as_view(), name='user-create'),
]