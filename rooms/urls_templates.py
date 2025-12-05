# rooms/urls_templates.py

from django.urls import path
from . import views # views do app 'rooms'

# Importação CRÍTICA: views do app 'characters'
from characters.views import CharacterCreateView 

from .views import RoomDeleteView #

app_name = 'room_templates'

urlpatterns = [
    # URLs de Sala
    path('', views.RoomListView.as_view(), name='room-list-template'), 
    path('create/', views.RoomCreateView.as_view(), name='room-create-template'),
    path('<int:pk>/', views.RoomDetailTemplateView.as_view(), name='room-detail-template'), 
    path('<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room-update-template'),
    
    path('<int:pk>/delete/', RoomDeleteView.as_view(), name='room-delete-template'),

    # URL de Criação de Personagem no Contexto da Sala (usa views de 'characters')
    path('<int:room_pk>/characters/create/', 
         CharacterCreateView.as_view(), 
         name='character-create-in-room'),
    
    # URLs de Ação (Funções)
    path('<int:room_pk>/toggle-player/<int:user_pk>/', views.toggle_player_in_room, name='toggle-player-in-room'),
    path('<int:room_pk>/add-character/<int:character_pk>/', views.add_character_to_room, name='add-character-to-room'),
]