from pathlib import Path
from PIL import Image
import numpy as np

ui = Path(r"C:\Users\halls_18d2lri\Coding_Projects\github\keydahknow\CANTO\assets\ui")


def trim_whitespace(im: Image.Image, threshold: int = 245, pad: int = 6) -> Image.Image:
    """Crop near-white margins from an image."""
    rgba = im.convert("RGBA")
    arr = np.asarray(rgba)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]
    # Non-background: not near-white, or has meaningful alpha
    not_white = (rgb.min(axis=2) < threshold) | (alpha < 250)
    rows = np.any(not_white, axis=1)
    cols = np.any(not_white, axis=0)
    if not rows.any() or not cols.any():
        return im
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    rmin = max(0, rmin - pad)
    cmin = max(0, cmin - pad)
    rmax = min(im.height - 1, rmax + pad)
    cmax = min(im.width - 1, cmax + pad)
    return im.crop((cmin, rmin, cmax + 1, rmax + 1))


for name in ["how_monitor.png", "how_detect.png", "how_alert.png"]:
    path = ui / name
    im = Image.open(path)
    trimmed = trim_whitespace(im)
    # Save as RGB on transparent-safe PNG if needed
    if trimmed.mode == "RGBA":
        # Composite onto white for cleaner Streamlit display of remaining edges
        bg = Image.new("RGB", trimmed.size, (255, 255, 255))
        bg.paste(trimmed, mask=trimmed.split()[-1])
        trimmed = bg
    else:
        trimmed = trimmed.convert("RGB")
    trimmed.save(path)
    print(f"{name}: {im.size} -> {trimmed.size}")
