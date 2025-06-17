#!/bin/bash

ARQ="windows/compositor_window.py"

echo "🔧 Limpando instâncias diretas de WebcamWindow e BaseWindow..."

# Apaga qualquer linha que instancia diretamente essas janelas no escopo global ou no __init__
sed -i '/WebcamWindow()/d' "$ARQ"
sed -i '/BaseWindow()/d' "$ARQ"
sed -i '/from windows.webcam_window import WebcamWindow/d' "$ARQ"
sed -i '/from windows.base_window import BaseWindow/d' "$ARQ"

# Confere se os métodos open_* estão lá, senão injeta
grep -q 'def open_webcam_window' "$ARQ" || cat <<EOF >> "$ARQ"

    def open_webcam_window(self):
        from windows.webcam_window import WebcamWindow
        self.webcam_window = WebcamWindow()
        self.webcam_window.show()

    def open_base_window(self):
        from windows.base_window import BaseWindow
        self.base_window = BaseWindow()
        self.base_window.show()
EOF

# Roda black pra limpar
echo "🧹 Formatando com black..."
black "$ARQ"

echo "✅ Etapa 5: Correções aplicadas com sucesso!"
