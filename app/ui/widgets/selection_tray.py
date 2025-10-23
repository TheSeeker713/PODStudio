"""
Selection Tray Widget - Bottom tray with selection count and Build Pack button

STEP 2: Placeholder only
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class SelectionTray(QWidget):
    """
    Bottom tray showing selection count and pack builder button

    Components:
    - Selection counter (e.g., "30 selected")
    - Clear selection button
    - Build Pack button (primary action)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize selection tray layout"""
        layout = QHBoxLayout()

        # Selection counter
        self.selection_label = QLabel("0 selected")
        self.selection_label.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(self.selection_label)

        # Clear selection button
        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.setEnabled(False)
        layout.addWidget(self.clear_btn)

        layout.addStretch()

        # Build Pack button (primary action)
        self.build_pack_btn = QPushButton("Build Pack")
        self.build_pack_btn.setEnabled(False)
        self.build_pack_btn.setStyleSheet(
            "background-color: #0078d4; color: white; font-weight: bold; padding: 8px 24px;"
        )
        layout.addWidget(self.build_pack_btn)

        self.setLayout(layout)

    def update_selection_count(self, count: int):
        """
        Update selection counter and button states

        Args:
            count: Number of selected assets
        """
        self.selection_label.setText(f"{count} selected")
        has_selection = count > 0
        self.clear_btn.setEnabled(has_selection)
        self.build_pack_btn.setEnabled(has_selection)
