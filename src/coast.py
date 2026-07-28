"""
C.O.A.S.T. — Official demo entry point.

Runs the full prototype: track swimmers, detect distress, send alerts.

USAGE (from project root, venv active):

    python src/coast.py --source data/videos/demo.mp4
    python src/coast.py --source data/videos/demo.mp4 --no-window
    python src/coast.py --source 0
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline import run


def parse_args():
    parser = argparse.ArgumentParser(
        description="C.O.A.S.T. — AI lifeguard assistance prototype (demo)"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Video path, webcam index (0), or RTSP URL.",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="Skip live preview (faster; use for demo video export).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run(source=args.source, no_window=args.no_window)


if __name__ == "__main__":
    main()
