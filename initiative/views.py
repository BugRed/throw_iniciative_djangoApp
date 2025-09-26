from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Initiative
from .serializers import InitiativeSerializer, InitiativeRollSerializer

class InitiativeListView(generics.ListAPIView):
    serializer_class = InitiativeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        # Permitir acesso a mestres e jogadores da sala
        return Initiative.objects.filter(room_id=room_id)

@api_view(['POST'])
def roll_initiative(request, room_id):
    serializer = InitiativeRollSerializer(data=request.data)
    if serializer.is_valid():
        from characters.models import Character
        from rooms.models import Room
        
        try:
            room = Room.objects.get(id=room_id, players=request.user)
            character = Character.objects.get(
                id=serializer.validated_data['character_id'],
                owner=request.user
            )
            
            initiative = Initiative.roll_initiative_for_character(room, character)
            return Response(InitiativeSerializer(initiative).data)
            
        except (Room.DoesNotExist, Character.DoesNotExist):
            return Response(
                {'error': 'Sala ou personagem não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)