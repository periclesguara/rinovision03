#!/bin/bash

ARQ="windows/compositor_window.py"
echo "🔍 Checando integridade de $ARQ..."

# 1. Importação
grep -q 'from windows.image_composer_window import ImageComposerWindow' "$ARQ" && \
echo "✅ Importação do ImageComposerWindow OK" || \
echo "❌ Importação do ImageComposerWindow FALTANDO"

# 2. Instanciação
grep -q 'self.image_composer_window = ImageComposerWindow(self.scene_manager)' "$ARQ" && \
echo "✅ Instanciação no método OK" || \
echo "❌ Instanciação da janela FALTANDO"

# 3. Método open_image_composer
grep -q 'def open_image_composer(self):' "$ARQ" && \
echo "✅ Função open_image_composer OK" || \
echo "❌ Função open_image_composer FALTANDO"

# 4. Criação do botão
grep -q 'self.image_composer_btn = self.create_button("🧩 Compositor de Imagens"' "$ARQ" && \
echo "✅ Criação do botão image_composer_btn OK" || \
echo "❌ Criação do botão image_composer_btn FALTANDO"

# 5. Adição ao layout
grep -q 'self.top_button_layout.addWidget(self.image_composer_btn)' "$ARQ" && \
echo "✅ Botão adicionado ao layout OK" || \
echo "❌ Botão adicionado ao layout FALTANDO"

# 6. Teste de sintaxe
echo "🧪 Testando se arquivo pode ser interpretado..."
python3 -m py_compile "$ARQ" && \
echo "✅ Arquivo compila com sucesso!" || \
echo "❌ ERRO de sintaxe detectado"
