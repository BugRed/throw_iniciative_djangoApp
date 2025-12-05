# accounts/urls_templates.py (Versão Corrigida)

from django.urls import path
from . import views
from .views import (
    # Views de Classe
    UserListView, 
    UserDetailView, 
    UserUpdateView, 
    UserDeleteView,
    # A classe UserProfileUpdateView (se existir) ou UserUpdateView.
    # Usaremos UserUpdateView por simplicidade, tratando a URL 'profile/' de forma especial.
)

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'), 
    
    # ------------------ GESTÃO DE PERFIL (Usuário Logado) ------------------
    # Usando UserUpdateView (ou ProfileUpdateView dedicada), mas sem PK,
    # A View precisará buscar o usuário logado (request.user)
    # Por agora, definimos a rota para ser o target do link do dashboard
    path('profile/', views.dashboard, name='profile-template'), 
    # ^^^^^ MANTENDO O NOME 'profile-template' PARA RESOLVER O ERRO NO DASHBOARD.
    # NOTA: O tratamento lógico da edição do perfil deve ser feito na View 'profile_view'
    # ou usando uma ProfileUpdateView dedicada. Para resolver o erro rapidamente,
    # vamos usar 'profile-template' para apontar para a Dashboard por enquanto, ou
    # idealmente, para uma view de edição de perfil.
    
    # Vamos assumir que criaremos uma view específica para edição de perfil mais tarde,
    # e por enquanto, usamos o nome 'profile-template' apontando para uma URL temporária
    # ou remapeamos o dashboard.
    
    # SOLUÇÃO REALISTA: Criar uma URL de edição de perfil que o dashboard possa chamar.
    # Se você for usar a UserUpdateView para edição do próprio perfil, a URL deve ser:
    path('profile/edit/', UserUpdateView.as_view(), name='profile-edit-template'), # Usaremos este nome no dashboard
    
    # ------------------ CRUD ADMINISTRATIVO (Mestres) ------------------
    path('users/', UserListView.as_view(), name='user-list'), 
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
]