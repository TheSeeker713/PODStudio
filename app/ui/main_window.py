"""
Main Window - PODStudio Desktop UI
Video editor-style layout with collapsible docks

STEP 4: Added file watcher controls and status indicator
"""


from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDockWidget, QMainWindow, QMenu, QStatusBar, QTabWidget, QToolBar

from app.core.logging import get_logger
from app.core.watcher import get_watcher
from app.ui.widgets.asset_grid import AssetGrid
from app.ui.widgets.dock_left import LeftDock
from app.ui.widgets.dock_right import RightDock
from app.ui.widgets.selection_tray import SelectionTray
from app.ui.widgets.top_bar import TopBar

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window with video editor-style layout

    Layout:
    - Top: Custom top bar (status, hardware pill, search)
    - Left Dock: Instructions, Listener, Filters
    - Center: Tabbed grid (Images/Audio/Video)
    - Right Dock: Inspector, Actions, History
    - Bottom: Selection tray + Build Pack button
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PODStudio - AI Asset Pack Builder")
        self.setMinimumSize(1200, 800)

        # Watcher state tracking
        self._watcher_running = False
        self._watcher_status_timer = QTimer()
        self._watcher_status_timer.timeout.connect(self._update_watcher_status)

        # Initialize UI components
        self._init_menubar()
        self._init_ui()
        self._init_docks()
        self._init_statusbar()

        # Restore window state (placeholder)
        self._restore_window_state()

        # Start maximized by default
        self.showMaximized()

        # Start watcher status update timer (every 2 seconds)
        self._watcher_status_timer.start(2000)

    def _init_menubar(self):
        """Initialize menu bar with Tools menu"""
        menubar = self.menuBar()

        # Tools menu with watcher controls
        tools_menu: QMenu = menubar.addMenu("&Tools")

        # Start Watcher action
        self.action_start_watcher = QAction("Start File Watcher", self)
        self.action_start_watcher.setStatusTip("Start monitoring folders for new assets")
        self.action_start_watcher.triggered.connect(self._start_watcher)
        tools_menu.addAction(self.action_start_watcher)

        # Stop Watcher action
        self.action_stop_watcher = QAction("Stop File Watcher", self)
        self.action_stop_watcher.setStatusTip("Stop monitoring folders")
        self.action_stop_watcher.triggered.connect(self._stop_watcher)
        self.action_stop_watcher.setEnabled(False)  # Disabled by default
        tools_menu.addAction(self.action_stop_watcher)

    def _init_ui(self):
        """Initialize central widget and tabs"""
        # Central widget: Tabbed asset grids
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabPosition(QTabWidget.North)

        # Create tabs for each asset type (placeholder grids)
        self.images_grid = AssetGrid(asset_type="image")
        self.audio_grid = AssetGrid(asset_type="audio")
        self.video_grid = AssetGrid(asset_type="video")

        self.central_tabs.addTab(self.images_grid, "Images")
        self.central_tabs.addTab(self.audio_grid, "Audio")
        self.central_tabs.addTab(self.video_grid, "Video")

        self.setCentralWidget(self.central_tabs)

    def _init_docks(self):
        """Initialize left and right dock widgets"""
        # Left Dock: Instructions, Listener, Filters
        self.left_dock = QDockWidget("Controls", self)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.left_dock.setWidget(LeftDock())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Right Dock: Inspector, Actions, History
        self.right_dock = QDockWidget("Inspector", self)
        self.right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.right_dock_widget = RightDock()
        self.right_dock.setWidget(self.right_dock_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        # Connect grid selection to right dock
        self.images_grid.selection_changed.connect(self.right_dock_widget.update_selection)
        self.audio_grid.selection_changed.connect(self.right_dock_widget.update_selection)
        self.video_grid.selection_changed.connect(self.right_dock_widget.update_selection)

        # Connect right dock refresh signal to grids
        self.right_dock_widget.refresh_requested.connect(self.images_grid.refresh)
        self.right_dock_widget.refresh_requested.connect(self.audio_grid.refresh)
        self.right_dock_widget.refresh_requested.connect(self.video_grid.refresh)

        # Bottom Tray: Selection counter + Build Pack button
        self.bottom_tray = SelectionTray()
        self.bottom_dock = QDockWidget("Selection", self)
        self.bottom_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.bottom_dock.setWidget(self.bottom_tray)
        self.bottom_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Fixed position
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)

    def _init_statusbar(self):
        """Initialize custom top bar and status bar"""
        # Top bar (add as toolbar at the top with custom widget)
        self.top_bar = TopBar()
        toolbar = QToolBar("Top Bar")
        toolbar.setMovable(False)
        toolbar.addWidget(self.top_bar)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Status bar at bottom with watcher status
        self.status = QStatusBar()
        self.status.showMessage("Ready | Watcher: Stopped")
        self.setStatusBar(self.status)

    def _start_watcher(self):
        """Start file watcher"""
        try:
            watcher = get_watcher()
            watcher.start()
            self._watcher_running = True
            self.action_start_watcher.setEnabled(False)
            self.action_stop_watcher.setEnabled(True)
            logger.info("File watcher started from UI")
            self._update_watcher_status()
        except Exception as e:
            logger.error(f"Failed to start watcher: {e}")
            self.status.showMessage(f"Error: Failed to start watcher - {e}")

    def _stop_watcher(self):
        """Stop file watcher"""
        try:
            watcher = get_watcher()
            watcher.stop()
            self._watcher_running = False
            self.action_start_watcher.setEnabled(True)
            self.action_stop_watcher.setEnabled(False)
            logger.info("File watcher stopped from UI")
            self._update_watcher_status()
        except Exception as e:
            logger.error(f"Failed to stop watcher: {e}")
            self.status.showMessage(f"Error: Failed to stop watcher - {e}")

    def _update_watcher_status(self):
        """Update status bar with current watcher state"""
        try:
            watcher = get_watcher()
            is_running = watcher.is_running()

            if is_running:
                folder_count = len(watcher.folders)
                status_text = f"Ready | Watcher: Running ({folder_count} folders)"
            else:
                status_text = "Ready | Watcher: Stopped"

            self.status.showMessage(status_text)
        except Exception as e:
            logger.error(f"Failed to update watcher status: {e}")

    def _restore_window_state(self):
        """
        Restore window geometry and dock positions from QSettings

        STEP 2: Placeholder - no actual restoration yet
        """
        # TODO (Step 3+): Implement with QSettings
        # settings = QSettings("PODStudio", "MainWindow")
        # geometry = settings.value("geometry")
        # if geometry:
        #     self.restoreGeometry(geometry)
        # state = settings.value("windowState")
        # if state:
        #     self.restoreState(state)
        pass

    def _save_window_state(self):
        """
        Save window geometry and dock positions to QSettings

        STEP 2: Placeholder - no actual saving yet
        """
        # TODO (Step 3+): Implement with QSettings
        # settings = QSettings("PODStudio", "MainWindow")
        # settings.setValue("geometry", self.saveGeometry())
        # settings.setValue("windowState", self.saveState())
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop watcher timer
        self._watcher_status_timer.stop()

        # Stop watcher if running
        if self._watcher_running:
            try:
                watcher = get_watcher()
                watcher.stop()
                logger.info("Stopped file watcher on window close")
            except Exception as e:
                logger.error(f"Failed to stop watcher on close: {e}")

        self._save_window_state()
        event.accept()


def main():
    """Main entry point for PODStudio UI (when implemented)"""
    print("PODStudio Main Window - Scaffold created (Step 2)")
    print("To run UI: python -m app.ui.app")


if __name__ == "__main__":
    main()
