from django.db import models
from django.urls import reverse_lazy

# Importações para API (DRF)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RoomSerializer, RoomCreateSerializer

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model() 
from django.db.models import Q

# Importação CRÍTICA para Personagens (Assumindo que está no app 'characters')
from characters.models import Character 

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
    
def player_has_character(self, user):
        """
        Verifica se um usuário (player) já tem um personagem (PJ) nesta sala.
        Mestres não estão sujeitos a esta restrição aqui.
        """
        if user.user_type != 'player':
            return False 
            
        # Filtra os personagens que pertencem a este usuário, estão nesta sala, 
        # e são do tipo 'player' (PJ).
        return self.characters.filter(owner=user, character_type='player').exists()

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
        # ✅ CORREÇÃO APLICADA AQUI: Incluindo o namespace 'room_templates'
        return reverse_lazy('room_templates:room-list-template')

# 3. DETALHES DA SALA (Template: room-detail-template) - CORRIGIDA
class RoomDetailTemplateView(LoginRequiredMixin, DetailView):
    """Exibe os detalhes de uma sala (view de Template), incluindo a gestão de personagens."""
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        user = self.request.user
        
        # --- 1. Lógica de Gestão de Personagens ---
        context['current_characters'] = room.characters.all().select_related('owner')

        if user.is_authenticated:
            # 🌟 NOVO: Variável de permissão de PJ para o usuário logado
            context['can_add_player_character'] = (
                user.user_type == 'player' and 
                # Usa o método que definimos no rooms/models.py
                not room.player_has_character(user) 
            )
            
            # Personagens disponíveis (SÓ VISÍVEL PARA O MESTRE)
            if user == room.master:
                
                # Filtra personagens disponíveis:
                # 1. PJs (character_type='player') de qualquer dono 
                #    QUE AINDA NÃO ESTÃO NA SALA.
                # 2. NPCs e Monstros (character_type in ['npc', 'monster']) que SÃO do Mestre (owner=user).
                
                available_characters_qs = Character.objects.filter(
                    Q(character_type='player') | Q(owner=user, character_type__in=['npc', 'monster'])
                ).exclude(
                    rooms=room
                ).order_by('character_type', 'name')
                
                context['available_characters'] = available_characters_qs
            # --- Fim da Lógica de Gestão de Personagens ---

            # --- 2. Lógica de Gestão de Jogadores (EXISTENTE) ---
            players_in_room_pks = room.players.values_list('pk', flat=True)
            
            context['all_users'] = User.objects.filter(user_type='player').exclude(
                Q(pk=user.pk) | Q(pk__in=players_in_room_pks)
            ).order_by('username')
            # --- Fim da Lógica de Gestão de Jogadores ---

        return context

    

# 4. ATUALIZAÇÃO DE SALA (Template: room-update-template)
class RoomUpdateView(RoomMasterRequiredMixin, UpdateView):
    """Permite que o mestre da sala atualize os dados."""
    model = Room
    fields = ['name', 'description', 'story', 'code', 'is_active']
    template_name = 'rooms/room_form.html'
    
    def get_success_url(self):
        return reverse_lazy('room_templates:room-detail-template', kwargs={'pk': self.object.pk})
    
# 5. DELEÇÃO DE SALA (Template: room-delete-template)
class RoomDeleteView(RoomMasterRequiredMixin, DeleteView):
    """Permite que o mestre da sala delete-a."""
    model = Room
    template_name = 'rooms/room_confirm_delete.html'
    
    # ✅ CORREÇÃO AQUI: Deve ser 'room_templates:room-list-template'
    success_url = reverse_lazy('room_templates:room-list-template')



# ==================== VIEWS BASEADAS EM FUNÇÃO (Gestão) ====================

@login_required
def toggle_player_in_room(request, room_pk, user_pk):
    """
    Permite ao Mestre da Sala adicionar ou remover um Jogador (usuário).
    """
    room = get_object_or_404(Room, pk=room_pk)
    target_user = get_object_or_404(User, pk=user_pk)

    # 1. Checagem de Autorização
    # Apenas o mestre da sala E do tipo 'master' pode gerenciar.
    if request.user != room.master or request.user.user_type != 'master':
        messages.error(request, "Apenas o Mestre desta sala pode gerenciar jogadores.")
        # CORRIGIDO: Adicionado o namespace
        return redirect('room_templates:room-detail-template', pk=room_pk) 

    # 2. Impedir que o Mestre seja adicionado como Jogador
    if target_user == room.master:
        messages.warning(request, "O Mestre não pode ser adicionado/removido como Jogador por esta interface.")
        # CORRIGIDO: Adicionado o namespace
        return redirect('room_templates:room-detail-template', pk=room_pk)
    
    # 3. Impedir que outros Mestres sejam adicionados como Jogadores
    if target_user.user_type == 'master':
        messages.warning(request, f"O usuário {target_user.username} é um Mestre e não pode ser adicionado como Jogador nesta sala.")
        # CORRIGIDO: Adicionado o namespace
        return redirect('room_templates:room-detail-template', pk=room_pk)


    # 4. Lógica de Toggle
    if room.players.filter(pk=target_user.pk).exists():
        # Remover Jogador
        room.players.remove(target_user)
        messages.success(request, f"O Jogador {target_user.username} foi removido da sala.")
    else:
        # Adicionar Jogador
        room.players.add(target_user)
        messages.success(request, f"O Jogador {target_user.username} foi adicionado à sala com sucesso.")

    # CORRIGIDO: Adicionado o namespace
    return redirect('room_templates:room-detail-template', pk=room_pk)


@login_required
def add_character_to_room(request, room_pk, character_pk):
    """
    Adiciona um personagem existente a uma sala (apenas para o Mestre da sala) via POST.
    """
    if request.method != 'POST':
        messages.error(request, "Ação inválida.")
        return redirect('room-detail-template', pk=room_pk)
        
    room = get_object_or_404(Room, pk=room_pk)
    character = get_object_or_404(Character, pk=character_pk) 
    
    # 1. Checagem de Permissão: Apenas o dono da sala (Mestre) pode adicionar
    if room.master != request.user:
        messages.error(request, "Você não tem permissão para gerenciar personagens nesta sala.")
        return redirect('room-detail-template', pk=room_pk)

    # 2. Checagem de Lógica: Master pode adicionar PJs de outros ou seus próprios NPCs/Monstros
    can_be_added = (
        character.character_type == 'player' or 
        (character.owner == request.user and character.character_type in ['npc', 'monster'])
    )
    
    if not can_be_added:
        messages.error(request, "Este personagem não é válido para ser adicionado nesta sala.")
        return redirect('room-detail-template', pk=room_pk)
    
    # 3. Adição
    room.characters.add(character)
    messages.success(request, f"Personagem '{character.name}' adicionado à sala '{room.name}'.")
    
    return redirect('room-detail-template', pk=room_pk)


@login_required
def add_character_to_room(request, room_pk): 
    """
    Adiciona um personagem existente a uma sala (apenas para o Mestre da sala) via POST.
    """
    
    if request.method != 'POST':
        messages.error(request, "Ação inválida.")
        return redirect('room_templates:room-detail-template', pk=room_pk)
        
    room = get_object_or_404(Room, pk=room_pk)
    
    character_pk = request.POST.get('character_pk')
    if not character_pk:
        messages.error(request, "Nenhum personagem foi selecionado para adicionar.")
        return redirect('room_templates:room-detail-template', pk=room_pk)
        
    character = get_object_or_404(Character, pk=character_pk) 
    
    # 1. Checagem de Permissão
    if room.master != request.user:
        messages.error(request, "Você não tem permissão para gerenciar personagens nesta sala.")
        return redirect('room_templates:room-detail-template', pk=room_pk)

    # 2. Checagem de Elegibilidade (PJ de qualquer um, NPC/Monstro só do Mestre)
    can_be_added = (
        character.character_type == 'player' or 
        (character.owner == request.user and character.character_type in ['npc', 'monster'])
    )
    
    if not can_be_added:
        messages.error(request, f"O personagem {character.name} não é elegível para ser adicionado.")
        return redirect('room_templates:room-detail-template', pk=room_pk)
        
    # 3. VALIDAÇÃO DE 1 PJ POR SALA
    if character.character_type == 'player' and room.player_has_character(character.owner):
        messages.error(request, f"O Jogador {character.owner.username} já possui um Personagem Jogador (PJ) ativo nesta sala.")
        return redirect('room_templates:room-detail-template', pk=room_pk)
    
    # 4. Adição
    room.characters.add(character)
    messages.success(request, f"Personagem '{character.name}' adicionado à sala '{room.name}'.")
    
    return redirect('room_templates:room-detail-template', pk=room_pk)