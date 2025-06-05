import sounddevice as sd
import soundfile as sf
import threading


class AudioManager:
    def __init__(self):
        self.is_recording = False
        self.audio_data = None
        self.samplerate = 44100
        self.channels = 2
        self.filename = "audio_temp.wav"
        self._thread = None

    def start_recording(self):
        if self.is_recording:
            print("[AudioManager] Já está gravando!")
            return

        print("[AudioManager] Iniciando gravação de áudio...")
        self.is_recording = True
        self.audio_data = []

        self._thread = threading.Thread(target=self._record)
        self._thread.start()

    def _record(self):
        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self._callback):
            while self.is_recording:
                sd.sleep(100)

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[AudioManager] Status: {status}")
        self.audio_data.append(indata.copy())

    def stop_recording(self):
        if not self.is_recording:
            print("[AudioManager] Não estava gravando.")
            return

        print("[AudioManager] Parando gravação...")
        self.is_recording = False
        self._thread.join()

        audio_np = b''.join([x.tobytes() for x in self.audio_data])
        total_frames = sum(x.shape[0] for x in self.audio_data)

        with sf.SoundFile(self.filename, mode='w', samplerate=self.samplerate,
                           channels=self.channels, subtype='PCM_16') as file:
            for chunk in self.audio_data:
                file.write(chunk)

        print(f"[AudioManager] Áudio salvo em {self.filename}")

    def reset(self):
        self.audio_data = []
        self.is_recording = False


if __name__ == "__main__":
    # 🚀 Teste independente
    import time

    audio = AudioManager()

    print("Gravando por 5 segundos...")
    audio.start_recording()
    time.sleep(5)
    audio.stop_recording()
    print("Áudio gravado com sucesso!")
