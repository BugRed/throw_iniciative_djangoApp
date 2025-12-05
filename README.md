## Throw Iniciative 
Este é um sistema completo de gerenciamento de sessões de RPG (Role-Playing Game) desenvolvido em Django. Ele oferece uma interface robusta para Mestres criarem e gerenciarem salas, jogadores criarem seus personagens, e controlar ações críticas como a Fila de Iniciativa.


## Funcionalidades e Regras de Negócio

| Funcionalidade | Detalhes |
| :--- | :--- |
| **Gerenciamento de Salas** | Criação, edição, visualização de detalhes e exclusão de salas de jogo. |
| **Controle de Acesso** | Definição de Mestres (`master`) e Jogadores (`player`). |
| **Restrição de PJ** | Jogadores são limitados a **um Personagem Jogador (PJ)** por sala (`room.player_has_character()`). |
| **Gestão de Personagens** | Adição de PJs (de outros jogadores) e **Personagens Não Jogadores (NPCs) / Monstros** (gerenciados pelo Mestre) à sala. |
| **Sistema de Iniciativa** | Gerenciamento de turnos e rodadas de combate. |

## Estrutura e Endpoints Chave (`rooms/urls_templates.py`)

O namespace principal para as URLs de *frontend* é `room_templates`.

| URL Pattern | Name | Ação | Permissão |
| :--- | :--- | :--- | :--- |
| `rooms/` | `room-list-template` | Lista de salas do usuário. | Login Requerido |
| `rooms/<int:pk>/` | `room-detail-template` | Detalhes e gestão da sala. | Login Requerido |
| `rooms/<int:room_pk>/characters/create/` | `character-create-in-room` | Criação de Personagens (PJ ou NPC) no contexto da Sala. | Jogador (1 PJ/sala) ou Mestre |
| `rooms/<int:room_pk>/toggle-player/<int:user_pk>/` | `toggle-player-in-room` | Adiciona/Remove Jogador da sala. | Apenas Mestre |
| `rooms/<int:room_pk>/add-character/` | `add-character-to-room` | Adiciona Personagem (via **POST** do `character_pk`). | Apenas Mestre |

---


## Como Executar
# Pré-requisitos
 - Python 3.x
 - Django (versão utilizada no projeto)

 - Django REST Framework (DRF) (para o módulo API)

# Módulos characters e initiative (assumidos como existentes).

 1. Clonar o Repositório
 ```
    bash

    git clone https://www.youtube.com/watch?v=X49Wz3icO3E
    cd throw_iniciative*
 
 ```
2. Configurar o Ambiente
Bash

python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt # Crie este arquivo com as dependências
3. Configurar o Banco de Dados
Bash

python manage.py makemigrations
python manage.py migrate
4. Rodar o Servidor
Bash

python manage.py runserver
Acesse http://127.0.0.1:8000/ no seu navegador.