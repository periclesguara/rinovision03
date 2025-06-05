#!/bin/bash

# PATCH: Geração de legenda automática após gravação de áudio+vídeo

# Adiciona método get_audio_file ao AudioManager
if ! grep -q "get_audio_file" managers/audio_manager.py; then
  echo "[PATCH] Adicionando get_audio_file() ao AudioManager..."
  cat >> managers/audio_manager.py << 'EOF'

    def get_audio_file(self):
        return self.filename
EOF
fi

# Cria subtitle_manager.py com função gerar_legenda
if [ ! -f managers/subtitle_manager.py ]; then
  echo "[PATCH] Criando managers/subtitle_manager.py..."
  cat > managers/subtitle_manager.py << 'EOF'
import speech_recognition as sr
import os

def gerar_legenda(audio_path="audio_temp.wav"):
    if not os.path.exists(audio_path):
        print(f"[Legenda] Arquivo não encontrado: {audio_path}")
        return ""

    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)

    try:
        texto = r.recognize_google(audio, language="pt-BR")
        print(f"[Legenda] Transcrição detectada:\n{texto}")
        return texto
    except sr.UnknownValueError:
        print("[Legenda] Não foi possível entender o áudio.")
        return ""
    except sr.RequestError as e:
        print(f"[Legenda] Erro de requisição: {e}")
        return ""
EOF
fi

# Injeta chamada à legenda no stop_recording do RecordManager
if ! grep -q "gerar_legenda" managers/record_manager.py; then
  echo "[PATCH] Inserindo geração de legenda em RecordManager..."
  sed -i '/return final_output/i \
        # Gerar legenda a partir do áudio\
        from managers.subtitle_manager import gerar_legenda\
        legenda = gerar_legenda(self.audio_manager.get_audio_file())\
        legenda_path = os.path.join(self.output_dir, "gravacao_final.txt")\
        with open(legenda_path, "w", encoding="utf-8") as f:\
            f.write(legenda)\
        print(f"📝 [RecordManager] Legenda salva em {legenda_path}")\
' managers/record_manager.py
fi

echo "[✔] Patch de legenda aplicado com sucesso."
