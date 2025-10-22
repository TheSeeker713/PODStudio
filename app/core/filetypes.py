"""
File Type Detection
MIME type + magic signature + ffprobe fallback

TODO (Step 2+): Implement robust filetype detection with:
- python-magic for MIME
- ffprobe for video/audio metadata
- Manual signature checks for AI metadata
"""


def detect_filetype(path: str) -> str:
    """
    Detect file type from path

    Args:
        path: File path to analyze

    Returns:
        Type string: 'image', 'audio', 'video', or 'unknown'
    """
    # TODO: Implement with magic + ffprobe
    return "unknown"
