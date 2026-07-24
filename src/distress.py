"""
M4 — Distress logic: decide when a tracked swimmer may need help.

This module does NOT use AI. It applies simple rules over time on top of
tracking (M2):

  1. STATIONARY — ID is visible but barely moving (e.g. treading in one spot).
  2. SUBMERSION — ID was visible, then disappears for several seconds
     (possible underwater / out of view).

Both rules need SECONDS of evidence so one missed frame does not trigger
a false alarm. Tune thresholds in config.py.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

import config
from tracker import Swimmer


@dataclass
class TrackRecord:
    """Everything we remember about one track ID over time."""

    track_id: int
    first_seen_frame: int
    last_seen_frame: int
    last_box: Tuple[int, int, int, int]
    last_center: Tuple[int, int]
    # Recent (frame_index, center) pairs — used for the stationary check.
    center_history: List[Tuple[int, Tuple[int, int]]] = field(default_factory=list)


def _frames_for_seconds(seconds: float, fps: float) -> int:
    return max(1, int(seconds * fps))


def _movement_pixels(history: List[Tuple[int, Tuple[int, int]]]) -> float:
    """Total path length (pixels) across the stored center history."""
    if len(history) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(history)):
        x0, y0 = history[i - 1][1]
        x1, y1 = history[i][1]
        total += ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    return total


class DistressMonitor:
    """
    Stateful monitor — call process() once per video frame.

    Keeps memory of each track ID even when YOLO briefly loses them,
    so we can detect submersion (vanished too long).
    """

    def __init__(self, fps: float):
        self.fps = fps
        self.records: Dict[int, TrackRecord] = {}
        self.stationary_frames = _frames_for_seconds(
            config.STATIONARY_SECONDS, fps
        )
        self.submersion_frames = _frames_for_seconds(
            config.SUBMERSION_SECONDS, fps
        )
        self.min_visible_frames = _frames_for_seconds(
            config.SUBMERSION_MIN_VISIBLE_SECONDS, fps
        )

    def process(
        self, swimmers: List[Swimmer], frame_index: int
    ) -> List[Swimmer]:
        """
        Update distress flags on visible swimmers and return extra Swimmer
        stubs for IDs that disappeared (submersion alerts at last position).
        """
        seen_ids: Set[int] = set()
        submerged_stubs: List[Swimmer] = []

        for swimmer in swimmers:
            seen_ids.add(swimmer.id)
            self._update_record(swimmer, frame_index)
            self._check_stationary(swimmer, frame_index)

        for track_id, record in self.records.items():
            if track_id in seen_ids:
                continue
            missing_frames = frame_index - record.last_seen_frame
            visible_long_enough = (
                record.last_seen_frame - record.first_seen_frame
                >= self.min_visible_frames
            )
            if (
                visible_long_enough
                and missing_frames >= self.submersion_frames
            ):
                submerged_stubs.append(
                    Swimmer(
                        id=track_id,
                        box=record.last_box,
                        center=record.last_center,
                        confidence=0.0,
                        is_distress=True,
                        severity="alert",
                        is_submerged=True,
                    )
                )

        return submerged_stubs

    def _update_record(self, swimmer: Swimmer, frame_index: int) -> None:
        record = self.records.get(swimmer.id)
        if record is None:
            record = TrackRecord(
                track_id=swimmer.id,
                first_seen_frame=frame_index,
                last_seen_frame=frame_index,
                last_box=swimmer.box,
                last_center=swimmer.center,
            )
            self.records[swimmer.id] = record
        else:
            record.last_seen_frame = frame_index
            record.last_box = swimmer.box
            record.last_center = swimmer.center

        record.center_history.append((frame_index, swimmer.center))
        # Keep only the window we need for the stationary check.
        cutoff = frame_index - self.stationary_frames
        record.center_history = [
            item for item in record.center_history if item[0] >= cutoff
        ]

    def _check_stationary(self, swimmer: Swimmer, frame_index: int) -> None:
        record = self.records[swimmer.id]
        history = record.center_history
        if len(history) < 2:
            return

        span_frames = frame_index - history[0][0]
        if span_frames < self.stationary_frames:
            return

        moved = _movement_pixels(history)
        if moved <= config.STATIONARY_PIXELS:
            swimmer.is_distress = True
            swimmer.severity = "warning"

    def active_alerts(self) -> List[str]:
        """Short text lines for on-screen HUD / future Telegram alerts."""
        lines: List[str] = []
        for record in self.records.values():
            # Submersion messages are built from stubs in track.py; here we
            # only summarize visible warnings still in memory if needed.
            pass
        return lines
