"""
C.O.A.S.T. Streamlit app.

Landing page → onboarding (placeholder) or detection dashboard.

    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ui.dashboard import render_dashboard
from ui.landing import render_landing
from ui.onboarding import render_onboarding
from ui.styles import init_nav_state

st.set_page_config(
    page_title="C.O.A.S.T.",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_nav_state()
page = st.session_state.page

if page == "onboarding":
    render_onboarding()
elif page == "dashboard":
    render_dashboard()
else:
    render_landing()
