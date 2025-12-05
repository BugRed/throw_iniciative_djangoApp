from django.urls import path
from . import views

urlpatterns = [
    path('', views.CharacterListCreateView.as_view(), name='character-list'),
    path('<int:pk>/', views.CharacterDetailView.as_view(), name='character-detail'),
    path('<int:pk>/delete/', views.CharacterDeleteView.as_view(), name='character-delete-template'),
]