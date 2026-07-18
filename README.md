# C.O.A.S.T. — Coastal Observation & Analytic Sensing Technology

AI camera monitoring that detects swimmers in distress and alerts lifeguards to their location.
Prototype for the **CANTO Innovation Challenge 2026** — *Climate & Disaster Resilience* track.

**Team: The Buoyz** — Asia Cooper · Imani Zakuri · Samuel Blache · Keedanu Halls

> ⚠️ This is a research **prototype / proof-of-concept**. It is designed to **assist, not replace**
> trained lifeguards. It must not be relied on as a sole means of drowning prevention.

---

## What it does right now

- Runs a pretrained **YOLO** model on a **video file** (or webcam) using **OpenCV**.
- Draws a box around every detected person and shows a live count.
- Optionally saves an annotated video to `output/`.

This is milestone 1 ("it sees people"). Distress detection and alerting come next — see the roadmap below.

---

## Project layout

```
CANTO/
├── src/
│   ├── detect.py      # main script — run YOLO on a video
│   └── config.py      # all tunable settings live here
├── data/
│   └── videos/        # put test videos here (NOT committed to git)
├── output/            # annotated videos land here (NOT committed to git)
├── requirements.txt   # Python dependencies (pinned versions)
├── .gitignore         # keeps big/secret files out of git
├── LICENSE
└── README.md
```

---

## Setup (every teammate does this once)

You need **Python 3.10 or newer**. Check with `python --version`.

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd CANTO
```

### 2. Create a virtual environment (keeps dependencies isolated)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If PowerShell blocks activation, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You'll know it worked when your prompt starts with `(.venv)`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This pulls in YOLO (ultralytics), OpenCV, and PyTorch. First install is a few hundred MB and may take a few minutes — that's normal.

---

## Running it

1. Put a test video in `data/videos/` (e.g. `test.mp4`). A pool or beach clip filmed from above works best.
2. With your virtual environment active, run:

```bash
python src/detect.py --source data/videos/test.mp4
```

The first run downloads the YOLO model (`yolov8n.pt`, ~6 MB) automatically. Press **`q`** to quit the preview window.

**Other options:**

```bash
python src/detect.py --source 0                       # use the webcam
python src/detect.py --source data/videos/test.mp4 --no-window   # no preview, just save output
```

Change detection sensitivity, output settings, etc. in `src/config.py`.

---

## Where to get test videos

- **Film your own** (best): a friend swimming normally vs. gently "struggling" in a shallow, supervised pool.
- **YouTube**: search "pool swimmers overhead", "beach swimmers drone". Use a downloader like `yt-dlp`.
- Keep videos **out of git** — share them via Google Drive / WhatsApp. Git is for code, not media.

---

## Team git workflow (keep it simple)

1. **Pull before you start:** `git pull`
2. **Work on a branch**, not directly on `main`:
   ```bash
   git checkout -b feature/tracking      # e.g. Samuel adds tracking
   ```
3. **Commit small, clear changes:**
   ```bash
   git add .
   git commit -m "Add grid overlay to detection"
   ```
4. **Push and open a Pull Request** on GitHub so a teammate can review before merging.

**Golden rules for this repo:**
- Never commit the `.venv/` folder, model weights (`*.pt`), or videos — `.gitignore` handles this for you.
- Never commit API keys/tokens (Telegram, Twilio). Those go in a `.env` file (already git-ignored).
- If someone edits `requirements.txt`, everyone else re-runs `pip install -r requirements.txt`.

---

## Roadmap

- [x] **M1 — Detection:** find people in a video (YOLO + OpenCV).
- [ ] **M2 — Tracking:** stable ID per swimmer across frames.
- [ ] **M3 — Grid & zones:** overlay a location grid; report which cell a person is in.
- [ ] **M4 — Distress logic:** flag prolonged submersion, near-stationary swimmers, danger-zone entry.
- [ ] **M5 — Alerting:** on-screen alarm + highlighted zone, then a Telegram alert to a phone.
- [ ] **M6 — Demo polish:** dashboard + recorded demo video for judges.

*Deployment vision (from the proposal, not built in the prototype): solar buoys, Raspberry Pi edge units, LoRaWAN, smartwatch alerts.*
