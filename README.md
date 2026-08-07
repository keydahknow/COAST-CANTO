# C.O.A.S.T. — Coastal Observation & Analytic Sensing Technology

AI camera monitoring that detects swimmers in distress and alerts lifeguards.
Prototype for the **CANTO Innovation Challenge 2026** — *Climate & Disaster Resilience* track.

**Team: The Buoyz** — Asia Cooper · Imani Zakuri · Samuel Blache · Keedanu Halls

> This is a **prototype / proof-of-concept**. It **assists, not replaces** trained lifeguards.

---

## What it does

C.O.A.S.T. runs a full video pipeline on beach or pool footage:

1. **Detect & track** swimmers with stable IDs (YOLOv8 + ByteTrack)
2. **Locate** each swimmer on a **6-cell grid** (A B C top row, 1 2 3 bottom row)
3. **Flag distress** — stationary too long (orange warning) or vanished from view (red alert)
4. **Alert** — on-screen banner, console log, optional **Discord** webhook

Distress logic includes an **ID-swap guard** to reduce false submersion alerts when the tracker reassigns IDs.

---

## Quick start

### Option A — Command line (best for demo video export)

```powershell
python src/coast.py --source data/videos/demo.mp4 --no-window
```

Output: `output/demo_coast.mp4` (annotated video for judges).

### Option B — Dashboard (upload, webcam, live settings)

```powershell
streamlit run app.py
```

Opens a local browser UI at `http://localhost:8501` with:

- COAST overview and description
- **Upload video** — process a file, preview frames, download annotated output
- **Webcam (live)** — run the pipeline on your camera with sidebar tuning
- **Configuration sidebar** — change model, confidence, distress thresholds, grid, and alerts without editing code

**Close the dashboard:** press `Ctrl+C` in the terminal where Streamlit is running.

> **Webcam note:** Live mode runs full YOLO inference on every frame, so it can feel slow on CPU. For smoother preview, use `yolov8n.pt` and image size `640` in the sidebar. Uploaded video is recommended for the competition demo.

---

## Project layout

```
CANTO/
├── app.py             # Streamlit dashboard (M6 UI)
├── .streamlit/        # Streamlit config
├── src/
│   ├── coast.py       # official CLI demo entry point
│   ├── pipeline.py    # full pipeline orchestrator
│   ├── detect.py      # M1 only (detection, no tracking)
│   ├── track.py       # legacy alias → use coast.py
│   ├── tracker.py     # M2 tracking + Swimmer objects
│   ├── grid.py        # M3 six-cell grid overlay + zone assignment
│   ├── distress.py    # M4 distress rules + ID-swap guard
│   ├── alerts.py      # M5 on-screen banner + Discord alerts
│   ├── settings.py    # runtime config overrides (dashboard)
│   └── config.py      # default tunable settings
├── models/            # optional custom .pt weights (not in git)
├── data/videos/       # test clips (not in git)
├── output/            # annotated videos (not in git)
├── notebooks/         # optional YOLO fine-tuning (Google Colab)
├── .env.example       # Discord webhook template
└── requirements.txt
```

---

## Setup (each teammate, once)

**Requires Python 3.12** (not 3.13/3.14 — avoids package build issues on Windows).

```powershell
git clone https://github.com/keydahknow/COAST-CANTO.git
cd COAST-CANTO
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy secrets for Discord (optional):

```powershell
copy .env.example .env
# Edit .env and paste your DISCORD_WEBHOOK_URL
```

---

## Run commands

```powershell
# Full pipeline — export annotated demo video (recommended for judges):
python src/coast.py --source data/videos/demo.mp4 --no-window

# Full pipeline — live OpenCV window (press q to quit):
python src/coast.py --source data/videos/demo.mp4

# Webcam via CLI:
python src/coast.py --source 0

# Dashboard (browser UI):
streamlit run app.py

# M1 only — detection baseline, no tracking/distress:
python src/detect.py --source data/videos/demo.mp4
```

---

## Grid (M3)

The main camera view is split into **6 equal zones**:

```
┌───────┬───────┬───────┐
│   A   │   B   │   C   │  ← top half (near / upper frame)
├───────┼───────┼───────┤
│   1   │   2   │   3   │  ← bottom half (far / lower frame)
└───────┴───────┴───────┘
```

Each swimmer is mapped to a zone from their bounding-box centre. Alerts include the zone, e.g. `Zone: B`.

*Future expansion (proposal): side cameras with their own grids, cross-referenced to the main camera view.*

---

## Configuration

### Edit defaults — `src/config.py`

| Setting | Default | Purpose |
|---------|---------|---------|
| `MODEL_NAME` | `yolov8s.pt` | YOLO weights (`yolov8n` = faster, `yolov8m` = more accurate) |
| `CONFIDENCE_THRESHOLD` | `0.15` | Detection sensitivity |
| `IMAGE_SIZE` | `1280` | Input resolution (higher = slower, better on distant swimmers) |
| `STATIONARY_SECONDS` | `15.0` | Seconds barely moving → orange warning |
| `SUBMERSION_SECONDS` | `2.0` | Seconds missing from view → red alert |
| `SHOW_GRID` | `True` | Draw 6-cell overlay |
| `SHOW_ALERT_BANNER` | `True` | Bottom alert bar on distress |
| `ENABLE_DISCORD` | `True` | Send webhook alerts |

Custom models: place a `.pt` file in `models/` and set `MODEL_NAME = "models/your_model.pt"`.

### Tune in the dashboard — sidebar sliders

The Streamlit app applies settings at run time via `src/settings.py`. Webcam mode can sync distress thresholds on each frame. Changing the model requires starting a new run.

---

## Discord alerts (optional, free)

1. Discord channel → Integrations → Webhooks → New Webhook → copy URL
2. Paste into `.env`:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```
3. Run `coast.py` or the dashboard with **Send Discord alerts** enabled

Test webhook (PowerShell):

```powershell
Invoke-RestMethod -Uri "YOUR_WEBHOOK_URL" -Method Post -ContentType "application/json" -Body '{"content":"C.O.A.S.T. test OK"}'
```

---

## Milestone status

- [x] **M1 — Detection** (`detect.py`)
- [x] **M2 — Tracking** (`tracker.py`, ByteTrack)
- [x] **M3 — Grid & zones** (`grid.py` — 6 cells: A B C / 1 2 3)
- [x] **M4 — Distress logic** (`distress.py`, ID-swap guard)
- [x] **M5 — Alerting** (`alerts.py`, on-screen + Discord)
- [x] **M6 — Demo entry point** (`coast.py`)
- [x] **M6 — Streamlit dashboard** (`app.py`)
- [ ] **Fine-tuning** (optional custom model via Colab notebook)

*Hardware deployment (proposal vision): solar buoys, Raspberry Pi, LoRaWAN, smartwatch + lifeguard dashboard — not fully built in this software prototype.*

---

## Git workflow

```powershell
git checkout main
git pull
git checkout -b feature/your-task
# ... work ...
git add .
git commit -m "Describe change"
git push -u origin feature/your-task
```

Open a Pull Request on GitHub. Never commit `.env`, `.venv/`, videos, or `*.pt` weights.

---

## Demo checklist (competition)

- [ ] Best test clip in `data/videos/` (fixed camera, 1 swimmer, clear distress scenario)
- [ ] Run `coast.py --no-window` → check `output/*_coast.mp4`
- [ ] Or run `streamlit run app.py` → upload clip → download annotated output
- [ ] Discord `#coast-alerts` channel open during presentation
- [ ] Slides explain: assists lifeguards, 6-zone grid, surface-based detection, future hardware
- [ ] Record screen capture as backup if live demo fails

---

## Known limitations

- Generic YOLO can miss partial submersion or distant swimmers in water
- Moving-camera footage may leave alert markers at stale pixel positions — use fixed-camera clips
- CPU inference is slow for live webcam; prefer pre-recorded video for demos
- On-screen text uses ASCII only (OpenCV `putText` does not render em dashes or emoji)
