#!/bin/bash

TARGET=~/Projetos/RINOVISION03/windows/compositor_window.py

echo "🔧 Patchando: $TARGET"

# Adiciona botão no __init__
sed -i '/button_row.addStretch()/i \

# Adiciona função ao final do arquivo
echo '
    def add_manual_caption(self):
        from managers.subtitle_manager import DraggableSubtitle
        subtitle = DraggableSubtitle("Digite sua legenda", self)
        subtitle.move(100, 900)
        subtitle.show()
' >> "$TARGET"

echo "✅ Patch aplicado com sucesso!"
