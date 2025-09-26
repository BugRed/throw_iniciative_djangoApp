# initiative/models.py
from django.db import models
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class Initiative(models.Model):
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='initiatives')
    character = models.ForeignKey('characters.Character', on_delete=models.CASCADE)
    
    # Dados da iniciativa
    initiative_roll = models.IntegerField()  # Resultado do d20
    initiative_bonus = models.IntegerField()  # Bônus do personagem
    initiative_total = models.IntegerField()  # roll + bonus
    
    # Controle de rodada e turno
    initiative_round = models.IntegerField(default=0)
    current_turn = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character.name} - {self.initiative_total} (d{self.initiative_roll} + {self.initiative_bonus})"

    def roll_initiative(self):
        """Rola a iniciativa usando o método do personagem"""
        # Usa o método do Character para rolar
        self.initiative_roll = random.randint(1, 20)
        self.initiative_bonus = self.character.get_initiative_modifier()
        self.initiative_total = self.initiative_roll + self.initiative_bonus
        self.save()
        return self.initiative_total

    @classmethod
    def roll_initiative_for_character(cls, room, character):
        """Rola iniciativa para um personagem em uma sala"""
        initiative, created = cls.objects.get_or_create(
            room=room,
            character=character,
            initiative_round=room.current_initiative_round,
            defaults={
                'initiative_roll': 0,
                'initiative_bonus': character.get_initiative_modifier(),
                'initiative_total': 0
            }
        )
        initiative.roll_initiative()
        return initiative

    @classmethod
    def create_initiative_for_room(cls, room):
        """Cria entradas de iniciativa para todos os personagens da sala"""
        initiatives = []
        for character in room.characters.all():
            initiative = cls.roll_initiative_for_character(room, character)
            initiatives.append(initiative)
        return initiatives

    class Meta:
        ordering = ['-initiative_total', 'character__name']
        unique_together = ['room', 'character', 'initiative_round']