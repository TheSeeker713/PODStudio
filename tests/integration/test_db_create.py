"""
Integration tests for database creation and table initialization

Tests that database file is created and all tables exist after server startup
"""

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, inspect, select

from app.backend.models.entities import Asset, Job, Pack
from app.core.db import create_db_and_tables, get_engine, reset_engine


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield db_path


def test_create_db_and_tables(temp_db_path, monkeypatch):
    """Test that create_db_and_tables() creates database file and tables"""
    # Override settings.db_path to use temp path
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", str(temp_db_path))
    reset_engine()  # Clear cached engine

    # Database file should not exist yet
    assert not temp_db_path.exists()

    # Create database and tables
    create_db_and_tables()

    # Database file should exist now
    assert temp_db_path.exists()

    # Verify tables exist by inspecting schema
    engine = get_engine()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Check for all expected tables
    assert "assets" in table_names
    assert "packs" in table_names
    assert "jobs" in table_names


def test_tables_have_correct_columns(temp_db_path, monkeypatch):
    """Test that tables have expected columns"""
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", str(temp_db_path))
    reset_engine()  # Clear cached engine

    # Create database
    create_db_and_tables()
    engine = get_engine()
    inspector = inspect(engine)

    # Check Asset table columns (table name is plural: "assets")
    asset_columns = {col["name"] for col in inspector.get_columns("assets")}
    assert "id" in asset_columns
    assert "path" in asset_columns
    assert "type" in asset_columns
    assert "hash" in asset_columns
    assert "approved" in asset_columns
    assert "created_at" in asset_columns

    # Check Pack table columns (table name is plural: "packs")
    pack_columns = {col["name"] for col in inspector.get_columns("packs")}
    assert "id" in pack_columns
    assert "name" in pack_columns
    assert "theme" in pack_columns
    assert "license_type" in pack_columns

    # Check Job table columns (table name is plural: "jobs")
    job_columns = {col["name"] for col in inspector.get_columns("jobs")}
    assert "id" in job_columns
    assert "kind" in job_columns
    assert "status" in job_columns
    assert "progress" in job_columns


def test_insert_asset_record(temp_db_path, monkeypatch):
    """Test inserting an Asset record into database"""
    from app.backend.models.entities import AssetProvenance, AssetType
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", str(temp_db_path))
    reset_engine()  # Clear cached engine

    # Create database
    create_db_and_tables()
    engine = get_engine()

    # Insert test asset
    with Session(engine) as session:
        asset = Asset(
            path="/test/image.png",
            type=AssetType.IMAGE,
            hash="abc123",
            provenance=AssetProvenance.UNKNOWN,
            approved=False,
        )
        session.add(asset)
        session.commit()
        session.refresh(asset)

        # Verify asset has ID
        assert asset.id is not None

    # Verify asset can be queried
    with Session(engine) as session:
        result = session.exec(select(Asset).where(Asset.path == "/test/image.png")).first()
        assert result is not None
        assert result.type == AssetType.IMAGE
        assert result.hash == "abc123"
        assert result.approved is False


def test_insert_pack_record(temp_db_path, monkeypatch):
    """Test inserting a Pack record into database"""
    from app.backend.models.entities import LicenseType
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", str(temp_db_path))
    reset_engine()  # Clear cached engine

    # Create database
    create_db_and_tables()
    engine = get_engine()

    # Insert test pack (use PERSONAL instead of ROYALTY_FREE)
    with Session(engine) as session:
        pack = Pack(
            name="Test Pack",
            theme="nature",
            license_type=LicenseType.PERSONAL,
            asset_count=10,
            total_size_mb=50.5,
        )
        session.add(pack)
        session.commit()
        session.refresh(pack)

        # Verify pack has ID
        assert pack.id is not None

    # Verify pack can be queried
    with Session(engine) as session:
        result = session.exec(select(Pack).where(Pack.name == "Test Pack")).first()
        assert result is not None
        assert result.theme == "nature"
        assert result.license_type == LicenseType.PERSONAL
        assert result.asset_count == 10


def test_insert_job_record(temp_db_path, monkeypatch):
    """Test inserting a Job record into database"""
    from app.backend.models.entities import JobKind, JobStatus
    from app.core import config

    monkeypatch.setattr(config.settings, "db_path", str(temp_db_path))
    reset_engine()  # Clear cached engine

    # Create database
    create_db_and_tables()
    engine = get_engine()

    # Insert test job
    with Session(engine) as session:
        job = Job(
            kind=JobKind.UPSCALE,
            status=JobStatus.PENDING,
            progress=0.0,
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        # Verify job has ID
        assert job.id is not None

    # Verify job can be queried
    with Session(engine) as session:
        result = session.exec(select(Job).where(Job.kind == JobKind.UPSCALE)).first()
        assert result is not None
        assert result.status == JobStatus.PENDING
        assert result.progress == 0.0


def test_server_startup_creates_database(monkeypatch):
    """Test that server startup creates database via startup event"""
    from app.backend.server import app
    from app.core import config

    # Create temp path for this test
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "startup_test.db"
        monkeypatch.setattr(config.settings, "db_path", str(db_path))
        reset_engine()  # Clear cached engine

        # Database should not exist yet
        assert not db_path.exists()

        # Create test client (triggers startup event)
        with TestClient(app):
            # Database should be created during startup
            assert db_path.exists()

            # Verify tables exist
            engine = get_engine()
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            assert "assets" in table_names
            assert "packs" in table_names
            assert "jobs" in table_names
