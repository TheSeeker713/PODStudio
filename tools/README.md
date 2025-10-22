# External Tools Directory

This directory is for optional external binaries used by PODStudio.

## Real-ESRGAN (Windows)

**Purpose**: GPU-accelerated image upscaling (2x, 4x)

**Download**: https://github.com/xinntao/Real-ESRGAN/releases

1. Download `realesrgan-ncnn-vulkan-<version>-windows.zip`
2. Extract to `tools/realesrgan/`
3. Verify `realesrgan-ncnn-vulkan.exe` is present
4. Update `.env`:
   ```
   MEDIA_TOOLS_REALESRGAN=tools/realesrgan/realesrgan-ncnn-vulkan.exe
   ```

**Note**: Do NOT commit binaries to Git (see `.gitignore`). Document only.

## audiowaveform (Optional)

**Purpose**: Audio waveform PNG generation

**Download**: https://github.com/bbc/audiowaveform/releases

1. Download `audiowaveform-<version>-win64.zip`
2. Extract to `tools/audiowaveform/`
3. Add to PATH or use absolute path in `.env`

## FFmpeg (Required - System PATH)

**Purpose**: Video/audio transcoding, metadata extraction

**Download**: https://ffmpeg.org/download.html (Windows builds)

1. Download static build from https://www.gyan.dev/ffmpeg/builds/
2. Extract and add `bin/` folder to Windows PATH
3. Verify:
   ```powershell
   ffmpeg -version
   ffprobe -version
   ```

## ExifTool (Recommended - System PATH)

**Purpose**: EXIF metadata extraction from images

**Download**: https://exiftool.org/

1. Download Windows Executable
2. Rename `exiftool(-k).exe` → `exiftool.exe`
3. Add to PATH or place in project root

---

**Do not commit binaries to this folder** — see `.gitignore` for exclusions.
