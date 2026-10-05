"""The 100on100 logo, "pixel zeros" (owner's choice, 2026-10-05), drawn as pure geometry: no font.

usage: python3 tools/brand.py      (writes brand/*.svg, favicon.svg, favicon.ico, apple-touch-icon.png)

Wordmark: 1 0 0 on 1 0 0, where every zero is a square pixel frame and the last zero holds one lit
pixel. Mark: the last two zeros, side by side, the second lit. (A single frame with a centred square
was dropped: it reads too close to an existing well-known payments logo. The lit pixel sits
low right, never centred, and the icon tile has tight corners, per the logo screen.)
All shapes are rectangles and arcs on a 40-unit cap height, so the logo renders the same everywhere.
"""
import io, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(ROOT, "brand"), exist_ok=True)

CAP, XH = 40, 28                 # cap height; x-height of "on"
W1, WZ, WALL, GAP = 22, 26, 6, 5  # width of "1", width of a zero, zero wall, letter gap
PIX = 8                           # the lit pixel
PX_X, PX_Y = WZ - WALL - PIX - 2, CAP - WALL - PIX - 3   # off-centre, low right: never concentric (logo screen 2026-10-04)


def one(x):
    """A monospaced-style 1: stem, flag, foot."""
    return (f'<path d="M{x + 8} 0h7v34h6v6h-19v-6h6V8.5l-6 3.5V5.6z"/>')


def zero(x, lit=False):
    """A square pixel frame, cap height; optionally the lit pixel inside."""
    s = (f'<path fill-rule="evenodd" d="M{x} 0h{WZ}v{CAP}h-{WZ}z M{x + WALL} {WALL}v{CAP - 2 * WALL}'
         f'h{WZ - 2 * WALL}v-{CAP - 2 * WALL}z"/>')
    if lit:
        s += (f'<rect class="ac" x="{x + PX_X}" y="{PX_Y}" width="{PIX}" height="{PIX}"/>')
    return s


def o(x):
    """Lower-case o: a ring on the x-height."""
    r, rin, cx, cy = XH / 2, XH / 2 - 6, x + XH / 2, CAP - XH / 2
    return (f'<path class="ac" fill-rule="evenodd" d="M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 -{2 * r} 0z'
            f'M{cx - rin} {cy}a{rin} {rin} 0 1 0 {2 * rin} 0a{rin} {rin} 0 1 0 -{2 * rin} 0z"/>')


def n(x):
    """Lower-case n: two stems joined by an arch."""
    w, t, top = 24, 6, CAP - XH
    ro, ri = w / 2, w / 2 - t
    return (f'<path class="ac" d="M{x} {CAP}V{top + ro}a{ro} {ro} 0 0 1 {w} 0V{CAP}h-{t}V{top + ro}'
            f'a{ri} {ri} 0 0 0 -{2 * ri} 0V{CAP}z"/>')


def wordmark():
    parts, x = [], 0
    parts.append(one(x)); x += W1 + GAP - 2
    parts.append(zero(x)); x += WZ + GAP
    parts.append(zero(x)); x += WZ + GAP + 3
    parts.append(o(x)); x += XH + GAP - 1
    parts.append(n(x)); x += 24 + GAP + 3
    parts.append(one(x)); x += W1 + GAP - 2
    parts.append(zero(x)); x += WZ + GAP
    parts.append(zero(x, lit=True)); x += WZ
    return "".join(parts), x


def mark():
    """The last two zeros: one frame, one lit."""
    return zero(0) + zero(WZ + GAP, lit=True), 2 * WZ + GAP


def svg(body, w, h, fg, ac, pad=0, bg=None, rx=0, extra_style=""):
    vb = f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"
    back = f'<rect x="{-pad}" y="{-pad}" width="{w + 2 * pad}" height="{h + 2 * pad}" rx="{rx}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="100on100">'
            f'<style>path,rect{{fill:{fg}}} .ac{{fill:{ac}}}{extra_style}</style>{back}<g>{body}</g></svg>')


BLUE, DEEP, INK, SKY = "#0d4f91", "#0a2f57", "#16243a", "#7cc0ff"
wm, ww = wordmark()
mk, mw = mark()
out = {
    "brand/100on100-wordmark.svg": svg(wm, ww, CAP, INK, BLUE, pad=2),
    "brand/100on100-wordmark-white.svg": svg(wm, ww, CAP, "#ffffff", SKY, pad=2),
    "brand/100on100-mark.svg": svg(mk, mw, CAP, INK, BLUE, pad=2),
    "brand/100on100-mark-white.svg": svg(mk, mw, CAP, "#ffffff", SKY, pad=2),
}
# favicon.svg: the mark on a rounded brand-blue square, readable on light and dark tabs
fav_pad = 12
side = mw + 2 * fav_pad
fy = (side - CAP) / 2
out["favicon.svg"] = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side} {side}">'
                      f'<rect width="{side}" height="{side}" rx="{side * 0.07:.1f}" fill="{BLUE}"/>'
                      f'<g transform="translate({fav_pad} {fy})" fill="#ffffff">'
                      + mk.replace('class="ac"', f'fill="{SKY}"') + "</g></svg>")
for p, s in out.items():
    open(os.path.join(ROOT, p), "w").write(s)
    print(p, len(s))
# the wordmark as a fragment for the site header: inherits colour, accent from the page tokens
open(os.path.join(ROOT, "brand", "wordmark-inline.svg"), "w").write(
    f'<svg class="logo" viewBox="-2 -2 {ww + 4} {CAP + 4}" role="img" aria-label="100on100" '
    f'xmlns="http://www.w3.org/2000/svg"><g style="fill:currentColor">'
    + wm.replace('class="ac"', 'style="fill:var(--brand)"') + "</g></svg>")


# raster favicons, drawn directly from the same geometry (no SVG renderer needed)
def raster(px):
    k = 8                                        # supersample
    S = px * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.07), fill=(13, 79, 145, 255))
    u = S / side                                 # units to pixels
    ox, oy = fav_pad * u, fy * u
    for zx, lit in ((0, False), (WZ + GAP, True)):
        x0, y0 = ox + zx * u, oy
        d.rectangle([x0, y0, x0 + WZ * u - 1, y0 + CAP * u - 1], fill=(255, 255, 255, 255))
        d.rectangle([x0 + WALL * u, y0 + WALL * u, x0 + (WZ - WALL) * u - 1, y0 + (CAP - WALL) * u - 1],
                    fill=(13, 79, 145, 255))
        if lit:
            px0, py0 = x0 + PX_X * u, y0 + PX_Y * u
            d.rectangle([px0, py0, px0 + PIX * u - 1, py0 + PIX * u - 1], fill=(124, 192, 255, 255))
    return im.resize((px, px), Image.LANCZOS)


icons = [raster(s) for s in (16, 32, 48)]
icons[2].save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)], append_images=icons[:2])
raster(180).save(os.path.join(ROOT, "apple-touch-icon.png"))
raster(512).save(os.path.join(ROOT, "brand", "100on100-icon-512.png"))
print("favicon.ico, apple-touch-icon.png, brand/100on100-icon-512.png")
