"""Core Utilities - Shared Helper Functions

STEP 5: File operations for curation (move, rename, hash)
"""

import hashlib
import shutil
from pathlib import Path

from sqlmodel import Session, select

from app.backend.models.entities import Asset
from app.core.db import get_engine
from app.core.logging import get_logger

logger = get_logger(__name__)


def compute_hash(path: str, algorithm: str = "sha256") -> str:
    """
    Compute file hash

    Args:
        path: File path
        algorithm: Hash algorithm (sha256, md5)

    Returns:
        Hex digest string
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    with file_path.open("rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


def safe_move_file(source: str | Path, dest_dir: str | Path, update_db: bool = True) -> Path:
    """
    Safely move file to destination directory with collision handling

    Handles name collisions by adding suffix (file_1.ext, file_2.ext, etc)
    Updates Asset.path in database if update_db=True

    Args:
        source: Source file path
        dest_dir: Destination directory
        update_db: Whether to update database Asset record

    Returns:
        Final destination path

    Raises:
        FileNotFoundError: If source doesn't exist
        ValueError: If destination is not a directory
    """
    source_path = Path(source)
    dest_dir_path = Path(dest_dir)

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    if not dest_dir_path.exists():
        dest_dir_path.mkdir(parents=True, exist_ok=True)
    elif not dest_dir_path.is_dir():
        raise ValueError(f"Destination is not a directory: {dest_dir}")

    # Determine final destination path with collision handling
    dest_path = dest_dir_path / source_path.name
    counter = 1

    while dest_path.exists():
        # Add suffix before extension: file_1.ext, file_2.ext, etc
        stem = source_path.stem
        suffix = source_path.suffix
        dest_path = dest_dir_path / f"{stem}_{counter}{suffix}"
        counter += 1

        if counter > 1000:  # Safety limit
            raise RuntimeError(f"Too many collision attempts for {source_path.name}")

    # Perform move
    try:
        shutil.move(str(source_path), str(dest_path))
        logger.info(f"Moved file: {source_path} -> {dest_path}")

        # Update database if requested
        if update_db:
            engine = get_engine()
            with Session(engine) as session:
                asset = session.exec(select(Asset).where(Asset.path == str(source_path))).first()
                if asset:
                    asset.path = str(dest_path)
                    session.add(asset)
                    session.commit()
                    logger.debug(f"Updated Asset path in DB: {dest_path}")
                else:
                    logger.warning(f"Asset not found in DB for path: {source_path}")

        return dest_path

    except Exception as e:
        logger.error(f"Failed to move file {source_path}: {e}")
        raise


def safe_rename_file(source: str | Path, new_name: str, update_db: bool = True) -> Path:
    """
    Safely rename file with collision handling

    Handles name collisions by adding suffix
    Updates Asset.path in database if update_db=True

    Args:
        source: Source file path
        new_name: New filename (without path)
        update_db: Whether to update database Asset record

    Returns:
        Final path after rename

    Raises:
        FileNotFoundError: If source doesn't exist
        ValueError: If new_name contains path separators
    """
    source_path = Path(source)

    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    if "/" in new_name or "\\" in new_name:
        raise ValueError(f"new_name must not contain path separators: {new_name}")

    # Determine final destination path
    dest_path = source_path.parent / new_name
    counter = 1

    while dest_path.exists() and dest_path != source_path:
        # Add suffix before extension
        name_path = Path(new_name)
        stem = name_path.stem
        suffix = name_path.suffix
        dest_path = source_path.parent / f"{stem}_{counter}{suffix}"
        counter += 1

        if counter > 1000:  # Safety limit
            raise RuntimeError(f"Too many collision attempts for {new_name}")

    # If dest_path is same as source, no rename needed
    if dest_path == source_path:
        return source_path

    # Perform rename
    try:
        source_path.rename(dest_path)
        logger.info(f"Renamed file: {source_path.name} -> {dest_path.name}")

        # Update database if requested
        if update_db:
            engine = get_engine()
            with Session(engine) as session:
                asset = session.exec(select(Asset).where(Asset.path == str(source_path))).first()
                if asset:
                    asset.path = str(dest_path)
                    session.add(asset)
                    session.commit()
                    logger.debug(f"Updated Asset path in DB: {dest_path}")
                else:
                    logger.warning(f"Asset not found in DB for path: {source_path}")

        return dest_path

    except Exception as e:
        logger.error(f"Failed to rename file {source_path}: {e}")
        raise


def delete_asset_and_file(asset_id: int, delete_file: bool = True) -> bool:
    """
    Delete Asset record from database and optionally delete the file

    Args:
        asset_id: Asset ID to delete
        delete_file: Whether to also delete the physical file

    Returns:
        True if successful, False otherwise
    """
    engine = get_engine()

    try:
        with Session(engine) as session:
            asset = session.get(Asset, asset_id)
            if not asset:
                logger.warning(f"Asset {asset_id} not found in database")
                return False

            file_path = Path(asset.path)

            # Delete from database
            session.delete(asset)
            session.commit()
            logger.info(f"Deleted Asset {asset_id} from database")

            # Delete physical file if requested
            if delete_file and file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Deleted file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete file {file_path}: {e}")
                    return False

            return True

    except Exception as e:
        logger.error(f"Failed to delete asset {asset_id}: {e}")
        return False
