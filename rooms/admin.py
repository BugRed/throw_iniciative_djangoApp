from django.contrib import admin
from .models import Room

class CharacterInline(admin.TabularInline):
    model = Room.characters.through
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'master', 'initiative_started', 'is_active')
    list_filter = ('initiative_started', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('players',)
    inlines = [CharacterInline]
    fieldsets = (
        ('Informações da Sala', {
            'fields': ('name', 'code', 'description', 'story')
        }),
        ('Gerenciamento', {
            'fields': ('master', 'players', 'initiative_started', 'current_initiative_round', 'current_turn_index')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )