"""
Top Bar Widget - Custom status bar with hardware pills and search

STEP 2: Placeholder only
STEP 3: Added backend API status indicator
"""

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from app.ui.helpers.backend_status import backend_status_checker


class BackendPingThread(QThread):
    """Background thread to ping backend API without blocking UI"""

    status_updated = Signal(bool, str, str)  # (connected, mode, error)

    def run(self):
        """Check backend health and probe"""
        status = backend_status_checker.check_all()
        self.status_updated.emit(
            status.api_connected,
            status.hardware_mode,
            status.error or "",
        )


class TopBar(QWidget):
    """
    Custom top bar widget

    Components:
    - App logo/title
    - Backend API status indicator (STEP 3)
    - Hardware mode pill (CPU/GPU indicator)
    - Job queue status icon
    - Search box (future)
    - Settings button
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._ping_backend()

    def _init_ui(self):
        """Initialize top bar layout and components"""
        layout = QHBoxLayout()

        # App title
        self.title = QLabel("PODStudio")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title)

        layout.addStretch()

        # API status indicator (STEP 3)
        self.api_status = QLabel("API: Checking...")
        self.api_status.setStyleSheet("color: #888; font-size: 11px; padding: 2px 8px;")
        layout.addWidget(self.api_status)

        # Hardware mode pill (placeholder)
        self.hardware_pill = QLabel("Hardware: UNKNOWN")
        self.hardware_pill.setStyleSheet(
            "background-color: #888; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;"
        )
        layout.addWidget(self.hardware_pill)

        # Job queue icon (placeholder)
        self.job_icon = QPushButton("Jobs: 0")
        self.job_icon.setEnabled(False)
        layout.addWidget(self.job_icon)

        self.setLayout(layout)

    def _ping_backend(self):
        """Ping backend API in background thread"""
        self.ping_thread = BackendPingThread()
        self.ping_thread.status_updated.connect(self._on_backend_status_updated)
        self.ping_thread.start()

    def _on_backend_status_updated(self, connected: bool, mode: str, error: str):  # noqa: ARG002
        """
        Handle backend status update from background thread

        Args:
            connected: Whether API is reachable
            mode: Hardware mode (green/yellow/red/unknown)
            error: Error message if connection failed (not used yet, for future logging)
        """
        if connected:
            self.api_status.setText("API: OK")
            self.api_status.setStyleSheet("color: #10b981; font-size: 11px; padding: 2px 8px;")

            # Update hardware pill with mode
            mode_upper = mode.upper()
            if mode == "green":
                bg_color = "#10b981"  # Emerald green
            elif mode == "yellow":
                bg_color = "#f59e0b"  # Amber
            elif mode == "red":
                bg_color = "#ef4444"  # Red
            else:
                bg_color = "#888"  # Gray for unknown

            self.hardware_pill.setText(f"Mode: {mode_upper}")
            self.hardware_pill.setStyleSheet(
                f"background-color: {bg_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;"
            )
        else:
            self.api_status.setText("API: OFFLINE")
            self.api_status.setStyleSheet("color: #ef4444; font-size: 11px; padding: 2px 8px;")
            self.hardware_pill.setText("Mode: OFFLINE")
            self.hardware_pill.setStyleSheet(
                "background-color: #888; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;"
            )

    def update_hardware_status(self, tier: str):
        """
        Update hardware mode pill (legacy method - can still be called externally)

        Args:
            tier: GREEN, YELLOW, or RED
        """
        self._on_backend_status_updated(True, tier.lower(), "")
