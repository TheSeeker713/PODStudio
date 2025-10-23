"""
PODStudio Application Entry Point

Launches the PySide6 desktop UI with QApplication event loop.
"""

import sys

from PySide6.QtWidgets import QApplication

from app.core.config import settings
from app.ui.main_window import MainWindow


def main():
    """
    Main entry point for PODStudio desktop application

    STEP 2: Scaffold only - creates QApplication and main window
    """
    # Print active profile
    print(f"PODStudio v0.1.0 - Environment: {settings.app_env}")
    print(f"Debug mode: {settings.app_debug}")

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("PODStudio")
    app.setOrganizationName("PODStudio")
    app.setApplicationVersion("0.1.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
