# accounts/views.py - VERSÃO COMPLETA
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash, logout
from .serializers import (
    UserSerializer, 
    UserRegisterSerializer, 
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from django.contrib.auth import authenticate, login  
from django.contrib import messages 
User = get_user_model()

# ==================== VIEWS BASEADAS EM CLASSE ====================

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# ==================== VIEWS BASEADAS EM FUNÇÃO (API) ====================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Registro público de usuário
    POST /api/auth/register/
    """
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Usuário criado com sucesso'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request, pk):
    """
    Detalhes de um usuário específico
    GET /api/auth/users/<pk>/
    """
    if request.user.user_type == 'master' or request.user.pk == pk:
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    return Response(
        {'error': 'Permissão negada'}, 
        status=status.HTTP_403_FORBIDDEN
    )

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_update(request, pk):
    """
    Atualizar usuário
    PUT/PATCH /api/auth/users/<pk>/
    """
    if request.user.user_type == 'master' or request.user.pk == pk:
        user = get_object_or_404(User, pk=pk)
        
        if request.user.user_type != 'master' and 'user_type' in request.data:
            return Response(
                {'error': 'Apenas mestres podem mudar o tipo de usuário'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = request.method == 'PATCH'
        serializer = UserSerializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(
        {'error': 'Permissão negada'}, 
        status=status.HTTP_403_FORBIDDEN
    )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_delete(request, pk):
    """
    Deletar usuário
    DELETE /api/auth/users/<pk>/
    """
    if request.user.user_type == 'master' or request.user.pk == pk:
        user = get_object_or_404(User, pk=pk)
        
        if user.user_type == 'master' and User.objects.filter(user_type='master').count() <= 1:
            return Response(
                {'error': 'Não é possível deletar o último mestre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.delete()
        return Response(
            {'message': 'Usuário deletado com sucesso'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    return Response(
        {'error': 'Permissão negada'}, 
        status=status.HTTP_403_FORBIDDEN
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    """
    Listar usuários
    GET /api/auth/users/
    """
    if request.user.user_type == 'master':
        users = User.objects.all()
    else:
        users = User.objects.filter(pk=request.user.pk)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    """
    Obter dados do usuário logado
    GET /api/auth/me/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Alterar senha do usuário logado
    POST /api/auth/change-password/
    """
    if not request.user.check_password(request.data.get('old_password', '')):
        return Response(
            {'error': 'Senha atual incorreta'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    new_password = request.data.get('new_password', '')
    new_password_confirmation = request.data.get('new_password_confirmation', '')
    
    if not new_password or len(new_password) < 8:
        return Response(
            {'error': 'A nova senha deve ter pelo menos 8 caracteres'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != new_password_confirmation:
        return Response(
            {'error': 'As novas senhas não coincidem'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)
    
    return Response({'message': 'Senha alterada com sucesso'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    Estatísticas do usuário
    GET /api/auth/stats/
    """
    from django.utils import timezone
    
    user = request.user
    
    try:
        character_count = user.characters.count()
    except:
        character_count = 0
    
    try:
        mastered_rooms = user.mastered_rooms.count()
    except:
        mastered_rooms = 0
    
    try:
        joined_rooms = user.joined_rooms.count()
    except:
        joined_rooms = 0
    
    stats = {
        'username': user.username,
        'user_type': user.user_type,
        'account_age_days': (timezone.now() - user.date_joined).days,
        'character_count': character_count,
        'mastered_rooms': mastered_rooms,
        'joined_rooms': joined_rooms,
        'is_active': user.is_active,
        'last_login': user.last_login,
    }
    
    return Response(stats)

# ==================== VIEWS DE TEMPLATES (HTML) - VERSÃO CORRIGIDA ====================

def login_view(request):
    """Renderizar template de login COM autenticação"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos')
    
    return render(request, 'accounts/login.html')

def register_view(request):
    """Renderizar template de registro COM criação de usuário"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        email = request.POST.get('email', '')
        user_type = request.POST.get('user_type', 'player')
        bio = request.POST.get('bio', '')
        
        # Validações básicas
        if password != password_confirmation:
            messages.error(request, 'As senhas não coincidem')
        elif len(password) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já existe')
        else:
            try:
                # Criar usuário
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email if email else None,
                    user_type=user_type,
                    bio=bio
                )
                messages.success(request, 'Conta criada com sucesso! Faça login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'accounts/register.html')

def logout_view(request):
    """Fazer logout do usuário"""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')  # ← CORRIGIR: 'login' em vez de 'login-template'


@login_required
def dashboard(request):
    """Dashboard principal"""
    context = {
        'user': request.user,
        'is_master': request.user.user_type == 'master' if request.user.is_authenticated else False
    }
    return render(request, 'accounts/dashboard.html', context)