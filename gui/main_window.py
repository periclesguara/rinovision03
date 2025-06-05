from PySide6.QtWidgets import (
    QMainWindow, QMdiArea, QToolBar, QPushButton, QStatusBar,
    QMenuBar, QMenu, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

# Importando as janelas do projeto
from windows.compositor_window import CompositorWindow
from windows.webcam_window import WebcamWindow
from windows.base_window import BaseWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RinoVision03 - Studio Pro")
        self.setGeometry(100, 100, 1600, 900)

        # Área de múltiplas janelas internas (workspaces)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        # Construindo UI
        self._create_menubar()
        self._create_toolbar()
        self._create_statusbar()

    # =====================
    # Barra de Menus
    # =====================
    def _create_menubar(self):
        menubar = self.menuBar()

        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")

        new_action = QAction("Novo Projeto", self)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Janelas
        window_menu = menubar.addMenu("Janelas")

        compositor_action = QAction("Abrir Compositor", self)
        compositor_action.triggered.connect(self.open_compositor)
        window_menu.addAction(compositor_action)

        webcam_action = QAction("Abrir Webcam", self)
        webcam_action.triggered.connect(self.open_webcam)
        window_menu.addAction(webcam_action)

        base_action = QAction("Abrir BaseWindow", self)
        base_action.triggered.connect(self.open_base)
        window_menu.addAction(base_action)

        # Menu Ajuda
        help_menu = menubar.addMenu("Ajuda")

        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # =====================
    # Toolbar
    # =====================
    def _create_toolbar(self):
        toolbar = QToolBar("Painel de Ferramentas")
        self.addToolBar(toolbar)

        compositor_btn = QPushButton("Compositor")
        compositor_btn.clicked.connect(self.open_compositor)
        toolbar.addWidget(compositor_btn)

        webcam_btn = QPushButton("Webcam")
        webcam_btn.clicked.connect(self.open_webcam)
        toolbar.addWidget(webcam_btn)

        base_btn = QPushButton("Base")
        base_btn.clicked.connect(self.open_base)
        toolbar.addWidget(base_btn)

    # =====================
    # StatusBar
    # =====================
    def _create_statusbar(self):
        status = QStatusBar()
        status.showMessage("Pronto")
        self.setStatusBar(status)

    def update_status(self, message):
        """Atualiza a barra de status."""
        self.statusBar().showMessage(message, 5000)  # Mensagem fica por 5 segundos

    # =====================
    # Funções dos Menus
    # =====================
    def _new_project(self):
        """Fecha todas as janelas e inicia novo projeto."""
        self.mdi.closeAllSubWindows()
        self.update_status("Novo projeto iniciado.")

    def _show_about(self):
        """Exibe a janela Sobre."""
        QMessageBox.information(
            self, "Sobre RinoVision03",
            "RinoVision03 Studio Pro\nDesenvolvido por Péricles.\nVersão 1.0"
        )

    # =====================
    # Abertura das Janelas
    # =====================
    def open_compositor(self):
        compositor = CompositorWindow()
        compositor.setAttribute(Qt.WA_DeleteOnClose)
        self.mdi.addSubWindow(compositor)
        compositor.show()
        self.update_status("Compositor aberto.")

    def open_webcam(self):
        webcam = WebcamWindow()
        webcam.setAttribute(Qt.WA_DeleteOnClose)
        self.mdi.addSubWindow(webcam)
        webcam.show()
        self.update_status("Webcam aberta.")

    def open_base(self):
        base = BaseWindow()
        base.setAttribute(Qt.WA_DeleteOnClose)
        self.mdi.addSubWindow(base)
        base.show()
        self.update_status("Base aberta.")
