from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    story = models.TextField(blank=True, null=True)
    
    # Relacionamentos
    master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mastered_rooms')
    players = models.ManyToManyField(User, related_name='joined_rooms', blank=True)
    characters = models.ManyToManyField('characters.Character', related_name='rooms', blank=True)
    
    # Estado da iniciativa
    initiative_started = models.BooleanField(default=False)
    current_initiative_round = models.IntegerField(default=0)
    current_turn_index = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Code: {self.code})"

    def get_initiative_queue(self):
        """Retorna a fila de iniciativa ordenada para esta sala"""
        return self.initiatives.filter(
            initiative_round=self.current_initiative_round
        ).order_by('-initiative_total', 'character__name')
    
    def get_current_turn(self):
        """Retorna a iniciativa do turno atual"""
        queue = self.get_initiative_queue()
        if queue.exists() and self.current_turn_index < queue.count():
            return queue[self.current_turn_index]
        return None
    
    def next_turn(self):
        """Avança para o próximo turno"""
        queue = self.get_initiative_queue()
        if queue.exists():
            self.current_turn_index = (self.current_turn_index + 1) % queue.count()
            self.save()
            return self.get_current_turn()
        return None
    
    def reset_initiative(self):
        """Reseta a iniciativa para nova rodada"""
        self.initiative_started = False
        self.current_initiative_round += 1
        self.current_turn_index = 0
        self.save()

    def start_initiative(self):
        """Inicia uma nova rodada de iniciativa"""
        from initiative.models import Initiative
        
        self.initiative_started = True
        self.current_initiative_round += 1
        self.current_turn_index = 0
        self.save()
        
        # Rola iniciativa para todos os personagens
        Initiative.create_initiative_for_room(self)
        return self.get_initiative_queue()

    def get_initiative_queue(self):
        """Retorna a fila de iniciativa ordenada"""
        return self.initiatives.filter(
            initiative_round=self.current_initiative_round
        ).order_by('-initiative_total', 'character__name')
    
    def get_current_turn(self):
        """Retorna a iniciativa do turno atual"""
        queue = list(self.get_initiative_queue())
        if queue and self.current_turn_index < len(queue):
            return queue[self.current_turn_index]
        return None
    
    def next_turn(self):
        """Avança para o próximo turno"""
        queue = list(self.get_initiative_queue())
        if queue:
            # Marca turno atual como completo
            current = self.get_current_turn()
            if current:
                current.completed = True
                current.current_turn = False
                current.save()
            
            # Avança para próximo turno
            self.current_turn_index = (self.current_turn_index + 1) % len(queue)
            self.save()
            
            # Marca novo turno atual
            new_current = self.get_current_turn()
            if new_current:
                new_current.current_turn = True
                new_current.completed = False
                new_current.save()
            
            return new_current
        return None

    def reset_initiative(self):
        """Reseta a iniciativa para nova rodada"""
        self.initiative_started = False
        self.current_turn_index = 0
        self.save()

    class Meta:
        ordering = ['-created_at']