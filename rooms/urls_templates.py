# rooms/urls_templates.py

from django.urls import path
from .views import (
    RoomListView, 
    RoomCreateView, 
    RoomDetailTemplateView, # Nome de View atualizado para Template
    RoomUpdateView, 
    RoomDeleteView
) 

urlpatterns = [
    # Listagem (URL que o dashboard chama)
    path('', RoomListView.as_view(), name='room-list-template'), 
    
    # CRUD
    path('create/', RoomCreateView.as_view(), name='room-create-template'),
    path('<int:pk>/', RoomDetailTemplateView.as_view(), name='room-detail-template'),
    path('<int:pk>/edit/', RoomUpdateView.as_view(), name='room-update-template'),
    path('<int:pk>/delete/', RoomDeleteView.as_view(), name='room-delete-template'),
]