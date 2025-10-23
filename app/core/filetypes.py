"""
File Type Detection
Extension-based detection for STEP 4 (metadata stubs only)

Future: MIME type + magic signature + ffprobe fallback for robust detection
"""

from pathlib import Path

from app.backend.models.entities import AssetType

# Extension to AssetType mapping
EXTENSION_MAP = {
    # Images
    ".png": AssetType.IMAGE,
    ".jpg": AssetType.IMAGE,
    ".jpeg": AssetType.IMAGE,
    ".gif": AssetType.IMAGE,
    ".bmp": AssetType.IMAGE,
    ".tiff": AssetType.IMAGE,
    ".tif": AssetType.IMAGE,
    ".webp": AssetType.IMAGE,
    # Audio
    ".wav": AssetType.AUDIO,
    ".mp3": AssetType.AUDIO,
    ".flac": AssetType.AUDIO,
    ".ogg": AssetType.AUDIO,
    ".m4a": AssetType.AUDIO,
    ".aac": AssetType.AUDIO,
    # Video
    ".mp4": AssetType.VIDEO,
    ".mov": AssetType.VIDEO,
    ".avi": AssetType.VIDEO,
    ".mkv": AssetType.VIDEO,
    ".webm": AssetType.VIDEO,
    ".flv": AssetType.VIDEO,
}

# Supported extensions (all keys from EXTENSION_MAP)
SUPPORTED_EXTENSIONS = set(EXTENSION_MAP.keys())


def guess_type_by_extension(path: str | Path) -> AssetType | None:
    """
    Guess asset type from file extension

    Args:
        path: File path to analyze

    Returns:
        AssetType enum value or None if unsupported
    """
    ext = Path(path).suffix.lower()
    return EXTENSION_MAP.get(ext)


def is_supported(path: str | Path) -> bool:
    """
    Check if file extension is supported

    Args:
        path: File path to check

    Returns:
        True if extension is in SUPPORTED_EXTENSIONS
    """
    ext = Path(path).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def detect_filetype(path: str) -> str:
    """
    Detect file type from path (legacy function for compatibility)

    Args:
        path: File path to analyze

    Returns:
        Type string: 'image', 'audio', 'video', or 'unknown'
    """
    asset_type = guess_type_by_extension(path)
    if asset_type is None:
        return "unknown"
    return asset_type.value  # Returns 'image', 'audio', or 'video'
