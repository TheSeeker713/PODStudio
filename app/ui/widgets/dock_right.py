"""
Right Dock Widget - Inspector, Actions, History

STEP 2: Placeholder only
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class RightDock(QWidget):
    """
    Right dock panel with inspector cards

    Cards:
    - Inspector: Selected asset metadata
    - Quick Actions: Approve/Reject/Enhance
    - History: Recent operations
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize right dock cards"""
        layout = QVBoxLayout()

        # Inspector card (placeholder)
        inspector_label = QLabel("Inspector")
        inspector_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(inspector_label)

        inspector_placeholder = QLabel("Asset metadata here")
        inspector_placeholder.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(inspector_placeholder)

        layout.addSpacing(20)

        # Quick Actions card (placeholder)
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(actions_label)

        actions_placeholder = QLabel("Approve/Reject/Enhance buttons here")
        actions_placeholder.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(actions_placeholder)

        layout.addSpacing(20)

        # History card (placeholder)
        history_label = QLabel("History")
        history_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(history_label)

        history_placeholder = QLabel("Recent operations here")
        history_placeholder.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(history_placeholder)

        layout.addStretch()
        self.setLayout(layout)
