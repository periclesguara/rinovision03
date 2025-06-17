#!/bin/bash

ARQ="windows/compositor_window.py"
echo "🔍 Checando integridade de $ARQ..."

check() {
    local label="$1"
    local pattern="$2"
    if grep -q "$pattern" "$ARQ"; then
        echo "✅ $label OK"
    else
        echo "❌ $label FALTANDO"
    fi
}

# Checagens principais
check "Importação do ImageComposerWindow" "from windows.image_composer_window import ImageComposerWindow"
check "Instanciação no método" "self\.image_composer_window = ImageComposerWindow()"
check "Função open_image_composer" "def open_image_composer"
check "Criação do botão image_composer_btn" "self\.image_composer_btn = self\.create_button(.*ImageComposerWindow"
check "Botão adicionado ao layout" "self\.top_button_layout\.addWidget\(self\.image_composer_btn\)"

# Opcional: verificar se arquivo está parseável
echo "🧪 Testando se arquivo pode ser interpretado..."
python -m py_compile "$ARQ" && echo "✅ Python parsing OK" || echo "❌ ERRO de sintaxe detectado"

echo "✅ Verificação concluída."
