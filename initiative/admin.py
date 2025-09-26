from django.contrib import admin
from .models import Initiative

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('character', 'room', 'initiative_total', 'initiative_round', 'current_turn')
    list_filter = ('initiative_round', 'current_turn', 'completed', 'created_at')
    search_fields = ('character__name', 'room__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Dados da Iniciativa', {
            'fields': ('room', 'character', 'initiative_roll', 'initiative_bonus', 'initiative_total')
        }),
        ('Controle de Turno', {
            'fields': ('initiative_round', 'current_turn', 'completed')
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )