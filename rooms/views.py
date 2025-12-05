from django.db import models
from django.urls import reverse_lazy

# Importações para API (DRF)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RoomSerializer, RoomCreateSerializer

# Importações para Templates (Django CBV)
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Room 

# ==================== VIEWS BASEADAS EM CLASSE (API - DRF) ====================

# 1. LIST/CREATE API VIEW (RESTAURADA)
class RoomListCreateView(generics.ListCreateAPIView):
    """API para listar e criar salas."""
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

# 2. DETAIL/UPDATE/DELETE API VIEW
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API para detalhes, atualização e deleção de sala."""
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Room.objects.filter(
            models.Q(master=self.request.user) | 
            models.Q(players=self.request.user)
        ).distinct()

# ==================== VIEWS BASEADAS EM FUNÇÃO (API - DRF) ====================

@api_view(['POST'])
def start_initiative(request, room_id):
    """API para iniciar a iniciativa em uma sala."""
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

# ==================== VIEWS BASEADAS EM CLASSE (Templates - Django CBV) ====================

# Mixin de permissão para Rooms (somente Master da Sala tem acesso)
class RoomMasterRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Room
    
    def test_func(self):
        # Permite acesso se o usuário for o master da sala ou superuser
        room = self.get_object()
        # Assumindo que 'master' é uma ForeignKey em Room
        return self.request.user == room.master or self.request.user.is_superuser

# 1. LISTAGEM DE SALAS (Template: room-list-template)
class RoomListView(LoginRequiredMixin, ListView):
    """Exibe a lista de salas das quais o usuário é Mestre ou Jogador."""
    model = Room
    template_name = 'rooms/room_list.html' 
    context_object_name = 'rooms'

    def get_queryset(self):
        user = self.request.user
        return Room.objects.filter(
            models.Q(master=user) | 
            models.Q(players=user)
        ).distinct().select_related('master').prefetch_related('players') 
        
# 2. CRIAÇÃO DE SALA (Template: room-create-template)
class RoomCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova sala para o usuário logado."""
    model = Room
    fields = ['name', 'description', 'story', 'code']
    template_name = 'rooms/room_form.html'
    
    def form_valid(self, form):
        form.instance.master = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('room-list-template')

# 3. DETALHES DA SALA (Template: room-detail-template)
class RoomDetailTemplateView(LoginRequiredMixin, DetailView):
    """Exibe os detalhes de uma sala (view de Template)."""
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'

# 4. ATUALIZAÇÃO DE SALA (Template: room-update-template)
class RoomUpdateView(RoomMasterRequiredMixin, UpdateView):
    """Permite que o mestre da sala atualize os dados."""
    model = Room
    fields = ['name', 'description', 'story', 'code', 'is_active']
    template_name = 'rooms/room_form.html'
    
    def get_success_url(self):
        return reverse_lazy('room-detail-template', kwargs={'pk': self.object.pk})

# 5. DELEÇÃO DE SALA (Template: room-delete-template)
class RoomDeleteView(RoomMasterRequiredMixin, DeleteView):
    """Permite que o mestre da sala delete-a."""
    model = Room
    template_name = 'rooms/room_confirm_delete.html'
    success_url = reverse_lazy('room-list-template')