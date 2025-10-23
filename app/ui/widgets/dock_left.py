"""
Left Dock Widget - Instructions, Listener, Filters

STEP 2: Placeholder only
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LeftDock(QWidget):
    """
    Left dock panel with collapsible sections

    Sections:
    - Instructions/Prompts: Prompt generation UI
    - Listener: File watcher controls
    - Filters: Asset filtering (type, status, tags, date)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize left dock sections"""
        layout = QVBoxLayout()

        # Instructions section (placeholder)
        instructions_label = QLabel("Instructions/Prompts")
        instructions_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(instructions_label)

        instructions_placeholder = QLabel("Prompt generation UI here")
        instructions_placeholder.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(instructions_placeholder)

        layout.addSpacing(20)

        # Listener section (placeholder)
        listener_label = QLabel("File Listener")
        listener_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(listener_label)

        listener_placeholder = QLabel("Watch folder controls here")
        listener_placeholder.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(listener_placeholder)

        layout.addSpacing(20)

        # Filters section (placeholder)
        filters_label = QLabel("Filters")
        filters_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(filters_label)

        filters_placeholder = QLabel("Filter controls here (type, status, tags)")
        filters_placeholder.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(filters_placeholder)

        layout.addStretch()
        self.setLayout(layout)
