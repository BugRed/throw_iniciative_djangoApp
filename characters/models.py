# characters/models.py
from django.db import models
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class Character(models.Model):
    CHARACTER_TYPE_CHOICES = (
        ('player', 'Personagem Jogador'),
        ('npc', 'NPC (Mestre)'),
        ('monster', 'Monstro'),
    )
    
    name = models.CharField(max_length=100)
    character_type = models.CharField(max_length=10, choices=CHARACTER_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='characters/', blank=True, null=True)
    model_3d = models.FileField(upload_to='models_3d/', blank=True, null=True)
    
    # Atributos D20
    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    constitution = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    wisdom = models.IntegerField(default=10)
    charisma = models.IntegerField(default=10)
    
    # Informações de combate
    armor_class = models.IntegerField(default=10)
    hit_points = models.IntegerField(default=10)
    speed = models.IntegerField(default=30)
    
    # Relacionamentos
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_character_type_display()})"

    # === MÉTODOS DE CÁLCULO ===
    def get_ability_modifier(self, ability_score):
        """Calcula modificador de habilidade: (score - 10) // 2"""
        return (ability_score - 10) // 2

    def get_initiative_modifier(self):
        """Calcula o modificador de iniciativa baseado em Destreza"""
        return self.get_ability_modifier(self.dexterity)

    def get_armor_class(self):
        """Calcula a classe de armadura (10 + mod. destreza)"""
        return 10 + self.get_ability_modifier(self.dexterity)

    def roll_dice(self, dice_count=1, dice_sides=20, bonus=0):
        """Rola dados genéricos"""
        total = sum(random.randint(1, dice_sides) for _ in range(dice_count)) + bonus
        return total

    def roll_initiative(self):
        """Rola iniciativa: d20 + mod. destreza"""
        return self.roll_dice(1, 20, self.get_initiative_modifier())

    def roll_attack(self, attack_bonus=0):
        """Rola ataque: d20 + bônus de ataque"""
        return self.roll_dice(1, 20, attack_bonus)

    def roll_damage(self, dice_count=1, dice_sides=6, bonus=0):
        """Rola dano com mínimo de 1"""
        total = self.roll_dice(dice_count, dice_sides, bonus)
        return max(1, total)

    def save(self, *args, **kwargs):
        """Garante que armor_class seja calculado automaticamente"""
        self.armor_class = self.get_armor_class()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']