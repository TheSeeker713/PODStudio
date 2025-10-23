"""
Top Bar Widget - Custom status bar with hardware pills and search

STEP 2: Placeholder only
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class TopBar(QWidget):
    """
    Custom top bar widget

    Components:
    - App logo/title
    - Hardware mode pill (CPU/GPU indicator)
    - Job queue status icon
    - Search box (future)
    - Settings button
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize top bar layout and components"""
        layout = QHBoxLayout()

        # App title
        self.title = QLabel("PODStudio")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title)

        layout.addStretch()

        # Hardware mode pill (placeholder)
        self.hardware_pill = QLabel("Hardware: UNKNOWN")
        self.hardware_pill.setStyleSheet(
            "background-color: #888; color: white; padding: 4px 12px; border-radius: 12px;"
        )
        layout.addWidget(self.hardware_pill)

        # Job queue icon (placeholder)
        self.job_icon = QPushButton("Jobs: 0")
        self.job_icon.setEnabled(False)
        layout.addWidget(self.job_icon)

        self.setLayout(layout)

    def update_hardware_status(self, tier: str):
        """
        Update hardware mode pill

        Args:
            tier: GREEN, YELLOW, or RED
        """
        # TODO (Step 3+): Implement color coding
        self.hardware_pill.setText(f"Hardware: {tier}")
