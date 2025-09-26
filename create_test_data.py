import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser
from rooms.models import Room
from characters.models import Character
from initiative.models import Initiative

def create_test_data():
    print("🎮 Criando dados de teste para o sistema RPG...")
    
    # Criar usuários
    try:
        mestre = CustomUser.objects.create_user(
            username='mestre',
            email='mestre@rpg.com',
            password='senha123',
            user_type='master',
            bio='Mestre experiente de D&D'
        )
        print(f"✅ Mestre criado: {mestre.username}")
    except:
        mestre = CustomUser.objects.get(username='mestre')
        print("✅ Mestre já existe")

    try:
        jogador1 = CustomUser.objects.create_user(
            username='jogador1',
            email='jogador1@rpg.com',
            password='senha123',
            user_type='player',
            bio='Guerreiro destemido'
        )
        print(f"✅ Jogador 1 criado: {jogador1.username}")
    except:
        jogador1 = CustomUser.objects.get(username='jogador1')
        print("✅ Jogador 1 já existe")

    try:
        jogador2 = CustomUser.objects.create_user(
            username='jogador2',
            email='jogador2@rpg.com',
            password='senha123',
            user_type='player',
            bio='Mago poderoso'
        )
        print(f"✅ Jogador 2 criado: {jogador2.username}")
    except:
        jogador2 = CustomUser.objects.get(username='jogador2')
        print("✅ Jogador 2 já existe")

    # Criar sala
    sala, created = Room.objects.get_or_create(
        name='Mina Perdida de Phandelver',
        code='MINA123',
        defaults={
            'master': mestre,
            'description': 'Uma aventura épica nas minas esquecidas',
            'story': 'Os heróis devem explorar as minas em busca do tesouro lendário...'
        }
    )
    
    if created:
        sala.players.add(jogador1, jogador2)
        print(f"✅ Sala criada: {sala.name} (Código: {sala.code})")
    else:
        print("✅ Sala já existe")

    # Criar personagens do mestre (NPCs/Monstros)
    npc1, _ = Character.objects.get_or_create(
        name='Goblin Archer',
        character_type='monster',
        owner=mestre,
        defaults={
            'strength': 8, 'dexterity': 14, 'constitution': 10,
            'intelligence': 6, 'wisdom': 8, 'charisma': 6,
            'hit_points': 7, 'armor_class': 13
        }
    )

    npc2, _ = Character.objects.get_or_create(
        name='Orc Warrior',
        character_type='monster', 
        owner=mestre,
        defaults={
            'strength': 16, 'dexterity': 12, 'constitution': 16,
            'intelligence': 7, 'wisdom': 11, 'charisma': 10,
            'hit_points': 15, 'armor_class': 13
        }
    )

    # Criar personagens dos jogadores
    guerreiro, _ = Character.objects.get_or_create(
        name='Thorin Escudo-de-Ferro',
        character_type='player',
        owner=jogador1,
        defaults={
            'strength': 16, 'dexterity': 12, 'constitution': 14,
            'intelligence': 10, 'wisdom': 13, 'charisma': 8,
            'hit_points': 12, 'armor_class': 16
        }
    )

    mago, _ = Character.objects.get_or_create(
        name='Eldrin Arcanista',
        character_type='player', 
        owner=jogador2,
        defaults={
            'strength': 8, 'dexterity': 14, 'constitution': 12,
            'intelligence': 16, 'wisdom': 14, 'charisma': 10,
            'hit_points': 8, 'armor_class': 12
        }
    )

    # Adicionar personagens à sala
    sala.characters.add(npc1, npc2, guerreiro, mago)
    print("✅ Personagens adicionados à sala")

    # Criar iniciativa de exemplo
    if not Initiative.objects.filter(room=sala).exists():
        Initiative.roll_initiative_for_character(sala, npc1)
        Initiative.roll_initiative_for_character(sala, npc2) 
        Initiative.roll_initiative_for_character(sala, guerreiro)
        Initiative.roll_initiative_for_character(sala, mago)
        print("✅ Iniciativa rolada para todos os personagens")

    print("\n🎯 Dados de teste criados com sucesso!")
    print(f"📊 Sala ID: {sala.id}")
    print(f"👤 Credenciais para teste:")
    print(f"   Mestre: usuario=mestre, senha=senha123")
    print(f"   Jogador 1: usuario=jogador1, senha=senha123") 
    print(f"   Jogador 2: usuario=jogador2, senha=senha123")
    print(f"\n�� URLs para testar:")
    print(f"   Iniciativa da sala: http://127.0.0.1:8000/api/initiative/room/{sala.id}/")
    print(f"   Personagens: http://127.0.0.1:8000/api/characters/")
    print(f"   Salas: http://127.0.0.1:8000/api/rooms/")

if __name__ == '__main__':
    create_test_data()
