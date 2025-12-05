from rest_framework import generics, permissions
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
) # Importar Views de Classe para Templates
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy # Para redirecionamento após sucesso

from .models import Character
from .serializers import CharacterSerializer # Manter este se for usado apenas para API

from django.shortcuts import get_object_or_404 # Importar se não existir
from django.urls import reverse_lazy 

try:
    from rooms.models import Room
except ImportError:
    pass

# ==================== VIEWS BASEADAS EM CLASSE (API - DRF) ====================

class CharacterListCreateView(generics.ListCreateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Character.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Character.objects.filter(owner=self.request.user)
    

# ==================== VIEWS BASEADAS EM CLASSE (Templates - Django CBV) ====================

# 1. LISTAGEM DE PERSONAGENS (Template: character-list-template)
class CharacterListView(LoginRequiredMixin, ListView):
    """Exibe a lista de personagens do usuário logado."""
    model = Character
    template_name = 'characters/character_list.html' 
    context_object_name = 'characters'

    def get_queryset(self):
        # Garante que apenas os personagens do usuário logado são listados
        return Character.objects.filter(owner=self.request.user).order_by('name') 
        
# 2. CRIAÇÃO DE PERSONAGEM (Template: character-create-template)
class CharacterCreateView(LoginRequiredMixin, CreateView):
    """Cria um novo personagem, forçando o tipo baseado no user_type do criador."""
    model = Character
    fields = [
        'name', 'character_type', 'description', 'image', 'model_3d',
        'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
        'hit_points', 'speed'
    ]
    template_name = 'characters/character_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_type = self.request.user.user_type
        
        # Restringe as opções do campo 'character_type' no formulário
        if user_type == 'player':
            form.fields['character_type'].choices = [('player', 'Personagem Jogador')]
            form.fields['character_type'].initial = 'player'
        elif user_type == 'master':
            form.fields['character_type'].choices = [
                ('npc', 'NPC (Mestre)'), 
                ('monster', 'Monstro')
            ]
        
        return form
    def get_success_url(self):
        room_pk = self.kwargs.get('room_pk')
        if room_pk:
            # ✅ Deve usar o namespace 'room_templates'
            return reverse_lazy('room_templates:room-detail-template', kwargs={'pk': room_pk})
            
        # Redirecionamento de fallback (se não estiver criando dentro de uma sala)
        return reverse_lazy('character-list-template')

    def form_valid(self, form):
        char_type = form.cleaned_data.get('character_type')
        user_type = self.request.user.user_type
        
        # VALIDAÇÃO DE SUBMISSÃO (Garante que o tipo não foi manipulado)
        if user_type == 'player' and char_type != 'player':
             form.add_error('character_type', 'Erro: Jogadores só podem criar Personagens Jogadores (PJ).')
             return self.form_invalid(form)
        
        if user_type == 'master' and char_type == 'player':
            form.add_error('character_type', 'Erro: Mestres devem criar NPCs ou Monstros.')
            return self.form_invalid(form)

        form.instance.owner = self.request.user
        
        # Chama super().form_valid() para salvar o personagem e obter o objeto
        response = super().form_valid(form)
        
        # ASSOCIAÇÃO DO PERSONAGEM À SALA
        room_pk = self.kwargs.get('room_pk')
        if room_pk:
            try:
                room = Room.objects.get(pk=room_pk)
                room.characters.add(self.object) 
            except Room.DoesNotExist:
                pass 
        
        return response

    def get_success_url(self):
        # Redireciona para a Sala se a criação foi feita no contexto da Sala
        room_pk = self.kwargs.get('room_pk')
        if room_pk:
            # ✅ CORREÇÃO APLICADA AQUI: Adicionado 'room_templates:'
            return reverse_lazy('room_templates:room-detail-template', kwargs={'pk': room_pk})
            
        # Caso contrário, redireciona para a lista geral de personagens
        return reverse_lazy('character-list-template')