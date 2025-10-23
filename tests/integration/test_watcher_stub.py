"""
Integration tests for file watcher

Tests that file watcher detects new files and inserts Asset records
"""

import tempfile
import time
from pathlib import Path

import pytest
from sqlmodel import Session, select

from app.backend.models.entities import Asset, AssetProvenance, AssetType
from app.core.db import create_db_and_tables, get_engine
from app.core.watcher import FileWatcher


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with database and watch folder"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        db_path = workspace / "test.db"
        watch_folder = workspace / "watch"
        watch_folder.mkdir()

        yield {
            "workspace": workspace,
            "db_path": db_path,
            "watch_folder": watch_folder,
        }


def test_watcher_detects_image_file(temp_workspace, monkeypatch):
    """Test that watcher detects new image file and inserts Asset"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()

    try:
        # Wait for watcher to initialize
        time.sleep(0.5)

        # Create test image file
        test_file = watch_folder / "test_image.png"
        test_file.write_bytes(b"fake png data")

        # Wait for watcher to process file (debounce + processing time)
        time.sleep(3)

        # Verify Asset was inserted
        engine = get_engine()
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 1

            asset = assets[0]
            assert asset.path == str(test_file)
            assert asset.type == AssetType.IMAGE
            assert asset.approved is False
            assert asset.provenance == AssetProvenance.UNKNOWN
            assert asset.hash is not None  # Hash should be calculated

    finally:
        watcher.stop()


def test_watcher_detects_audio_file(temp_workspace, monkeypatch):
    """Test that watcher detects new audio file and inserts Asset"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()

    try:
        time.sleep(0.5)

        # Create test audio file
        test_file = watch_folder / "test_audio.wav"
        test_file.write_bytes(b"fake wav data")

        time.sleep(3)

        # Verify Asset was inserted
        engine = get_engine()
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 1

            asset = assets[0]
            assert asset.path == str(test_file)
            assert asset.type == AssetType.AUDIO

    finally:
        watcher.stop()


def test_watcher_detects_video_file(temp_workspace, monkeypatch):
    """Test that watcher detects new video file and inserts Asset"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()

    try:
        time.sleep(0.5)

        # Create test video file
        test_file = watch_folder / "test_video.mp4"
        test_file.write_bytes(b"fake mp4 data")

        time.sleep(3)

        # Verify Asset was inserted
        engine = get_engine()
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 1

            asset = assets[0]
            assert asset.path == str(test_file)
            assert asset.type == AssetType.VIDEO

    finally:
        watcher.stop()


def test_watcher_ignores_unsupported_file(temp_workspace, monkeypatch):
    """Test that watcher ignores unsupported file types"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()

    try:
        time.sleep(0.5)

        # Create unsupported file
        test_file = watch_folder / "test.txt"
        test_file.write_text("unsupported file")

        time.sleep(3)

        # Verify no Asset was inserted
        engine = get_engine()
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 0

    finally:
        watcher.stop()


def test_watcher_handles_multiple_files(temp_workspace, monkeypatch):
    """Test that watcher handles multiple files correctly"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()

    try:
        time.sleep(0.5)

        # Create multiple files
        (watch_folder / "image1.png").write_bytes(b"png 1")
        (watch_folder / "image2.jpg").write_bytes(b"jpg 2")
        (watch_folder / "audio1.wav").write_bytes(b"wav 1")

        time.sleep(5)  # Wait for all files to be processed

        # Verify all Assets were inserted
        engine = get_engine()
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 3

            # Check asset types
            asset_types = {asset.type for asset in assets}
            assert AssetType.IMAGE in asset_types
            assert AssetType.AUDIO in asset_types

    finally:
        watcher.stop()


def test_watcher_deduplicates_existing_file(temp_workspace, monkeypatch):
    """Test that watcher doesn't insert duplicate for existing file"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Create file before starting watcher
    test_file = watch_folder / "existing.png"
    test_file.write_bytes(b"existing png")

    # Manually insert asset for this file
    engine = get_engine()
    with Session(engine) as session:
        asset = Asset(
            path=str(test_file),
            type=AssetType.IMAGE,
            hash="abc123",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()

    try:
        time.sleep(0.5)

        # Modify existing file (simulates re-save)
        test_file.write_bytes(b"modified png data")

        time.sleep(3)

        # Verify only one Asset exists (no duplicate)
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 1

    finally:
        watcher.stop()


def test_watcher_stop_and_restart(temp_workspace, monkeypatch):
    """Test that watcher can be stopped and restarted"""
    from app.core import config

    db_path = temp_workspace["db_path"]
    watch_folder = temp_workspace["watch_folder"]

    # Setup database
    monkeypatch.setattr(config.settings, "db_path", str(db_path))
    create_db_and_tables()

    # Start watcher
    watcher = FileWatcher([str(watch_folder)])
    watcher.start()
    assert watcher.is_running()

    # Stop watcher
    watcher.stop()
    assert not watcher.is_running()

    # Restart watcher
    watcher.start()
    assert watcher.is_running()

    try:
        time.sleep(0.5)

        # Create file after restart
        test_file = watch_folder / "after_restart.png"
        test_file.write_bytes(b"png after restart")

        time.sleep(3)

        # Verify Asset was inserted
        engine = get_engine()
        with Session(engine) as session:
            assets = session.exec(select(Asset)).all()
            assert len(assets) == 1

    finally:
        watcher.stop()
