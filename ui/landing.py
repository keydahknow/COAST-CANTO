"""Landing page modelled on the Canva design."""

from __future__ import annotations

import streamlit as st

from ui.assets import asset_path, data_uri, show_logo
from ui.styles import LANDING_CSS, go_to, inject_css, inject_html


def _img_tag(key: str, alt: str, css_class: str) -> str:
    path = asset_path(key)
    if not path:
        fname = {
            "device_watch": "device_watch.svg (or .png)",
            "device_desktop": "device_desktop.svg (or .png)",
        }.get(key, key)
        return f'<div class="missing-slot">Add <code>{fname}</code></div>'
    return f'<img class="{css_class}" src="{data_uri(path)}" alt="{alt}" />'


def render_landing() -> None:
    inject_css(LANDING_CSS)

    # ---- Nav ----
    nav_logo, _, nav_how, nav_start, nav_dash = st.columns([2.0, 3.2, 1.4, 1.4, 1.8])
    with nav_logo:
        show_logo("light", width=170)
    with nav_how:
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        if st.button("How it Works", key="nav_how"):
            st.session_state.jump_how = True
            st.rerun()
    with nav_start:
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        if st.button("Get Started", key="nav_start"):
            go_to("onboarding")
    with nav_dash:
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        if st.button("Open Dashboard", type="primary", key="nav_dash"):
            go_to("dashboard")

    # ---- Hero ----
    hero_l, hero_r = st.columns([1.05, 1], gap="large")
    with hero_l:
        inject_html(
            """
            <p class="hero-title">
              <span class="hero-kicker">Safer</span> waters start<br>with smarter awareness.
            </p>
            <p class="hero-sub">
              C.O.A.S.T. uses computer vision to monitor swimmers, identify signs
              of distress and alert lifeguards with a precise location.
            </p>
            """
        )
    with hero_r:
        path = asset_path("hero")
        if path:
            inject_html(
                f'<div class="hero-mock"><img src="{data_uri(path)}" alt="Detection Dashboard" /></div>'
            )
        else:
            inject_html(
                """
                <div class="dash-preview">
                  <div class="dash-preview-bar">
                    <span>Detection Dashboard</span>
                    <span style="color:#84CC16;">● System online</span>
                  </div>
                  <div class="preview-feed"><span class="preview-live">LIVE</span></div>
                </div>
                """
            )

    # Scroll script after How it works exists in the DOM
    scroll_script = ""
    if st.session_state.pop("jump_how", False):
        scroll_script = """
        <script>
        (function () {
          function go() {
            const docs = [document, window.parent && window.parent.document].filter(Boolean);
            for (const doc of docs) {
              try {
                const el = doc.getElementById("how-it-works");
                if (el) {
                  el.scrollIntoView({ behavior: "smooth", block: "start" });
                  return;
                }
              } catch (e) {}
            }
          }
          setTimeout(go, 80);
          setTimeout(go, 300);
        })();
        </script>
        """

    # ---- Blue band: How it works + devices ----
    how_cards = [
        (
            "monitor",
            "MONITOR",
            "AI-enabled cameras continuously observe swimmers in real time.",
        ),
        (
            "detect",
            "DETECT",
            "COAST tracks movement and identifies possible signs of distress.",
        ),
        (
            "alert",
            "ALERT",
            "Lifeguards receive the swimmer's location and supporting alert information.",
        ),
    ]
    cards_html = []
    for key, title, body in how_cards:
        cards_html.append(
            f"""
            <div class="how-col">
              {_img_tag(key, title, "how-img")}
              <div class="how-text-box">
                <h3>{title}</h3>
                <p>{body}</p>
              </div>
            </div>
            """
        )

    watch = _img_tag("device_watch", "Smartwatch", "device-img")
    desktop = _img_tag("device_desktop", "Desktop dashboard", "device-img")

    inject_html(
        f"""
        <div class="blue-band" id="how-it-works">
          <h2 class="how-heading">How it works</h2>
          <div class="how-grid">
            {''.join(cards_html)}
          </div>
          <div class="devices-grid">
            <div class="device-col">{watch}</div>
            <div class="device-col device-col-wide">{desktop}</div>
          </div>
        </div>
        {scroll_script}
        """
    )

    # ---- Environments ----
    env_l, env_r = st.columns([1.05, 1], gap="large")
    with env_l:
        inject_html(
            '<p class="env-title">One system,<br>Different aquatic<br>environments.</p>'
        )
    with env_r:
        for key, label in (
            ("env_beach", "Coastal beaches"),
            ("env_nature", "Natural water"),
            ("env_pool", "Pools and training facilities"),
        ):
            path = asset_path(key)
            if path:
                inject_html(
                    f'<div class="env-photo"><img src="{data_uri(path)}" alt="{label}" /></div>'
                )
            else:
                inject_html(f'<div class="env-chip chip-beach">{label}</div>')

    inject_html(
        """
        <div class="coast-footer">
          Created for the CANTO Innovation Challenge 2026 by The Buoyz —
          Asia Cooper | Imani Zakuri | Samuel Blache | Keedanu Halls
        </div>
        """
    )
