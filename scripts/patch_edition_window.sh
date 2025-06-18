#!/bin/bash

TARGET=~/Projetos/RINOVISION03/windows/edition_window.py

echo "🔧 Patchando: $TARGET"

# Adiciona a função para nome sequencial no topo do arquivo
sed -i '1i\
def gerar_nome_arquivo_sequencial(pasta, prefixo="gravacao_final", extensao=".mp4"):\n\
    i = 1\n\
    while True:\n\
        nome = f"{prefixo}_{i:03d}{extensao}"\n\
        caminho = os.path.join(pasta, nome)\n\
        if not os.path.exists(caminho):\n\
            return caminho\n\
        i += 1\n' "$TARGET"

# Substitui a linha final de stop_recording com lógica de renomear
sed -i '/def stop_recording(self):/,/print(f"🎥 Vídeo salvo em:/c\
    def stop_recording(self):\n\
        print("⏹️ Parando gravação...")\n\
        output_path = gerar_nome_arquivo_sequencial("output", "gravacao_final")\n\
        final_path = self.record_manager.stop_recording()\n\
        os.rename(final_path, output_path)\n\
        print(f"🎥 Vídeo salvo em: {output_path}")' "$TARGET"

echo "✅ Patch aplicado ao EditionWindow!"
