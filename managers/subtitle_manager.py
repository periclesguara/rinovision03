import json
from PySide6.QtWidgets import QLabel, QLineEdit
from PySide6.QtCore import Qt, QPoint, QTimer


class DraggableSubtitle(QLabel):
    """Legenda móvel e editável."""
    def __init__(self, text, parent=None, start_time=0, end_time=None):
        super().__init__(text, parent)
        self.start_time = start_time
        self.end_time = end_time
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            color: white;
            font-size: 28px;
            padding: 8px;
            border-radius: 6px;
        """)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAlignment(Qt.AlignCenter)

        self._drag_active = False
        self._drag_position = QPoint()

        self.edit_mode = False
        self.editor = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ControlModifier:
                self.toggle_edit()
            else:
                self._drag_active = True
                self._drag_position = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            new_pos = event.globalPosition().toPoint() - self._drag_position
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        self._drag_active = False

    def toggle_edit(self):
        if not self.edit_mode:
            self.editor = QLineEdit(self.text(), self.parent())
            self.editor.setGeometry(self.geometry())
            self.editor.setStyleSheet(self.styleSheet())
            self.editor.returnPressed.connect(self.finish_edit)
            self.hide()
            self.editor.show()
            self.editor.setFocus()
            self.edit_mode = True
        else:
            self.finish_edit()

    def finish_edit(self):
        new_text = self.editor.text()
        self.setText(new_text)
        self.editor.hide()
        self.editor.deleteLater()
        self.show()
        self.edit_mode = False


class SubtitleManager:
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.subtitles = []
        self.timer = QTimer()
        self.current_time = 0  # segundos
        self.timer.timeout.connect(self.update_visibility)

    def start_timer(self):
        self.timer.start(1000)
        print("[SubtitleManager] ⏱️ Timer iniciado.")

    def stop_timer(self):
        self.timer.stop()
        print("[SubtitleManager] ⏹️ Timer parado.")

    def reset_timer(self):
        self.current_time = 0
        print("[SubtitleManager] 🔄 Timer zerado.")

    def tick(self):
        self.current_time += 1
        self.update_visibility()

    def update_visibility(self):
        for label in self.subtitles:
            if (label.start_time <= self.current_time and
                (label.end_time is None or self.current_time <= label.end_time)):
                label.show()
            else:
                label.hide()

    def add_subtitle(self, text, x=None, y=None, start_time=0, end_time=None):
        label = DraggableSubtitle(text, self.parent, start_time, end_time)
        label.adjustSize()

        if x is None or y is None:
            x = (self.parent.width() - label.width()) // 2
            y = self.parent.height() - label.height() - 50

        label.move(x, y)
        label.show()

        self.subtitles.append(label)
        print(f"[SubtitleManager] ➕ Legenda adicionada: '{text}' ({start_time}s - {end_time}s)")

        return label

    def remove_subtitle(self, label):
        if label in self.subtitles:
            label.hide()
            label.deleteLater()
            self.subtitles.remove(label)
            print("[SubtitleManager] ➖ Legenda removida.")

    def clear_subtitles(self):
        for label in self.subtitles:
            label.hide()
            label.deleteLater()
        self.subtitles = []
        print("[SubtitleManager] 🗑️ Todas as legendas removidas.")

    def export_subtitles(self, filename="subtitles.json"):
        data = []
        for label in self.subtitles:
            item = {
                "text": label.text(),
                "x": label.x(),
                "y": label.y(),
                "start_time": label.start_time,
                "end_time": label.end_time
            }
            data.append(item)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[SubtitleManager] 💾 Legendas exportadas para {filename}")

    def import_subtitles(self, filename="subtitles.json"):
        if not filename or not filename.endswith(".json"):
            print("[SubtitleManager] ❌ Arquivo inválido.")
            return

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.clear_subtitles()

        for item in data:
            self.add_subtitle(
                text=item["text"],
                x=item["x"],
                y=item["y"],
                start_time=item.get("start_time", 0),
                end_time=item.get("end_time", None)
            )

        print(f"[SubtitleManager] ✅ Legendas importadas de {filename}")


if __name__ == "__main__":
    # 🚀 Teste independente
    from PySide6.QtWidgets import QApplication, QWidget
    import sys

    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 1280, 720)
    window.setWindowTitle("Test Subtitle Manager")
    window.show()

    sm = SubtitleManager(window)
    sm.add_subtitle("Legenda 1", start_time=0, end_time=5)
    sm.add_subtitle("Legenda 2", start_time=5, end_time=10)

    sm.start_timer()

    sys.exit(app.exec())
