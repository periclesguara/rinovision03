import os
import threading
import time
import sounddevice as sd
import soundfile as sf


class MusicManager:
    def __init__(self):
        self.music_file = None
        self.music_data = None
        self.samplerate = 44100
        self.play_thread = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0  # Em frames
        self.volume = 1.0

    def load_music(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

        self.music_data, self.samplerate = sf.read(file_path, dtype='float32')
        self.music_file = file_path
        self.position = 0
        print(f"🎶 [MusicManager] Música carregada: {file_path}")

    def play(self):
        if self.music_data is None:
            print("[MusicManager] Nenhuma música carregada.")
            return

        if self.is_playing and not self.is_paused:
            print("[MusicManager] Já está tocando.")
            return

        self.is_playing = True
        self.is_paused = False

        self.play_thread = threading.Thread(target=self._playback)
        self.play_thread.start()
        print("[MusicManager] ▶ Tocando trilha...")

    def _playback(self):
        remaining = self.music_data[self.position:]
        sd.play(remaining * self.volume, self.samplerate)

        while self.is_playing and self.position < len(self.music_data):
            time.sleep(0.1)
            if self.is_paused:
                sd.stop()
                return

        self.stop()

    def pause(self):
        if not self.is_playing:
            return

        self.is_paused = True
        self.is_playing = False
        self.position += int(self.samplerate * sd.get_stream().time)
        sd.stop()
        print("[MusicManager] ⏸ Pausado.")

    def stop(self):
        if not self.is_playing and not self.is_paused:
            return

        self.is_playing = False
        self.is_paused = False
        self.position = 0
        sd.stop()
        print("[MusicManager] ⏹ Parado.")

    def set_volume(self, volume):
        """Volume entre 0.0 e 1.0"""
        self.volume = max(0.0, min(volume, 1.0))
        print(f"[MusicManager] 🔊 Volume ajustado para {self.volume}")

    def reset(self):
        self.stop()
        self.music_file = None
        self.music_data = None
        self.position = 0
        self.volume = 1.0
        print("[MusicManager] 🔄 Resetado.")


if __name__ == "__main__":
    # 🚀 Teste independente
    mm = MusicManager()
    mm.load_music("music_test.wav")

    mm.set_volume(0.8)
    mm.play()

    time.sleep(5)
    mm.pause()

    time.sleep(2)
    mm.play()

    time.sleep(3)
    mm.stop()
