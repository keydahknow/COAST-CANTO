"""
Legacy alias — use coast.py for demos.

    python src/coast.py --source data/videos/demo.mp4
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline import run


def parse_args():
    parser = argparse.ArgumentParser(description="C.O.A.S.T. (use coast.py instead)")
    parser.add_argument("--source", required=True)
    parser.add_argument("--no-window", action="store_true")
    return parser.parse_args()


def main():
    print("[NOTE] track.py is a legacy alias. Prefer: python src/coast.py ...")
    args = parse_args()
    run(source=args.source, no_window=args.no_window)


if __name__ == "__main__":
    main()
