from rest_framework import serializers
from .models import Initiative
from characters.serializers import CharacterSerializer

class InitiativeSerializer(serializers.ModelSerializer):
    character_name = serializers.ReadOnlyField(source='character.name')
    character_type = serializers.ReadOnlyField(source='character.character_type')

    class Meta:
        model = Initiative
        fields = '__all__'
        read_only_fields = ('initiative_roll', 'initiative_bonus', 'initiative_total', 'created_at')

class InitiativeRollSerializer(serializers.Serializer):
    character_id = serializers.IntegerField()

    def validate_character_id(self, value):
        from characters.models import Character
        try:
            Character.objects.get(id=value)
        except Character.DoesNotExist:
            raise serializers.ValidationError("Personagem não encontrado")
        return value