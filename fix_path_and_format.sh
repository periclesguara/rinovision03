#!/bin/bash

echo "[1/3] Verificando e injetando sys.path no main.py..."

# Verifica se sys.path já existe no main.py
if ! grep -q "sys.path.insert" main.py; then
    sed -i '1i import sys\nimport os\nsys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))\n' main.py
    echo "[✓] sys.path foi inserido no topo do main.py"
else
    echo "[✓] sys.path já estava presente em main.py"
fi

echo "[2/3] Criando pastas úteis, se não existirem..."
mkdir -p logs scripts output test
touch logs/runtime.log

echo "[3/3] Rodando black para limpar o código..."
black . || echo "[X] Erro: Black não encontrado. Ative o venv ou instale com 'pip install black'"

echo "[✔] Tudo pronto, chefe!"
