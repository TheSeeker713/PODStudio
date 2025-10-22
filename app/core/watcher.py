"""
File Watcher
Monitor folders for new assets using watchdog

TODO (Step 2+): Implement with:
- watchdog FileSystemEventHandler
- Auto-ingest pipeline (detect → move → DB insert)
- Configurable watch folders from .env
"""

from watchdog.observers import Observer


def start_watcher(folders: list[str]):
    """
    Start watching folders for new files

    Args:
        folders: List of folder paths to monitor
    """
    # TODO: Implement file watcher with auto-ingest
    pass
