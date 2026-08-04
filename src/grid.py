"""
M3 — Grid / lane logic for locating swimmers in the water.

DEMO (single main camera):
  The frame is split into 3 vertical lanes — Left | Center | Right.
  Each swimmer's center point maps to one lane. Distress alerts include
  that lane name (e.g. "Lane: Center").

FUTURE EXPANSION (not implemented — documented for proposal alignment):
  Additional cameras (left/right of main) would each have their own lane grid.
  Those grids would be cross-referenced to the MAIN camera grid so all alerts
  are still reported from the main camera's perspective, e.g.:
    side-cam "far left" → main grid "Left"
  See LaneGrid and the note on map_external_lane() below.
"""

from typing import List

import cv2

import config
from tracker import Swimmer

# Display labels for the three demo lanes (capitalized for alerts).
LANE_LEFT = "Left"
LANE_CENTER = "Center"
LANE_RIGHT = "Right"


class LaneGrid:
    """
    Three vertical lanes across one camera view (equal width thirds).

    Boundaries update if the video resolution changes (e.g. first frame).
    """

    def __init__(self, frame_width: int, frame_height: int):
        self.width = frame_width
        self.height = frame_height
        self.boundary_x1 = frame_width // 3
        self.boundary_x2 = 2 * frame_width // 3

    def update_size(self, frame_width: int, frame_height: int) -> None:
        """Recompute boundaries if frame size changes (webcam)."""
        if frame_width != self.width or frame_height != self.height:
            self.width = frame_width
            self.height = frame_height
            self.boundary_x1 = frame_width // 3
            self.boundary_x2 = 2 * frame_width // 3

    def lane_for_point(self, x: int, y: int) -> str:
        """Return lane label (Left / Center / Right) for a pixel position."""
        if x < self.boundary_x1:
            return LANE_LEFT
        if x < self.boundary_x2:
            return LANE_CENTER
        return LANE_RIGHT

    def assign_lanes(self, swimmers: List[Swimmer]) -> None:
        """Set grid_cell on each swimmer from their center point."""
        for swimmer in swimmers:
            cx, cy = swimmer.center
            swimmer.grid_cell = self.lane_for_point(cx, cy)

    def draw(self, frame) -> None:
        """Draw lane dividers and labels on the frame."""
        if not config.SHOW_GRID:
            return

        h, w = frame.shape[:2]
        self.update_size(w, h)

        color = config.GRID_COLOR
        thickness = config.GRID_LINE_THICKNESS

        # Vertical lane dividers (full height).
        cv2.line(frame, (self.boundary_x1, 0), (self.boundary_x1, h), color, thickness)
        cv2.line(frame, (self.boundary_x2, 0), (self.boundary_x2, h), color, thickness)

        # Lane names at the top of each third.
        labels = [
            (LANE_LEFT, w // 6),
            (LANE_CENTER, w // 2),
            (LANE_RIGHT, 5 * w // 6),
        ]
        for label, x_center in labels:
            text_size = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, config.GRID_LABEL_SCALE, 2
            )[0]
            x = x_center - text_size[0] // 2
            cv2.putText(
                frame,
                label,
                (x, config.GRID_LABEL_Y),
                cv2.FONT_HERSHEY_SIMPLEX,
                config.GRID_LABEL_SCALE,
                color,
                2,
            )


def map_external_lane(side_camera_lane: str, camera_side: str) -> str:
    """
    FUTURE: map a side camera's lane to the main camera grid.

    Not used in the demo. Example stub for multi-camera expansion:
      map_external_lane("center", "left")  → "Left" on main grid

    Implement mapping tables when side cameras are added.
    """
    _ = (side_camera_lane, camera_side)
    return LANE_CENTER
