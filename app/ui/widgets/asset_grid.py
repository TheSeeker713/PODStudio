"""
Asset Grid Widget - Grid/list view for assets

STEP 2: Placeholder only - no actual asset loading
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AssetGrid(QWidget):
    """
    Grid view widget for displaying assets (images/audio/video)

    STEP 2: Shows placeholder text
    TODO (Step 3+): Implement with QListView/QGridView and thumbnail model
    """

    def __init__(self, asset_type: str = "image", parent=None):
        super().__init__(parent)
        self.asset_type = asset_type
        self._init_ui()

    def _init_ui(self):
        """Initialize grid placeholder"""
        layout = QVBoxLayout()

        # Placeholder label
        placeholder = QLabel(f"📁 {self.asset_type.capitalize()} Grid")
        placeholder.setStyleSheet("font-size: 32px; color: #ccc; padding: 100px; qproperty-alignment: AlignCenter;")
        layout.addWidget(placeholder)

        info = QLabel(f"No {self.asset_type}s loaded\n\nDrag & drop files or enable File Listener")
        info.setStyleSheet("color: #888; padding: 20px; qproperty-alignment: AlignCenter;")
        layout.addWidget(info)

        self.setLayout(layout)

    def load_assets(self, assets: list):
        """
        Load assets into grid

        Args:
            assets: List of asset records from database

        TODO (Step 3+): Implement grid population
        """
        pass

    def clear(self):
        """Clear all assets from grid"""
        pass
