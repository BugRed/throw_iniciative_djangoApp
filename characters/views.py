from rest_framework import generics, permissions
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
) # Importar Views de Classe para Templates
from django.urls import reverse_lazy # Para redirecionamento após sucesso

from .models import Character
from .serializers import CharacterSerializer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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
        # Redireciona para a Sala se a criação foi feita no contexto da Sala
        room_pk = self.kwargs.get('room_pk')
        if room_pk:
            # OK: Este já usa o namespace 'room_templates'
            return reverse_lazy('room_templates:room-detail-template', kwargs={'pk': room_pk})
            
        return reverse_lazy('characters:character-list-template')

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
    
# 3. EDIÇÃO DE PERSONAGEM (Template: character-form.html)
class CharacterUpdateTemplateView(LoginRequiredMixin, UpdateView):
    """Permite que o dono edite seu personagem."""
    model = Character
    # Reutiliza a lista de campos da criação
    fields = [
        'name', 'character_type', 'description', 'image', 'model_3d',
        'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma',
        'hit_points', 'speed'
    ]
    template_name = 'characters/character_form.html'
    context_object_name = 'character'
    
    def get_queryset(self):
        """Garante que apenas o dono do personagem (ou o mestre, se aplicável) possa editá-lo."""
        # Filtra os personagens que pertencem ao usuário logado
        # Se você quiser que o Mestre possa editar, adicione lógica OR para room.master == user
        return Character.objects.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_type = self.request.user.user_type
        
        # Se for um PJ, impeça a alteração do tipo de personagem
        if form.instance.character_type == 'player':
            form.fields['character_type'].disabled = True
        
        # Restringe as opções se o usuário for um player (apenas pode ser 'player')
        if user_type == 'player':
            form.fields['character_type'].choices = [('player', 'Personagem Jogador')]
            # O campo já está desabilitado acima, mas garantimos que não haja outra opção.
        elif user_type == 'master':
             # Mestres podem alternar entre NPC e Monstro
             form.fields['character_type'].choices = [
                ('npc', 'NPC (Mestre)'), 
                ('monster', 'Monstro')
            ]
        
        return form

    def get_success_url(self):
        """Redireciona para a página de detalhes do personagem após a edição."""
        return reverse_lazy('characters:character-detail-template', kwargs={'pk': self.object.pk})

# 4. DETALHES DE PERSONAGEM (Template: character-detail.html)
class CharacterDetailTemplateView(LoginRequiredMixin, DetailView):
    """Exibe os detalhes de um personagem. Deve ser visível apenas para o dono."""
    model = Character
    template_name = 'characters/character_detail.html'
    context_object_name = 'character'

    def get_queryset(self):
        """Permite que o dono do personagem (ou mestre da sala) veja os detalhes."""
        # Retorna todos os personagens, a permissão mais restrita pode ser aplicada no template.
        # Por simplicidade, faremos a verificação de propriedade no template ou em um mixin mais complexo.
        return Character.objects.all()
    
class CharacterOwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Character
    
    def test_func(self):
        # Permite acesso se o usuário for o dono do personagem
        character = self.get_object()
        return self.request.user == character.owner or self.request.user.is_superuser

# 5. VIEW DE DELEÇÃO
class CharacterDeleteView(CharacterOwnerRequiredMixin, DeleteView):
    model = Character
    template_name = 'characters/character_confirm_delete.html' 
    context_object_name = 'character'

    def get_success_url(self):
        # Retorna para a lista de personagens após a deleção
        return reverse_lazy('characters:character-list-template')