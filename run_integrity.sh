#!/bin/bash
echo "🔍 Rodando testes de integridade..." > logs/integrity_check.log
find . -name "*.py" | while read file; do
  echo "🧪 Testando $file" >> logs/integrity_check.log
  python -m py_compile "$file" 2>> logs/integrity_check.log
done

if grep -i "ImportError\|RecursionError" logs/integrity_check.log; then
  echo "❌ Erros de integridade encontrados! Veja logs/integrity_check.log"
else
  echo "✅ Nenhum erro encontrado. Código limpo!"
fi
