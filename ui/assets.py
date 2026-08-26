"""Load optional Canva images from assets/ui when they are present."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from ui.styles import LOGO_SVG_DARK, LOGO_SVG_LIGHT, inject_html

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "assets" / "ui"

# Preferred filenames. asset_path() also tries common alternate extensions.
FILES = {
    "logo_light": "logo_blue.svg",
    "logo_dark": "logo_dark.svg",
    "hero": "hero_dashboard.jpg",
    "monitor": "how_monitor.png",
    "detect": "how_detect.png",
    "alert": "how_alert.png",
    "env_beach": "env_beach.png",
    "env_nature": "env_nature.png",
    "env_pool": "env_pool.png",
    "device_watch": "device_watch.svg",
    "device_desktop": "device_desktop.svg",
}

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def asset_path(key: str) -> Path | None:
    """Resolve an asset, trying preferred name then svg/png/jpg variants."""
    name = FILES.get(key)
    if not name:
        return None

    preferred = ASSET_DIR / name
    if preferred.is_file():
        return preferred

    stem = Path(name).stem
    for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp"):
        candidate = ASSET_DIR / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def data_uri(path: Path) -> str:
    mime = _MIME.get(path.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def _canva_svg_preview_uri(path: Path) -> str:
    """
    Canva 'SVG' exports are often a full slide with embedded PNGs.
    Inlining that XML is too large for Streamlit. Prefer the best embedded PNG.
    """
    import re

    text = path.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(
        r"data:image/(png|jpeg|jpg);base64,([A-Za-z0-9+/=]+)", text, flags=re.I
    )
    if not matches:
        return data_uri(path)

    best = max(matches, key=lambda m: len(m[1]))
    kind, b64 = best
    mime = "image/jpeg" if kind.lower() in ("jpeg", "jpg") else "image/png"
    return f"data:{mime};base64,{b64}"


def show_logo(variant: str = "light", width: int | None = 180, css_class: str = "logo-wrap") -> None:
    key = "logo_dark" if variant == "dark" else "logo_light"
    path = asset_path(key)
    w = width or 180
    if path:
        src = (
            _canva_svg_preview_uri(path)
            if path.suffix.lower() == ".svg"
            else data_uri(path)
        )
        inject_html(
            f'<div class="{css_class}" style="max-width:{w}px;width:100%;">'
            f'<img src="{src}" alt="COAST" /></div>'
        )
    else:
        svg = LOGO_SVG_DARK if variant == "dark" else LOGO_SVG_LIGHT
        inject_html(
            f'<div class="{css_class}" style="max-width:{w}px;width:100%;">{svg}</div>'
        )


def show_image(key: str, **kwargs) -> bool:
    path = asset_path(key)
    if not path:
        return False
    if path.suffix.lower() == ".svg":
        inject_html(
            f'<img src="{data_uri(path)}" alt="{key}" style="width:100%;height:auto;" />'
        )
        return True
    kwargs.setdefault("use_container_width", True)
    st.image(str(path), **kwargs)
    return True
