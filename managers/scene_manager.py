import ffmpeg
import time
import threading
import subprocess


class SceneManager:
    def __init__(self):
        self.objects = {}
        self.is_recording = False
        self.video_process = None
        self.output_file = "output_final.mp4"

    def add_object(
        self, name, x=0, y=0, width=100, height=100, z_index=0, visible=True
    ):
        self.objects[name] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "locked": False,
            "z_index": z_index,
            "visible": visible,
        }
        print(f"[SceneManager] Objeto '{name}' adicionado.")

    def update_position(self, name, x, y):
        if name in self.objects and not self.objects[name]["locked"]:
            self.objects[name]["x"] = x
            self.objects[name]["y"] = y
            print(f"[SceneManager] Objeto '{name}' movido para ({x}, {y}).")

    def update_size(self, name, width, height):
        if name in self.objects and not self.objects[name]["locked"]:
            self.objects[name]["width"] = width
            self.objects[name]["height"] = height
            print(
                f"[SceneManager] Objeto '{name}' redimensionado para {width}x{height}."
            )

    def set_locked(self, name, locked=True):
        if name in self.objects:
            self.objects[name]["locked"] = locked
            estado = "travado" if locked else "destravado"
            print(f"[SceneManager] Objeto '{name}' {estado}.")

    def set_visibility(self, name, visible=True):
        if name in self.objects:
            self.objects[name]["visible"] = visible
            estado = "visível" if visible else "oculto"
            print(f"[SceneManager] Objeto '{name}' agora está {estado}.")

    def lock_group(self, names):
        for name in names:
            self.set_locked(name, True)
        print(f"[SceneManager] Grupo {names} travado como conjunto.")

    def unlock_group(self, names):
        for name in names:
            self.set_locked(name, False)
        print(f"[SceneManager] Grupo {names} destravado como conjunto.")

    def get_object_state(self, name):
        return self.objects.get(name, None)

    def get_all_objects(self):
        return self.objects

    def reset(self):
        self.objects.clear()
        print("[SceneManager] Todos os objetos foram removidos.")

    def iniciar_gravacao(self):
        if self.is_recording:
            print("[SceneManager] Gravação já está em andamento.")
            return

        print("[SceneManager] Iniciando gravação com ffmpeg...")
        self.is_recording = True

        def gravar():
            try:
                self.output_file = f"gravacao_{int(time.time())}.mp4"
                comando = [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "pulse",
                    "-i",
                    "default",
                    "-f",
                    "x11grab",
                    "-r",
                    "30",
                    "-s",
                    "1280x720",
                    "-i",
                    ":0.0",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-c:a",
                    "aac",
                    self.output_file,
                ]
                self.video_process = subprocess.Popen(comando)
                print(f"[SceneManager] Gravando em: {self.output_file}")
            except Exception as e:
                print(f"[SceneManager] Erro ao iniciar gravação: {e}")

        threading.Thread(target=gravar, daemon=True).start()

    def parar_gravacao(self):
        if self.is_recording and self.video_process:
            print("[SceneManager] Parando gravação...")
            self.video_process.terminate()
            self.video_process = None
            self.is_recording = False
            print(f"[SceneManager] Gravação finalizada: {self.output_file}")
        else:
            print("[SceneManager] Nenhuma gravação ativa para parar.")
