"""
Asset Grid Widget - Grid/list view for assets

STEP 5: Full implementation with database loading, thumbnails, and multi-select
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGridLayout, QLabel, QMenu, QScrollArea, QVBoxLayout, QWidget
from sqlmodel import Session, select

from app.backend.models.entities import Asset, AssetType
from app.core.db import get_engine
from app.core.logging import get_logger
from app.core.thumbnails import generate_thumbnail

logger = get_logger(__name__)


class AssetCard(QWidget):
    """
    Individual asset card with thumbnail and metadata

    Signals:
        clicked: Emitted when card is clicked with (asset_id, modifiers)
        context_menu_requested: Emitted when right-clicked with (asset_id, QPoint)
    """

    clicked = Signal(int, Qt.KeyboardModifiers)
    context_menu_requested = Signal(int, object)  # asset_id, QPoint

    def __init__(self, asset: Asset, parent=None):
        super().__init__(parent)
        self.asset = asset
        self.selected = False
        self._init_ui()

    def _init_ui(self):
        """Initialize card UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Thumbnail
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(128, 128)
        self.thumb_label.setScaledContents(True)
        self.thumb_label.setStyleSheet("border: 2px solid #444; border-radius: 4px;")

        # Load thumbnail
        try:
            thumb_path = generate_thumbnail(self.asset.path, size=128)
            pixmap = QPixmap(thumb_path)
            if not pixmap.isNull():
                self.thumb_label.setPixmap(pixmap)
            else:
                self.thumb_label.setText("?")
                self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            logger.error(f"Failed to load thumbnail for {self.asset.path}: {e}")
            self.thumb_label.setText("?")
            self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.thumb_label)

        # Filename
        filename = Path(self.asset.path).name
        name_label = QLabel(filename)
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(128)
        name_label.setStyleSheet("font-size: 10px; color: #ccc;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Status indicator
        status_text = "✓ Approved" if self.asset.approved else "○ Pending"
        status_color = "#10b981" if self.asset.approved else "#f59e0b"
        self.status_label = QLabel(status_text)
        self.status_label.setStyleSheet(f"font-size: 9px; color: {status_color}; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setFixedSize(138, 190)

        # Apply initial style
        self._update_style()

    def _update_style(self):
        """Update card style based on selection state"""
        if self.selected:
            self.setStyleSheet(
                """
                AssetCard {
                    background-color: #10b981;
                    border: 2px solid #059669;
                    border-radius: 6px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                AssetCard {
                    background-color: #1f2937;
                    border: 2px solid #374151;
                    border-radius: 6px;
                }
                AssetCard:hover {
                    background-color: #374151;
                    border-color: #10b981;
                }
            """
            )

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected
        self._update_style()

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse press for selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.asset.id, event.modifiers())
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu_requested.emit(self.asset.id, event.globalPosition().toPoint())

    def update_status(self, approved: bool):
        """Update approval status display"""
        self.asset.approved = approved
        status_text = "✓ Approved" if approved else "○ Pending"
        status_color = "#10b981" if approved else "#f59e0b"
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"font-size: 9px; color: {status_color}; font-weight: bold;")


class AssetGrid(QWidget):
    """
    Grid view widget for displaying assets (images/audio/video)

    STEP 5: Full implementation with database loading and multi-select

    Signals:
        selection_changed: Emitted when selection changes with list of selected asset IDs
    """

    selection_changed = Signal(list)  # List of selected asset IDs

    def __init__(self, asset_type: str = "image", parent=None):
        super().__init__(parent)
        self.asset_type = asset_type
        self.asset_cards: dict[int, AssetCard] = {}  # asset_id -> AssetCard
        self.selected_ids: set[int] = set()
        self._init_ui()

    def _init_ui(self):
        """Initialize grid UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Grid container
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_widget.setLayout(self.grid_layout)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        self.setLayout(layout)

        # Load assets from database
        self.refresh()

    def refresh(self):
        """Reload assets from database"""
        # Clear existing
        self.clear()

        # Load from DB
        engine = get_engine()
        try:
            with Session(engine) as session:
                # Query assets by type
                asset_type_enum = AssetType(self.asset_type.upper())
                assets = session.exec(select(Asset).where(Asset.type == asset_type_enum)).all()

                logger.info(f"Loaded {len(assets)} {self.asset_type} assets from database")

                # Create cards
                for idx, asset in enumerate(assets):
                    if asset.id is None:
                        continue

                    card = AssetCard(asset)
                    card.clicked.connect(self._on_card_clicked)
                    card.context_menu_requested.connect(self._on_context_menu)

                    # Add to grid (4 columns)
                    row = idx // 4
                    col = idx % 4
                    self.grid_layout.addWidget(card, row, col)

                    self.asset_cards[asset.id] = card

        except Exception as e:
            logger.error(f"Failed to load assets: {e}")

    def _on_card_clicked(self, asset_id: int, modifiers: Qt.KeyboardModifiers):
        """Handle card click for multi-select"""
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Click: Toggle selection
            if asset_id in self.selected_ids:
                self.selected_ids.remove(asset_id)
                self.asset_cards[asset_id].set_selected(False)
            else:
                self.selected_ids.add(asset_id)
                self.asset_cards[asset_id].set_selected(True)

        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Shift+Click: Range select (simplified - just add to selection for now)
            if asset_id not in self.selected_ids:
                self.selected_ids.add(asset_id)
                self.asset_cards[asset_id].set_selected(True)

        else:
            # Normal click: Single select
            # Clear previous selection
            for prev_id in self.selected_ids:
                if prev_id in self.asset_cards:
                    self.asset_cards[prev_id].set_selected(False)

            self.selected_ids = {asset_id}
            self.asset_cards[asset_id].set_selected(True)

        # Emit selection change
        self.selection_changed.emit(list(self.selected_ids))
        logger.debug(f"Selection changed: {len(self.selected_ids)} assets selected")

    def _on_context_menu(self, asset_id: int, pos):
        """Handle right-click context menu"""
        # Ensure clicked asset is selected
        if asset_id not in self.selected_ids:
            self._on_card_clicked(asset_id, Qt.KeyboardModifier.NoModifier)

        # Create context menu
        menu = QMenu(self)
        menu.addAction("Approve", lambda: self._approve_selected())
        menu.addAction("Reject/Delete", lambda: self._reject_selected())
        menu.addSeparator()
        menu.addAction("Tag...", lambda: self._tag_selected())
        menu.addAction("Move...", lambda: self._move_selected())
        menu.addAction("Rename...", lambda: self._rename_selected())

        menu.exec(pos)

    def _approve_selected(self):
        """Approve selected assets"""
        logger.info(f"Approve action triggered for {len(self.selected_ids)} assets")
        # Signal to parent/dock to handle
        # TODO: Implement via signal to right dock

    def _reject_selected(self):
        """Reject/delete selected assets"""
        logger.info(f"Reject action triggered for {len(self.selected_ids)} assets")
        # Signal to parent/dock to handle

    def _tag_selected(self):
        """Tag selected assets"""
        logger.info(f"Tag action triggered for {len(self.selected_ids)} assets")

    def _move_selected(self):
        """Move selected assets"""
        logger.info(f"Move action triggered for {len(self.selected_ids)} assets")

    def _rename_selected(self):
        """Rename selected asset (single only)"""
        if len(self.selected_ids) == 1:
            logger.info(f"Rename action triggered for asset {list(self.selected_ids)[0]}")

    def get_selected_ids(self) -> list[int]:
        """Get list of selected asset IDs"""
        return list(self.selected_ids)

    def clear_selection(self):
        """Clear all selections"""
        for asset_id in self.selected_ids:
            if asset_id in self.asset_cards:
                self.asset_cards[asset_id].set_selected(False)
        self.selected_ids.clear()
        self.selection_changed.emit([])

    def clear(self):
        """Clear all assets from grid"""
        # Remove all cards
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.asset_cards.clear()
        self.selected_ids.clear()

    def load_assets(self, assets: list[Asset]):
        """
        Load assets into grid (alternative to refresh() for manual loading)

        Args:
            assets: List of Asset objects
        """
        self.clear()

        for idx, asset in enumerate(assets):
            if asset.id is None:
                continue

            card = AssetCard(asset)
            card.clicked.connect(self._on_card_clicked)
            card.context_menu_requested.connect(self._on_context_menu)

            row = idx // 4
            col = idx % 4
            self.grid_layout.addWidget(card, row, col)

            self.asset_cards[asset.id] = card
