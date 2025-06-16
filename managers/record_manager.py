import os
import subprocess
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap


class RecordManager:
    def __init__(self, audio_manager, output_dir="output"):
        self.audio_manager = audio_manager
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.frames = []
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._frame_tick)

        self.counter_timer = QTimer()
        self.counter_timer.timeout.connect(self.update_counter)
        self.elapsed_seconds = 0

        self.recording = False
        self._frame_callback = None  # função externa que injeta o frame

    def set_frame_callback(self, callback_func):
        """Define função externa que fornece o frame."""
        self._frame_callback = callback_func

    def start_recording(self):
        print("🎥 [RecordManager] Gravação INICIADA.")
        self.frames = []
        self.elapsed_seconds = 0
        self.audio_manager.start_audio_recording()
        self.frame_timer.start(1000 // 30)  # 30 FPS
        self.counter_timer.start(1000)
        self.recording = True

    def stop_recording(self):
        print("🛑 [RecordManager] Gravação FINALIZADA.")
        self.frame_timer.stop()
        self.counter_timer.stop()
        self.recording = False
        self.audio_manager.stop_audio_recording()

        video_output = os.path.join(self.output_dir, "video_temp.mp4")
        final_output = os.path.join(self.output_dir, "gravacao_final.mp4")
        frame_pattern = os.path.join(self.output_dir, "frame_%04d.png")

        for idx, frame in enumerate(self.frames):
            frame.save(os.path.join(self.output_dir, f"frame_{idx:04d}.png"))

        subprocess.call(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                "30",
                "-i",
                frame_pattern,
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                video_output,
            ]
        )

        subprocess.call(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_output,
                "-i",
                self.audio_manager.get_audio_file(),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                final_output,
            ]
        )

        print(f"✅ [RecordManager] Vídeo final salvo em {final_output}")

        from managers.subtitle_manager import gerar_legenda

        legenda = gerar_legenda(self.audio_manager.get_audio_file())
        legenda_path = os.path.join(self.output_dir, "gravacao_final.txt")
        with open(legenda_path, "w", encoding="utf-8") as f:
            f.write(legenda)
        print(f"📝 [RecordManager] Legenda salva em {legenda_path}")

        return final_output

    def _frame_tick(self):
        if self._frame_callback:
            pixmap = self._frame_callback()
            if isinstance(pixmap, QPixmap):
                self.frames.append(pixmap)

    def update_counter(self):
        self.elapsed_seconds += 1
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        print(f"⏱️ [RecordManager] {mins:02d}:{secs:02d}")

    def is_recording(self):
        return self.recording

    def reset(self):
        self.frames = []
        self.elapsed_seconds = 0
        self.audio_manager.reset()
