"""
UI Import Smoke Tests

Verify UI modules can be imported without errors.
STEP 2: Basic import checks, no actual UI tests yet.
"""

import pytest


def test_import_ui_app():
    """Test that app.ui.app can be imported"""
    try:
        from app.ui import app

        assert hasattr(app, "main")
    except ImportError as e:
        pytest.fail(f"Failed to import app.ui.app: {e}")


def test_import_main_window():
    """Test that MainWindow class can be imported"""
    try:
        from app.ui.main_window import MainWindow

        assert MainWindow is not None
    except ImportError as e:
        pytest.fail(f"Failed to import MainWindow: {e}")


def test_import_widgets():
    """Test that all widget modules can be imported"""
    widgets = [
        "top_bar",
        "dock_left",
        "dock_right",
        "asset_grid",
        "selection_tray",
    ]

    for widget_name in widgets:
        try:
            module = __import__(f"app.ui.widgets.{widget_name}", fromlist=[widget_name])
            assert module is not None
        except ImportError as e:
            pytest.fail(f"Failed to import app.ui.widgets.{widget_name}: {e}")


def test_config_settings():
    """Test that settings can be loaded"""
    try:
        from app.core.config import settings

        assert settings.app_env in ["development", "production", "test"]
        assert isinstance(settings.app_debug, bool)
    except ImportError as e:
        pytest.fail(f"Failed to import settings: {e}")


@pytest.mark.skip(reason="Requires display/GUI environment")
def test_create_main_window():
    """
    Test creating MainWindow instance (requires Qt display)

    SKIP: This test requires a display environment.
    Run manually with: pytest -v -m "not skip"
    """
    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow

    app = QApplication([])  # noqa: F841
    window = MainWindow()
    assert window is not None
    assert window.windowTitle() == "PODStudio - AI Asset Pack Builder"
