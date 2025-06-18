import pytest
from PySide6.QtWidgets import QApplication
from windows.compositor_window import CompositorWindow


@pytest.fixture
def app(qtbot):
    test_app = QApplication.instance() or QApplication([])
    yield test_app


def test_window_title(qtbot, app):
    window = CompositorWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() != ""
    assert "RinoVision" in window.windowTitle()
