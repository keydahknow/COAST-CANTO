"""
Central settings for C.O.A.S.T.
Keep tunable values here so teammates change behavior in ONE place
instead of hunting through the code.
"""

# --- Model ---
# "yolov8n.pt" = nano = smallest/fastest, best for CPU laptops.
# Ultralytics downloads it automatically on first run.
# Step up to "yolov8s.pt" (small) later if the laptop can handle it.
MODEL_NAME = "yolov8n.pt"

# Only care about the "person" class (COCO class id 0).
PERSON_CLASS_ID = 0

# Ignore weak detections. Raise to reduce false boxes, lower to catch more.
CONFIDENCE_THRESHOLD = 0.35

# --- Display / output ---
# Show a live window while processing. Set False if running headless.
SHOW_WINDOW = True

# Save an annotated copy of the video to the output/ folder.
SAVE_OUTPUT = True
OUTPUT_DIR = "output"

# Box + text colors (Blue, Green, Red — OpenCV uses BGR, not RGB).
BOX_COLOR = (0, 200, 0)
TEXT_COLOR = (255, 255, 255)
