"""
Central settings for C.O.A.S.T. (ADDING IAMNI TEST)
Keep tunable values here so teammates change behavior in ONE place
instead of hunting through the code. (ADDING KEEDANU TEST)
"""

# --- Model ---
# Bigger model = more accurate but slower on CPU. Pick based on your scene:
#   "yolov8n.pt"  nano   - fastest, weakest (misses small/distant swimmers)
#   "yolov8s.pt"  small  - good balance (recommended starting point)
#   "yolov8m.pt"  medium - noticeably better in crowds, slower on CPU
# Ultralytics downloads whichever you choose automatically on first run.
MODEL_NAME = "yolov8s.pt"

# Only care about the "person" class (COCO class id 0).
PERSON_CLASS_ID = 0

# Ignore weak detections. Raise to reduce false boxes, lower to catch more.
# Swimmers in water are hard to see, so we keep this fairly low.
CONFIDENCE_THRESHOLD = 0.15

# Resolution the model analyzes at (input is resized to this before detection).
# BIGGEST lever for spotting small/distant swimmers: higher = more small people
# detected, but slower on CPU. Try 1280 for wide/crowded shots, 640 for speed.
IMAGE_SIZE = 1280

# --- Tracking (M2) ---
# ByteTrack is a common, fast tracker bundled with Ultralytics.
TRACKER_CONFIG = "bytetrack.yaml"
# Draw a short line showing where each ID has moved recently.
SHOW_TRAIL = True
TRAIL_LENGTH = 30  # how many past positions to keep per ID

# --- Distress (M4) ---
# How long (seconds) before we flag someone. Higher = fewer false alarms.
STATIONARY_SECONDS = 8.0       # visible but barely moving → orange WARNING
STATIONARY_PIXELS = 30         # total movement in that window (pixels)
SUBMERSION_SECONDS = 3.0       # vanished from view → red ALERT
SUBMERSION_MIN_VISIBLE_SECONDS = 1.0  # must be tracked this long first
DISTRESS_COLOR = (0, 0, 255)   # red (BGR)
WARNING_COLOR = (0, 165, 255)  # orange (BGR)


# --- Display / output ---
# Show a live window while processing. Set False if running headless.
SHOW_WINDOW = True

# Save an annotated copy of the video to the output/ folder.
SAVE_OUTPUT = True
OUTPUT_DIR = "output"

# Box + text colors (Blue, Green, Red — OpenCV uses BGR, not RGB).
BOX_COLOR = (0, 200, 0)
TEXT_COLOR = (255, 255, 255)
