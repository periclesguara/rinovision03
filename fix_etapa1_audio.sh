#!/bin/bash

ARQUIVO="windows/compositor_window.py"

echo "🔧 Corrigindo chamadas incorretas no $ARQUIVO ..."

# Corrige método de INÍCIO de gravação de áudio
sed -i 's/self.audio_manager.start_recording()/self.audio_manager.start_audio_recording()/g' "$ARQUIVO"

# Corrige método de PARADA de gravação de áudio
sed -i 's/self.audio_manager.stop_recording()/self.audio_manager.stop_audio_recording()/g' "$ARQUIVO"

echo "✅ Etapa 1 concluída: Métodos de áudio corrigidos no $ARQUIVO."
