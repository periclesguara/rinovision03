#!/bin/bash

ARQ="windows/compositor_window.py"

echo "🛠️ Inserindo ImageComposerWindow no Compositor..."

# 1. Importação se não existir
grep -q 'from windows.image_composer_window import ImageComposerWindow' "$ARQ" || \
sed -i '/from windows.base_window import BaseWindow/a from windows.image_composer_window import ImageComposerWindow' "$ARQ"

# 2. Instanciação no __init__ se não existir
grep -q 'self.image_composer_window = ImageComposerWindow()' "$ARQ" || \
sed -i '/self.base_window = BaseWindow()/a \ \ \ \ \ \ \ \ self.image_composer_window = ImageComposerWindow()' "$ARQ"

# 3. Adiciona botão no init_ui (ou setup_ui)
grep -q 'self.image_composer_btn' "$ARQ" || \
sed -i '/self.base_btn = self.create_button/a \ \ \ \ \ \ \ \ self.image_composer_btn = self.create_button("🧩 Compositor de Imagens", self.open_image_composer, primary=True)\n        self.top_button_layout.addWidget(self.image_composer_btn)' "$ARQ"

# 4. Adiciona método open_image_composer
grep -q 'def open_image_composer' "$ARQ" || cat <<EOM >> "$ARQ"

    def open_image_composer(self):
        self.image_composer_window.show()
EOM

# 5. Rodar black pra formatar bonito
black "$ARQ"

echo "✅ ImageComposerWindow injetado com sucesso!"
