"""
C.O.A.S.T. — M2: track people in a video with stable IDs.

Same idea as detect.py, but uses model.track() so each swimmer keeps
the same number as they move (ID 1, ID 2, ...).

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
from tracker import draw_swimmer, track_frame, update_trails


def parse_args():
    parser = argparse.ArgumentParser(description="C.O.A.S.T. person tracking (M2)")
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
    out_path = os.path.join(config.OUTPUT_DIR, f"{base}_tracked.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    return writer, out_path


def main():
    args = parse_args()
    show_window = config.SHOW_WINDOW and not args.no_window

    print(f"[INFO] Loading model: {config.MODEL_NAME} ...")
    print(f"[INFO] Tracker: {config.TRACKER_CONFIG}")
    model = YOLO(config.MODEL_NAME)

    cap = open_source(args.source)

    writer, out_path = (None, None)
    if config.SAVE_OUTPUT:
        writer, out_path = make_writer(cap, args.source)

    # Remember past center points per track ID (for the colored trail).
    trail_history = {}

    print("[INFO] Tracking... press 'q' in the window to quit early.")
    print("[INFO] Look for 'ID 1', 'ID 2' labels — same person = same ID.")
    frame_count = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_count += 1

        # --- M2 core: detect + assign stable IDs ---
        _, swimmers = track_frame(model, frame, persist=True)
        update_trails(swimmers, trail_history)

        for swimmer in swimmers:
            draw_swimmer(frame, swimmer)

        active_ids = sorted({s.id for s in swimmers})
        cv2.putText(
            frame,
            f"Tracked: {len(swimmers)}  IDs: {active_ids}",
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        if writer is not None:
            writer.write(frame)

        if show_window:
            cv2.imshow("C.O.A.S.T. - tracking (M2)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if writer is not None:
        writer.release()
        print(f"[INFO] Saved tracked video -> {out_path}")
    cv2.destroyAllWindows()
    print(f"[INFO] Done. Processed {frame_count} frames.")


if __name__ == "__main__":
    main()
