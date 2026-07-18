"""
C.O.A.S.T. — Win #1: detect people in a video file.

This is the foundation. It runs a pretrained YOLO model on a video,
draws a box around every person, and (optionally) shows a live window
and saves an annotated video to output/.

No training required — YOLO already knows what a "person" looks like.
Later milestones add: tracking (stable IDs), a grid overlay,
distress heuristics, and alerts.

USAGE (from the project root, with your virtual environment active):

    python src/detect.py --source data/videos/test.mp4

    # use your webcam instead of a file:
    python src/detect.py --source 0

    # quieter run (no live window, just save output):
    python src/detect.py --source data/videos/test.mp4 --no-window
"""

import argparse
import os
import sys

import cv2
from ultralytics import YOLO

# Allow running as "python src/detect.py" by making local imports work.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config


def parse_args():
    parser = argparse.ArgumentParser(description="C.O.A.S.T. person detection")
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
    """Return a cv2.VideoCapture. '0' (etc.) is treated as a webcam index."""
    if source.isdigit():
        cap = cv2.VideoCapture(int(source))
    else:
        if not os.path.exists(source):
            sys.exit(f"[ERROR] Video not found: {source}\n"
                     f"        Put a video in data/videos/ and pass its path.")
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        sys.exit(f"[ERROR] Could not open source: {source}")
    return cap


def make_writer(cap, source):
    """Create a VideoWriter that mirrors the input's size and FPS."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0  # webcams sometimes report 0

    base = "webcam" if source.isdigit() else os.path.splitext(os.path.basename(source))[0]
    out_path = os.path.join(config.OUTPUT_DIR, f"{base}_annotated.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    return writer, out_path


def draw_person(frame, box, conf):
    x1, y1, x2, y2 = (int(v) for v in box)
    cv2.rectangle(frame, (x1, y1), (x2, y2), config.BOX_COLOR, 2)
    label = f"person {conf:.2f}"
    cv2.putText(frame, label, (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.TEXT_COLOR, 2)


def main():
    args = parse_args()
    show_window = config.SHOW_WINDOW and not args.no_window

    print(f"[INFO] Loading model: {config.MODEL_NAME} (downloads on first run)...")
    model = YOLO(config.MODEL_NAME)

    cap = open_source(args.source)

    writer, out_path = (None, None)
    if config.SAVE_OUTPUT:
        writer, out_path = make_writer(cap, args.source)

    print("[INFO] Processing... press 'q' in the window to quit early.")
    frame_count = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_count += 1

        # Run YOLO on this frame. We only ask for the 'person' class.
        results = model(
            frame,
            classes=[config.PERSON_CLASS_ID],
            conf=config.CONFIDENCE_THRESHOLD,
            verbose=False,
        )

        people = 0
        for box in results[0].boxes:
            people += 1
            draw_person(frame, box.xyxy[0], float(box.conf[0]))

        cv2.putText(frame, f"People detected: {people}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if writer is not None:
            writer.write(frame)

        if show_window:
            cv2.imshow("C.O.A.S.T. - person detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if writer is not None:
        writer.release()
        print(f"[INFO] Saved annotated video -> {out_path}")
    cv2.destroyAllWindows()
    print(f"[INFO] Done. Processed {frame_count} frames.")


if __name__ == "__main__":
    main()
