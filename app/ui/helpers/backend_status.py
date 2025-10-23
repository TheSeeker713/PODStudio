"""
Backend Status Helper
STEP 3: Ping backend API to check if it's running and get hardware status

This module provides a simple way for the UI to check backend availability.
No error popups - just stores status for display in top bar.
"""

import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BackendStatus:
    """Backend API status"""

    api_connected: bool = False
    api_version: str | None = None
    hardware_mode: str = "unknown"  # green, yellow, red, unknown
    gpu_name: str | None = None
    error: str | None = None


class BackendStatusChecker:
    """
    Check backend API health and hardware probe

    STEP 3: Simple HTTP GET requests, no error dialogs.
    Stores results in memory for UI to display.
    """

    def __init__(self):
        self.status = BackendStatus()
        self.base_url = settings.api_base_url

    def check_health(self, timeout: float = 2.0) -> bool:
        """
        Ping /api/health endpoint

        Args:
            timeout: Request timeout in seconds

        Returns:
            True if API is reachable, False otherwise
        """
        try:
            url = f"{self.base_url}/api/health"
            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    # Parse JSON response (simple approach without external libs)
                    import json

                    data = json.loads(response.read().decode("utf-8"))
                    self.status.api_connected = True
                    self.status.api_version = data.get("version", "unknown")
                    self.status.error = None
                    logger.info(f"Backend health check OK: version {self.status.api_version}")
                    return True

        except urllib.error.URLError as e:
            self.status.api_connected = False
            self.status.error = f"Connection failed: {e.reason}"
            logger.warning(f"Backend health check failed: {e}")
        except Exception as e:
            self.status.api_connected = False
            self.status.error = f"Unexpected error: {e}"
            logger.error(f"Backend health check error: {e}")

        return False

    def check_probe(self, timeout: float = 2.0) -> bool:
        """
        Ping /api/probe endpoint for hardware info

        Args:
            timeout: Request timeout in seconds

        Returns:
            True if probe succeeded, False otherwise
        """
        try:
            url = f"{self.base_url}/api/probe"
            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    import json

                    data = json.loads(response.read().decode("utf-8"))
                    self.status.hardware_mode = data.get("mode", "unknown")
                    self.status.gpu_name = data.get("gpu", "unknown")
                    logger.info(f"Hardware probe OK: mode={self.status.hardware_mode}, gpu={self.status.gpu_name}")
                    return True

        except urllib.error.URLError as e:
            logger.warning(f"Backend probe check failed: {e}")
        except Exception as e:
            logger.error(f"Backend probe error: {e}")

        return False

    def check_all(self) -> BackendStatus:
        """
        Check both health and probe endpoints

        Returns:
            BackendStatus with all available info
        """
        self.check_health()
        if self.status.api_connected:
            self.check_probe()

        return self.status


# Singleton instance for UI to use
backend_status_checker = BackendStatusChecker()
