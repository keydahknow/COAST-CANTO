"""
M3 — Grid logic for locating swimmers in the water.

DEMO (single main camera):
  3 columns × 2 rows = 6 cells.
  Two vertical lines (thirds) + one horizontal line (middle) divide the frame.
  Top row labels: A | B | C  (left → right)
  Bottom row labels: 1 | 2 | 3  (left → right)
  Alerts include the cell name (e.g. "Zone: B").

FUTURE EXPANSION (not implemented — documented for proposal alignment):
  Additional cameras (left/right of main) would each have their own grid.
  Those grids would be cross-referenced to the MAIN camera grid so all alerts
  are still reported from the main camera's perspective.
"""

from typing import List

import cv2

import config
from tracker import Swimmer

# Top row (near / upper half of frame) — left to right.
ROW_TOP = ("A", "B", "C")
# Bottom row (far / lower half of frame) — left to right.
ROW_BOTTOM = ("1", "2", "3")


class LaneGrid:
    """
    Six-cell grid: 3 equal columns × 2 equal rows on one camera view.

    Boundaries update if the video resolution changes (e.g. first frame).
    """

    def __init__(self, frame_width: int, frame_height: int):
        self.width = frame_width
        self.height = frame_height
        self.boundary_x1 = frame_width // 3
        self.boundary_x2 = 2 * frame_width // 3
        self.boundary_y = frame_height // 2

    def update_size(self, frame_width: int, frame_height: int) -> None:
        """Recompute boundaries if frame size changes (webcam)."""
        if frame_width != self.width or frame_height != self.height:
            self.width = frame_width
            self.height = frame_height
            self.boundary_x1 = frame_width // 3
            self.boundary_x2 = 2 * frame_width // 3
            self.boundary_y = frame_height // 2

    def _column_index(self, x: int) -> int:
        if x < self.boundary_x1:
            return 0
        if x < self.boundary_x2:
            return 1
        return 2

    def cell_for_point(self, x: int, y: int) -> str:
        """Return cell label (A–C top row, 1–3 bottom row) for a pixel position."""
        col = self._column_index(x)
        if y < self.boundary_y:
            return ROW_TOP[col]
        return ROW_BOTTOM[col]

    def assign_lanes(self, swimmers: List[Swimmer]) -> None:
        """Set grid_cell on each swimmer from their center point."""
        for swimmer in swimmers:
            cx, cy = swimmer.center
            swimmer.grid_cell = self.cell_for_point(cx, cy)

    def draw(self, frame) -> None:
        """Draw grid lines and cell labels on the frame."""
        if not config.SHOW_GRID:
            return

        h, w = frame.shape[:2]
        self.update_size(w, h)

        color = config.GRID_COLOR
        thickness = config.GRID_LINE_THICKNESS

        # Vertical dividers (full height).
        cv2.line(frame, (self.boundary_x1, 0), (self.boundary_x1, h), color, thickness)
        cv2.line(frame, (self.boundary_x2, 0), (self.boundary_x2, h), color, thickness)

        # Horizontal divider (middle row split).
        cv2.line(frame, (0, self.boundary_y), (w, self.boundary_y), color, thickness)

        # Label each cell at its center.
        col_centers = (w // 6, w // 2, 5 * w // 6)
        row_centers = (h // 4, 3 * h // 4)
        cell_labels = [
            (ROW_TOP, row_centers[0]),
            (ROW_BOTTOM, row_centers[1]),
        ]
        for labels, y_center in cell_labels:
            for label, x_center in zip(labels, col_centers):
                text_size = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, config.GRID_LABEL_SCALE, 2
                )[0]
                x = x_center - text_size[0] // 2
                y = y_center + text_size[1] // 2
                cv2.putText(
                    frame,
                    label,
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    config.GRID_LABEL_SCALE,
                    color,
                    2,
                )


def map_external_lane(side_camera_cell: str, camera_side: str) -> str:
    """
    FUTURE: map a side camera's cell to the main camera grid.

    Not used in the demo. Implement mapping tables when side cameras are added.
    """
    _ = (side_camera_cell, camera_side)
    return "B"
