#!/bin/bash

echo "🔧 Corrigindo layout e botões no compositor_window.py ..."

ARQUIVO="windows/compositor_window.py"

# Adiciona os botões se ainda não existem
grep -q 'Webcam' "$ARQUIVO" || sed -i "/def setup_ui(self):/a \ \ \ \ \ \ \ \ self.add_button(\"Webcam\", self.open_webcam_window)" "$ARQUIVO"
grep -q 'Base' "$ARQUIVO" || sed -i "/def setup_ui(self):/a \ \ \ \ \ \ \ \ self.add_button(\"Base\", self.open_base_window)" "$ARQUIVO"

# Garante os métodos de abertura
grep -q 'def open_webcam_window' "$ARQUIVO" || cat <<EOF >> "$ARQUIVO"

    def open_webcam_window(self):
        from windows.webcam_window import WebcamWindow
        self.webcam_window = WebcamWindow()
        self.webcam_window.show()

    def open_base_window(self):
        from windows.base_window import BaseWindow
        self.base_window = BaseWindow()
        self.base_window.show()
EOF

# Corrige layout para alinhar o painel ao topo
sed -i "s/self.setLayout(layout)/layout.setAlignment(self.control_panel, Qt.AlignTop)\n    self.setLayout(layout)/" "$ARQUIVO"

# Rodar black para organizar tudo
echo "🧹 Rodando black para formatar..."
black "$ARQUIVO"

echo "✅ Etapa 4 finalizada: botões corrigidos e alinhamento ajustado!"
