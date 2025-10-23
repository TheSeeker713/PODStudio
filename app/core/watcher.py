"""
File Watcher
Monitor folders for new assets using watchdog

STEP 4: Basic file watcher with DB insert (metadata stubs only)
Future: Auto-ingest pipeline with file moving and metadata extraction
"""

import hashlib
import time
from datetime import UTC, datetime
from pathlib import Path

from sqlmodel import Session, select
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.backend.models.entities import Asset, AssetProvenance
from app.core.config import settings
from app.core.db import get_engine
from app.core.filetypes import guess_type_by_extension, is_supported
from app.core.logging import get_logger

logger = get_logger(__name__)


class AssetFileHandler(FileSystemEventHandler):
    """
    Watchdog event handler for new asset files

    Inserts Asset records into database when supported files are created
    """

    def __init__(self):
        super().__init__()
        self._recent_files = {}  # path -> timestamp (for debouncing)
        self._debounce_seconds = 2.0

    def on_created(self, event: FileCreatedEvent):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if file is supported
        if not is_supported(file_path):
            return

        # Debounce: Skip if we've seen this file recently
        now = time.time()
        if file_path in self._recent_files and now - self._recent_files[file_path] < self._debounce_seconds:
            return

        self._recent_files[file_path] = now

        # Insert asset into database
        try:
            self._insert_asset(file_path)
        except Exception as e:
            logger.error(f"Failed to insert asset {file_path}: {e}")

    def _insert_asset(self, file_path: Path):
        """Insert new Asset record into database"""
        # Ensure file exists and is readable
        if not file_path.exists():
            logger.warning(f"File vanished before insert: {file_path}")
            return

        # Guess asset type from extension
        asset_type = guess_type_by_extension(file_path)
        if asset_type is None:
            logger.warning(f"Unsupported file type: {file_path}")
            return

        # Calculate file hash (for deduplication)
        file_hash = self._calculate_hash(file_path)

        # Check if asset already exists
        engine = get_engine()
        with Session(engine) as session:
            existing = session.exec(select(Asset).where(Asset.path == str(file_path))).first()
            if existing:
                logger.info(f"Asset already exists: {file_path}")
                return

            # Create new asset (metadata stubs only)
            asset = Asset(
                path=str(file_path),
                type=asset_type,
                hash=file_hash,
                width=None,  # TODO: Extract from image metadata
                height=None,
                duration_sec=None,  # TODO: Extract from audio/video metadata
                samplerate_hz=None,
                theme=None,  # User will set this later
                source=None,
                provenance=AssetProvenance.UNKNOWN,  # User will curate this later
                approved=False,  # Requires manual approval
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            session.add(asset)
            session.commit()
            session.refresh(asset)

            logger.info(f"Inserted asset: {file_path} (id={asset.id}, type={asset_type.value})")

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()


class FileWatcher:
    """
    Watchdog-based file watcher for asset folders

    Monitors configured folders and inserts new assets into database
    """

    def __init__(self, folders: list[str] | None = None):
        """
        Initialize file watcher

        Args:
            folders: List of folder paths to watch (defaults to settings.watch_folders)
        """
        if folders is None:
            # Parse comma-separated folders from settings
            folder_str = settings.watch_folders or ""
            folders = [f.strip() for f in folder_str.split(",") if f.strip()]

        self.folders = [Path(f) for f in folders]
        self.observer = Observer()
        self.handler = AssetFileHandler()
        self._running = False

    def start(self):
        """Start watching folders"""
        if self._running:
            logger.warning("File watcher already running")
            return

        if not self.folders:
            logger.warning("No folders to watch (check WATCH_FOLDERS in .env)")
            return

        for folder in self.folders:
            if not folder.exists():
                logger.warning(f"Watch folder does not exist: {folder}")
                continue

            self.observer.schedule(self.handler, str(folder), recursive=False)
            logger.info(f"Watching folder: {folder}")

        self.observer.start()
        self._running = True
        logger.info("File watcher started")

    def stop(self):
        """Stop watching folders"""
        if not self._running:
            return

        self.observer.stop()
        self.observer.join()
        self._running = False
        logger.info("File watcher stopped")

    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self._running


# Global watcher instance (lazy-initialized)
_watcher: FileWatcher | None = None


def get_watcher() -> FileWatcher:
    """Get global file watcher instance"""
    global _watcher
    if _watcher is None:
        _watcher = FileWatcher()
    return _watcher


def start_watcher(folders: list[str] | None = None):
    """
    Start watching folders for new files

    Args:
        folders: List of folder paths to monitor (defaults to settings.watch_folders)
    """
    watcher = get_watcher() if folders is None else FileWatcher(folders)
    watcher.start()


def stop_watcher():
    """Stop file watcher"""
    watcher = get_watcher()
    watcher.stop()
