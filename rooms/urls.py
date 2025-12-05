# rooms/urls.py

from django.urls import path
from . import views


urlpatterns = [
    # Rotas da API (v1/rooms/)
    path('', views.RoomListCreateView.as_view(), name='api-room-list'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='api-room-detail'),
    path('<int:room_id>/start-initiative/', views.start_initiative, name='api-start-initiative'),

]