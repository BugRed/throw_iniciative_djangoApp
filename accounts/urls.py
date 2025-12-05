# accounts/urls_api.py
from django.urls import path
from . import views

urlpatterns = [
    # API Authentication
    path('register/', views.register_user, name='api-register'),
    path('profile/', views.UserProfileView.as_view(), name='api-profile'),
    
    # API CRUD Users
    path('users/', views.user_list, name='api-user-list'),
    path('users/<int:pk>/', views.user_detail, name='api-user-detail'),
    path('users/<int:pk>/update/', views.user_update, name='api-user-update'),
    path('users/<int:pk>/delete/', views.user_delete, name='api-user-delete'),
    
    # API Actions
    path('me/', views.me, name='api-me'),
    path('change-password/', views.change_password, name='api-change-password'),
    path('stats/', views.user_stats, name='api-stats'),
    path('profile/', views.ProfileUpdateTemplateView.as_view(), name='profile-template'),
]
