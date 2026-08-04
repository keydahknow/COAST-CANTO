# C.O.A.S.T. — Coastal Observation & Analytic Sensing Technology

AI camera monitoring that detects swimmers in distress and alerts lifeguards.
Prototype for the **CANTO Innovation Challenge 2026** — *Climate & Disaster Resilience* track.

**Team: The Buoyz** — Asia Cooper · Imani Zakuri · Samuel Blache · Keedanu Halls

> This is a **prototype / proof-of-concept**. It **assists, not replaces** trained lifeguards.

---

## What it does (demo)

One command runs the full pipeline:

1. **Detect & track** swimmers with stable IDs (YOLO + ByteTrack)
2. **Flag distress** — stationary too long, or vanished from surface (submersion)
3. **Alert** — on-screen banner + optional **Discord** message

```powershell
python src/coast.py --source data/videos/demo.mp4 --no-window
```

Output: `output/demo_coast.mp4` (annotated demo video for judges).

---

## Project layout

```
CANTO/
├── src/
│   ├── coast.py       # ★ official demo entry point
│   ├── pipeline.py    # full M2 + M4 + M5 pipeline
│   ├── detect.py      # M1 only (person detection, no tracking)
│   ├── track.py       # legacy alias → use coast.py
│   ├── tracker.py     # M2 tracking + Swimmer objects
│   ├── distress.py    # M4 distress rules
│   ├── alerts.py      # M5 on-screen + Discord alerts
│   └── config.py      # all tunable settings
├── data/videos/       # test clips (not in git)
├── output/            # demo videos (not in git)
├── notebooks/         # optional YOLO training (Google Colab)
├── .env.example       # Discord webhook template
└── requirements.txt
```

---

## Setup (each teammate, once)

**Requires Python 3.12** (not 3.13/3.14 — avoids package build issues).

```powershell
git clone https://github.com/keydahknow/COAST-CANTO.git
cd COAST-CANTO
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Run the demo

```powershell
# Best for export (no slow live window):
python src/coast.py --source data/videos/demo.mp4 --no-window

# Webcam live demo:
python src/coast.py --source 0

# M1 only (detection, no tracking/distress):
python src/detect.py --source data/videos/demo.mp4
```

Tune settings in `src/config.py` (model, thresholds, alert cooldown).

---

## Discord alerts (optional, free)

1. Discord channel → Integrations → Webhooks → New Webhook → copy URL
2. `copy .env.example .env` and paste URL:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```
3. Re-run `coast.py` — messages appear in channel when distress triggers

Test webhook (PowerShell):

```powershell
Invoke-RestMethod -Uri "YOUR_WEBHOOK_URL" -Method Post -ContentType "application/json" -Body '{"content":"C.O.A.S.T. test OK"}'
```

---

## Milestone status

- [x] **M1 — Detection** (`detect.py`)
- [x] **M2 — Tracking** (`tracker.py`)
- [x] **M3 — Grid & lanes** (`grid.py` — Left | Center | Right on main camera)
- [x] **M4 — Distress logic** (`distress.py`)
- [x] **M5 — Alerting** (`alerts.py`, Discord)
- [x] **M6 — Demo entry point** (`coast.py`)
- [ ] **M6 — Streamlit dashboard** (optional polish)
- [ ] **Fine-tuning** (thresholds + optional custom model via Colab notebook)

*Hardware deployment (proposal vision): solar buoys, Raspberry Pi, LoRaWAN, smartwatch — not in this software prototype.*

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

- [ ] Best test clip in `data/videos/` (1 swimmer, clear distress scenario)
- [ ] Run `coast.py --no-window` → check `output/*_coast.mp4`
- [ ] Discord `#coast-alerts` channel open during presentation
- [ ] Slides explain: assists lifeguards, surface-based detection, future grid/hardware
- [ ] Record screen capture as backup if live demo fails
