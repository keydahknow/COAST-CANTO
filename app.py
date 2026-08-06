"""
C.O.A.S.T. dashboard — local Streamlit UI for the competition prototype.

Run from project root:
    streamlit run app.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import cv2
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import config  # noqa: E402
from pipeline import run  # noqa: E402
from settings import default_settings  # noqa: E402

st.set_page_config(
    page_title="C.O.A.S.T.",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="expanded",
)


def bgr_to_rgb(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def build_settings_from_sidebar() -> dict:
    """Read sidebar widgets into a config override dict."""
    st.sidebar.subheader("Detection")
    model_options = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"]
    if config.MODEL_NAME not in model_options:
        model_options.append(config.MODEL_NAME)
    model_name = st.sidebar.selectbox(
        "Model",
        options=model_options,
        index=model_options.index(config.MODEL_NAME),
    )
    confidence = st.sidebar.slider(
        "Confidence threshold",
        min_value=0.05,
        max_value=0.50,
        value=float(config.CONFIDENCE_THRESHOLD),
        step=0.01,
        help="Lower = detect more swimmers (more false positives).",
    )
    image_size = st.sidebar.select_slider(
        "Image size",
        options=[640, 960, 1280],
        value=config.IMAGE_SIZE,
        help="Higher = better on small/distant swimmers, slower on CPU.",
    )

    st.sidebar.subheader("Distress rules")
    stationary_seconds = st.sidebar.slider(
        "Stationary warning (seconds)",
        min_value=3.0,
        max_value=30.0,
        value=float(config.STATIONARY_SECONDS),
        step=0.5,
    )
    stationary_pixels = st.sidebar.slider(
        "Stationary movement limit (pixels)",
        min_value=10,
        max_value=100,
        value=int(config.STATIONARY_PIXELS),
        step=5,
    )
    submersion_seconds = st.sidebar.slider(
        "Submersion alert (seconds)",
        min_value=1.0,
        max_value=10.0,
        value=float(config.SUBMERSION_SECONDS),
        step=0.5,
    )

    st.sidebar.subheader("Display & alerts")
    show_grid = st.sidebar.checkbox("Show 6-cell grid", value=config.SHOW_GRID)
    show_trail = st.sidebar.checkbox("Show movement trails", value=config.SHOW_TRAIL)
    show_banner = st.sidebar.checkbox(
        "Show on-screen alert banner", value=config.SHOW_ALERT_BANNER
    )
    enable_discord = st.sidebar.checkbox(
        "Send Discord alerts", value=config.ENABLE_DISCORD
    )
    save_output = st.sidebar.checkbox(
        "Save annotated output video", value=config.SAVE_OUTPUT
    )

    return {
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


def render_intro():
    st.title("C.O.A.S.T.")
    st.subheader("Coastal Observation & Analytic Sensing Technology")
    st.markdown(
        """
        **AI-assisted swimmer monitoring for lifeguards** — a prototype for the
        CANTO Innovation Challenge 2026 (*Climate & Disaster Resilience*).

        C.O.A.S.T. detects and tracks swimmers in video, flags possible distress
        (prolonged stationary behavior or sudden disappearance from view), maps
        each swimmer to a **6-zone grid** (A B C top row, 1 2 3 bottom row), and
        raises alerts on-screen and via Discord.

        > This system **assists, not replaces**, trained lifeguards.

        **Team: The Buoyz** — Asia Cooper · Imani Zakuri · Samuel Blache · Keedanu Halls
        """
    )


def process_source(
    source: str,
    settings: dict,
    *,
    preview_placeholder,
    progress_placeholder,
    status_placeholder,
    sync_live: bool = False,
    max_frames: int | None = None,
):
    """Run pipeline with Streamlit preview + optional progress bar."""
    frame_stats = {"warnings": 0, "alerts": 0}
    preview_every = 3 if max_frames is None else 5
    progress = progress_placeholder.progress(0.0, text="Starting...")
    status = status_placeholder.empty()

    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if not source.isdigit() else 0
    cap.release()

    if max_frames is not None:
        total_frames = max_frames

    processed = {"count": 0}

    def on_frame(frame, frame_index, swimmers, submerged_stubs):
        processed["count"] = frame_index
        warnings = sum(
            1 for s in swimmers if s.is_distress and s.severity == "warning"
        )
        alerts = len(submerged_stubs) + sum(
            1 for s in swimmers if s.is_distress and s.severity == "alert"
        )
        frame_stats["warnings"] = warnings
        frame_stats["alerts"] = alerts

        if frame_index % preview_every == 0:
            preview_placeholder.image(
                bgr_to_rgb(frame),
                caption=f"Frame {frame_index} | Warnings: {warnings} | Alerts: {alerts}",
                use_container_width=True,
            )

        if total_frames > 0:
            pct = min(frame_index / total_frames, 1.0)
            progress.progress(pct, text=f"Processing frame {frame_index}...")
        else:
            progress.progress(
                min(frame_index / max(max_frames or 300, 1), 1.0),
                text=f"Live frame {frame_index}...",
            )

        status.info(
            f"Frame **{frame_index}** — active IDs: "
            f"{sorted({s.id for s in swimmers})} — "
            f"warnings: **{warnings}**, alerts: **{alerts}**"
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
    )

    progress.progress(1.0, text="Done.")
    return out_path, processed["count"], frame_stats


def main():
    render_intro()
    settings = build_settings_from_sidebar()

    st.divider()
    st.header("Run C.O.A.S.T.")

    mode = st.radio(
        "Input source",
        options=["Upload video", "Webcam (live)"],
        horizontal=True,
    )

    preview_placeholder = st.empty()
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    result_placeholder = st.empty()

    col_run, col_stop = st.columns([1, 1])
    with col_stop:
        if st.button("Stop", type="secondary"):
            st.session_state.stop_pipeline = True
            st.warning("Stop requested — will halt after the current frame.")

    if mode == "Upload video":
        uploaded = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv"],
            help="Beach or pool footage with visible swimmers works best.",
        )

        with col_run:
            start_upload = st.button("Process video", type="primary", disabled=not uploaded)

        if start_upload and uploaded:
            st.session_state.stop_pipeline = False
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
                        sync_live=False,
                    )
                result_placeholder.success(
                    f"Finished **{frames}** frames. "
                    f"Last frame: **{stats['warnings']}** warnings, "
                    f"**{stats['alerts']}** alerts."
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

    else:
        webcam_index = st.number_input(
            "Webcam index",
            min_value=0,
            max_value=4,
            value=0,
            step=1,
            help="Usually 0 for the built-in camera.",
        )
        max_seconds = st.slider(
            "Max live run (seconds)",
            min_value=5,
            max_value=120,
            value=30,
            step=5,
            help="Limits how long the live preview runs (CPU-friendly).",
        )
        st.caption(
            "Live mode applies sidebar settings on each frame. "
            "Adjust sliders while the preview runs."
        )

        with col_run:
            start_webcam = st.button("Start webcam", type="primary")

        if start_webcam:
            st.session_state.stop_pipeline = False
            approx_fps = 25
            max_frames = int(max_seconds * approx_fps)
            try:
                with st.spinner("Webcam live — allow camera access if prompted..."):
                    out_path, frames, stats = process_source(
                        str(int(webcam_index)),
                        settings,
                        preview_placeholder=preview_placeholder,
                        progress_placeholder=progress_placeholder,
                        status_placeholder=status_placeholder,
                        sync_live=True,
                        max_frames=max_frames,
                    )
                result_placeholder.success(
                    f"Live run stopped after **{frames}** frames. "
                    f"Last frame: **{stats['warnings']}** warnings, "
                    f"**{stats['alerts']}** alerts."
                )
                if out_path and os.path.exists(out_path):
                    st.subheader("Recorded output")
                    st.video(out_path)
            except Exception as exc:
                result_placeholder.error(f"Webcam failed: {exc}")

    with st.expander("Current settings snapshot"):
        st.json({**default_settings(), **settings})


if __name__ == "__main__":
    main()
