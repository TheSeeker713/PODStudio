"""
Main Window - PODStudio Desktop UI
Video editor-style layout with collapsible docks

STEP 2: Scaffold only - no business logic
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QMainWindow, QStatusBar, QTabWidget, QToolBar

from app.ui.widgets.asset_grid import AssetGrid
from app.ui.widgets.dock_left import LeftDock
from app.ui.widgets.dock_right import RightDock
from app.ui.widgets.selection_tray import SelectionTray
from app.ui.widgets.top_bar import TopBar


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

        # Initialize UI components
        self._init_ui()
        self._init_docks()
        self._init_statusbar()

        # Restore window state (placeholder)
        self._restore_window_state()

        # Start maximized by default
        self.showMaximized()

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
        self.right_dock.setWidget(RightDock())
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

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

        # Status bar at bottom
        self.status = QStatusBar()
        self.status.showMessage("Ready | No assets loaded")
        self.setStatusBar(self.status)

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
        self._save_window_state()
        event.accept()


def main():
    """Main entry point for PODStudio UI (when implemented)"""
    print("PODStudio Main Window - Scaffold created (Step 2)")
    print("To run UI: python -m app.ui.app")


if __name__ == "__main__":
    main()
