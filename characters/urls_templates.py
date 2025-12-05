# characters/urls_templates.py

from django.urls import path
from .views import (
    CharacterListView, 
    CharacterCreateView, 
    CharacterUpdateTemplateView, 
    CharacterDetailTemplateView,
    CharacterDeleteView,  # <--- 1. IMPORTAR A VIEW DE DELEÇÃO
)

app_name = 'characters'
 
urlpatterns = [
    # Listagem de Personagens do Usuário Logado
    path('', CharacterListView.as_view(), name='character-list-template'), 
    
    # Formulário de Criação de Personagem
    path('create/', CharacterCreateView.as_view(), name='character-create-template'),

    # URL de criação em sala (melhor mover para o app 'rooms' se houver conflito, mas mantendo por enquanto)
    # Recomenda-se mover esta URL para rooms/urls_templates.py se ela não for essencial aqui.
    path('<int:room_pk>/characters/create/', 
         CharacterCreateView.as_view(), 
         name='character-create-in-room'),
    
    # Detalhes e Edição (IMPORTANTE: URLs com PK devem vir após URLs estáticas)
    path('<int:pk>/', CharacterDetailTemplateView.as_view(), name='character-detail-template'), # Detalhes
    path('<int:pk>/edit/', CharacterUpdateTemplateView.as_view(), name='character-update-template'), # Edição
    
    # 2. ADICIONAR O PATH DE DELEÇÃO
    path('<int:pk>/delete/', CharacterDeleteView.as_view(), name='character-delete-template'), # Deleção
]