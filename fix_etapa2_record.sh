#!/bin/bash

ARQUIVO="windows/compositor_window.py"

echo "🔧 Corrigindo ordem de argumentos do RecordManager..."

# Corrige instanciamento incorreto do RecordManager
sed -i 's/self.record_manager = RecordManager(preview_widget, self.audio_manager)/self.record_manager = RecordManager(self.audio_manager)\n        self.record_manager.set_frame_callback(preview_widget.grab)/g' "$ARQUIVO"

echo "✅ Etapa 2 concluída: RecordManager corrigido no $ARQUIVO."
