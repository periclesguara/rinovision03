#!/bin/bash
# insert_code.sh <arquivo> <marcador> <codigo>
ARQUIVO="$1"
MARCADOR="$2"
CODIGO="$3"

if grep -q "$MARCADOR" "$ARQUIVO"; then
  sed -i "/$MARCADOR/a $CODIGO" "$ARQUIVO"
  echo "✅ Código inserido após '$MARCADOR' no arquivo '$ARQUIVO'"
else
  echo "⚠️ Marcador '$MARCADOR' não encontrado em '$ARQUIVO'"
fi
