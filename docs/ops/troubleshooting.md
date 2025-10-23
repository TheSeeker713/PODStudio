# Troubleshooting - PODStudio

## File Watcher Issues

### Watcher not detecting files

**Symptom**: New files created in watch folders are not being detected by PODStudio.

**Possible Causes**:

1. **Watcher not started**
   - Check status bar: Should show "Watcher: Running (N folders)"
   - Start watcher: `Tools > Start File Watcher` menu

2. **Watch folders not configured**
   - Check `.env` file for `WATCH_FOLDERS` setting
   - Example: `WATCH_FOLDERS=C:\Users\YourName\Downloads,D:\Assets`
   - Folders must be comma-separated absolute paths
   - Restart backend after changing `.env`

3. **Folder does not exist**
   - Check backend logs for warnings: `Watch folder does not exist: <path>`
   - Create missing folders or update `WATCH_FOLDERS`

4. **Unsupported file type**
   - Check file extension against supported list:
     - **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`
     - **Audio**: `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`
     - **Video**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`
   - Case-insensitive extension matching

---

### Files detected but not appearing in UI

**Symptom**: Watcher logs show file detection, but assets don't appear in grid.

**Possible Causes**:

1. **Asset not approved**
   - New assets default to `approved=False`
   - STEP 4: UI grid does not filter by approval status yet
   - STEP 5+: Check "Show Unapproved" filter

2. **Database connection issue**
   - Check backend logs for database errors
   - Verify `podstudio.db` file exists in project root
   - Try restarting backend

3. **UI not refreshing**
   - STEP 4: No automatic refresh yet
   - STEP 5+: Click "Refresh" button in grid

---

### Indexing delays (antivirus interference)

**Symptom**: Long delays (5-30 seconds) between file creation and detection.

**Possible Causes**:

1. **Antivirus scanning**
   - **Windows Defender**: Scans new files before allowing access
   - **Third-party AV**: Norton, McAfee, Avast, etc.
   - **Solution**: Add watch folders to antivirus exclusion list
     - Windows Defender: Settings > Virus & Threat Protection > Exclusions
     - Add folders, not files (recursive exclusion)

2. **Cloud storage sync delays**
   - **OneDrive, Dropbox, Google Drive**: Sync delays can trigger multiple events
   - **Solution**: Use local folders for watch paths, not cloud-synced folders
   - Alternative: Increase debounce time in `app/core/watcher.py` (default: 2 seconds)

3. **Network drives**
   - **Symptom**: File watcher not working on mapped network drives
   - **Cause**: Watchdog library limited support for network paths on Windows
   - **Solution**: Use local drives or UNC paths (`\\server\share` instead of `Z:\`)

---

### Duplicate assets in database

**Symptom**: Same file appears multiple times in database.

**Possible Causes**:

1. **File moved/renamed after initial detection**
   - STEP 4: Watcher tracks by `path`, not hash
   - Moving file creates new `path`, triggers new insert
   - STEP 5+: Hash-based deduplication will prevent this

2. **Watcher restarted while file being written**
   - Large files may trigger multiple events
   - Debounce time (2 seconds) may not be enough
   - **Solution**: Increase `_debounce_seconds` in `AssetFileHandler.__init__()`

3. **Database constraint violation**
   - `path` column has UNIQUE constraint
   - Check logs for "Asset already exists" warnings
   - This should prevent duplicates - if you see duplicates, file a bug report

---

## Database Issues

### Database locked errors

**Symptom**: `sqlite3.OperationalError: database is locked`

**Possible Causes**:

1. **Multiple processes accessing database**
   - STEP 4: Backend and UI both access database
   - SQLite has limited concurrency
   - **Solution**: Use `check_same_thread=False` (already configured in `db.py`)

2. **Long-running transaction**
   - File watcher inserts can block reads
   - **Solution**: Keep transactions short (already implemented)

3. **Database file corruption**
   - Rare, but can happen if process killed during write
   - **Solution**: Delete `podstudio.db` and restart backend (recreates tables)

---

### Missing tables error

**Symptom**: `sqlalchemy.exc.OperationalError: no such table: asset`

**Possible Causes**:

1. **Backend not started**
   - Tables created on backend startup via `@app.on_event("startup")`
   - **Solution**: Start backend first: `python -m uvicorn app.backend.server:app --reload --port 8971`

2. **Database path mismatch**
   - Check `.env` for `DB_PATH` setting
   - Default: `./podstudio.db` (relative to project root)
   - **Solution**: Ensure backend and UI use same `DB_PATH`

3. **Schema changes not applied**
   - STEP 4: No migrations - schema changes require recreating database
   - **Solution**: Delete `podstudio.db` and restart backend

---

## Backend API Issues

### Backend not responding

**Symptom**: UI shows "API: ERROR" in red pill

**Possible Causes**:

1. **Backend not started**
   - **Solution**: Run `python -m uvicorn app.backend.server:app --reload --port 8971`
   - Check terminal for startup messages

2. **Port 8971 already in use**
   - **Solution**: Kill existing process or change port in `.env`:
     ```
     BACKEND_PORT=8972
     ```
   - Update `API_BASE_URL` in `.env` to match

3. **Firewall blocking localhost**
   - Rare on Windows, but possible
   - **Solution**: Allow Python through Windows Firewall

---

### Slow API responses

**Symptom**: UI freezes or slow to respond

**Possible Causes**:

1. **File watcher inserting many assets**
   - Large batch of files can cause database contention
   - **Solution**: Stop watcher during initial indexing, restart after

2. **Database not indexed**
   - STEP 4: `path` column has index, but queries may still be slow
   - STEP 5+: Add indexes for `theme`, `type`, `approved`

---

## UI Issues

### Top bar not visible

**Fixed in commit 3f40f2b** - if you see this issue, pull latest changes.

---

### Window hiding behind taskbar

**Fixed in commit 3f40f2b** - window now starts maximized.

---

### "Watcher: Running (0 folders)"

**Symptom**: Watcher started but shows 0 folders.

**Possible Causes**:

1. **No folders configured**
   - Check `.env` for `WATCH_FOLDERS`
   - Must be comma-separated absolute paths

2. **Folders do not exist**
   - Check backend logs for warnings
   - Create folders or update configuration

---

## Logging and Debugging

### Enable debug mode

Edit `.env`:
```
APP_DEBUG=true
```

Restart backend - this will:
- Print SQL queries to console
- Enable verbose logging
- Show detailed error messages

### View backend logs

Backend logs printed to console where `python -m uvicorn ...` was run.

Key log messages:
- `Watching folder: <path>` - Watcher started for folder
- `Inserted asset: <path>` - Asset successfully added
- `Asset already exists: <path>` - Deduplication skipped insert
- `Initializing database...` - Database startup

### View UI logs

STEP 4: UI logs printed to console where `python -m app.ui.app` was run.

Key log messages:
- `File watcher started from UI` - User clicked "Start Watcher"
- `File watcher stopped from UI` - User clicked "Stop Watcher"
- `Backend Status: OK` - API health check passed

---

## Performance Tips

### Reduce watcher overhead

1. **Limit watch folders** - Only watch folders where new assets arrive
2. **Use local drives** - Avoid network/cloud drives
3. **Batch file operations** - Stop watcher, add files, restart watcher

### Database optimization

1. **Regular vacuum** (STEP 5+):
   ```sql
   VACUUM;
   ```
2. **Delete old jobs**:
   ```sql
   DELETE FROM job WHERE status = 'completed' AND completed_at < datetime('now', '-30 days');
   ```

---

## Common Error Messages

### `Import "watchdog" could not be resolved`

**Lint error** - ignore if app runs fine. Pylance missing type stubs for watchdog.

### `Import "sqlmodel" could not be resolved`

**Lint error** - ignore if app runs fine. Pylance missing type stubs for sqlmodel.

### `table=True parameter warnings`

**Lint error** - false positive from Pylance. SQLModel uses this parameter correctly.

---

## Getting Help

1. **Check logs** - Backend console + UI console
2. **Check `.env`** - Configuration issues
3. **Check GitHub issues** - Known bugs and workarounds
4. **File a bug report** - Include logs and configuration

---

## Reset Everything

If all else fails, nuke and restart:

1. Stop backend and UI
2. Delete `podstudio.db`
3. Delete `__pycache__` folders: `find . -type d -name __pycache__ -exec rm -rf {} +` (Linux/Mac) or manually delete on Windows
4. Restart backend: `python -m uvicorn app.backend.server:app --reload --port 8971`
5. Restart UI: `python -m app.ui.app`

Database will be recreated with empty tables.
