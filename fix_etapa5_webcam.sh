#!/bin/bash
echo "🧩 Corrigindo instanciamento direto de WebcamWindow no compositor_window.py..."

ARQUIVO="windows/compositor_window.py"

# Remove instanciação direta incorreta
sed -i '/self.webcam_window = WebcamWindow()/d' "$ARQUIVO"
sed -i '/self.webcam_window.show()/d' "$ARQUIVO"
sed -i '/self.base_window = BaseWindow()/d' "$ARQUIVO"
sed -i '/self.base_window.show()/d' "$ARQUIVO"

# Rodar black para organizar
echo "🧹 Rodando black..."
black "$ARQUIVO"

echo "✅ Correção aplicada: webcam e base instanciadas apenas quando clicadas."
