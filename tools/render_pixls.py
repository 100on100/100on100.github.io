"""Render site images from the raw.pixls.us corpus (CC0), a public camera corpus.

usage: render_pixls.py <pixls dir with manifest.json> <out dir> sheet
       render_pixls.py <pixls dir> <out dir> photo <npy> <slug> [width]
       render_pixls.py <pixls dir> <out dir> mosaic <npy> <slug> <row> <col>
       render_pixls.py <pixls dir> <out dir> tiles <npy> <slug> [width]

Each frame is an RGGB mosaic (rephased to R at 0,0). A preview is a half-size demosaic: R, the mean
of the two greens, B; black level subtracted; grey-world white balance; 99.5th-percentile white
point; sRGB-like gamma. A mosaic crop shows the stored samples themselves, each in its filter colour.
Runs on the host; only the rendered JPEGs leave it.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw

SRC, OUT, MODE = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
man = {r["npy"]: r for r in json.load(open(os.path.join(SRC, "manifest.json"))) if not r.get("rejected")}


def load(npy):
    m = np.load(os.path.join(SRC, npy), mmap_mode="r")
    return m, man.get(npy, {})


def preview(m, meta, width=None):
    h, w = (m.shape[0] // 2) * 2, (m.shape[1] // 2) * 2
    step = 1
    if width:                                   # subsample whole 2x2 cells so phases stay aligned
        step = max(1, (w // 2) // width)
    r = m[0:h:2 * step, 0:w:2 * step].astype(np.float32)
    g = (m[0:h:2 * step, 1:w:2 * step].astype(np.float32) + m[1:h:2 * step, 0:w:2 * step]) / 2
    b = m[1:h:2 * step, 1:w:2 * step].astype(np.float32)
    bl = meta.get("black", [0, 0, 0, 0])
    rgb = np.stack([r - bl[0], g - (bl[1] + bl[2]) / 2, b - bl[3]], -1).clip(0, None)
    means = rgb.reshape(-1, 3).mean(0) + 1e-6
    rgb *= means[1] / means
    wp = np.percentile(rgb, 99.5) + 1e-6
    rgb = (rgb / wp).clip(0, 1) ** (1 / 2.2)
    # no camera colour matrix is applied, so lift contrast and saturation for display
    lum = rgb.mean(-1, keepdims=True)
    rgb = (lum + 1.45 * (rgb - lum)).clip(0, 1)
    rgb = 0.5 - 0.5 * np.cos(np.pi * rgb) * 0.6 + (rgb - 0.5) * 0.4   # gentle S-curve
    return Image.fromarray((rgb.clip(0, 1) * 255 + 0.5).astype(np.uint8))


def save(img, slug):
    p = os.path.join(OUT, slug + ".jpg")
    img.save(p, quality=82, optimize=True, progressive=True)
    print(p, img.size, os.path.getsize(p))


if MODE == "sheet":                             # contact sheet of every camera, for choosing and for the site
    names = sorted(man)
    tw, th, cols = 240, 160, 8
    rows = -(-len(names) // cols)
    sheet = Image.new("RGB", (cols * tw, rows * th), (16, 24, 36))
    for k, npy in enumerate(names):
        m, meta = load(npy)
        p = preview(m, meta, width=480)
        p.thumbnail((tw - 4, th - 4))
        sheet.paste(p, ((k % cols) * tw + (tw - p.width) // 2, (k // cols) * th + (th - p.height) // 2))
    save(sheet, "cameras-sheet")
    json.dump(names, open(os.path.join(OUT, "cameras-sheet.json"), "w"), indent=0)
elif MODE == "photo":
    m, meta = load(sys.argv[4])
    save(preview(m, meta, width=int(sys.argv[6]) if len(sys.argv) > 6 else 1400), sys.argv[5])
elif MODE == "mosaic":                          # the stored samples, magnified, each in its filter colour
    m, meta = load(sys.argv[4]); r0, c0 = int(sys.argv[6]) // 2 * 2, int(sys.argv[7]) // 2 * 2
    crop = m[r0:r0 + 16, c0:c0 + 24].astype(np.float32)
    bl = np.array(meta.get("black", [0, 0, 0, 0]), np.float32)
    blk = np.empty_like(crop); blk[0::2, 0::2], blk[0::2, 1::2], blk[1::2, 0::2], blk[1::2, 1::2] = bl
    v = ((crop - blk).clip(0, None) / (np.percentile(crop - blk, 99) + 1e-6)).clip(0, 1) ** (1 / 2.2)
    s = 40
    img = Image.new("RGB", (24 * s, 16 * s), (10, 14, 20)); d = ImageDraw.Draw(img)
    for y in range(16):
        for x in range(24):
            col = [(1, 0.18, 0.15), (0.2, 1, 0.3)][x % 2] if y % 2 == 0 else [(0.2, 1, 0.3), (0.2, 0.35, 1)][x % 2]
            c = tuple(int(255 * (0.08 + 0.92 * v[y, x]) * k) for k in col)
            d.rectangle([x * s + 1, y * s + 1, x * s + s - 2, y * s + s - 2], fill=c)
    save(img, sys.argv[5])
elif MODE == "tiles":                           # the frame with its 256 x 256-sample tile grid
    m, meta = load(sys.argv[4]); width = int(sys.argv[6]) if len(sys.argv) > 6 else 1400
    img = preview(m, meta, width=width)
    scale = img.width / (m.shape[1] / 2)        # preview pixels per plane sample
    t = 256 * scale                             # a tile is 256 x 256 samples of one phase plane
    d = ImageDraw.Draw(img, "RGBA")
    xs = np.arange(0, img.width, t); ys = np.arange(0, img.height, t)
    for x in xs: d.line([(x, 0), (x, img.height)], fill=(255, 255, 255, 110), width=2)
    for y in ys: d.line([(0, y), (img.width, y)], fill=(255, 255, 255, 110), width=2)
    tx, ty = xs[len(xs) * 3 // 5], ys[len(ys) // 3]
    d.rectangle([tx, ty, tx + t, ty + t], outline=(64, 170, 255, 255), width=5, fill=(64, 170, 255, 40))
    save(img, sys.argv[5])
