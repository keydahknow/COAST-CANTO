"""Apply UI overrides to the shared config module at runtime."""

from typing import Any, Dict, Optional

import config

# Keys the dashboard is allowed to change on the fly.
RUNTIME_SETTINGS = (
    "MODEL_NAME",
    "CONFIDENCE_THRESHOLD",
    "IMAGE_SIZE",
    "STATIONARY_SECONDS",
    "STATIONARY_PIXELS",
    "SUBMERSION_SECONDS",
    "SUBMERSION_MIN_VISIBLE_SECONDS",
    "ID_SWAP_SECONDS",
    "ID_SWAP_MAX_PIXELS",
    "SHOW_GRID",
    "SHOW_TRAIL",
    "SHOW_ALERT_BANNER",
    "ENABLE_DISCORD",
    "ALERT_COOLDOWN_SECONDS",
    "SAVE_OUTPUT",
)


def default_settings() -> Dict[str, Any]:
    """Snapshot of current config values for the dashboard."""
    return {key: getattr(config, key) for key in RUNTIME_SETTINGS}


def apply_runtime_settings(overrides: Optional[Dict[str, Any]]) -> None:
    """Write UI values into config before a pipeline run."""
    if not overrides:
        return
    for key, value in overrides.items():
        if key in RUNTIME_SETTINGS:
            setattr(config, key, value)
