# PODStudio — Windows Installation Guide

**Version**: 0.1.0  
**Platform**: Windows 10/11  
**Last Updated**: October 22, 2025

---

## Prerequisites

### System Requirements

**Minimum**:
- OS: Windows 10 (64-bit) or Windows 11
- CPU: Intel i5 / AMD Ryzen 5 (4+ cores)
- RAM: 8GB
- Storage: 10GB free space
- Python: 3.11 or 3.12

**Recommended**:
- OS: Windows 11
- CPU: Intel i7 / AMD Ryzen 7 (8+ cores)
- RAM: 16GB+
- GPU: NVIDIA RTX 3060 or better (6GB+ VRAM)
- Storage: 50GB free space (for assets + cache)
- Python: 3.11

---

## Installation Steps

### 1. Install Python 3.11+

Download from: https://www.python.org/downloads/

**Important**: Check "Add Python to PATH" during installation.

Verify:
```powershell
python --version
# Output: Python 3.11.x or 3.12.x
```

### 2. Clone Repository

```powershell
git clone https://github.com/<youruser>/PODStudio.git
cd PODStudio
```

### 3. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Verify activation (prompt should show `(.venv)`):
```powershell
(.venv) PS C:\...\PODStudio>
```

### 4. Install Dependencies

```powershell
# Upgrade core tools
python -m pip install --upgrade pip wheel setuptools pip-tools

# Compile requirements (locks versions)
pip-compile requirements.in -o requirements.txt
pip-compile dev-requirements.in -o dev-requirements.txt

# Install all dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

### 5. Install External Tools

#### FFmpeg (Required)

1. Download from: https://www.gyan.dev/ffmpeg/builds/ (ffmpeg-release-essentials.zip)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to Windows PATH:
   - Search "Environment Variables" in Start Menu
   - Edit "Path" → New → `C:\ffmpeg\bin`
   - Click OK

Verify:
```powershell
ffmpeg -version
ffprobe -version
```

#### ExifTool (Recommended)

1. Download from: https://exiftool.org/
2. Rename `exiftool(-k).exe` → `exiftool.exe`
3. Place in `C:\Windows` or add to PATH

Verify:
```powershell
exiftool -ver
```

#### Real-ESRGAN (Optional, for GPU upscaling)

1. Download from: https://github.com/xinntao/Real-ESRGAN/releases
   - `realesrgan-ncnn-vulkan-<version>-windows.zip`
2. Extract to `PODStudio\tools\realesrgan\`
3. Verify `realesrgan-ncnn-vulkan.exe` exists

### 6. Configure Environment

```powershell
# Copy template
copy .env.example .env

# Edit .env (use Notepad or VS Code)
notepad .env
```

Update paths if needed:
```env
MEDIA_TOOLS_FFMPEG=ffmpeg
MEDIA_TOOLS_EXIFTOOL=exiftool
MEDIA_TOOLS_REALESRGAN=tools/realesrgan/realesrgan-ncnn-vulkan.exe
LIBRARY_ROOT=./Library
PACKS_ROOT=./Packs
```

### 7. Initialize Database

```powershell
# Run CLI tool to create DB schema (when implemented in Step 2+)
python -m app.cli.manage db-init
```

### 8. Run Application

**Option A: Desktop UI Only (STEP 2)**:
```powershell
# Run the PySide6 desktop app
python -m app.ui.app
```

Expected behavior:
- Main window appears with placeholder widgets
- Left/right docks are collapsible
- Center shows 3 tabs (Images, Audio, Video) with empty grid states
- Bottom tray shows "0 selected" with disabled Build Pack button
- Top bar shows "API: OFFLINE" (backend not running)

**Option B: Backend + UI Together (STEP 3+)**:

You need **two terminal windows**:

**Terminal 1 - Backend API**:
```powershell
# Start FastAPI backend server
python -m uvicorn app.backend.server:app --reload --port 8971
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8971 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Terminal 2 - Desktop UI**:
```powershell
# Run the PySide6 desktop app
python -m app.ui.app
```

Expected behavior:
- Main window appears
- Top bar shows "API: OK" in green (backend connected)
- Hardware pill shows "Mode: UNKNOWN" (probe endpoint returns placeholder)
- All other UI elements same as Option A

**Verify Backend**:
Open browser to http://127.0.0.1:8971/docs to see FastAPI Swagger UI.

**Stop Backend**:
Press `Ctrl+C` in Terminal 1 to stop the backend server.
- Bottom tray shows "0 selected" with disabled Build Pack button
- Status bar shows "Ready | No assets loaded"

**Backend Service (Testing Only)**:
```powershell
# Run FastAPI backend (when implemented in Step 3+)
uvicorn app.backend.server:app --host 127.0.0.1 --port 8765
```

**CLI Tools (Future)**:
```powershell
# Database management (when implemented)
python -m app.cli.manage db-init
python -m app.cli.manage db-migrate
```

---

## Troubleshooting

### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or manually add `C:\Users\<You>\AppData\Local\Programs\Python\Python311` to PATH

### "pip-compile not found"
```powershell
python -m pip install pip-tools
```

### "FFmpeg not found"
- Verify PATH contains `C:\ffmpeg\bin`
- Restart PowerShell after editing PATH

### "rembg fails with CUDA error"
- Check NVIDIA drivers updated (latest from nvidia.com)
- Fallback to CPU mode (slower): Edit `.env` → `FORCE_CPU_ONLY=true`

### "SQLite database locked"
- Close any DB browser tools (DB Browser for SQLite)
- Delete `podstudio.db` and re-run `db-init`

---

## Updating PODStudio

```powershell
# Pull latest changes
git pull origin main

# Recompile requirements (in case deps changed)
pip-compile requirements.in -o requirements.txt
pip install -r requirements.txt

# Run migrations (future feature)
python -m app.cli.manage db-migrate
```

---

## Uninstallation

```powershell
# Deactivate venv
deactivate

# Delete project folder
cd ..
rmdir /s PODStudio

# Optional: Remove FFmpeg, ExifTool from PATH
```

---

**Next**: See [external_tools.md](external_tools.md) for detailed tool setup.
