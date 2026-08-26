"""Detection dashboard. Same pipeline as the original app, restyled."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path

import cv2
import streamlit as st

import config
from pipeline import run
from ui.assets import show_logo
from ui.styles import DASHBOARD_CSS, go_to, inject_css

# Fake multi-camera labels → OpenCV device index (prototype: one feed at a time).
CAMERA_OPTIONS: list[tuple[str, int]] = [
    ("Camera 1", 0),
    ("Camera 2", 1),
    ("Camera 3", 2),
]
DEFAULT_LIVE_SECONDS = 30


def bgr_to_rgb(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def _model_options() -> list[str]:
    options = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"]
    if config.MODEL_NAME not in options:
        options.append(config.MODEL_NAME)
    return options


def collect_frame_stats(swimmers, submerged_stubs) -> dict:
    warnings = sum(1 for s in swimmers if s.is_distress and s.severity == "warning")
    alerts = len(submerged_stubs) + sum(
        1 for s in swimmers if s.is_distress and s.severity == "alert"
    )
    extra = max(alerts + warnings - 1, 0)
    high = None
    for stub in submerged_stubs:
        high = {
            "id": stub.id,
            "zone": stub.grid_cell or "unknown",
            "reason": "submersion",
            "severity": "alert",
            "label": "High Distress",
        }
    if high is None:
        for swimmer in swimmers:
            if not swimmer.is_distress:
                continue
            if swimmer.severity == "alert":
                high = {
                    "id": swimmer.id,
                    "zone": swimmer.grid_cell or "unknown",
                    "reason": "submersion",
                    "severity": "alert",
                    "label": "High Distress",
                }
                break
            if swimmer.severity == "warning":
                high = {
                    "id": swimmer.id,
                    "zone": swimmer.grid_cell or "unknown",
                    "reason": "stationary",
                    "severity": "warning",
                    "label": "Possible Distress",
                }
    return {
        "warnings": warnings,
        "alerts": alerts,
        "active": alerts + warnings,
        "extra": extra,
        "ids": sorted({s.id for s in swimmers}),
        "high": high,
    }


def process_source(
    source: str,
    settings: dict,
    *,
    preview_placeholder,
    progress_placeholder,
    status_placeholder,
    alert_placeholder,
    count_placeholder,
    feed_idle_placeholder=None,
    sync_live: bool = False,
    max_frames: int | None = None,
):
    frame_stats = {"warnings": 0, "alerts": 0, "active": 0, "high": None, "ids": []}
    preview_every = 1 if max_frames is not None else 3
    progress = progress_placeholder.progress(0.0, text="Starting...")

    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if not source.isdigit() else 0
    cap.release()
    if max_frames is not None:
        total_frames = max_frames

    processed = {"count": 0}

    def on_frame(frame, frame_index, swimmers, submerged_stubs):
        processed["count"] = frame_index
        stats = collect_frame_stats(swimmers, submerged_stubs)
        frame_stats.update(stats)

        if frame_index % preview_every == 0:
            if feed_idle_placeholder is not None:
                feed_idle_placeholder.empty()
            preview_placeholder.image(bgr_to_rgb(frame), use_container_width=True)

        if total_frames > 0:
            progress.progress(
                min(frame_index / total_frames, 1.0),
                text=f"Processing frame {frame_index}...",
            )
        else:
            progress.progress(
                min(frame_index / max(max_frames or 300, 1), 1.0),
                text=f"Live frame {frame_index}...",
            )

        count_placeholder.markdown(
            f'<span class="alert-pill">Active Alerts {stats["active"]}</span>',
            unsafe_allow_html=True,
        )
        _render_alert_card(alert_placeholder, stats["high"], stats["extra"])
        status_placeholder.caption(
            f"Frame {frame_index}  |  IDs {stats['ids']}  |  "
            f"Warnings {stats['warnings']}  |  Alerts {stats['alerts']}"
        )

    def stop_check():
        if max_frames is not None and processed["count"] >= max_frames:
            return True
        return st.session_state.get("stop_pipeline", False)

    out_path = run(
        source=source,
        no_window=True,
        settings=settings,
        frame_callback=on_frame,
        stop_check=stop_check,
        sync_settings_each_frame=sync_live,
        draw_video_hud=False,
    )
    progress.progress(1.0, text="Done.")
    return out_path, processed["count"], frame_stats


def _render_alert_card(placeholder, high: dict | None, extra: int) -> None:
    if st.session_state.get("acknowledged") and high:
        placeholder.info("Latest alert acknowledged. Monitoring continues.")
        return
    if not high:
        placeholder.info("No active distress events.")
        return
    color = "#E02424" if high["severity"] == "alert" else "#F59E0B"
    extra_line = f"<p>+ {extra} more active</p>" if extra else ""
    placeholder.markdown(
        f"""
        <div style="border:3px solid {color}; border-radius:18px; padding:1rem 1.1rem; background:white;">
          <h3 style="color:{color}; margin:0 0 0.4rem 0;">{high["label"]}</h3>
          <p style="margin:0; font-weight:700;">Swimmer ID {high["id"]}</p>
          <p style="margin:0.15rem 0 0.4rem; font-weight:700;">Zone {high["zone"]}</p>
          <p style="margin:0; color:#667; font-size:0.85rem;">
            {high["reason"].title()} · {datetime.now().strftime("%I:%M:%S %p")}
          </p>
          {extra_line}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _camera_index_from_label(label: str) -> int:
    for name, idx in CAMERA_OPTIONS:
        if name == label:
            return idx
    return 0


def _render_feed_toolbar(live: bool) -> None:
    """Camera picker + mode toggle above the feed box, aligned top-right."""
    _, toolbar = st.columns([2.8, 2.2])
    with toolbar:
        cam_col, mode_col = st.columns([1.15, 1.35], gap="small")
        with cam_col:
            labels = [name for name, _ in CAMERA_OPTIONS]
            st.selectbox(
                "Camera",
                labels,
                label_visibility="collapsed",
                key="camera_label",
            )
        with mode_col:
            b1, b2 = st.columns(2, gap="small")
            with b1:
                if st.button(
                    "Video Upload",
                    type="primary" if not live else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.dash_mode = "upload"
                    st.rerun()
            with b2:
                if st.button(
                    "Live Camera",
                    type="primary" if live else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.dash_mode = "camera"
                    st.rerun()


def render_dashboard() -> None:
    inject_css(DASHBOARD_CSS)

    logo_l, status_l = st.columns([3, 1])
    with logo_l:
        show_logo("light", width=110, css_class="dash-logo-wrap")
    with status_l:
        st.markdown(
            '<p class="status-online" style="text-align:right; margin-top:0.35rem;">● System Online</p>',
            unsafe_allow_html=True,
        )

    top_l, _ = st.columns([3, 1])
    with top_l:
        if st.button("← Back to home", key="back_home_btn"):
            go_to("landing")
        st.markdown('<p class="dash-title">Detection Dashboard</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="dash-sub">Monitor swimmers and manage distress detection.</p>',
            unsafe_allow_html=True,
        )
        count_placeholder = st.empty()
        count_placeholder.markdown(
            '<span class="alert-pill">Active Alerts 0</span>',
            unsafe_allow_html=True,
        )

    live = st.session_state.dash_mode == "camera"
    start_upload = False
    start_camera = False
    uploaded = None
    max_seconds = DEFAULT_LIVE_SECONDS

    _render_feed_toolbar(live)

    with st.container(border=True):
        if not live:
            st.caption("Upload a clip to run detection (mp4, avi, mov, mkv).")
            uploaded = st.file_uploader(
                "Video file",
                type=["mp4", "avi", "mov", "mkv"],
                label_visibility="collapsed",
            )
        else:
            uploaded = None
            show_advanced = st.checkbox("Advanced live options", value=False)
            if show_advanced:
                max_seconds = st.slider(
                    "Max live run (seconds)",
                    5,
                    120,
                    DEFAULT_LIVE_SECONDS,
                    5,
                    help="Safety cap so a forgotten tab does not run forever. Use Stop to end early.",
                )
            st.caption(
                "Live mode is CPU-heavy. Use yolov8n and image size 640 for a faster preview."
            )

        st.markdown('<div class="feed-controls-row">', unsafe_allow_html=True)
        run_col, stop_col = st.columns(2)
        with run_col:
            if not live:
                start_upload = st.button(
                    "Process video", type="primary", disabled=not uploaded
                )
            else:
                start_camera = st.button("Start camera", type="primary")
        with stop_col:
            if st.button("Stop", key="stop_pipeline_btn"):
                st.session_state.stop_pipeline = True
                st.warning("Stop requested. Halts after the current frame.")

        feed_header = st.empty()
        feed_idle = st.empty()
        preview_placeholder = st.empty()
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        result_placeholder = st.empty()

        if live and start_camera:
            feed_header.markdown(
                '<div class="feed-header-row">'
                '<span style="font-size:1.25rem;font-weight:700;">Camera Feed</span>'
                '<span class="live-badge">LIVE</span>'
                "</div>",
                unsafe_allow_html=True,
            )
            feed_idle.empty()
        elif live:
            feed_header.empty()
            feed_idle.markdown(
                '<div class="feed-preview-panel is-idle">'
                "Press <strong>Start camera</strong> to open the live feed."
                "</div>",
                unsafe_allow_html=True,
            )
        elif uploaded:
            feed_header.empty()
            feed_idle.markdown(
                '<div class="feed-preview-panel is-idle">'
                "Press <strong>Process video</strong> to preview detection here."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            feed_header.empty()
            feed_idle.empty()

    mid_l, mid_r = st.columns(2, gap="medium")
    with mid_l:
        with st.container(border=True):
            st.subheader("Display and Alerts")
            show_grid = st.toggle("Show 6-cell grid", value=config.SHOW_GRID)
            show_trail = st.toggle("Movement trails", value=config.SHOW_TRAIL)
            show_banner = st.toggle(
                "On-screen alert banner",
                value=False,
                help="Off by default so alerts show in the dashboard card instead of on the video.",
            )
            enable_discord = st.toggle("Discord alerts", value=config.ENABLE_DISCORD)
            save_output = st.toggle("Save annotated output video", value=config.SAVE_OUTPUT)
    with mid_r:
        alert_placeholder = st.empty()
        _render_alert_card(alert_placeholder, None, 0)
        ack_col, hist_col = st.columns(2)
        with ack_col:
            if st.button("Acknowledge", type="primary"):
                st.session_state.acknowledged = True
                st.toast("Alert acknowledged (dashboard only).")
        with hist_col:
            if st.button("Incident History"):
                st.toast("Incident History is a preview control in this prototype.")

    d_left, d_right = st.columns(2, gap="medium")
    with d_left:
        with st.container(border=True):
            st.subheader("Detection Controls")
            options = _model_options()
            model_name = st.selectbox(
                "Model", options, index=options.index(config.MODEL_NAME)
            )
            confidence = st.slider(
                "Confidence threshold",
                min_value=0.05,
                max_value=0.50,
                value=float(config.CONFIDENCE_THRESHOLD),
                step=0.01,
            )
            image_size = st.select_slider(
                "Image size",
                options=[640, 960, 1280],
                value=config.IMAGE_SIZE,
            )
    with d_right:
        with st.container(border=True):
            st.subheader("Distress Rules")
            stationary_seconds = st.slider(
                "Stationary warning (seconds)",
                min_value=3.0,
                max_value=30.0,
                value=float(config.STATIONARY_SECONDS),
                step=0.5,
            )
            stationary_pixels = st.slider(
                "Movement limit (pixels)",
                min_value=10,
                max_value=100,
                value=int(config.STATIONARY_PIXELS),
                step=5,
            )
            submersion_seconds = st.slider(
                "Submersion alert (seconds)",
                min_value=1.0,
                max_value=30.0,
                value=min(float(config.SUBMERSION_SECONDS), 30.0),
                step=0.5,
            )

    settings = {
        "MODEL_NAME": model_name,
        "CONFIDENCE_THRESHOLD": confidence,
        "IMAGE_SIZE": image_size,
        "STATIONARY_SECONDS": stationary_seconds,
        "STATIONARY_PIXELS": stationary_pixels,
        "SUBMERSION_SECONDS": submersion_seconds,
        "SHOW_GRID": show_grid,
        "SHOW_TRAIL": show_trail,
        "SHOW_ALERT_BANNER": show_banner,
        "ENABLE_DISCORD": enable_discord,
        "SAVE_OUTPUT": save_output,
    }

    if start_upload and uploaded:
        st.session_state.stop_pipeline = False
        st.session_state.acknowledged = False
        suffix = Path(uploaded.name).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getbuffer())
            temp_path = tmp.name
        try:
            with st.spinner("Running detection, tracking, distress logic, and alerts..."):
                out_path, frames, stats = process_source(
                    temp_path,
                    settings,
                    preview_placeholder=preview_placeholder,
                    progress_placeholder=progress_placeholder,
                    status_placeholder=status_placeholder,
                    alert_placeholder=alert_placeholder,
                    count_placeholder=count_placeholder,
                    feed_idle_placeholder=feed_idle,
                    sync_live=False,
                )
            result_placeholder.success(
                f"Finished **{frames}** frames. "
                f"Warnings: **{stats['warnings']}**. Alerts: **{stats['alerts']}**."
            )
            if out_path and os.path.exists(out_path):
                st.subheader("Annotated output")
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button(
                        "Download annotated video",
                        data=f,
                        file_name=Path(out_path).name,
                        mime="video/mp4",
                    )
        except Exception as exc:
            result_placeholder.error(f"Processing failed: {exc}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    if start_camera:
        st.session_state.stop_pipeline = False
        st.session_state.acknowledged = False
        camera_index = _camera_index_from_label(
            st.session_state.get("camera_label", CAMERA_OPTIONS[0][0])
        )
        max_frames = int(max_seconds * 25)
        try:
            feed_idle.empty()
            feed_header.markdown(
                '<div class="feed-header-row">'
                '<span style="font-size:1.25rem;font-weight:700;">Camera Feed</span>'
                '<span class="live-badge">LIVE</span>'
                "</div>",
                unsafe_allow_html=True,
            )
            with st.spinner("Live camera running. Allow camera access if prompted..."):
                out_path, frames, stats = process_source(
                    str(camera_index),
                    settings,
                    preview_placeholder=preview_placeholder,
                    progress_placeholder=progress_placeholder,
                    status_placeholder=status_placeholder,
                    alert_placeholder=alert_placeholder,
                    count_placeholder=count_placeholder,
                    feed_idle_placeholder=feed_idle,
                    sync_live=True,
                    max_frames=max_frames,
                )
            result_placeholder.success(
                f"Live run stopped after **{frames}** frames. "
                f"Warnings: **{stats['warnings']}**. Alerts: **{stats['alerts']}**."
            )
            if out_path and os.path.exists(out_path):
                st.subheader("Recorded output")
                st.video(out_path)
        except Exception as exc:
            result_placeholder.error(f"Camera failed: {exc}")
