# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        token['username'] = user.username
        return token

class UserSerializer(serializers.ModelSerializer):
    """Serializer para leitura de dados do usuário"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'bio', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de novo usuário"""
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation', 'user_type', 'bio')

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("As senhas não coincidem")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para atualização de usuário"""
    class Meta:
        model = User
        fields = ('email', 'bio', 'user_type')
        read_only_fields = ('username',)  # Não permitir mudar username
    
    def validate_user_type(self, value):
        """Apenas mestres podem mudar o tipo de usuário"""
        request = self.context.get('request')
        if request and request.user.user_type != 'master':
            raise serializers.ValidationError("Apenas mestres podem mudar o tipo de usuário")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para mudança de senha"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirmation = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError("As novas senhas não coincidem")
        return data