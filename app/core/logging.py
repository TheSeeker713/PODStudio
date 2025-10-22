"""
Logging Configuration
Structured logging for file + console output

TODO (Step 2+): Set up logging with JSON format, rotation, levels
"""

import logging

# Placeholder logger
logger = logging.getLogger("podstudio")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
