"""
Right Dock Widget - Inspector, Actions, History

STEP 5: Full implementation with curation controls
"""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from sqlmodel import Session

from app.backend.models.entities import Asset
from app.core.db import get_engine
from app.core.logging import get_logger
from app.core.utils import delete_asset_and_file, safe_move_file, safe_rename_file

logger = get_logger(__name__)


class RightDock(QWidget):
    """
    Right dock panel with inspector cards

    STEP 5: Full implementation with curation controls

    Cards:
    - Inspector: Selected asset metadata
    - Quick Actions: Approve/Reject/Rename/Move/Delete
    - History: Recent operations

    Signals:
        refresh_requested: Emitted when grid should refresh after curation actions
    """

    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_ids: list[int] = []
        self._init_ui()

    def _init_ui(self):
        """Initialize right dock cards"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Inspector card
        self.inspector_group = QGroupBox("Inspector")
        inspector_layout = QVBoxLayout()

        self.inspector_label = QLabel("No selection")
        self.inspector_label.setWordWrap(True)
        self.inspector_label.setStyleSheet("color: #888; padding: 8px;")
        inspector_layout.addWidget(self.inspector_label)

        self.inspector_group.setLayout(inspector_layout)
        layout.addWidget(self.inspector_group)

        # Quick Actions card
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        # Row 1: Approve and Reject
        row1 = QHBoxLayout()
        self.approve_btn = QPushButton("✓ Approve")
        self.approve_btn.setStyleSheet("background-color: #10b981; color: white; font-weight: bold;")
        self.approve_btn.clicked.connect(self._on_approve)
        self.approve_btn.setEnabled(False)
        row1.addWidget(self.approve_btn)

        self.reject_btn = QPushButton("✗ Reject/Delete")
        self.reject_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold;")
        self.reject_btn.clicked.connect(self._on_reject)
        self.reject_btn.setEnabled(False)
        row1.addWidget(self.reject_btn)

        actions_layout.addLayout(row1)

        # Row 2: Rename and Move
        row2 = QHBoxLayout()
        self.rename_btn = QPushButton("🏷 Rename")
        self.rename_btn.clicked.connect(self._on_rename)
        self.rename_btn.setEnabled(False)
        row2.addWidget(self.rename_btn)

        self.move_btn = QPushButton("📁 Move")
        self.move_btn.clicked.connect(self._on_move)
        self.move_btn.setEnabled(False)
        row2.addWidget(self.move_btn)

        actions_layout.addLayout(row2)

        # Row 3: Tag
        self.tag_btn = QPushButton("🏷 Tag Theme")
        self.tag_btn.clicked.connect(self._on_tag)
        self.tag_btn.setEnabled(False)
        actions_layout.addWidget(self.tag_btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # History card (placeholder for now)
        history_group = QGroupBox("History")
        history_layout = QVBoxLayout()

        self.history_label = QLabel("No recent operations")
        self.history_label.setStyleSheet("color: #888; padding: 8px;")
        history_layout.addWidget(self.history_label)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        layout.addStretch()
        self.setLayout(layout)

    def update_selection(self, asset_ids: list[int]):
        """
        Update displayed information based on selected assets

        Args:
            asset_ids: List of selected asset IDs
        """
        self.selected_ids = asset_ids
        count = len(asset_ids)

        # Update inspector
        if count == 0:
            self.inspector_label.setText("No selection")
            self._disable_all_buttons()
        elif count == 1:
            self._load_single_asset_info(asset_ids[0])
            self._enable_all_buttons()
        else:
            self.inspector_label.setText(f"{count} assets selected")
            self._enable_multi_buttons()

    def _load_single_asset_info(self, asset_id: int):
        """Load and display info for single asset"""
        engine = get_engine()
        try:
            with Session(engine) as session:
                asset = session.get(Asset, asset_id)
                if asset:
                    path = Path(asset.path)
                    info_text = (
                        f"<b>File:</b> {path.name}<br>"
                        f"<b>Type:</b> {asset.type.value}<br>"
                        f"<b>Theme:</b> {asset.theme or 'None'}<br>"
                        f"<b>Status:</b> {'Approved' if asset.approved else 'Pending'}<br>"
                        f"<b>Size:</b> {asset.size_bytes / 1024:.1f} KB<br>"
                        f"<b>Hash:</b> {asset.hash[:8]}..."
                        if asset.hash
                        else ""
                    )
                    self.inspector_label.setText(info_text)
                else:
                    self.inspector_label.setText("Asset not found")
        except Exception as e:
            logger.error(f"Failed to load asset info: {e}")
            self.inspector_label.setText("Error loading info")

    def _enable_all_buttons(self):
        """Enable all action buttons (single selection)"""
        self.approve_btn.setEnabled(True)
        self.reject_btn.setEnabled(True)
        self.rename_btn.setEnabled(True)
        self.move_btn.setEnabled(True)
        self.tag_btn.setEnabled(True)

    def _enable_multi_buttons(self):
        """Enable buttons valid for multi-selection"""
        self.approve_btn.setEnabled(True)
        self.reject_btn.setEnabled(True)
        self.rename_btn.setEnabled(False)  # Rename only for single
        self.move_btn.setEnabled(True)
        self.tag_btn.setEnabled(True)

    def _disable_all_buttons(self):
        """Disable all action buttons"""
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)
        self.move_btn.setEnabled(False)
        self.tag_btn.setEnabled(False)

    def _on_approve(self):
        """Approve selected assets"""
        if not self.selected_ids:
            return

        engine = get_engine()
        try:
            with Session(engine) as session:
                for asset_id in self.selected_ids:
                    asset = session.get(Asset, asset_id)
                    if asset:
                        asset.approved = True
                        session.add(asset)
                session.commit()

            logger.info(f"Approved {len(self.selected_ids)} assets")
            self._add_history(f"Approved {len(self.selected_ids)} assets")
            self.refresh_requested.emit()

        except Exception as e:
            logger.error(f"Failed to approve assets: {e}")
            QMessageBox.critical(self, "Error", f"Failed to approve assets: {e}")

    def _on_reject(self):
        """Reject/delete selected assets"""
        if not self.selected_ids:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(self.selected_ids)} asset(s)?\n\nThis will remove both database records and physical files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted = 0
        for asset_id in self.selected_ids:
            if delete_asset_and_file(asset_id, delete_file=True):
                deleted += 1

        logger.info(f"Deleted {deleted}/{len(self.selected_ids)} assets")
        self._add_history(f"Deleted {deleted} assets")
        self.refresh_requested.emit()

    def _on_rename(self):
        """Rename single selected asset"""
        if len(self.selected_ids) != 1:
            return

        asset_id = self.selected_ids[0]
        engine = get_engine()

        try:
            with Session(engine) as session:
                asset = session.get(Asset, asset_id)
                if not asset:
                    return

                old_path = Path(asset.path)
                old_name = old_path.name

                # Prompt for new name
                new_name, ok = QInputDialog.getText(
                    self, "Rename Asset", f"Enter new name for '{old_name}':", text=old_name
                )

                if not ok or not new_name or new_name == old_name:
                    return

                # Rename file
                new_path = safe_rename_file(old_path, new_name, update_db=True)
                if new_path:
                    logger.info(f"Renamed {old_name} to {new_path.name}")
                    self._add_history(f"Renamed {old_name}")
                    self.refresh_requested.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to rename file")

        except Exception as e:
            logger.error(f"Failed to rename asset: {e}")
            QMessageBox.critical(self, "Error", f"Failed to rename: {e}")

    def _on_move(self):
        """Move selected assets to new theme folder"""
        if not self.selected_ids:
            return

        # Prompt for destination theme
        theme, ok = QInputDialog.getText(
            self,
            "Move Assets",
            f"Enter theme folder to move {len(self.selected_ids)} asset(s) to:",
            text="Default",
        )

        if not ok or not theme:
            return

        moved = 0
        for asset_id in self.selected_ids:
            engine = get_engine()
            try:
                with Session(engine) as session:
                    asset = session.get(Asset, asset_id)
                    if not asset:
                        continue

                    old_path = Path(asset.path)
                    # Determine destination based on asset type
                    dest_dir = Path("Workspace") / theme / asset.type.value.capitalize()
                    dest_dir.mkdir(parents=True, exist_ok=True)

                    # Move file
                    new_path = safe_move_file(old_path, dest_dir, update_db=True)
                    if new_path:
                        # Update theme in database
                        asset = session.get(Asset, asset_id)
                        if asset:
                            asset.theme = theme
                            session.add(asset)
                            session.commit()
                        moved += 1

            except Exception as e:
                logger.error(f"Failed to move asset {asset_id}: {e}")

        logger.info(f"Moved {moved}/{len(self.selected_ids)} assets to theme '{theme}'")
        self._add_history(f"Moved {moved} assets to '{theme}'")
        self.refresh_requested.emit()

    def _on_tag(self):
        """Tag selected assets with theme"""
        if not self.selected_ids:
            return

        # Prompt for theme
        theme, ok = QInputDialog.getText(
            self, "Tag Theme", f"Enter theme tag for {len(self.selected_ids)} asset(s):", text=""
        )

        if not ok:
            return

        engine = get_engine()
        try:
            with Session(engine) as session:
                for asset_id in self.selected_ids:
                    asset = session.get(Asset, asset_id)
                    if asset:
                        asset.theme = theme if theme else None
                        session.add(asset)
                session.commit()

            logger.info(f"Tagged {len(self.selected_ids)} assets with theme '{theme}'")
            self._add_history(f"Tagged {len(self.selected_ids)} assets")
            self.refresh_requested.emit()

        except Exception as e:
            logger.error(f"Failed to tag assets: {e}")
            QMessageBox.critical(self, "Error", f"Failed to tag assets: {e}")

    def _add_history(self, message: str):
        """Add operation to history display"""
        current = self.history_label.text()
        if current == "No recent operations":
            self.history_label.setText(f"• {message}")
        else:
            # Keep last 5 operations
            lines = current.split("\n")
            lines.insert(0, f"• {message}")
            self.history_label.setText("\n".join(lines[:5]))
