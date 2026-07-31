"""
M5 — Alerts: tell a lifeguard when distress is detected.

Channels:
  1. ON-SCREEN — banner on the video (always works, no setup).
  2. DISCORD   — message to a server channel (recommended for demo; free).
  3. TELEGRAM  — optional phone alerts (needs bot token in .env).
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import cv2

import config

# Load .env from project root (folder above src/) so it works regardless of cwd.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(_ENV_FILE)
except ImportError:
    pass

try:
    import requests
except ImportError:
    requests = None


@dataclass
class AlertEvent:
    """One distress event worth notifying about."""

    track_id: int
    severity: str  # "warning" | "alert"
    reason: str  # "stationary" | "submersion"
    grid_cell: str = ""
    frame_index: int = 0

    @property
    def location_text(self) -> str:
        if self.grid_cell:
            return f"Zone {self.grid_cell}"
        return "location pending (grid not wired yet)"

    def message(self) -> str:
        level = "WARNING" if self.severity == "warning" else "ALERT"
        detail = "stationary swimmer" if self.reason == "stationary" else "possible submersion"
        return (
            f"C.O.A.S.T. {level}\n"
            f"Swimmer ID {self.track_id} — {detail}\n"
            f"{self.location_text}\n"
            f"Frame {self.frame_index}"
        )


class AlertManager:
    """
    Handles on-screen banners + optional Discord/Telegram for each frame.

    Call handle_frame() once per loop iteration after distress logic runs.
    """

    def __init__(self, fps: float):
        self.fps = fps
        self.cooldown_frames = max(1, int(config.ALERT_COOLDOWN_SECONDS * fps))
        self._last_sent: Dict[Tuple[int, str], int] = {}

        self._discord_webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        self._discord_enabled = bool(
            config.ENABLE_DISCORD and self._discord_webhook and requests is not None
        )

        self._telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self._telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self._telegram_enabled = bool(
            config.ENABLE_TELEGRAM
            and self._telegram_token
            and self._telegram_chat_id
            and requests is not None
        )

        if config.ENABLE_DISCORD and not self._discord_enabled:
            if not self._discord_webhook:
                print(
                    "[WARN] Discord disabled — DISCORD_WEBHOOK_URL is empty in "
                    f"{_ENV_FILE}\n"
                    "       Create a webhook in Discord and paste the URL in .env"
                )
            elif requests is None:
                print("[WARN] Discord disabled — run: pip install requests")
            else:
                print("[WARN] Discord disabled — check ENABLE_DISCORD in config.py")
        elif self._discord_enabled:
            print("[INFO] Discord alerts enabled (webhook loaded from .env)")
        if config.ENABLE_TELEGRAM and not self._telegram_enabled:
            print(
                "[WARN] Telegram alerts disabled — set TELEGRAM_BOT_TOKEN and "
                "TELEGRAM_CHAT_ID in .env, or set ENABLE_TELEGRAM = False in config.py"
            )

    def collect_events(self, swimmers, submerged_stubs, frame_index) -> List[AlertEvent]:
        """Turn M4 distress flags into alert events for this frame."""
        events: List[AlertEvent] = []

        for swimmer in swimmers:
            if not swimmer.is_distress:
                continue
            if swimmer.severity == "warning":
                events.append(
                    AlertEvent(
                        track_id=swimmer.id,
                        severity="warning",
                        reason="stationary",
                        grid_cell=swimmer.grid_cell,
                        frame_index=frame_index,
                    )
                )
            elif swimmer.severity == "alert":
                events.append(
                    AlertEvent(
                        track_id=swimmer.id,
                        severity="alert",
                        reason="submersion",
                        grid_cell=swimmer.grid_cell,
                        frame_index=frame_index,
                    )
                )

        for stub in submerged_stubs:
            events.append(
                AlertEvent(
                    track_id=stub.id,
                    severity="alert",
                    reason="submersion",
                    grid_cell=stub.grid_cell,
                    frame_index=frame_index,
                )
            )

        return events

    def _should_notify(self, event: AlertEvent, frame_index: int) -> bool:
        key = (event.track_id, event.reason)
        last = self._last_sent.get(key, -10_000)
        return frame_index - last >= self.cooldown_frames

    def _mark_notified(self, event: AlertEvent, frame_index: int) -> None:
        self._last_sent[(event.track_id, event.reason)] = frame_index

    def _send_discord(self, text: str) -> None:
        if not self._discord_enabled:
            return
        payload = {
            "content": text,
            "username": config.DISCORD_BOT_NAME,
        }
        try:
            response = requests.post(
                self._discord_webhook,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
        except Exception as exc:
            print(f"[WARN] Discord send failed: {exc}")

    def _send_telegram(self, text: str) -> None:
        if not self._telegram_enabled:
            return
        url = f"https://api.telegram.org/bot{self._telegram_token}/sendMessage"
        try:
            response = requests.post(
                url,
                json={"chat_id": self._telegram_chat_id, "text": text},
                timeout=10,
            )
            response.raise_for_status()
        except Exception as exc:
            print(f"[WARN] Telegram send failed: {exc}")

    def _play_sound(self) -> None:
        if not config.PLAY_ALERT_SOUND:
            return
        if sys.platform == "win32":
            try:
                import winsound

                winsound.Beep(880, 200)
            except Exception:
                pass

    def handle_frame(self, frame, swimmers, submerged_stubs, frame_index) -> List[AlertEvent]:
        """
        Process alerts for this frame: notify (once per cooldown), draw banner.
        Returns newly fired events (useful for logging / demo).
        """
        events = self.collect_events(swimmers, submerged_stubs, frame_index)
        new_events: List[AlertEvent] = []

        for event in events:
            if self._should_notify(event, frame_index):
                self._mark_notified(event, frame_index)
                new_events.append(event)
                print(f"[ALERT] {event.message().replace(chr(10), ' | ')}")
                self._send_discord(event.message())
                self._send_telegram(event.message())
                if event.severity == "alert":
                    self._play_sound()

        if events and config.SHOW_ALERT_BANNER:
            self._draw_banner(frame, events)

        return new_events

    def _draw_banner(self, frame, events: List[AlertEvent]) -> None:
        """Big top banner — red for alerts, orange if warnings only."""
        has_alert = any(e.severity == "alert" for e in events)
        color = config.DISTRESS_COLOR if has_alert else config.WARNING_COLOR
        label = "DISTRESS ALERT" if has_alert else "DISTRESS WARNING"

        h, w = frame.shape[:2]
        banner_h = 56
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, banner_h), color, -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        # Primary line
        primary = events[0]
        detail = (
            "submersion"
            if primary.reason == "submersion"
            else "stationary"
        )
        line1 = f"{label}: Swimmer ID {primary.track_id} — {detail} — {primary.location_text}"
        cv2.putText(
            frame,
            line1,
            (12, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        if len(events) > 1:
            cv2.putText(
                frame,
                f"+ {len(events) - 1} more active",
                (12, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
