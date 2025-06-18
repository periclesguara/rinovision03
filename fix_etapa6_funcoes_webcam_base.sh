#!/bin/bash

ARQUIVO="windows/compositor_window.py"
echo "🔧 Reescrevendo métodos open_webcam_window e open_base_window com indentação correta..."

# Remove métodos duplicados se existirem
sed -i '/def open_webcam_window/,/self.webcam_window.show()/d' "$ARQUIVO"
sed -i '/def open_base_window/,/self.base_window.show()/d' "$ARQUIVO"

# Adiciona blocos com indentação certinha ao final do arquivo
cat <<EOF >> "$ARQUIVO"

    def open_webcam_window(self):
        from windows.webcam_window import WebcamWindow
        self.webcam_window = WebcamWindow()
        self.webcam_window.show()

    def open_base_window(self):
        from windows.base_window import BaseWindow
        self.base_window = BaseWindow()
        self.base_window.show()
EOF

# Rodar black
echo "🧹 Formatando com black..."
black "$ARQUIVO"

echo "✅ Funções reescritas com sucesso e formatadas!"
