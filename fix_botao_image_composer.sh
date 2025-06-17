#!/bin/bash

ARQ="windows/compositor_window.py"

echo "🔧 Injetando botão '🧩 Compositor de Imagens'..."

# 1. Verifica se já existe o botão
if grep -q 'self.image_composer_btn = self.create_button("🧩 Compositor de Imagens"' "$ARQ"; then
    echo "⚠️ Botão já existe. Nenhuma alteração feita."
    exit 0
fi

# 2. Injeta a instância da janela se necessário
grep -q 'self.image_composer_window = ImageComposerWindow()' "$ARQ" || \
sed -i '/self.base_window = BaseWindow()/a \        self.image_composer_window = ImageComposerWindow()' "$ARQ"

# 3. Injeta a criação do botão
sed -i '/self.base_btn = self.create_button("🖼️ Base", self.open_base, primary=True)/a \        self.image_composer_btn = self.create_button("🧩 Compositor de Imagens", self.open_image_composer, primary=True)' "$ARQ"

# 4. Injeta o botão no layout
sed -i '/self.top_button_layout.addWidget(self.base_btn)/a \        self.top_button_layout.addWidget(self.image_composer_btn)' "$ARQ"

# 5. Adiciona o método open_image_composer se necessário
if ! grep -q 'def open_image_composer(self):' "$ARQ"; then
cat <<EOF >> "$ARQ"

    def open_image_composer(self):
        self.image_composer_window.show()
EOF
fi

echo "✅ Botão injetado com sucesso!"
