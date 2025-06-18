#!/bin/bash

ARQ="windows/compositor_window.py"

# Adiciona importações
sed -i '/from PySide6.QtCore import QUrl/a\
from PySide6.QtCore import QTimer, QTime\
from windows.edition_window import EditionWindow' $ARQ

# Adiciona atributos no __init__
sed -i '/self.audio_manager = AudioManager()/a\
        self.timer = QTimer()\
        self.time = QTime(0, 0)\
        self.timer.timeout.connect(self.update_timer)\
        self.timer_label = QLabel("00:00")\
        self.timer_label.setStyleSheet("font-size: 18px; color: #0f0;")\
        self.edition_button = QPushButton("Abrir Edition")\
        self.edition_button.clicked.connect(self.open_edition_window)' $ARQ

# Adiciona ao layout de controle
sed -i '/layout.addLayout(controls)/i\
        controls.addWidget(self.timer_label)\
        controls.addWidget(self.edition_button)' $ARQ

# Adiciona funções ao final do arquivo
cat << 'FIM' >> $ARQ

    def update_timer(self):
        self.time = self.time.addSecs(1)
        self.timer_label.setText(self.time.toString("mm:ss"))

    def open_edition_window(self):
        self.edition_window = EditionWindow()
        self.edition_window.show()

FIM

# Atualiza start_recording
sed -i '/def start_recording(self):/a\
        self.time = QTime(0, 0)\
        self.timer.start(1000)' $ARQ

# Atualiza stop_recording
sed -i '/def stop_recording(self):/a\
        self.timer.stop()\
        self.timer_label.setText("00:00")' $ARQ

echo "✅ Patch aplicado ao CompositorWindow com sucesso."
