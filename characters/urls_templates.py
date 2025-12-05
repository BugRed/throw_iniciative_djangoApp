# characters/urls_templates.py

from django.urls import path
from .views import (
    CharacterListView, 
    CharacterCreateView, 
) 


urlpatterns = [
    # Listagem de Personagens do Usuário Logado
    path('', CharacterListView.as_view(), name='character-list-template'), 
    
    # Formulário de Criação de Personagem
    path('create/', CharacterCreateView.as_view(), name='character-create-template'),
    path('<int:room_pk>/characters/create/', 
         CharacterCreateView.as_view(), 
         name='character-create-in-room'),
    
    # Se for implementar CRUD completo por templates:
    # path('<int:pk>/', CharacterDetailView.as_view(), name='character-detail-template'),
    # path('<int:pk>/edit/', CharacterUpdateView.as_view(), name='character-update-template'),
]