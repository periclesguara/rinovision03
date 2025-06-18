#!/bin/bash

ARQUIVO="managers/scene_manager.py"

echo "🔧 Corrigindo NameError de SceneOptionsWindow..."

# Adiciona import da janela se não existir
grep -qxF 'from windows.scene_options_window import SceneOptionsWindow' "$ARQUIVO" || echo 'from windows.scene_options_window import SceneOptionsWindow' >> "$ARQUIVO"

# Adiciona função open_scene_options ao final do arquivo
cat <<EOL >> "$ARQUIVO"

def open_scene_options():
    window = SceneOptionsWindow()
    window.show()
EOL

echo "✅ Etapa 3 concluída: SceneOptionsWindow corrigido no $ARQUIVO."
