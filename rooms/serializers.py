from rest_framework import serializers
from .models import Room
from characters.serializers import CharacterSerializer

class RoomSerializer(serializers.ModelSerializer):
    master_name = serializers.ReadOnlyField(source='master.username')
    player_count = serializers.ReadOnlyField()
    initiative_queue = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ('master', 'created_at', 'updated_at')

    def get_player_count(self, obj):
        return obj.players.count()

    def get_initiative_queue(self, obj):
        if obj.initiative_started:
            queue = obj.get_initiative_queue()
            from initiative.serializers import InitiativeSerializer
            return InitiativeSerializer(queue, many=True).data
        return []

class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('name', 'description', 'story')

    def create(self, validated_data):
        validated_data['master'] = self.context['request'].user
        return super().create(validated_data)