import os
import shutil


class FileManager:
    def __init__(self, base_dirs=None):
        if base_dirs is None:
            base_dirs = ["output", "frames", "music"]
        self.base_dirs = base_dirs
        self.ensure_directories()

    def ensure_directories(self):
        """Cria as pastas necessárias se não existirem."""
        for directory in self.base_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 [FileManager] Pasta garantida: {directory}")

    def clean_frames(self):
        """Limpa os frames temporários."""
        frame_dir = "frames"
        if os.path.exists(frame_dir):
            files = os.listdir(frame_dir)
            for file in files:
                if file.endswith(".png"):
                    os.remove(os.path.join(frame_dir, file))
            print("🧹 [FileManager] Frames temporários removidos.")

    def clean_output(self):
        """Limpa a pasta de output."""
        output_dir = "output"
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            for file in files:
                os.remove(os.path.join(output_dir, file))
            print("🧹 [FileManager] Output limpo.")

    def reset_project(self):
        """Apaga tudo de frames e output."""
        self.clean_frames()
        self.clean_output()

    def check_file_exists(self, filepath):
        """Verifica se um arquivo existe."""
        return os.path.exists(filepath)

    def delete_file(self, filepath):
        """Deleta um arquivo específico."""
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"❌ [FileManager] Arquivo deletado: {filepath}")

    def copy_file(self, src, dst):
        """Copia um arquivo."""
        shutil.copy2(src, dst)
        print(f"📁 [FileManager] Arquivo copiado de {src} para {dst}")
