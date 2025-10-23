"""
Integration tests for curation operations

STEP 5: Tests for approve/reject/tag/move/rename/delete operations
"""

from pathlib import Path

import pytest
from sqlmodel import Session

from app.backend.models.entities import Asset, AssetType
from app.core.db import get_engine
from app.core.thumbnails import generate_thumbnail
from app.core.utils import delete_asset_and_file, safe_move_file, safe_rename_file


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace structure"""
    workspace = tmp_path / "Workspace"
    workspace.mkdir()

    # Create theme folders
    for theme in ["Default", "TestTheme"]:
        for asset_type in ["Image", "Audio", "Video"]:
            (workspace / theme / asset_type).mkdir(parents=True)

    return workspace


@pytest.fixture
def temp_asset_files(temp_workspace):
    """Create temporary asset files for testing"""
    files = []

    # Create test image file
    img_path = temp_workspace / "Default" / "Image" / "test_image.jpg"
    img_path.write_bytes(b"fake image data")
    files.append(img_path)

    # Create test audio file
    audio_path = temp_workspace / "Default" / "Audio" / "test_audio.mp3"
    audio_path.write_bytes(b"fake audio data")
    files.append(audio_path)

    # Create test video file
    video_path = temp_workspace / "Default" / "Video" / "test_video.mp4"
    video_path.write_bytes(b"fake video data")
    files.append(video_path)

    return files


@pytest.fixture
def temp_assets_in_db(temp_asset_files):
    """Insert temp assets into database"""
    engine = get_engine()
    asset_ids = []

    with Session(engine) as session:
        for file_path in temp_asset_files:
            asset_type = AssetType.IMAGE
            if "audio" in file_path.name:
                asset_type = AssetType.AUDIO
            elif "video" in file_path.name:
                asset_type = AssetType.VIDEO

            asset = Asset(
                path=str(file_path),
                type=asset_type,
                theme="Default",
                approved=False,
                size_bytes=len(file_path.read_bytes()),
                hash=f"hash_{file_path.name}",
            )
            session.add(asset)
            session.commit()
            session.refresh(asset)
            asset_ids.append(asset.id)

    yield asset_ids

    # Cleanup: Delete assets from DB
    with Session(engine) as session:
        for asset_id in asset_ids:
            asset = session.get(Asset, asset_id)
            if asset:
                session.delete(asset)
        session.commit()


class TestApprovalOperations:
    """Test approve/reject operations"""

    def test_approve_asset(self, temp_assets_in_db):
        """Test approving an asset"""
        engine = get_engine()
        asset_id = temp_assets_in_db[0]

        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset is not None
            assert asset.approved is False

            # Approve
            asset.approved = True
            session.add(asset)
            session.commit()

        # Verify
        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset.approved is True

    def test_reject_delete_asset(self, temp_assets_in_db, temp_asset_files):
        """Test rejecting/deleting an asset"""
        asset_id = temp_assets_in_db[0]
        file_path = temp_asset_files[0]

        assert file_path.exists()

        # Delete
        result = delete_asset_and_file(asset_id, delete_file=True)
        assert result is True

        # Verify file deleted
        assert not file_path.exists()

        # Verify DB record deleted
        engine = get_engine()
        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset is None


class TestTagOperations:
    """Test tagging operations"""

    def test_tag_asset_with_theme(self, temp_assets_in_db):
        """Test tagging asset with theme"""
        engine = get_engine()
        asset_id = temp_assets_in_db[0]

        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset.theme == "Default"

            # Tag with new theme
            asset.theme = "NewTheme"
            session.add(asset)
            session.commit()

        # Verify
        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset.theme == "NewTheme"

    def test_clear_theme_tag(self, temp_assets_in_db):
        """Test clearing theme tag"""
        engine = get_engine()
        asset_id = temp_assets_in_db[0]

        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            asset.theme = None
            session.add(asset)
            session.commit()

        # Verify
        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset.theme is None


class TestFileOperations:
    """Test file move/rename/delete operations"""

    def test_safe_move_file(self, temp_asset_files, temp_workspace):
        """Test moving file with database update"""
        source = temp_asset_files[0]
        dest_dir = temp_workspace / "TestTheme" / "Image"
        dest_dir.mkdir(parents=True, exist_ok=True)

        assert source.exists()

        # Move file
        new_path = safe_move_file(source, dest_dir, update_db=True)

        assert new_path is not None
        assert new_path.exists()
        assert not source.exists()
        assert new_path.parent == dest_dir

    def test_safe_move_file_collision(self, temp_asset_files, temp_workspace):
        """Test moving file with name collision handling"""
        source = temp_asset_files[0]
        dest_dir = temp_workspace / "TestTheme" / "Image"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Create collision
        collision_file = dest_dir / source.name
        collision_file.write_bytes(b"existing file")

        # Move file
        new_path = safe_move_file(source, dest_dir, update_db=True)

        assert new_path is not None
        assert new_path.exists()
        assert not source.exists()
        # Should have _1 suffix
        assert "_1" in new_path.stem

    def test_safe_rename_file(self, temp_asset_files):
        """Test renaming file with database update"""
        source = temp_asset_files[0]
        new_name = "renamed_image.jpg"

        assert source.exists()

        # Rename
        new_path = safe_rename_file(source, new_name, update_db=True)

        assert new_path is not None
        assert new_path.exists()
        assert not source.exists()
        assert new_path.name == new_name

    def test_safe_rename_file_collision(self, temp_asset_files):
        """Test renaming file with collision"""
        source = temp_asset_files[0]
        collision_name = "collision.jpg"

        # Create collision
        collision_file = source.parent / collision_name
        collision_file.write_bytes(b"existing")

        # Rename
        new_path = safe_rename_file(source, collision_name, update_db=True)

        assert new_path is not None
        assert new_path.exists()
        assert not source.exists()
        # Should have _1 suffix
        assert new_path.name == "collision_1.jpg"

    def test_delete_asset_only_db(self, temp_assets_in_db, temp_asset_files):
        """Test deleting asset from DB without deleting file"""
        asset_id = temp_assets_in_db[0]
        file_path = temp_asset_files[0]

        assert file_path.exists()

        # Delete from DB only
        result = delete_asset_and_file(asset_id, delete_file=False)
        assert result is True

        # Verify file still exists
        assert file_path.exists()

        # Verify DB record deleted
        engine = get_engine()
        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            assert asset is None


class TestThumbnailGeneration:
    """Test thumbnail generation for different asset types"""

    def test_generate_thumbnail_creates_cache(self, temp_asset_files):
        """Test thumbnail generation creates cache file"""
        source = temp_asset_files[0]  # Image file

        # Generate thumbnail
        thumb_path = generate_thumbnail(source, size=128)

        assert thumb_path is not None
        assert Path(thumb_path).exists()
        # Should be in cache directory
        assert "Cache/thumbs" in str(thumb_path)

    def test_generate_thumbnail_placeholder_for_unknown(self):
        """Test placeholder generation for unknown file types"""
        from app.core.thumbnails import _get_placeholder_path

        # Get placeholder for each type
        img_placeholder = _get_placeholder_path(AssetType.IMAGE)
        audio_placeholder = _get_placeholder_path(AssetType.AUDIO)
        video_placeholder = _get_placeholder_path(AssetType.VIDEO)

        assert img_placeholder is not None
        assert audio_placeholder is not None
        assert video_placeholder is not None


class TestMultiSelectOperations:
    """Test operations on multiple selected assets"""

    def test_approve_multiple_assets(self, temp_assets_in_db):
        """Test approving multiple assets at once"""
        engine = get_engine()

        # Approve all
        with Session(engine) as session:
            for asset_id in temp_assets_in_db:
                asset = session.get(Asset, asset_id)
                asset.approved = True
                session.add(asset)
            session.commit()

        # Verify all approved
        with Session(engine) as session:
            for asset_id in temp_assets_in_db:
                asset = session.get(Asset, asset_id)
                assert asset.approved is True

    def test_tag_multiple_assets(self, temp_assets_in_db):
        """Test tagging multiple assets at once"""
        engine = get_engine()
        new_theme = "BulkTheme"

        # Tag all
        with Session(engine) as session:
            for asset_id in temp_assets_in_db:
                asset = session.get(Asset, asset_id)
                asset.theme = new_theme
                session.add(asset)
            session.commit()

        # Verify all tagged
        with Session(engine) as session:
            for asset_id in temp_assets_in_db:
                asset = session.get(Asset, asset_id)
                assert asset.theme == new_theme
