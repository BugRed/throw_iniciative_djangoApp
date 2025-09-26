TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "mestre", "password": "senha123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"

# Testar rooms com token
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/rooms/

# Testar initiative com token
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/initiative/room/1/