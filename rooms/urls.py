from django.urls import path
from . import views

urlpatterns = [
    path('', views.RoomListCreateView.as_view(), name='room-list'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    path('<int:room_id>/start-initiative/', views.start_initiative, name='start-initiative'),
]