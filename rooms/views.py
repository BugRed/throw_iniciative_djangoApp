from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Room
from .serializers import RoomSerializer, RoomCreateSerializer

class RoomListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoomCreateSerializer
        return RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(
            models.Q(master=self.request.user) | 
            models.Q(players=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(master=self.request.user)

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Room.objects.filter(
            models.Q(master=self.request.user) | 
            models.Q(players=self.request.user)
        ).distinct()

@api_view(['POST'])
def start_initiative(request, room_id):
    try:
        room = Room.objects.get(id=room_id, master=request.user)
        queue = room.start_initiative()
        from initiative.serializers import InitiativeSerializer
        return Response({
            'message': 'Iniciativa iniciada!',
            'queue': InitiativeSerializer(queue, many=True).data
        })
    except Room.DoesNotExist:
        return Response(
            {'error': 'Sala não encontrada ou você não é o mestre'}, 
            status=status.HTTP_404_NOT_FOUND
        )