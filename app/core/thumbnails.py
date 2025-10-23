"""
Thumbnail Generation
Image, video, audio waveform thumbnails

STEP 5: Basic thumbnail generation with caching
- Pillow for image thumbnails
- Placeholder icons for audio
- FFmpeg for video (fallback to placeholder)
"""

import hashlib
import subprocess
from pathlib import Path

from PIL import Image

from app.backend.models.entities import AssetType
from app.core.filetypes import guess_type_by_extension
from app.core.logging import get_logger

logger = get_logger(__name__)

# Thumbnail cache directory
THUMB_CACHE_DIR = Path("Cache/thumbs")
THUMB_SIZE = (256, 256)


def _ensure_cache_dir():
    """Ensure thumbnail cache directory exists"""
    THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_path(source_path: str, size: int = 256) -> Path:
    """
    Generate predictable cache path for thumbnail

    Uses hash of source path + size to create unique filename
    """
    path_hash = hashlib.md5(f"{source_path}_{size}".encode()).hexdigest()
    return THUMB_CACHE_DIR / f"{path_hash}.jpg"


def generate_image_thumbnail(source_path: Path, size: tuple[int, int] = THUMB_SIZE) -> Path:
    """
    Generate thumbnail for image file using Pillow

    Args:
        source_path: Path to source image
        size: Thumbnail size (width, height)

    Returns:
        Path to cached thumbnail
    """
    _ensure_cache_dir()
    cache_path = _get_cache_path(str(source_path), size[0])

    # Return cached if exists
    if cache_path.exists():
        return cache_path

    try:
        with Image.open(source_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background

            # Generate thumbnail maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save as JPEG
            img.save(cache_path, "JPEG", quality=85, optimize=True)
            logger.debug(f"Generated image thumbnail: {cache_path}")
            return cache_path

    except Exception as e:
        logger.error(f"Failed to generate image thumbnail for {source_path}: {e}")
        return _get_placeholder_path("image")


def generate_video_thumbnail(source_path: Path, size: tuple[int, int] = THUMB_SIZE) -> Path:
    """
    Generate thumbnail for video file using ffmpeg

    Extracts frame at 1 second or falls back to placeholder

    Args:
        source_path: Path to source video
        size: Thumbnail size (width, height)

    Returns:
        Path to cached thumbnail or placeholder
    """
    _ensure_cache_dir()
    cache_path = _get_cache_path(str(source_path), size[0])

    # Return cached if exists
    if cache_path.exists():
        return cache_path

    try:
        # Try to extract frame with ffmpeg
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(source_path),
                "-ss",
                "00:00:01",  # 1 second in
                "-vframes",
                "1",
                "-vf",
                f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
                "-y",
                str(cache_path),
            ],
            capture_output=True,
            timeout=10,
        )

        if result.returncode == 0 and cache_path.exists():
            logger.debug(f"Generated video thumbnail: {cache_path}")
            return cache_path
        else:
            logger.warning(f"ffmpeg failed for {source_path}, using placeholder")
            return _get_placeholder_path("video")

    except FileNotFoundError:
        logger.warning("ffmpeg not found, using video placeholder")
        return _get_placeholder_path("video")
    except Exception as e:
        logger.error(f"Failed to generate video thumbnail for {source_path}: {e}")
        return _get_placeholder_path("video")


def _get_placeholder_path(asset_type: str) -> Path:
    """
    Get path to placeholder icon for asset type

    For STEP 5, returns a simple colored placeholder
    TODO: Create actual icon files in assets/

    Args:
        asset_type: Type of asset (image, audio, video)

    Returns:
        Path to placeholder image
    """
    _ensure_cache_dir()
    placeholder_path = THUMB_CACHE_DIR / f"placeholder_{asset_type}.jpg"

    # Generate simple colored placeholder if it doesn't exist
    if not placeholder_path.exists():
        try:
            # Create colored rectangle as placeholder
            colors = {"image": (100, 200, 100), "audio": (100, 100, 200), "video": (200, 100, 100)}

            img = Image.new("RGB", THUMB_SIZE, colors.get(asset_type, (128, 128, 128)))
            img.save(placeholder_path, "JPEG", quality=85)
            logger.debug(f"Created placeholder: {placeholder_path}")
        except Exception as e:
            logger.error(f"Failed to create placeholder: {e}")

    return placeholder_path


def generate_thumbnail(path: str, size: int = 256) -> str:
    """
    Generate thumbnail for media file

    Dispatches to appropriate handler based on file type

    Args:
        path: Path to media file
        size: Thumbnail size in pixels (square)

    Returns:
        Path to generated thumbnail (cached or placeholder)
    """
    source_path = Path(path)

    if not source_path.exists():
        logger.warning(f"Source file not found: {path}")
        return str(_get_placeholder_path("unknown"))

    # Determine asset type
    asset_type = guess_type_by_extension(source_path)

    if asset_type is None:
        logger.warning(f"Unsupported file type: {path}")
        return str(_get_placeholder_path("unknown"))

    # Generate thumbnail based on type
    try:
        if asset_type == AssetType.IMAGE:
            thumb_path = generate_image_thumbnail(source_path, (size, size))
        elif asset_type == AssetType.VIDEO:
            thumb_path = generate_video_thumbnail(source_path, (size, size))
        elif asset_type == AssetType.AUDIO:
            # Audio gets placeholder for now (waveform in future)
            thumb_path = _get_placeholder_path("audio")
        else:
            thumb_path = _get_placeholder_path("unknown")

        return str(thumb_path)

    except Exception as e:
        logger.error(f"Thumbnail generation failed for {path}: {e}")
        return str(_get_placeholder_path(asset_type.value if asset_type else "unknown"))


def clear_thumbnail_cache():
    """Clear all cached thumbnails"""
    if THUMB_CACHE_DIR.exists():
        for thumb_file in THUMB_CACHE_DIR.glob("*.jpg"):
            try:
                thumb_file.unlink()
                logger.debug(f"Deleted thumbnail: {thumb_file}")
            except Exception as e:
                logger.error(f"Failed to delete thumbnail {thumb_file}: {e}")
