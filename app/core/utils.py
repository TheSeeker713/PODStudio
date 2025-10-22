"""Core Utilities - Shared Helper Functions"""


def compute_hash(path: str, algorithm: str = "sha256") -> str:
    """
    Compute file hash

    Args:
        path: File path
        algorithm: Hash algorithm (sha256, xxhash)

    Returns:
        Hex digest string
    """
    # TODO: Implement with hashlib or xxhash
    return ""
