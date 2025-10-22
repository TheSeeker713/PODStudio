# External Tools Setup

**Version**: 0.1.0  
**Platform**: Windows 10/11  
**Last Updated**: October 22, 2025

---

## Overview

PODStudio relies on external binaries for media processing. This doc covers installation and PATH configuration.

---

## FFmpeg (Required)

**Purpose**: Video/audio transcoding, metadata extraction

### Installation

1. **Download**: https://www.gyan.dev/ffmpeg/builds/
   - Choose: `ffmpeg-release-essentials.zip`
2. **Extract**: `C:\ffmpeg`
3. **Add to PATH**:
   - Windows Key → "Environment Variables"
   - System Variables → Path → Edit → New
   - Add: `C:\ffmpeg\bin`
   - Click OK (restart PowerShell)

### Verification

```powershell
ffmpeg -version
# Output: ffmpeg version 6.0-...

ffprobe -version
# Output: ffprobe version 6.0-...
```

### Troubleshooting

- **"ffmpeg not recognized"**: Restart PowerShell after editing PATH
- **Missing DLLs**: Download "essentials" build (not "full" or "static")

---

## ExifTool (Recommended)

**Purpose**: EXIF metadata extraction from images

### Installation

1. **Download**: https://exiftool.org/
   - Windows Executable: `exiftool-12.50.zip`
2. **Extract**: Anywhere (e.g., `C:\Tools\exiftool`)
3. **Rename**: `exiftool(-k).exe` → `exiftool.exe`
4. **Add to PATH**: Same process as FFmpeg

### Verification

```powershell
exiftool -ver
# Output: 12.50 (or current version)
```

### Troubleshooting

- **Slow first run**: ExifTool unpacks on first launch (~5 seconds)
- **Permission errors**: Run PowerShell as Administrator

---

## Real-ESRGAN (Optional, GPU Upscaling)

**Purpose**: AI-powered 2x/4x image upscaling (GPU-accelerated)

### Installation

1. **Download**: https://github.com/xinntao/Real-ESRGAN/releases
   - Windows: `realesrgan-ncnn-vulkan-<version>-windows.zip`
2. **Extract**: `PODStudio\tools\realesrgan\`
3. **Verify**: `tools\realesrgan\realesrgan-ncnn-vulkan.exe` exists
4. **No PATH needed**: PODStudio calls absolute path from `.env`

### Configuration

Edit `.env`:
```env
MEDIA_TOOLS_REALESRGAN=tools/realesrgan/realesrgan-ncnn-vulkan.exe
```

### Verification

```powershell
.\tools\realesrgan\realesrgan-ncnn-vulkan.exe
# Output: Usage: realesrgan-ncnn-vulkan -i input.jpg -o output.png ...
```

### GPU Requirements

- **Minimum**: NVIDIA GTX 1060 (6GB VRAM) or AMD equivalent
- **Recommended**: RTX 3060+ (8GB+ VRAM)
- **Fallback**: CPU mode (very slow; 10x longer)

### Troubleshooting

- **"Vulkan error"**: Update GPU drivers from NVIDIA/AMD website
- **Slow processing**: Check GPU mode with `-g 0` flag (0 = first GPU)
- **Out of memory**: Reduce batch size or use 2x instead of 4x

---

## audiowaveform (Optional, Audio Waveforms)

**Purpose**: Generate PNG waveforms for audio files

### Installation

1. **Download**: https://github.com/bbc/audiowaveform/releases
   - Windows: `audiowaveform-<version>-win64.zip`
2. **Extract**: `C:\Tools\audiowaveform`
3. **Add to PATH**: Same process as FFmpeg

### Verification

```powershell
audiowaveform --version
# Output: audiowaveform v1.6.0
```

### Troubleshooting

- **DLL errors**: Install Visual C++ Redistributable from Microsoft

---

## Redis (Optional, for RQ Task Queue)

**Purpose**: Backend for RQ (task queue alternative to ThreadPoolExecutor)

### Installation (Windows Subsystem for Linux)

1. **Install WSL2**:
   ```powershell
   wsl --install
   ```
2. **Install Redis in WSL**:
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo service redis-server start
   ```
3. **Test**:
   ```bash
   redis-cli ping
   # Output: PONG
   ```

### Configuration

Edit `.env`:
```env
WORKER_BACKEND=rq
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Troubleshooting

- **Connection refused**: Start Redis in WSL: `sudo service redis-server start`
- **Windows-native Redis**: Use Memurai (https://www.memurai.com/) as drop-in replacement

---

## Tool Version Matrix

| Tool | Tested Version | Required? | Purpose |
|------|----------------|-----------|---------|
| FFmpeg | 6.0+ | ✅ Yes | Video/audio processing |
| ExifTool | 12.50+ | Recommended | EXIF metadata |
| Real-ESRGAN | 0.2.5+ | Optional | GPU upscaling |
| audiowaveform | 1.6.0+ | Optional | Audio waveforms |
| Redis | 7.0+ | Optional | RQ task queue |

---

## Future Tools (Not Yet Supported)

- **yt-dlp**: Download reference videos (v1.1 feature)
- **ImageMagick**: Advanced image manipulation (v1.2 feature)
- **Whisper**: Audio transcription for captions (v2.0 feature)

---

**Next**: See [troubleshooting.md](troubleshooting.md) for common issues.
