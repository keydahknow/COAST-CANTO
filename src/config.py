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
# To use a custom / borrowed model, put the .pt file in models/ and set e.g.:
#   MODEL_NAME = "models/their_best.pt"
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

<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream
=======
>>>>>>> Stashed changes
# --- Distress (M4) ---
# How long (seconds) before we flag someone. Higher = fewer false alarms.
STATIONARY_SECONDS = 8.0       # visible but barely moving → orange WARNING
STATIONARY_PIXELS = 30         # total movement in that window (pixels)
SUBMERSION_SECONDS = 3.0       # vanished from view → red ALERT
SUBMERSION_MIN_VISIBLE_SECONDS = 1.0  # must be tracked this long first
<<<<<<< Updated upstream
DISTRESS_COLOR = (0, 0, 255)   # red (BGR)
WARNING_COLOR = (0, 165, 255)  # orange (BGR)
=======
# ID-swap guard: if a new ID appears this close (pixels) soon after another
# vanishes, assume tracker reassignment — do not trigger submersion on old ID.
ID_SWAP_SECONDS = 2.0
ID_SWAP_MAX_PIXELS = 100
DISTRESS_COLOR = (0, 0, 255)   # red (BGR)
WARNING_COLOR = (0, 165, 255)  # orange (BGR)

# --- Alerts (M5) ---
ENABLE_DISCORD = True          # recommended for demo (free webhook)
ENABLE_TELEGRAM = False        # optional; set True if using Telegram bot
DISCORD_BOT_NAME = "C.O.A.S.T. Alert"
SHOW_ALERT_BANNER = True       # big top banner when distress is active
ALERT_COOLDOWN_SECONDS = 15.0  # don't re-send same ID+reason too often
PLAY_ALERT_SOUND = False       # beep on alert (Windows only; annoying on video files)
>>>>>>> Stashed changes
>>>>>>> Stashed changes

# --- Alerts (M5) ---
ENABLE_DISCORD = True          # recommended for demo (free webhook)
ENABLE_TELEGRAM = False        # optional; set True if using Telegram bot
DISCORD_BOT_NAME = "C.O.A.S.T. Alert"
SHOW_ALERT_BANNER = True       # big top banner when distress is active
ALERT_COOLDOWN_SECONDS = 15.0  # don't re-send same ID+reason too often
PLAY_ALERT_SOUND = False       # beep on alert (Windows only; annoying on video files)


# --- Display / output ---
# Show a live window while processing. Set False if running headless.
SHOW_WINDOW = True

# Save an annotated copy of the video to the output/ folder.
SAVE_OUTPUT = True
OUTPUT_DIR = "output"

# Box + text colors (Blue, Green, Red — OpenCV uses BGR, not RGB).
BOX_COLOR = (0, 200, 0)
TEXT_COLOR = (255, 255, 255)
