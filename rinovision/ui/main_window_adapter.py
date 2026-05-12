def launch_legacy_gui():
    from PySide6.QtWidgets import QApplication
    import sys

    try:
        from gui.main_window import MainWindow

        window_class = MainWindow
    except Exception:
        from windows.compositor_window import CompositorWindow

        window_class = CompositorWindow

    app = QApplication.instance() or QApplication(sys.argv)
    window = window_class()
    window.show()
    return app.exec()


def launch_safe_mode():
    try:
        from PySide6.QtWidgets import QApplication, QLabel
        import sys

        app = QApplication.instance() or QApplication(sys.argv)
        label = QLabel("RinoVision safe mode: foundation package loaded.")
        label.resize(520, 120)
        label.show()
        return app.exec()
    except Exception:
        print("RinoVision safe mode: foundation package loaded. GUI dependencies unavailable.")
        return 0
