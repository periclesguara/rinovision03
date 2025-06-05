import os
import subprocess
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap


class RecordManager:
    def __init__(self, preview_widget, audio_manager, output_dir="output"):
        self.preview_widget = preview_widget
        self.audio_manager = audio_manager
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.frames = []
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.capture_frame)

        self.counter_timer = QTimer()
        self.counter_timer.timeout.connect(self.update_counter)
        self.elapsed_seconds = 0

        self.recording = False

    def start_recording(self):
        """Inicia a gravação de vídeo e áudio."""
        print("🎥 [RecordManager] Gravação INICIADA.")

        self.frames = []
        self.elapsed_seconds = 0

        self.audio_manager.start_audio_recording()

        self.frame_timer.start(1000 // 30)  # 30 FPS
        self.counter_timer.start(1000)
        self.recording = True

    def stop_recording(self):
        """Finaliza a gravação e faz o merge."""
        print("🛑 [RecordManager] Gravação FINALIZADA.")

        self.frame_timer.stop()
        self.counter_timer.stop()
        self.recording = False

        self.audio_manager.stop_audio_recording()

        video_output = os.path.join(self.output_dir, "video_temp.mp4")
        final_output = os.path.join(self.output_dir, "gravacao_final.mp4")
        frame_pattern = os.path.join(self.output_dir, "frame_%04d.png")

        # Salvar frames
        for idx, frame in enumerate(self.frames):
            frame.save(os.path.join(self.output_dir, f"frame_{idx:04d}.png"))

        # Gerar vídeo a partir dos frames
        subprocess.call([
            "ffmpeg", "-y", "-framerate", "30", "-i", frame_pattern,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", video_output
        ])

        # Combinar vídeo com áudio
        subprocess.call([
            "ffmpeg", "-y", "-i", video_output, "-i", self.audio_manager.get_audio_file(),
            "-c:v", "copy", "-c:a", "aac", final_output
        ])

        print(f"✅ [RecordManager] Vídeo final salvo em {final_output}")

        # Gerar legenda a partir do áudio
        from managers.subtitle_manager import gerar_legenda
        legenda = gerar_legenda(self.audio_manager.get_audio_file())
        legenda_path = os.path.join(self.output_dir, "gravacao_final.txt")
        with open(legenda_path, "w", encoding="utf-8") as f:
            f.write(legenda)
        print(f"📝 [RecordManager] Legenda salva em {legenda_path}")

        return final_output

    def capture_frame(self):
        """Captura um frame atual do preview."""
        pixmap = self.preview_widget.grab()
        self.frames.append(pixmap)

    def update_counter(self):
        """Atualiza contador interno."""
        self.elapsed_seconds += 1
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        print(f"⏱️ [RecordManager] {mins:02d}:{secs:02d}")

    def is_recording(self):
        """Retorna status atual."""
        return self.recording

    def reset(self):
        """Reseta dados para uma nova gravação."""
        self.frames = []
        self.elapsed_seconds = 0
        self.audio_manager.reset()
