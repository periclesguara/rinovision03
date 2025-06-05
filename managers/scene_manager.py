import json
import os


class SceneManager:
    def __init__(self):
        # Estrutura: {'nome_objeto': {propriedades}}
        self.objects = {}
        print("[SceneManager] ✅ Inicializado.")

    def add_object(self, name, x=0, y=0, width=640, height=360, locked=False, z_index=0, visible=True):
        self.objects[name] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'locked': locked,
            'z_index': z_index,
            'visible': visible
        }
        print(f"[SceneManager] ➕ Objeto '{name}' adicionado.")

    def update_position(self, name, x, y):
        if name in self.objects:
            self.objects[name]['x'] = x
            self.objects[name]['y'] = y
            print(f"[SceneManager] 🔄 Posição de '{name}' atualizada para ({x}, {y}).")

    def update_size(self, name, width, height):
        if name in self.objects:
            self.objects[name]['width'] = width
            self.objects[name]['height'] = height
            print(f"[SceneManager] 🔄 Tamanho de '{name}' atualizado para {width}x{height}.")

    def set_locked(self, name, locked=True):
        if name in self.objects:
            self.objects[name]['locked'] = locked
            status = "🔒" if locked else "🔓"
            print(f"[SceneManager] {status} '{name}'.")

    def set_visibility(self, name, visible=True):
        if name in self.objects:
            self.objects[name]['visible'] = visible
            status = "👁️" if visible else "🚫"
            print(f"[SceneManager] {status} '{name}'.")

    def set_z_index(self, name, z_index):
        if name in self.objects:
            self.objects[name]['z_index'] = z_index
            print(f"[SceneManager] 🔢 Z-Index de '{name}' definido como {z_index}.")

    def get_object_state(self, name):
        return self.objects.get(name, None)

    def remove_object(self, name):
        if name in self.objects:
            del self.objects[name]
            print(f"[SceneManager] ➖ Objeto '{name}' removido.")

    def clear_scene(self):
        self.objects = {}
        print("[SceneManager] 🗑️ Cena limpa.")

    def save_scene(self, filename="scene.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.objects, f, indent=4)
        print(f"[SceneManager] 💾 Cena salva em '{filename}'.")

    def load_scene(self, filename="scene.json"):
        if not os.path.exists(filename):
            print("[SceneManager] ❌ Arquivo de cena não encontrado.")
            return

        with open(filename, "r", encoding="utf-8") as f:
            self.objects = json.load(f)
        print(f"[SceneManager] ✅ Cena carregada de '{filename}'.")

    def list_objects(self):
        print("📜 [SceneManager] Objetos na cena:")
        for name, props in self.objects.items():
            print(f" → {name}: {props}")


if __name__ == "__main__":
    # 🚀 Teste independente
    sm = SceneManager()

    sm.add_object("Webcam", x=100, y=200, width=640, height=480, locked=False, z_index=1)
    sm.add_object("BaseWindow", x=300, y=100, width=1280, height=720, locked=True, z_index=0)

    sm.update_position("Webcam", 500, 500)
    sm.set_locked("Webcam", True)
    sm.set_z_index("Webcam", 3)

    sm.save_scene("meu_projeto.json")

    sm.clear_scene()
    sm.load_scene("meu_projeto.json")

    sm.list_objects()
