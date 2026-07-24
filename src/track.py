"""
C.O.A.S.T. — M2 + M4: track people and flag possible distress.

Runs tracking (stable IDs) plus distress rules (stationary / submersion).

USAGE (from project root, venv active):

    python src/track.py --source data/videos/single_swimmer.mp4
    python src/track.py --source data/videos/single_swimmer.mp4 --no-window
"""

import argparse
import os
import sys

import cv2
from ultralytics import YOLO

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from distress import DistressMonitor
from tracker import draw_swimmer, track_frame, update_trails


def parse_args():
    parser = argparse.ArgumentParser(
        description="C.O.A.S.T. tracking + distress (M2 + M4)"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a video file, or '0' for the default webcam.",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="Do not open a live preview window.",
    )
    return parser.parse_args()


def open_source(source):
    if source.isdigit():
        cap = cv2.VideoCapture(int(source))
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


def make_writer(cap, source):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    base = "webcam" if source.isdigit() else os.path.splitext(os.path.basename(source))[0]
    out_path = os.path.join(config.OUTPUT_DIR, f"{base}_distress.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    return writer, out_path, fps


def draw_hud(frame, swimmers, submerged_stubs, frame_index):
    """Top-of-screen summary: counts and any active distress labels."""
    warnings = sum(
        1 for s in swimmers if s.is_distress and s.severity == "warning"
    )
    alerts = len(submerged_stubs) + sum(
        1 for s in swimmers if s.is_distress and s.severity == "alert"
    )
    active_ids = sorted({s.id for s in swimmers})

    cv2.putText(
        frame,
        f"Frame {frame_index}  Tracked: {len(swimmers)}  IDs: {active_ids}",
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
        cv2.putText(
            frame,
            f"ALERT: ID {stub.id} submersion (last seen here)",
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            config.DISTRESS_COLOR,
            2,
        )
        y += 22


def main():
    args = parse_args()
    show_window = config.SHOW_WINDOW and not args.no_window

    print(f"[INFO] Loading model: {config.MODEL_NAME} ...")
    print(f"[INFO] Tracker: {config.TRACKER_CONFIG}")
    print(
        f"[INFO] Distress: stationary={config.STATIONARY_SECONDS}s, "
        f"submersion={config.SUBMERSION_SECONDS}s"
    )
    model = YOLO(config.MODEL_NAME)

    cap = open_source(args.source)

    writer, out_path, fps = (None, None, 25.0)
    if config.SAVE_OUTPUT:
        writer, out_path, fps = make_writer(cap, args.source)

    distress_monitor = DistressMonitor(fps=fps)
    trail_history = {}

    print("[INFO] Processing... press 'q' in the window to quit early.")
    print("[INFO] Orange box = STATIONARY  |  Red box = SUBMERGED / ALERT")
    frame_count = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_count += 1

        # M2: detect + stable IDs
        _, swimmers = track_frame(model, frame, persist=True)
        update_trails(swimmers, trail_history)

        # M4: apply distress rules (mutates swimmers + returns submersion stubs)
        submerged_stubs = distress_monitor.process(swimmers, frame_count)

        for swimmer in swimmers:
            draw_swimmer(frame, swimmer)
        for stub in submerged_stubs:
            draw_swimmer(frame, stub)

        draw_hud(frame, swimmers, submerged_stubs, frame_count)

        if writer is not None:
            writer.write(frame)

        if show_window:
            cv2.imshow("C.O.A.S.T. - tracking + distress (M2+M4)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if writer is not None:
        writer.release()
        print(f"[INFO] Saved video -> {out_path}")
    cv2.destroyAllWindows()
    print(f"[INFO] Done. Processed {frame_count} frames.")


if __name__ == "__main__":
    main()
