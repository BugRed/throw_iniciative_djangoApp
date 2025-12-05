from django.urls import path
from .views import (
    RoomListView, 
    RoomCreateView, 
    RoomDetailTemplateView,
    RoomUpdateView, 
    RoomDeleteView
) 
from . import views

app_name = 'room_templates'

urlpatterns = [
    # Listagem 
    path('', RoomListView.as_view(), name='room-list-template'), 
    
    # CRUD
    path('create/', RoomCreateView.as_view(), name='room-create-template'),
    path('<int:pk>/', RoomDetailTemplateView.as_view(), name='room-detail-template'),
    path('<int:pk>/edit/', RoomUpdateView.as_view(), name='room-update-template'),
    path('<int:pk>/delete/', RoomDeleteView.as_view(), name='room-delete-template'),
    
    # Gerenciamento de Jogadores (Função de mestre)
    path('<int:room_pk>/toggle-player/<int:user_pk>/', 
         views.toggle_player_in_room, 
         name='toggle-player-in-room'),

    # Adicionar Personagem (Função de mestre)
    path('<int:room_pk>/characters/<int:character_pk>/add/', 
         views.add_character_to_room, 
         name='room-add-character'),
]