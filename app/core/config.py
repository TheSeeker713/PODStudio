"""
Application Configuration
Uses pydantic-settings for type-safe config from .env

STEP 2: Expanded settings schema
"""


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env

    All settings have defaults for development mode
    """

    # Application
    app_env: str = "development"
    app_debug: bool = True
    app_log_level: str = "INFO"

    # Database
    db_path: str = "./podstudio.db"

    # External Tools
    media_tools_ffmpeg: str = "ffmpeg"
    media_tools_ffprobe: str = "ffprobe"
    media_tools_exiftool: str = "exiftool"
    media_tools_realesrgan: str = "tools/realesrgan/realesrgan-ncnn-vulkan.exe"
    media_tools_audiowaveform: str = "audiowaveform"

    # Directories
    library_root: str = "./Library"
    packs_root: str = "./Packs"
    work_root: str = "./Work"
    logs_root: str = "./Logs"
    cache_root: str = "./Cache"

    # File Watcher
    watch_folders: str = ""  # Comma-separated paths

    # Worker Configuration
    worker_backend: str = "threadpool"
    worker_threads: int = 4

    # Backend Service
    backend_host: str = "127.0.0.1"
    backend_port: int = 8971  # Updated from 8765 to match Step 3
    api_base_url: str = "http://127.0.0.1:8971"  # Full URL for UI to connect to backend

    # Processing Defaults
    bg_remove_model: str = "u2net"
    upscale_default_scale: int = 2
    upscale_gpu_batch_size: int = 4
    video_codec: str = "libx264"
    video_preset: str = "medium"
    audio_target_lufs: float = -16.0

    # UI Settings
    ui_theme: str = "light"
    ui_thumbnail_size: int = 256
    ui_grid_columns: str = "auto"

    # Export Settings
    export_default_license: str = "personal"
    export_compression_level: int = 6
    export_include_checksums: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Singleton instance
settings = Settings()
