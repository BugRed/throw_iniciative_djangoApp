from rest_framework import serializers
from .models import Character

class CharacterSerializer(serializers.ModelSerializer):
    initiative_modifier = serializers.ReadOnlyField()
    armor_class_calculated = serializers.ReadOnlyField()

    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['initiative_modifier'] = instance.get_initiative_modifier()
        representation['armor_class_calculated'] = instance.get_armor_class()
        return representation