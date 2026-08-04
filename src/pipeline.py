"""
C.O.A.S.T. pipeline — full prototype in one pass.

M2 tracking → M3 grid lanes → M4 distress → M5 alerts (on-screen + Discord).
"""

import os
import sys

import cv2
from ultralytics import YOLO

import config
from alerts import AlertManager
from distress import DistressMonitor
from grid import LaneGrid
from tracker import draw_swimmer, track_frame, update_trails


def open_source(source: str):
    if source.isdigit():
        cap = cv2.VideoCapture(int(source))
    elif source.startswith(("rtsp://", "http://", "https://")):
        cap = cv2.VideoCapture(source)
    else:
        if not os.path.exists(source):
            sys.exit(
                f"[ERROR] Video not found: {source}\n"
                f"        Put a video in data/videos/ and pass its path."
            )
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        sys.exit(f"[ERROR] Could not open source: {source}")
    return cap


def make_writer(cap, source: str):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    base = "webcam" if source.isdigit() else os.path.splitext(os.path.basename(source))[0]
    out_path = os.path.join(config.OUTPUT_DIR, f"{base}_coast.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    return writer, out_path, fps


def draw_hud(frame, swimmers, submerged_stubs, frame_index):
    warnings = sum(
        1 for s in swimmers if s.is_distress and s.severity == "warning"
    )
    alerts = len(submerged_stubs) + sum(
        1 for s in swimmers if s.is_distress and s.severity == "alert"
    )
    active_ids = sorted({s.id for s in swimmers})

    cv2.putText(
        frame,
        f"C.O.A.S.T.  |  Frame {frame_index}  |  IDs: {active_ids}",
        (12, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        f"Warnings: {warnings}  Alerts: {alerts}",
        (12, 52),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 255),
        2,
    )

    y = 76
    for stub in submerged_stubs:
        lane = stub.grid_cell or "unknown"
        cv2.putText(
            frame,
            f"ALERT: ID {stub.id} submersion — Lane {lane}",
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            config.DISTRESS_COLOR,
            2,
        )
        y += 22


def run(source: str, no_window: bool = False) -> str | None:
    """
    Run the full C.O.A.S.T. pipeline on a video file, webcam index, or RTSP URL.

    Returns the output video path, or None if SAVE_OUTPUT is False.
    """
    show_window = config.SHOW_WINDOW and not no_window

    print("=" * 56)
    print("  C.O.A.S.T. — Coastal Observation & Analytic Sensing Technology")
    print("=" * 56)
    print(f"[INFO] Source: {source}")
    print(f"[INFO] Model: {config.MODEL_NAME}")
    print(f"[INFO] Tracker: {config.TRACKER_CONFIG}")
    print(
        f"[INFO] Distress: stationary={config.STATIONARY_SECONDS}s, "
        f"submersion={config.SUBMERSION_SECONDS}s"
    )
    print(
        f"[INFO] Alerts: Discord={'on' if config.ENABLE_DISCORD else 'off'}, "
        f"banner={'on' if config.SHOW_ALERT_BANNER else 'off'}"
    )
    print(f"[INFO] Grid: 3 lanes (Left | Center | Right), show={config.SHOW_GRID}")

    model = YOLO(config.MODEL_NAME)
    cap = open_source(source)

    writer, out_path, fps = (None, None, 25.0)
    if config.SAVE_OUTPUT:
        writer, out_path, fps = make_writer(cap, source)

    distress_monitor = DistressMonitor(fps=fps)
    alert_manager = AlertManager(fps=fps)
    trail_history = {}
    lane_grid: LaneGrid | None = None

    print("[INFO] Running pipeline... press 'q' in the preview window to quit.")
    print("[INFO] Orange = STATIONARY  |  Red = SUBMERGED  |  Banner = alert")
    frame_count = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_count += 1

        h, w = frame.shape[:2]
        if lane_grid is None:
            lane_grid = LaneGrid(w, h)
        else:
            lane_grid.update_size(w, h)

        _, swimmers = track_frame(model, frame, persist=True)
        update_trails(swimmers, trail_history)

        # M3: assign lane before distress so alerts include Left/Center/Right.
        lane_grid.assign_lanes(swimmers)

        submerged_stubs = distress_monitor.process(swimmers, frame_count)
        lane_grid.assign_lanes(submerged_stubs)

        alert_manager.handle_frame(frame, swimmers, submerged_stubs, frame_count)

        lane_grid.draw(frame)
        for swimmer in swimmers:
            draw_swimmer(frame, swimmer)
        for stub in submerged_stubs:
            draw_swimmer(frame, stub)
        draw_hud(frame, swimmers, submerged_stubs, frame_count)

        if writer is not None:
            writer.write(frame)

        if show_window:
            cv2.imshow("C.O.A.S.T.", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if writer is not None:
        writer.release()
        print(f"[INFO] Saved demo video -> {out_path}")
    cv2.destroyAllWindows()
    print(f"[INFO] Done. Processed {frame_count} frames.")
    return out_path
