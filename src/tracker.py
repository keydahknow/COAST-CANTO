"""
M2 — Tracking: give each detected person a stable ID across frames.

Detection (M1) answers: "Is there a person in THIS frame?"
Tracking (M2) answers: "Is THIS the same person as in the LAST frame?"

Ultralytics does the hard work with model.track(..., persist=True).
This file turns raw YOLO output into clean Swimmer objects that later
milestones (grid, distress, alerts) can read.
"""

from dataclasses import dataclass, field
from typing import List, Tuple

import cv2
import config

# A small palette so each track ID gets its own box color (BGR).
ID_COLORS = [
    (0, 200, 0),
    (255, 140, 0),
    (0, 165, 255),
    (255, 0, 255),
    (0, 255, 255),
    (180, 105, 255),
    (147, 20, 255),
    (0, 128, 255),
]


@dataclass
class Swimmer:
    """
    One tracked person — the shared 'contract' between modules.

    You (tracking/distress) fill id, box, center, confidence, is_distress, severity.
    Imani (grid/alerts) reads center and fills grid_cell, then uses severity.
    """

    id: int
    box: Tuple[int, int, int, int]  # x1, y1, x2, y2 in pixels
    center: Tuple[int, int]  # cx, cy — middle of the box
    confidence: float
    is_distress: bool = False
    severity: str = "none"  # "none" | "warning" | "alert"
    grid_cell: str = ""
    trail: List[Tuple[int, int]] = field(default_factory=list)


def box_center(box) -> Tuple[int, int]:
    """Middle point of a bounding box — used for 'did they move?' later."""
    x1, y1, x2, y2 = (int(v) for v in box)
    return ((x1 + x2) // 2, (y1 + y2) // 2)


def color_for_id(track_id: int) -> Tuple[int, int, int]:
    return ID_COLORS[track_id % len(ID_COLORS)]


def parse_tracks(results) -> List[Swimmer]:
    """
    Convert YOLO tracking output into a list of Swimmer objects.

    model.track() adds an ID to each box when it can match someone
    across frames. If id is missing (rare), we skip that detection.
    """
    swimmers: List[Swimmer] = []
    if results[0].boxes is None or len(results[0].boxes) == 0:
        return swimmers

    for box in results[0].boxes:
        if box.id is None:
            continue
        track_id = int(box.id.item())
        xyxy = box.xyxy[0]
        conf = float(box.conf[0])
        center = box_center(xyxy)
        swimmers.append(
            Swimmer(
                id=track_id,
                box=tuple(int(v) for v in xyxy),
                center=center,
                confidence=conf,
            )
        )
    return swimmers


def update_trails(swimmers: List[Swimmer], history: dict) -> None:
    """Remember recent center points per ID so we can draw a movement trail."""
    for s in swimmers:
        points = history.get(s.id, [])
        points.append(s.center)
        if len(points) > config.TRAIL_LENGTH:
            points = points[-config.TRAIL_LENGTH :]
        history[s.id] = points
        s.trail = list(points)


def draw_swimmer(frame, swimmer: Swimmer) -> None:
    """Draw box, ID label, and optional trail for one tracked person."""
    x1, y1, x2, y2 = swimmer.box
    color = color_for_id(swimmer.id)

    if config.SHOW_TRAIL and len(swimmer.trail) > 1:
        for i in range(1, len(swimmer.trail)):
            cv2.line(frame, swimmer.trail[i - 1], swimmer.trail[i], color, 2)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = f"ID {swimmer.id}  {swimmer.confidence:.2f}"
    cv2.putText(
        frame,
        label,
        (x1, max(y1 - 8, 12)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        config.TEXT_COLOR,
        2,
    )


def track_frame(model, frame, persist: bool = True):
    """
    Run one frame through YOLO *tracking* (not plain detection).

    persist=True tells the tracker to remember IDs from previous frames.
    Returns the raw results object (for debugging) and parsed Swimmer list.
    """
    results = model.track(
        frame,
        persist=persist,
        tracker=config.TRACKER_CONFIG,
        classes=[config.PERSON_CLASS_ID],
        conf=config.CONFIDENCE_THRESHOLD,
        imgsz=config.IMAGE_SIZE,
        verbose=False,
    )
    return results, parse_tracks(results)
