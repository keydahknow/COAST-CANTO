from pathlib import Path
from PIL import Image

ui = Path(r"C:\Users\halls_18d2lri\Coding_Projects\github\keydahknow\CANTO\assets\ui")


def trim_transparent(im: Image.Image, pad: int = 8) -> Image.Image:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    alpha = im.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(im.width, r + pad)
    b = min(im.height, b + pad)
    return im.crop((l, t, r, b))


for name in ["how_monitor.png", "how_detect.png", "how_alert.png"]:
    path = ui / name
    im = Image.open(path)
    trimmed = trim_transparent(im)
    trimmed.save(path)
    print(f"{name}: {im.size} -> {trimmed.size}")


def to_landscape(path: Path, size=(1024, 576)) -> None:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    target = size[0] / size[1]
    cur = w / h
    if cur < target:
        new_h = int(w / target)
        top = max(0, (h - new_h) // 2)
        im = im.crop((0, top, w, min(h, top + new_h)))
    else:
        new_w = int(h * target)
        left = max(0, (w - new_w) // 2)
        im = im.crop((left, 0, min(w, left + new_w), h))
    im = im.resize(size, Image.Resampling.LANCZOS)
    im.save(path)
    print(f"{path.name} -> {im.size}")


for name in ["env_beach.png", "env_nature.png", "env_pool.png"]:
    to_landscape(ui / name)
