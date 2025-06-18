#!/bin/bash

ARQ="windows/compositor_window.py"
TMP="tmp_fix_compositor.py"

echo "🚨 Limpando erros e refatorando $ARQ..."

# 1. Remove linhas automáticas mal inseridas
sed '/# \[AUTO-INSERT\]/d' "$ARQ" > "$TMP"

# 2. Remove imports duplicados mal indentados
sed -i '/^[[:space:]]*from windows\.image_composer_window import ImageComposerWindow/d' "$TMP"

# 3. Reinsere import corretamente após os outros imports de windows.*
awk '
/from windows\.webcam_window import WebcamWindow/ {
    print
    print "from windows.image_composer_window import ImageComposerWindow"
    next
}
{ print }
' "$TMP" > "$ARQ"

# 4. Remove função quebrada se houver
sed -i '/def open_image_composer/,/^$/d' "$ARQ"

# 5. Insere função correta ao final
cat << 'EOF' >> "$ARQ"

    def open_image_composer(self):
        if self.image_composer_window is None:
            self.image_composer_window = ImageComposerWindow(self.scene_manager)
        self.image_composer_window.show()

EOF

# 6. Valida sintaxe
echo "🧪 Validando sintaxe com Python..."
python3 -m py_compile "$ARQ" && echo "✅ Sintaxe OK" || echo "❌ ERRO de sintaxe em $ARQ"

# 7. Testes de integridade
echo "🔍 Rodando testes de integridade..."
grep -q 'from windows.image_composer_window import ImageComposerWindow' "$ARQ" && echo "✅ Importação OK" || echo "❌ Importação FALTANDO"
grep -q 'self.image_composer_window = ImageComposerWindow(self.scene_manager)' "$ARQ" && echo "✅ Instanciação OK" || echo "❌ Instanciação FALTANDO"
grep -q 'def open_image_composer(self):' "$ARQ" && echo "✅ Método open_image_composer OK" || echo "❌ Método open_image_composer FALTANDO"
grep -q 'self.image_composer_btn = self.create_button("🧩 Compositor de Imagens"' "$ARQ" && echo "✅ Botão image_composer_btn OK" || echo "❌ Botão FALTANDO"
