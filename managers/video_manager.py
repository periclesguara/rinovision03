import cv2
import numpy as np
import os


class VideoManager:
    def __init__(self, filename="output.mp4", fps=30, resolution=(1280, 720)):
        self.filename = filename
        self.fps = fps
        self.resolution = resolution
        self.is_recording = False
        self.video_writer = None
        print(f"[VideoManager] Configurado para {self.resolution} @ {self.fps} FPS")

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.filename, fourcc, self.fps, self.resolution
        )
        self.is_recording = True
        print("[VideoManager] Gravação iniciada.")

    def write_frame(self, frame):
        """Recebe frame como QPixmap (convertido) ou numpy array."""
        if not self.is_recording or self.video_writer is None:
            return

        if isinstance(frame, np.ndarray):
            frame_bgr = cv2.resize(frame, self.resolution)
        else:
            # Se vier QPixmap → converte
            image = frame.toImage()
            image = image.convertToFormat(4)  # Format_RGBA8888
            width = image.width()
            height = image.height()

            ptr = image.bits()
            ptr.setsize(image.byteCount())
            arr = np.array(ptr).reshape((height, width, 4))

            frame_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            frame_bgr = cv2.resize(frame_bgr, self.resolution)

        self.video_writer.write(frame_bgr)

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.video_writer.release()
            self.video_writer = None
            print(f"[VideoManager] Gravação finalizada em {self.filename}")

    def merge_audio(self, audio_file, output_file="final_output.mp4"):
        """Une vídeo + áudio usando ffmpeg."""
        print(f"[VideoManager] Mesclando {self.filename} + {audio_file} -> {output_file}")
        cmd = (
            f'ffmpeg -y -i {self.filename} -i {audio_file} '
            f'-c:v copy -c:a aac -strict experimental {output_file}'
        )
        os.system(cmd)
        print(f"[VideoManager] Arquivo final gerado em {output_file}")


if __name__ == "__main__":
    # 🚀 Teste independente
    import time

    vm = VideoManager(filename="teste_video.mp4", resolution=(640, 480))
    vm.start_recording()

    for _ in range(100):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        vm.write_frame(frame)
        time.sleep(1 / 30)

    vm.stop_recording()
    print("Vídeo salvo com sucesso!")
