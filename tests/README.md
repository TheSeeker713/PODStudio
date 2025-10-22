# PODStudio Test Suite

## Test Organization

- **`unit/`**: Fast, isolated unit tests (no external dependencies)
- **`integration/`**: Integration tests (may require FFmpeg, GPU, etc.)

## Running Tests

```powershell
# All tests
pytest

# Unit tests only
pytest tests/unit -m unit

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_thumbnails.py -v

# Skip slow tests
pytest -m "not slow"

# Skip GPU tests (CPU-only systems)
pytest -m "not gpu"
```

## Test Markers

Use markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_hash_computation():
    # Fast, no external deps
    pass

@pytest.mark.integration
def test_ffmpeg_transcoding():
    # Requires FFmpeg
    pass

@pytest.mark.slow
def test_large_video_processing():
    # Takes >10 seconds
    pass

@pytest.mark.gpu
def test_gpu_upscaling():
    # Requires NVIDIA GPU
    pass
```

## Mocking External Dependencies

For media processing tests, use golden files and mocks:

```python
from unittest.mock import patch, MagicMock

def test_bg_removal_with_mock():
    with patch('rembg.remove') as mock_remove:
        mock_remove.return_value = b'...'  # Mock output
        result = remove_background('test.png')
        assert result is not None
```

## Golden Files

Place golden files (expected outputs) in `tests/fixtures/`:

- `tests/fixtures/images/` - Test images
- `tests/fixtures/audio/` - Test audio files
- `tests/fixtures/video/` - Test video clips
- `tests/fixtures/expected/` - Expected outputs for comparison

## Coverage Goals

- **Overall**: >80%
- **Core modules** (`app/core/`): >90%
- **Workers** (`app/workers/`): >80%
- **UI**: >60% (harder to test)

## Future Enhancements

- Add GitHub Actions matrix testing (Windows 10/11, Python 3.11/3.12)
- Add performance benchmarks for media processing
- Add snapshot testing for UI components
