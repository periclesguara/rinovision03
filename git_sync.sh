#!/bin/bash

# Define timestamp e mensagem
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMMIT_MSG="Auto commit: $TIMESTAMP"

echo "🔄 Puxando atualizações do repositório remoto..."
git pull origin main --rebase

echo "📦 Adicionando todos os arquivos modificados..."
git add .

echo "📝 Commitando com mensagem automática..."
git commit -m "$COMMIT_MSG"

echo "🚀 Enviando para o GitHub..."
git push origin main

echo "✅ Versionamento sincronizado com sucesso!"
