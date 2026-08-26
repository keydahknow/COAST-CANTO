"""Placeholder onboarding page. Accessible from the landing page."""

from __future__ import annotations

import streamlit as st

from ui.assets import show_logo
from ui.styles import ONBOARDING_CSS, go_to, inject_css


def render_onboarding() -> None:
    inject_css(ONBOARDING_CSS)
    show_logo("light")
    st.title("Get started")
    st.caption("Facility onboarding will live here. This page is a placeholder.")

    with st.container(border=True):
        st.subheader("Onboarding form")
        st.text_input("Facility name", disabled=True, placeholder="Coming soon")
        st.text_input("Contact email", disabled=True, placeholder="Coming soon")
        st.selectbox("Site type", ["Beach", "Pool", "Other"], disabled=True)
        st.button("Submit", disabled=True, type="primary")

    back, dash = st.columns(2)
    with back:
        if st.button("Back to home"):
            go_to("landing")
    with dash:
        if st.button("Open Dashboard", type="primary"):
            go_to("dashboard")
