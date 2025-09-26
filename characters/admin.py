from django.contrib import admin
from .models import Character

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'character_type', 'owner', 'armor_class', 'hit_points')
    list_filter = ('character_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'character_type', 'description', 'image', 'model_3d')
        }),
        ('Atributos D20', {
            'fields': ('strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma')
        }),
        ('Combate', {
            'fields': ('armor_class', 'hit_points', 'speed')
        }),
        ('Relacionamentos', {
            'fields': ('owner',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )