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
elif MODE == "banner":                          # a wide page banner: preview cropped to width x height, centred at fy
    m, meta = load(sys.argv[4]); W, H = int(sys.argv[6]), int(sys.argv[7]); fy = float(sys.argv[8]) if len(sys.argv) > 8 else 0.5
    img = preview(m, meta, width=W)
    if img.width != W: img = img.resize((W, round(img.height * W / img.width)), Image.LANCZOS)
    top = int(max(0, min(img.height - H, fy * img.height - H / 2)))
    save(img.crop((0, top, W, top + H)), sys.argv[5])
elif MODE == "wall":                            # a wide wall of stored samples in filter colours, at the busiest region
    m, meta = load(sys.argv[4]); W, H, s = int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])
    nx, ny = W // s // 2 * 2, H // s // 2 * 2
    p = np.asarray(preview(m, meta, width=600)).astype(np.float32).mean(-1); k = (m.shape[1] // 2) / p.shape[1]
    best = None
    for y in range(p.shape[0] // 5, p.shape[0] * 4 // 5 - 8, 4):         # the most textured window, central 60%
        for x in range(p.shape[1] // 5, p.shape[1] * 4 // 5 - 24, 4):
            v = p[y:y + 8, x:x + 24].std()
            if best is None or v > best[0]: best = (v, y, x)
    r0 = int(best[1] * k * 2) // 2 * 2; c0 = int(best[2] * k * 2) // 2 * 2
    if len(sys.argv) > 10: r0, c0 = int(sys.argv[9]) // 2 * 2, int(sys.argv[10]) // 2 * 2   # explicit origin
    crop = m[r0:r0 + ny, c0:c0 + nx].astype(np.float32)
    bl = np.array(meta.get("black", [0, 0, 0, 0]), np.float32)
    blk = np.empty_like(crop); blk[0::2, 0::2], blk[0::2, 1::2], blk[1::2, 0::2], blk[1::2, 1::2] = bl
    v = ((crop - blk).clip(0, None) / (np.percentile(crop - blk, 99) + 1e-6)).clip(0, 1) ** (1 / 2.2)
    img = Image.new("RGB", (nx * s, ny * s), (10, 14, 20)); d = ImageDraw.Draw(img)
    for y in range(ny):
        for x in range(nx):
            col = [(1, 0.18, 0.15), (0.2, 1, 0.3)][x % 2] if y % 2 == 0 else [(0.2, 1, 0.3), (0.2, 0.35, 1)][x % 2]
            d.rectangle([x * s, y * s, x * s + s - 2, y * s + s - 2], fill=tuple(int(255 * (0.06 + 0.94 * v[y, x]) * c) for c in col))
    save(img, sys.argv[5])
elif MODE == "zoom":                            # frame -> close-up -> the stored samples, around the reddest detail
    from PIL import ImageFont
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    m, meta = load(sys.argv[4])
    full = preview(m, meta)                                   # half-size: one pixel per 2 x 2 cell
    from PIL import ImageFilter
    a = np.asarray(full.filter(ImageFilter.BoxBlur(12))).astype(np.float32)
    red = a[..., 0] - a[..., 1:].mean(-1)                     # the reddest detail, away from the borders
    my, mx = a.shape[0] // 6, a.shape[1] // 6
    ys, xs = np.unravel_index(np.argmax(red[my:-my, mx:-mx]), red[my:-my, mx:-mx].shape)
    cy, cx = int(ys + my), int(xs + mx)
    PW, PH = 600, 400
    z1 = full.resize((PW, round(full.height * PW / full.width)), Image.LANCZOS)
    cw, ch = full.width // 8, full.height // 8                # close-up: 1/8 of the frame
    bx = int(min(max(cx - cw // 2, 0), full.width - cw)); by = int(min(max(cy - ch // 2, 0), full.height - ch))
    z2 = full.crop((bx, by, bx + cw, by + ch)).resize((PW, round(ch * PW / cw)), Image.LANCZOS)
    r0, c0 = (cy * 2) // 2 * 2 - 8, (cx * 2) // 2 * 2 - 12    # 16 x 24 stored samples at the detail
    crop = m[r0:r0 + 16, c0:c0 + 24].astype(np.float32)
    bl = np.array(meta.get("black", [0, 0, 0, 0]), np.float32)
    blk = np.empty_like(crop); blk[0::2, 0::2], blk[0::2, 1::2], blk[1::2, 0::2], blk[1::2, 1::2] = bl
    v = ((crop - blk).clip(0, None) / (np.percentile(crop - blk, 99) + 1e-6)).clip(0, 1) ** (1 / 2.2)
    s = PW // 24; z3 = Image.new("RGB", (24 * s, 16 * s), (10, 14, 20)); d3 = ImageDraw.Draw(z3)
    for y in range(16):
        for x in range(24):
            col = [(1, 0.18, 0.15), (0.2, 1, 0.3)][x % 2] if y % 2 == 0 else [(0.2, 1, 0.3), (0.2, 0.35, 1)][x % 2]
            d3.rectangle([x * s + 1, y * s + 1, x * s + s - 2, y * s + s - 2], fill=tuple(int(255 * (0.08 + 0.92 * v[y, x]) * c) for c in col))
    hh = max(z1.height, z2.height, z3.height); gap = 28
    img = Image.new("RGB", (3 * PW + 4 * gap, hh + 2 * gap + 44), (12, 22, 36)); d = ImageDraw.Draw(img)
    for i, (z, label) in enumerate(((z1, "1  The whole frame"), (z2, "2  One-eighth of it"), (z3, "3  The stored samples"))):
        x0 = gap + i * (PW + gap); img.paste(z, (x0, gap + (hh - z.height) // 2)); d.text((x0, hh + gap + 8), label, font=F, fill=(214, 226, 240))
    k1 = PW / full.width                                       # mark the close-up on panel 1, the samples on panel 2
    d.rectangle([gap + bx * k1, gap + (hh - z1.height) // 2 + by * k1, gap + (bx + cw) * k1, gap + (hh - z1.height) // 2 + (by + ch) * k1], outline=(111, 182, 240), width=3)
    k2 = PW / cw; sx, sy = (c0 // 2 - bx) * k2, (r0 // 2 - by) * k2
    d.rectangle([gap + PW + gap + sx, gap + (hh - z2.height) // 2 + sy, gap + PW + gap + sx + 12 * k2, gap + (hh - z2.height) // 2 + sy + 8 * k2], outline=(111, 182, 240), width=3)
    save(img, sys.argv[5])
elif MODE == "damage":                          # illustration: tile grid, one tile refused, one tile decoded on its own
    from PIL import ImageFont
    m, meta = load(sys.argv[4]); width = int(sys.argv[6]) if len(sys.argv) > 6 else 1400
    img = preview(m, meta, width=width)
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(24, img.width // 48)); scale = img.width / (m.shape[1] / 2); t = 256 * scale
    d = ImageDraw.Draw(img, "RGBA"); xs = np.arange(0, img.width, t); ys = np.arange(0, img.height, t)
    for x in xs: d.line([(x, 0), (x, img.height)], fill=(255, 255, 255, 120), width=2)
    for y in ys: d.line([(0, y), (img.width, y)], fill=(255, 255, 255, 120), width=2)
    bx, by = xs[len(xs) * 2 // 3], ys[len(ys) // 2]           # the refused tile: blanked, crossed, labelled
    d.rectangle([bx, by, bx + t, by + t], fill=(150, 20, 20, 215), outline=(255, 120, 110, 255), width=5)
    d.line([(bx + 14, by + 14), (bx + t - 14, by + t - 14)], fill=(255, 210, 205, 255), width=6)
    d.line([(bx + t - 14, by + 14), (bx + 14, by + t - 14)], fill=(255, 210, 205, 255), width=6)
    d.text((bx + t / 2, by + t + 10), "damaged tile: refused", font=F, fill=(255, 255, 255, 255), anchor="ma", stroke_width=3, stroke_fill=(120, 10, 10, 255))
    gx, gy = xs[len(xs) // 5], ys[len(ys) // 4]               # a region decoded on its own
    d.rectangle([gx, gy, gx + 2 * t, gy + t], outline=(64, 170, 255, 255), width=6, fill=(64, 170, 255, 45))
    d.text((gx + t, gy - 12), "region decoded on its own", font=F, fill=(255, 255, 255, 255), anchor="md", stroke_width=3, stroke_fill=(8, 50, 100, 255))
    if img.width > width: img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    save(img, sys.argv[5])
elif MODE == "roundtrip":                       # proof panel from a real round trip: source | decoded | difference
    from PIL import ImageFont
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    m, meta = load(sys.argv[4]); pgm = sys.argv[6]                # the decoder's output for this frame
    raw = open(pgm, "rb").read(); parts = raw.split(b"\n", 3); w, h = map(int, parts[1].split());
    dec = np.frombuffer(parts[3][:2 * w * h], dtype=">u2").reshape(h, w)
    src = np.asarray(m)[:h, :w]
    diff = int((dec.astype(np.int64) != src.astype(np.int64)).sum())
    PW = 560
    a = preview(src, meta); b = preview(dec, meta)
    a = a.resize((PW, round(a.height * PW / a.width)), Image.LANCZOS); b = b.resize(a.size, Image.LANCZOS)
    c = Image.new("RGB", a.size, (0, 0, 0)); dc = ImageDraw.Draw(c)
    dc.text((PW // 2, a.height // 2 - 26), f"{diff:,}", font=FB, fill=(111, 220, 140), anchor="mm")
    dc.text((PW // 2, a.height // 2 + 26), f"of {h * w:,} samples differ", font=F, fill=(200, 214, 230), anchor="mm")
    gap = 28; img = Image.new("RGB", (3 * PW + 4 * gap, a.height + 2 * gap + 44), (12, 22, 36)); d = ImageDraw.Draw(img)
    for i, (z, label) in enumerate(((a, "Source raw frame"), (b, "Decoded from the compressed file"), (c, "Difference, sample by sample"))):
        x0 = gap + i * (PW + gap); img.paste(z, (x0, gap)); d.text((x0, a.height + gap + 8), label, font=F, fill=(214, 226, 240))
    save(img, sys.argv[5]); print("ROUNDTRIP", w, h, h * w, "differ", diff)
elif MODE == "phantom":                         # generated CT test phantom (Shepp-Logan, Toft's modified): no patient data
    from PIL import ImageFont
    E = [(1, .69, .92, 0, 0, 0), (-.8, .6624, .874, 0, -.0184, 0), (-.2, .11, .31, .22, 0, -18), (-.2, .16, .41, -.22, 0, 18),
         (.1, .21, .25, 0, .35, 0), (.1, .046, .046, 0, .1, 0), (.1, .046, .046, 0, -.1, 0), (.1, .046, .023, -.08, -.605, 0),
         (.1, .023, .023, 0, -.606, 0), (.1, .023, .046, .06, -.605, 0)]
    def ph(n, sc=1.0, z=0.0):
        yy, xx = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]; img = np.zeros((n, n))
        for A, a, b, x0, y0, phi in E:
            ca, sa = np.cos(np.radians(phi)), np.sin(np.radians(phi))
            # a "slice": the small inner features shrink away from the mid-plane
            k = sc if abs(A) < .5 else 1.0
            X, Y = (xx - x0) * ca + (yy - y0) * sa, -(xx - x0) * sa + (yy - y0) * ca
            img[(X / (a * k)) ** 2 + (Y / (b * k)) ** 2 <= 1] += A
        return img
    def show(p):                                               # display window, slight blue-grey tint
        v = (p.clip(0, 1.05) / 1.05) ** 0.8
        return Image.fromarray((np.stack([v * 225 + 12, v * 232 + 14, v * 240 + 18], -1)).astype(np.uint8))
    kind = sys.argv[4]
    if kind == "banner":
        W, H = 1800, 620; img = Image.new("RGB", (W, H), (8, 18, 32)); n = 400
        for i, sc in enumerate((.6, .85, 1.0, .85)):              # four "slices", side by side, none overlapping
            p = ph(n, sc); s = show(p); x = 560 + i * 310
            img.paste(s.crop((50, 0, n - 50, n)), (x, (H - n) // 2), Image.fromarray(((p > 0.005) * 255).astype(np.uint8)).crop((50, 0, n - 50, n)))
        d = ImageDraw.Draw(img, "RGBA")
        for x in range(0, W, 64): d.line([(x, 0), (x, H)], fill=(120, 170, 230, 22))
        for y in range(0, H, 64): d.line([(0, y), (W, y)], fill=(120, 170, 230, 22))
        save(img, sys.argv[5])
    else:                                                      # tiles: 1024 x 1024 phantom, 4 x 4 tiles, one refused
        F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        n = 1024; img = show(ph(n)).convert("RGB"); d = ImageDraw.Draw(img, "RGBA"); t = 256
        for x in range(0, n + 1, t): d.line([(x, 0), (x, n)], fill=(255, 255, 255, 110), width=3)
        for y in range(0, n + 1, t): d.line([(0, y), (n, y)], fill=(255, 255, 255, 110), width=3)
        bx, by = 2 * t, t
        d.rectangle([bx, by, bx + t, by + t], fill=(150, 20, 20, 220), outline=(255, 120, 110, 255), width=6)
        d.line([(bx + 20, by + 20), (bx + t - 20, by + t - 20)], fill=(255, 210, 205, 255), width=8)
        d.line([(bx + t - 20, by + 20), (bx + 20, by + t - 20)], fill=(255, 210, 205, 255), width=8)
        d.text((bx + t / 2, by + t + 14), "refused, with a numbered reason", font=F, fill=(255, 255, 255), anchor="ma", stroke_width=3, stroke_fill=(120, 10, 10))
        save(img.resize((760, 760), Image.LANCZOS), sys.argv[5])
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
