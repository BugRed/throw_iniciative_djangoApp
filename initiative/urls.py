from django.urls import path
from . import views

urlpatterns = [
    path('room/<int:room_id>/', views.InitiativeListView.as_view(), name='initiative-list'),
    path('room/<int:room_id>/roll/', views.roll_initiative, name='roll-initiative'),
]