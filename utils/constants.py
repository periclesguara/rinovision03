# 🚀 Configurações Gerais do RinoVision03

# 🗂️ Pastas padrão
FRAMES_DIR = "frames"
OUTPUT_DIR = "output"
MUSIC_DIR = "music"
ASSETS_DIR = "assets"
ICONS_DIR = "assets/icons"
BACKGROUNDS_DIR = "assets/backgrounds"

# 🎥 Configurações de vídeo
VIDEO_WIDTH = 1440
VIDEO_HEIGHT = 810
VIDEO_RESOLUTION = (VIDEO_WIDTH, VIDEO_HEIGHT)
FPS = 30

# 🎙️ Configurações de áudio
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2

# 🎬 Nomes padrão dos arquivos
FRAME_PATTERN = f"{FRAMES_DIR}/frame_%04d.png"
TEMP_VIDEO_FILE = f"{OUTPUT_DIR}/video_temp.mp4"
TEMP_AUDIO_FILE = f"{OUTPUT_DIR}/audio_temp.wav"
FINAL_VIDEO_FILE = f"{OUTPUT_DIR}/gravacao_final.mp4"

# 💡 Cores padrão (usável no futuro pra temas)
COLOR_BACKGROUND = "#f0f0f0"
COLOR_PANEL = "#333"
COLOR_BORDER = "#888"
COLOR_TEXT = "#fff"

# 📝 Legenda padrão
DEFAULT_CAPTION = ""

# 🔊 Debug Mode
DEBUG_MODE = True
