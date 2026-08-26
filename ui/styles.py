"""Shared CSS, logos, and navigation helpers for the Streamlit UI."""

from __future__ import annotations

import streamlit as st

NAVY = "#1A2138"
BLUE = "#0085FF"
HOW_BLUE = "#2B7DE9"
GREEN = "#70AD47"
LIME = "#84CC16"
RED = "#E02424"
LIGHT_BG = "#F5F6F8"

LOGO_SVG_LIGHT = """
<svg viewBox="0 0 280 72" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="COAST">
  <defs>
    <linearGradient id="cg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2F80ED"/>
      <stop offset="100%" stop-color="#1A2138"/>
    </linearGradient>
  </defs>
  <text x="8" y="46" font-family="League Spartan, Arial Black, sans-serif"
        font-size="42" font-weight="800" fill="url(#cg)">COAST</text>
  <path d="M8 54 C 40 40, 70 68, 110 52 S 180 40, 230 58 S 260 50, 272 54"
        fill="none" stroke="#2F80ED" stroke-width="5" stroke-linecap="round"/>
  <path d="M18 62 C 50 50, 90 70, 140 58 S 200 48, 268 62"
        fill="none" stroke="#5CB3FF" stroke-width="3.5" stroke-linecap="round"/>
</svg>
"""

LOGO_SVG_DARK = """
<svg viewBox="0 0 280 72" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="COAST">
  <text x="8" y="46" font-family="League Spartan, Arial Black, sans-serif"
        font-size="42" font-weight="800" fill="#FFFFFF">COAST</text>
  <path d="M8 54 C 40 40, 70 68, 110 52 S 180 40, 230 58 S 260 50, 272 54"
        fill="none" stroke="#0091FF" stroke-width="5" stroke-linecap="round"/>
  <path d="M18 62 C 50 50, 90 70, 140 58 S 200 48, 268 62"
        fill="none" stroke="#5CB3FF" stroke-width="3.5" stroke-linecap="round"/>
</svg>
"""

# Shared display size for the two big League Spartan headlines.
DISPLAY_SIZE = "clamp(3.1rem, 5.2vw, 4.6rem)"

BASE_CSS = f"""
html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, button {{
  font-family: 'Poppins', 'Segoe UI', sans-serif !important;
}}

h1, h2, h3, h4, .league, .hero-title, .env-title, .how-heading {{
  font-family: 'League Spartan', 'Arial Black', 'Arial', sans-serif !important;
  letter-spacing: -0.02em;
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{background: transparent;}}
div[data-testid="stToolbar"] {{display: none;}}
div[data-testid="stDecoration"] {{display: none;}}
.stAppDeployButton {{display: none;}}

.block-container {{
  padding-top: 0.85rem;
  padding-bottom: 2.5rem;
  padding-left: 2.5rem;
  padding-right: 2.5rem;
  max-width: 1240px;
}}
"""

LANDING_CSS = f"""
.stApp {{
  background:
    radial-gradient(circle at 8% 0%, rgba(43,125,233,0.07), transparent 42%),
    radial-gradient(circle at 92% 18%, rgba(112,173,71,0.07), transparent 36%),
    #FFFFFF;
}}

section[data-testid="stSidebar"] {{display: none !important;}}
div[data-testid="collapsedControl"] {{display: none !important;}}

/* First viewport: nav + hero; How it works starts immediately below */
.hero-fold {{
  min-height: 0;
}}
.fold-gap {{
  display: none;
  height: 0;
}}

.logo-wrap svg,
.logo-wrap img {{
  width: 100%;
  max-height: 52px;
  height: auto;
  display: block;
  object-fit: contain;
  object-position: left center;
}}

.nav-anchor {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2.4rem;
  padding: 0 0.95rem;
  border: 1px solid rgba(49, 51, 63, 0.2);
  border-radius: 0.5rem;
  color: #31333f !important;
  text-decoration: none !important;
  font-family: 'Poppins', 'Segoe UI', sans-serif !important;
  font-size: 0.95rem;
  font-weight: 500;
  background: #fff;
}}
.nav-anchor:hover {{
  border-color: #0085FF;
  color: #0085FF !important;
}}

.hero-kicker {{ color: #70AD47; font-weight: 800; }}
.hero-title {{
  font-family: 'League Spartan', 'Arial Black', sans-serif !important;
  font-size: {DISPLAY_SIZE};
  line-height: 1.02;
  font-weight: 800;
  color: #111;
  margin: 1.4rem 0 1rem 0;
}}
.hero-sub {{
  font-family: 'Poppins', 'Segoe UI', sans-serif !important;
  font-size: clamp(1.1rem, 1.55vw, 1.3rem);
  color: #333;
  max-width: 34rem;
  line-height: 1.65;
  margin-bottom: 0;
}}

.hero-mock {{
  margin-top: 0.4rem;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 18px 44px rgba(26,33,56,0.18);
}}
.hero-mock img {{
  width: 100%;
  height: auto;
  display: block;
}}

/* Continuous blue band for How it works + devices */
.blue-band {{
  background: #2B7DE9;
  margin: 1.25rem -2.5rem 0 -2.5rem;
  padding: 2.4rem 2.5rem 3rem;
  scroll-margin-top: 1rem;
}}
.how-heading {{
  font-family: 'League Spartan', 'Arial Black', sans-serif !important;
  color: #fff !important;
  text-align: center;
  font-size: clamp(2.2rem, 3.6vw, 3rem);
  font-weight: 800;
  margin: 0 0 1.8rem 0;
}}
.how-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.4rem;
  margin-bottom: 2rem;
}}
.how-col {{ min-width: 0; }}
.how-img {{
  width: 100%;
  height: auto;
  display: block;
  border-radius: 16px;
  margin-bottom: 0.85rem;
}}
.how-text-box {{
  background: #fff;
  color: #1A2138;
  border-radius: 18px;
  padding: 1.05rem 1.15rem 1.2rem;
  box-shadow: 0 10px 24px rgba(0,0,0,0.12);
  min-height: 118px;
}}
.how-text-box h3 {{
  font-family: 'League Spartan', 'Arial Black', sans-serif !important;
  margin: 0 0 0.35rem 0;
  font-size: 1.45rem;
  letter-spacing: 0.05em;
  color: #111 !important;
}}
.how-text-box p {{
  font-family: 'Poppins', 'Segoe UI', sans-serif !important;
  font-size: 0.98rem;
  color: #333;
  margin: 0;
  line-height: 1.45;
}}
.devices-grid {{
  display: grid;
  grid-template-columns: 1fr 1.35fr;
  gap: 1.5rem;
  align-items: center;
}}
.device-img {{
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}}
.missing-slot {{
  background: rgba(255,255,255,0.12);
  border: 2px dashed rgba(255,255,255,0.45);
  border-radius: 18px;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1.2rem;
  color: #fff;
  font-size: 0.95rem;
}}
.missing-slot code {{
  color: #dbeafe;
  background: rgba(0,0,0,0.2);
  padding: 0.1rem 0.35rem;
  border-radius: 6px;
}}

.env-title {{
  font-family: 'League Spartan', 'Arial Black', sans-serif !important;
  font-size: {DISPLAY_SIZE};
  font-weight: 800;
  line-height: 1.05;
  margin-top: 2.6rem;
  color: #111;
}}

.env-photo {{
  width: 100%;
  height: 128px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 0.85rem;
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}}
.env-photo img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}}

.env-chip {{
  border-radius: 16px;
  overflow: hidden;
  height: 128px;
  display: flex;
  align-items: flex-end;
  padding: 0.85rem 1rem;
  color: white;
  font-weight: 700;
  margin-bottom: 0.85rem;
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}}
.chip-beach {{ background: linear-gradient(120deg, #3aa0c8, #7ad3c7); }}
.chip-falls {{ background: linear-gradient(120deg, #2f6b3a, #8bc34a); }}
.chip-pool {{ background: linear-gradient(120deg, #1d4e89, #4aa3df); }}

.coast-footer {{
  background: #70AD47;
  color: white;
  text-align: center;
  padding: 1.2rem 1rem;
  margin: 2rem -2.5rem -2.5rem -2.5rem;
  font-size: 0.95rem;
  font-family: 'Poppins', 'Segoe UI', sans-serif !important;
}}

.dash-preview {{
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 16px 40px rgba(26,33,56,0.18);
  overflow: hidden;
  border: 1px solid #e6e8ee;
  margin-top: 1rem;
}}
.dash-preview-bar {{
  background: #1A2138;
  color: white;
  padding: 0.55rem 0.8rem;
  font-size: 0.78rem;
  display: flex;
  justify-content: space-between;
}}
.preview-feed {{
  height: 260px;
  background:
    linear-gradient(180deg, rgba(0,0,0,0.15), rgba(0,0,0,0.05)),
    repeating-linear-gradient(90deg, rgba(255,255,255,0.25) 0 2px, transparent 2px 33%),
    repeating-linear-gradient(180deg, rgba(255,255,255,0.2) 0 2px, transparent 2px 50%),
    linear-gradient(180deg, #2f7dcf, #1c5fa8);
  position: relative;
}}
.preview-live {{
  position: absolute; top: 10px; left: 10px;
  background: #E02424; color: white; font-size: 0.7rem;
  padding: 2px 8px; border-radius: 999px; font-weight: 700;
}}

@media (max-width: 900px) {{
  .fold-gap {{ height: 1.5rem; }}
  .hero-title, .env-title {{ font-size: 2.4rem; }}
  .how-grid, .devices-grid {{ grid-template-columns: 1fr; }}
  .blue-band, .coast-footer {{
    margin-left: -1rem;
    margin-right: -1rem;
  }}
}}
"""

DASHBOARD_CSS = """
.stApp { background: #F3F4F6; }

section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="collapsedControl"] {display: none !important;}

.dash-logo-wrap img,
.dash-logo-wrap svg {
  max-height: 38px !important;
  width: auto !important;
  display: block;
  object-fit: contain;
  object-position: left center;
}
.dash-header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}
.back-home-btn button,
button[data-testid="stBaseButton-back_home_btn"] {
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.82rem !important;
  padding: 0.12rem 0.55rem !important;
  min-height: 1.65rem !important;
  width: auto !important;
  max-width: fit-content;
}

.dash-title {
  font-family: 'League Spartan', 'Arial Black', sans-serif !important;
  font-size: 2.15rem;
  font-weight: 800;
  margin-bottom: 0;
}
.dash-sub {
  font-family: 'Poppins', 'Segoe UI', sans-serif !important;
  color: #5b6475;
  margin-top: 0.15rem;
}
.status-online { color: #65a30d; font-weight: 700; }
.alert-pill {
  display: inline-block;
  background: white;
  color: #E02424;
  border: 1px solid #f3b4b4;
  border-radius: 999px;
  padding: 0.28rem 0.85rem;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(224,36,36,0.12);
}
.live-badge {
  display: inline-block;
  background: #E02424;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  margin-right: 0.4rem;
}

.feed-toolbar-wrap {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.35rem;
}
.feed-toolbar-wrap .toolbar-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #5b6475;
  margin-right: 0.15rem;
}
.feed-mode-row [data-testid="column"] {
  padding-left: 0.15rem !important;
  padding-right: 0.15rem !important;
}
.feed-mode-row button {
  min-height: 2.05rem;
  padding: 0.2rem 0.55rem !important;
  font-size: 0.82rem !important;
}
.feed-mode-row div[data-testid="stHorizontalBlock"] {
  gap: 0.25rem !important;
}
.feed-preview-panel {
  background: #0f1419;
  border-radius: 14px;
  min-height: 340px;
  margin-top: 0.75rem;
  padding: 0.65rem;
  box-shadow: 0 10px 28px rgba(26, 33, 56, 0.18);
  overflow: hidden;
}
.feed-preview-panel.is-idle {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9aa3b2;
  font-size: 0.92rem;
  text-align: center;
  padding: 2rem 1rem;
}
.feed-preview-panel img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 10px;
}
.feed-controls-row {
  margin-top: 0.55rem;
  margin-bottom: 0.15rem;
}
.feed-controls-row [data-testid="column"] {
  display: flex;
  align-items: flex-end;
}
.feed-controls-row button {
  width: 100%;
}
.feed-upload-wrap {
  margin-bottom: 0.55rem;
}
[data-testid="stFileUploader"] {
  margin-bottom: 0.65rem !important;
}
[data-testid="stFileUploaderDropzone"] {
  padding: 0.85rem 1rem !important;
  min-height: 4.5rem !important;
}
[data-testid="stFileUploaderDropzone"] > div {
  line-height: 1.45 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 0.35rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
  white-space: normal !important;
  text-align: center !important;
  line-height: 1.35 !important;
}
[data-testid="stFileUploaderFileName"] {
  margin-top: 0.4rem !important;
  line-height: 1.35 !important;
}
.feed-upload-wrap [data-testid="stFileUploader"] {
  margin-bottom: 0;
}
.feed-upload-wrap [data-testid="stFileUploader"] label {
  font-size: 0.9rem !important;
  margin-bottom: 0.35rem !important;
}
.feed-upload-wrap [data-testid="stFileUploaderDropzone"] {
  padding: 0.75rem 1rem !important;
}
.feed-header-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0.75rem 0 0.35rem 0;
}
.feed-preview-slot [data-testid="stImage"] {
  background: #0f1419;
  border-radius: 14px;
  padding: 0.65rem;
  box-shadow: 0 10px 28px rgba(26, 33, 56, 0.18);
}
.feed-preview-slot [data-testid="stImage"] img {
  border-radius: 10px;
  width: 100%;
}
.feed-preview-slot [data-testid="stProgress"] {
  margin-top: 0.55rem;
}
.feed-preview-slot [data-testid="stCaptionContainer"] {
  margin-top: 0.35rem;
}

div[data-testid="stMetric"] {
  background: white;
  border-radius: 16px;
  padding: 0.6rem 0.8rem;
}
"""

ONBOARDING_CSS = """
.stApp { background: #F5F6F8; }
section[data-testid="stSidebar"] {display: none !important;}
div[data-testid="collapsedControl"] {display: none !important;}
"""


def inject_css(*chunks: str) -> None:
    """Inject CSS with st.html (st.markdown strips <style> in Streamlit 1.6x)."""
    css = f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=League+Spartan:wght@500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    {BASE_CSS}
    {''.join(chunks)}
    </style>
    """
    st.html(css)


def inject_html(html: str) -> None:
    """Render raw HTML without Streamlit sanitizing it into visible text."""
    st.html(html)


def go_to(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def init_nav_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "dash_mode" not in st.session_state:
        st.session_state.dash_mode = "camera"
    elif st.session_state.dash_mode == "webcam":
        st.session_state.dash_mode = "camera"
    if "stop_pipeline" not in st.session_state:
        st.session_state.stop_pipeline = False
    if "acknowledged" not in st.session_state:
        st.session_state.acknowledged = False
    if "camera_label" not in st.session_state:
        st.session_state.camera_label = "Camera 1"
