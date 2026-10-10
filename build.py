"""Build the 100on100 site: shared utility bar, masthead, sitemap footer and stylesheet; the pages below.

usage: python3 build.py        (writes the .html files next to this script)
Static output only: no script in the pages, nothing loaded from another server, no cookies.
Every figure on the site is backed by a 100on100 test record, available to evaluators under NDA.
Illustrations are SVG generated here from the subject's own objects, coloured from site.css tokens.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
part = lambda n: open(os.path.join(HERE, "parts", n)).read()

# ------------------------------------------------------------------ illustrations (generated SVG)
def svg(w, h, inner, label):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" '
            f'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">{inner}</svg>')


def txt(x, y, s, size=13, weight=600, fill="var(--ink)", anchor="start", mono=True):
    fam = "var(--mono)" if mono else "var(--sans)"
    return (f'<text x="{x}" y="{y}" style="font:{weight} {size}px {fam};fill:{fill}" '
            f'text-anchor="{anchor}">{s}</text>')


def art_mosaic(fg="var(--ink)"):
    """The raw sensor mosaic: an RGGB Bayer pattern, the data 100on100 stores before demosaicing."""
    cells, c = [], 30
    for y in range(6):
        for x in range(10):
            col = ("var(--r)", "var(--g)")[x % 2] if y % 2 == 0 else ("var(--g)", "var(--b)")[x % 2]
            op = 0.55 + 0.45 * (((x * 7 + y * 13) % 10) / 10)
            cells.append(f'<rect x="{10 + x * c}" y="{10 + y * c}" width="{c - 3}" height="{c - 3}" rx="2" '
                         f'style="fill:{col};opacity:{op:.2f}"/>')
    return svg(320, 220, "".join(cells) + txt(10, 212, "R G G B · raw sensor mosaic, 1 sample per site", 11, 600, fg),
               "A raw RGGB sensor mosaic")


def art_tiles():
    """256 x 256 tiles: decode one region, or spread a frame over machines."""
    out, c = [], 36
    for y in range(4):
        for x in range(7):
            hi = (x, y) == (4, 1)
            cls = ' class="tile-hi"' if hi else ""
            fill = "var(--brand)" if hi else "var(--ground)"
            out.append(f'<rect{cls} x="{12 + x * c}" y="{12 + y * c}" width="{c - 4}" height="{c - 4}" '
                       f'style="fill:{fill};stroke:var(--rule);stroke-width:1.5"/>')
    out.append(txt(12, 178, "one tile decoded · 256 × 256", 12, 600, "var(--ink-soft)"))
    return svg(270, 190, "".join(out), "A frame divided into tiles with one tile decoded")


def art_hashes(fg="var(--ink)", soft="var(--ink-soft)", box="var(--ground)", stroke="var(--rule)", val="var(--g)"):
    """One stream, four instruction sets, one result."""
    out = []
    for k, isa in enumerate(["x86-64", "ARM aarch64", "RISC-V RV64", "WebAssembly"]):
        y = 8 + k * 44
        out.append(f'<rect x="8" y="{y}" width="300" height="36" rx="3" style="fill:{box};stroke:{stroke}"/>')
        out.append(txt(20, y + 23, isa, 13, 700, fg))
        out.append(txt(296, y + 23, "1267710892", 13, 700, val, "end"))
    out.append(txt(8, 196, "one test stream · four instruction sets · one result", 11, 500, soft))
    return svg(316, 204, "".join(out), "Four instruction sets decode one stream to the same value 1267710892")


def art_refuse():
    """A damaged file meets the decoder: refused with its number."""
    out = ['<rect x="10" y="20" width="200" height="120" rx="4" style="fill:var(--ground);stroke:var(--rule)"/>',
           txt(22, 46, "incoming file", 13, 700), txt(22, 70, "header ✓", 12, 500, "var(--ink-soft)"),
           txt(22, 90, "tile 7 ✗", 12, 500, "var(--ink-soft)"),
           '<rect x="22" y="104" width="120" height="10" style="fill:var(--rule)"/>',
           '<rect x="96" y="104" width="22" height="10" style="fill:var(--refuse)"/>',
           '<g transform="rotate(-8 230 92)"><rect x="150" y="60" width="150" height="64" rx="4" '
           'style="fill:var(--ground);stroke:var(--refuse);stroke-width:3"/>',
           txt(225, 90, "REFUSED", 18, 800, "var(--refuse)", "middle"),
           txt(225, 112, "tile checksum", 12, 700, "var(--refuse)", "middle"), "</g>"]
    return svg(310, 160, "".join(out), "A damaged file refused with a numbered reason")


def art_archive():
    """A self-decoding archive: the decoder travels inside the file."""
    out = ['<rect x="10" y="10" width="290" height="150" rx="4" style="fill:var(--ground);stroke:var(--rule)"/>',
           txt(24, 36, "archive file", 13, 700),
           '<rect x="24" y="50" width="110" height="94" rx="3" style="fill:var(--brand)"/>',
           txt(79, 92, "decoder", 13, 700, "var(--brand-ink)", "middle"),
           txt(79, 112, "27,272 octets", 11, 600, "var(--brand-ink)", "middle"),
           txt(79, 128, "stack reserved", 9, 500, "var(--brand-ink)", "middle")]
    for k in range(6):
        out.append(f'<rect x="148" y="{52 + k * 15}" width="{136 - (k * 13) % 40}" height="9" style="fill:var(--rule)"/>')
    out.append(txt(148, 146, "image data", 11, 600, "var(--ink-soft)"))
    return svg(310, 170, "".join(out), "An archive file that carries its own decoder")


def art_sdk():
    """The SDK surface, as in the evaluation release header."""
    lines = ["rc = i100_probe(buf, len, &info);", "rc = i100_decode_tile(buf, len, 0, 7,",
             "        ws, ws_len, out, n, &tw, &th);", "if (rc) printf(\"refused: %d\\n\", rc);"]
    out = ['<rect x="8" y="8" width="304" height="150" rx="4" style="fill:var(--ground);stroke:var(--rule)"/>']
    for k, l in enumerate(lines):
        out.append(txt(22, 42 + k * 28, l.replace("&", "&amp;").replace("<", "&lt;"), 12, 500))
    out.append(txt(22, 150, "the library interface in the evaluation release", 10, 500, "var(--ink-soft)"))
    return svg(320, 166, "".join(out), "Illustration of a decode SDK call sequence")


# ------------------------------------------------------------------ head to head (research/compete-results.md, owner-approved 2026-10-05)
SIZES = [("100on100 v4 C99 (small build)", 9075, True), ("CCSDS 121 · libaec", 6435, False), ("JPEG-LS · CharLS", 84335, False),
         ("JPEG 2000 · OpenJPEG", 176050, False), ("JPEG XL · libjxl", 713139, False)]
DAMAGE = [("100on100", 9600, 0, 0), ("JPEG XL", 9569, 31, 0), ("JPEG-LS", 8032, 896, 672),
          ("CCSDS 121", 5052, 4548, 0), ("JPEG 2000", 2402, 7196, 0)]     # refused, wrong-as-success, slow refusal (> 5 s)


def chart_size():
    """Decoder code + data, octets, linear scale: the scale IS the message."""
    W, L, R, top, bh, gap = 720, 236, 150, 14, 26, 14
    mx = max(v for _, v, _ in SIZES); out = []
    for k, (name, v, ours) in enumerate(SIZES):
        y = top + k * (bh + gap); w = max(3, (W - L - R) * v / mx)
        fill = "var(--brand)" if ours else "var(--ink-soft)"
        mult = "" if ours else (f"{v / 9075:.0f}× larger" if v > 9075 else "smaller, simpler coder")
        out.append(txt(L - 10, y + 18, name, 13, 700 if ours else 500, "var(--ink)", "end", False))
        out.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="{bh}" rx="2" style="fill:{fill};opacity:{1 if ours else .55}"/>')
        out.append(txt(L + w + 8, y + 18, f"{v:,}" + (f"  ·  {mult}" if mult else ""), 12, 700 if ours else 500, "var(--ink)", "start", False))
    h = top + len(SIZES) * (bh + gap) + 6
    out.append(txt(L, h + 8, "decoder code + data, octets · built and measured the same way", 11, 500, "var(--ink-soft)", "start", False))
    return svg(W, h + 16, "".join(out), "Decoder sizes: 100on100 9,075 octets; libaec 6,435; CharLS 84,335; OpenJPEG 176,050; libjxl 713,139")


def chart_damage():
    """9,600 damaged files per codec: refused, slow refusal, wrong image reported as success."""
    W, L, top, bh, gap = 680, 110, 14, 26, 14; B = W - L - 70; out = []
    for k, (name, ref, wrong, slow) in enumerate(DAMAGE):
        y = top + k * (bh + gap); n = 9600; x = L
        out.append(txt(L - 10, y + 18, name, 13, 700 if k == 0 else 500, "var(--ink)", "end", False))
        for v, col in ((ref, "var(--g)"), (slow, "#d9a441"), (wrong, "var(--refuse)")):
            if v:
                w = B * v / n; out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bh}" style="fill:{col}"/>'); x += w
        out.append(txt(L + B + 8, y + 18, f"{100 * wrong / n:.1f}%" if wrong else "0", 13, 800, "var(--refuse)" if wrong else "var(--g)", "start", False))
    h = top + len(DAMAGE) * (bh + gap)
    lx = L
    for lab, col in (("refused", "var(--g)"), ("refused late", "#d9a441"), ("wrong image reported as success", "var(--refuse)")):
        out.append(f'<rect x="{lx}" y="{h + 2}" width="12" height="12" style="fill:{col}"/>'); out.append(txt(lx + 18, h + 13, lab, 11, 600, "var(--ink-soft)", "start", False))
        lx += 26 + 7 * len(lab)
    return svg(W, h + 22, "".join(out), "Damaged files: wrong images reported as success: 100on100 0%, JPEG XL 0.3%, JPEG-LS 9.3%, CCSDS 121 47.4%, JPEG 2000 75.0%")


FAIR = ("100on100 checks a checksum over its header and over every tile, so any change to the data is caught and refused. "
        "CCSDS 121 streams and JPEG 2000 codestreams carry no integrity check over the coded data, by design; JPEG XL and JPEG-LS "
        "catch most damage through their own decoding, but not all.")
METHOD = ("Method: libjxl 0.11.2, OpenJPEG 2.5.4, CharLS 2.4.3 and libaec 1.1.6, each built from its release source the same way "
          "(size-optimised, unused code removed, runtime libraries not counted). 24 raw camera crops (CC0) encoded losslessly by every codec; "
          "each file then damaged 400 ways (one bit flipped, 4 octets overwritten, 16 octets zeroed, cut short), identically for every codec: "
          "9,600 damaged files per codec, 48,000 in all.")


EVX = """
  <div class="tablewrap" style="margin-top:22px"><table class="data"><thead><tr><th>9,600 damaged files each</th><th>refused</th><th>wrong image, reported as success</th><th>refused late</th><th>crash</th></tr></thead><tbody>
    <tr><td><strong>100on100</strong></td><td class="n"><strong>9,600</strong></td><td class="n"><strong>0</strong></td><td class="n">0</td><td class="n">0</td></tr>
    <tr><td>JPEG XL (libjxl)</td><td class="n">9,569</td><td class="n">31 (0.3%)</td><td class="n">0</td><td class="n">0</td></tr>
    <tr><td>JPEG-LS (CharLS)</td><td class="n">8,032</td><td class="n">896 (9.3%)</td><td class="n">672 (7.0%)</td><td class="n">0</td></tr>
    <tr><td>CCSDS 121 (libaec)</td><td class="n">5,052</td><td class="n">4,548 (47.4%)</td><td class="n">0</td><td class="n">0</td></tr>
    <tr><td>JPEG 2000 (OpenJPEG)</td><td class="n">2,402</td><td class="n">7,196 (75.0%)</td><td class="n">0</td><td class="n">0</td></tr>
  </tbody></table></div>
  <p class="note"><strong>The wrong images are subtle.</strong> Checked independently, single-bit damage changed JPEG XL images by 1 to 268 samples (off by at most 24) and JPEG 2000 images by up to 16,000 samples (off by at most 80), and each was reported as a successful decode: a picture that looks right and is not. JPEG-LS refused some damaged files only late. JPEG 2000 also decoded 2 damaged files exactly.</p>"""


def head2head(intro, extra=""):
    return f"""
<section aria-labelledby="h2h-h"><div class="wrap">
  <div class="head"><p class="label">Head to head</p><h2 id="h2h-h">Smaller decoder. No undetected corruption.</h2><p>{intro}</p></div>
  <div class="opsrow">
    <figure class="ops">{chart_size()}<figcaption><strong>9,075 octets (original version 4 C99 library, small build): 79× smaller than JPEG XL, 19× smaller than JPEG 2000, 9× smaller than JPEG-LS.</strong> CCSDS 121 is smaller still: a simpler coder, which 100on100 out-compresses.</figcaption></figure>
    <figure class="ops">{chart_damage()}<figcaption><strong>0 of 9,600 damaged files produced undetected corruption: every one was refused.</strong> JPEG XL 0.3%, JPEG-LS 9.3%, CCSDS 121 47%, JPEG 2000 75% decoded to a wrong image and reported success.</figcaption></figure>
  </div>
  <p class="note">{FAIR}</p>{extra}
  <p class="cite">{METHOD} <a href="evidence.html#h2h-h">Full results</a>.</p>
</div></section>"""


# ------------------------------------------------------------------ operational scenes: where the decoder sits in a real flow
S = "fill:none;stroke:var(--ink);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round"


def icon(kind, x, y):
    """Small line icons, drawn around (x, y), about 56 px across."""
    g = {
        "drone": f'<path d="M{x-22} {y-10}h16M{x+6} {y-10}h16M{x-14} {y-10}v6M{x+14} {y-10}v6" style="{S}"/>'
                 f'<rect x="{x-16}" y="{y-4}" width="32" height="14" rx="4" style="{S}"/><circle cx="{x}" cy="{y+16}" r="5" style="{S}"/>',
        "sat": f'<rect x="{x-8}" y="{y-10}" width="16" height="20" rx="2" style="{S}"/>'
               f'<path d="M{x-8} {y}h-6M{x+8} {y}h6" style="{S}"/><rect x="{x-34}" y="{y-9}" width="20" height="18" style="{S}"/>'
               f'<rect x="{x+14}" y="{y-9}" width="20" height="18" style="{S}"/><path d="M{x} {y+10}v8" style="{S}"/>',
        "scanner": f'<circle cx="{x}" cy="{y-2}" r="20" style="{S}"/><circle cx="{x}" cy="{y-2}" r="9" style="{S}"/>'
                   f'<path d="M{x-28} {y+18}h56" style="{S}"/>',
        "dish": f'<path d="M{x-18} {y-14}a24 24 0 0 0 30 22z" style="{S}"/><path d="M{x+1} {y-4}l10 -10M{x-2} {y+8}v12M{x-14} {y+20}h24" style="{S}"/>',
        "rack": f'<rect x="{x-18}" y="{y-20}" width="36" height="40" rx="3" style="{S}"/>'
                f'<path d="M{x-11} {y-10}h22M{x-11} {y}h22M{x-11} {y+10}h22" style="{S}"/>',
        "screens": f'<rect x="{x-30}" y="{y-16}" width="26" height="20" rx="2" style="{S}"/><rect x="{x+4}" y="{y-16}" width="26" height="20" rx="2" style="{S}"/>'
                   f'<path d="M{x-17} {y+4}v8M{x+17} {y+4}v8M{x-24} {y+12}h14M{x+10} {y+12}h14" style="{S}"/>',
    }[kind]
    return g


def art_ops(steps, link, foot, label):
    """steps: three (icon, title, line1, line2, accent) stations; link: the label on the first hop."""
    W, out = 660, []
    xs = [90, 330, 570]
    for k, (ic, title, l1, l2, acc) in enumerate(steps):
        x = xs[k]
        out.append(f'<rect x="{x-80}" y="24" width="160" height="172" rx="6" style="fill:var(--ground);stroke:{acc};stroke-width:{2.5 if acc != "var(--rule)" else 1.5}"/>')
        out.append(icon(ic, x, 74))
        out.append(txt(x, 128, title, 14, 800, "var(--ink)", "middle", False))
        out.append(txt(x, 152, l1, 12, 500, "var(--ink-soft)", "middle", False))
        out.append(txt(x, 170, l2, 12, 500, "var(--ink-soft)", "middle", False))
    for k in range(2):                                        # the hops between stations
        a, b = xs[k] + 84, xs[k + 1] - 84
        dash = ' stroke-dasharray="7 6"' if k == 0 else ""
        out.append(f'<path d="M{a} 110H{b - 8}" style="fill:none;stroke:var(--signal);stroke-width:3"{dash}/>'
                   f'<path d="M{b - 12} 102l10 8l-10 8" style="fill:none;stroke:var(--signal);stroke-width:3"/>')
    out.append(txt((xs[0] + xs[1]) // 2, 98, link, 11, 700, "var(--signal)", "middle"))
    out.append(txt(W // 2, 226, foot, 12, 600, "var(--ink-soft)", "middle", False))
    return svg(W, 236, "".join(out), label)


OPS_FIELD = art_ops([("drone", "At the edge", "camera keeps the raw", "frame, tile by tile", "var(--rule)"),
                     ("dish", "Ground station", "decodes the region", "it needs first", "var(--signal)"),
                     ("rack", "Analysis", "the same pixels on", "every tested machine", "var(--rule)")],
                    "narrow link", "A tile damaged on the link is refused by number; the rest of the frame still decodes.",
                    "Field flow: edge camera, narrow link, ground station decoding a region, analysis machines")
OPS_SPACE = art_ops([("sat", "On orbit", "raw samples, tiled,", "each with a checksum", "var(--rule)"),
                     ("dish", "Downlink", "tiles arrive; a bad", "one is set aside", "var(--signal)"),
                     ("rack", "Ground segment", "one result on every", "tested machine", "var(--rule)")],
                    "downlink", "Region of interest first; the full frame when the pass allows. Encoder for the payload in development.",
                    "Space flow: satellite, downlink, ground segment machines")
OPS_MED = art_ops([("scanner", "Modality", "writes the study", "losslessly", "var(--rule)"),
                   ("rack", "Archive", "keeps it for decades,", "decoder alongside", "var(--rule)"),
                   ("screens", "Viewers", "the same pixels, or", "a numbered refusal", "var(--refuse)")],
                  "hospital network", "Version 1.2.0 includes a decoder for single-channel and multi-plane images (greyscale, unsigned or signed, 1 to 16 bits); medical results are not yet published.",
                  "Medical flow: modality, archive, viewers showing identical pixels or a numbered refusal")


# ------------------------------------------------------------------ photographs: open-licence imagery, decoded by our own decoder
# Every photograph was encoded and decoded by 100on100 and compared sample by sample before it was rendered for display.
# Sources, licences and the round-trip records are in NOTICE (filled from the decode manifest).
OAM = "Imagery: International Organization for Migration (IOM), via OpenAerialMap, CC BY 4.0"
PHANTOM = "Generated Shepp–Logan test phantom: no patient data"
CREDIT = {"hero-coast": "Contains modified Copernicus Sentinel data 2026", "space-band": "Landsat 8 imagery courtesy of the U.S. Geological Survey (public domain)", "aerial-tiles": OAM, "aerial-plain": OAM, "phantom": PHANTOM}
DECODED = " · decoded by 100on100, 0 samples differ"


def credit(k):
    return CREDIT[k] + DECODED


def pic(k, alt):
    return (f'<img src="img/{k}.webp" srcset="img/{k}-sm.webp 600w, img/{k}.webp 1200w" sizes="(max-width: 900px) 100vw, 600px" '
            f'alt="{alt}" loading="lazy" decoding="async">')


def img_art(k, alt):
    return f'<div class="art img">{pic(k, alt)}</div>'


def shot(k, alt, caption):
    return f'<figure class="shot">{pic(k, alt)}<figcaption>{caption} <span class="credit">{credit(k)}</span></figcaption></figure>'


def svg_art(inner):
    return f'<div class="art">{inner}</div>'


# ------------------------------------------------------------------ hand-made scenes (speed, scale, edge to ground, decades)
DEFS = ('<defs><linearGradient id="gB" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1463d6"/><stop offset="1" stop-color="#22b8f0"/></linearGradient>'
         '<radialGradient id="gGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#39d0ff" stop-opacity=".55"/><stop offset="1" stop-color="#39d0ff" stop-opacity="0"/></radialGradient></defs>')
GRADS = ""   # the gradients are defined once per page (DEFS, in page())
W_ = "fill:none;stroke:#cfe3ff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"


def _drone(x, y, st=W_):
    return (f'<g class="drift"><path d="M{x-24} {y-9}h17M{x+7} {y-9}h17M{x-15} {y-9}v6M{x+15} {y-9}v6" style="{st}"/>'
            f'<rect x="{x-14}" y="{y-3}" width="28" height="12" rx="4" style="{st}"/><circle cx="{x}" cy="{y+14}" r="4" style="{st}"/></g>')


def _dish(x, y, st=W_):
    return (f'<path d="M{x-18} {y-14}a24 24 0 0 0 30 22z" style="{st}"/><path d="M{x+1} {y-4}l10 -10M{x-2} {y+8}v12M{x-14} {y+20}h24" style="{st}"/>')


def _sat(x, y, st=W_):
    return (f'<g class="drift"><rect x="{x-8}" y="{y-10}" width="16" height="20" rx="2" style="{st}"/><path d="M{x-8} {y}h-6M{x+8} {y}h6" style="{st}"/>'
            f'<rect x="{x-34}" y="{y-9}" width="20" height="18" style="{st}"/><rect x="{x+14}" y="{y-9}" width="20" height="18" style="{st}"/></g>')


def _tiles(x0, y0, cols, rows, c, lit=(), bad=(), dim="rgba(207,227,255,.10)", stroke="rgba(207,227,255,.35)"):
    out = []
    for y in range(rows):
        for x in range(cols):
            k = (x, y)
            fill = "url(#gB)" if k in lit else ("#ff5a5f" if k in bad else dim)
            cls = ' class="tile-hi"' if k in bad else ""
            out.append(f'<rect{cls} x="{x0 + x * c}" y="{y0 + y * c}" width="{c - 3}" height="{c - 3}" rx="3" style="fill:{fill};stroke:{stroke};stroke-width:1"/>')
    return "".join(out)


def hero_art():
    """Edge to ground: a drone sends its region tiles first over a narrow link; a damaged tile is refused and sent again."""
    lit = {(2, 1), (3, 1), (2, 2), (3, 2), (4, 1), (4, 2)}
    out = [GRADS, '<circle cx="420" cy="90" r="120" style="fill:url(#gGlow)"/>', _drone(80, 70),
           '<path class="flow" d="M100 96C190 150 250 150 330 128" style="fill:none;stroke:#39d0ff;stroke-width:3"/>',
           txt(150, 168, "narrow link", 12, 700, "#8fd3ff", "start"), _dish(512, 236),
           _tiles(250, 150, 7, 4, 30, lit, {(5, 2)}),
           '<path class="flow" d="M462 210C478 210 486 216 492 222" style="fill:none;stroke:#39d0ff;stroke-width:2"/>',
           txt(250, 296, "region first", 12, 700, "#cfe3ff"), txt(250, 316, "damaged tile refused, sent again", 12, 600, "#ff8a8e")]
    return svg(560, 330, "".join(out), "A drone sends the tiles of its region first over a narrow link to a ground station; a damaged tile is refused and sent again")


def art_swarm():
    """Scale: several aircraft share one picture over limited links."""
    pts = [(70, 60), (210, 40), (330, 80), (130, 150)]
    out = [GRADS]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            out.append(f'<path class="flow" d="M{a[0]} {a[1]+10}L{b[0]} {b[1]+10}" style="fill:none;stroke:var(--signal);stroke-width:1.6;opacity:.7"/>')
    S2 = "fill:none;stroke:var(--ink);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"
    out += [_drone(x, y, S2) for x, y in pts]
    out.append('<path class="flow" d="M130 172L290 188" style="fill:none;stroke:var(--signal);stroke-width:2"/>')
    out.append(_dish(300, 180, S2))
    out.append(_tiles(22, 196, 8, 1, 22, {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)}, (), "var(--panel)", "var(--rule)"))
    return svg(380, 230, "".join(out), "Four aircraft and a ground station share one picture over limited links")


def art_collab():
    """Aircraft and ground build the same picture together, tile by tile."""
    S2 = "fill:none;stroke:var(--ink);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"
    out = [GRADS, _drone(70, 50, S2), _dish(310, 60, S2),
           '<path class="flow" d="M100 60H280" style="fill:none;stroke:var(--signal);stroke-width:2.5"/>',
           '<path class="flow" d="M280 80H100" style="fill:none;stroke:var(--brand-2);stroke-width:2.5"/>',
           _tiles(22, 110, 5, 3, 24, {(0, 0), (1, 0), (1, 1), (2, 1)}, (), "var(--panel)", "var(--rule)"),
           _tiles(238, 110, 5, 3, 24, {(0, 0), (1, 0), (1, 1), (2, 1)}, (), "var(--panel)", "var(--rule)"),
           txt(190, 150, "=", 26, 800, "var(--brand)", "middle", False)]
    return svg(380, 200, "".join(out), "An aircraft and a ground station assemble the same tiles and hold the same picture")


def art_decades():
    """Archive for decades: the file carries its own decoder along a timeline."""
    out = [GRADS, '<path d="M20 150H360" style="stroke:var(--rule);stroke-width:3"/>']
    for i, yr in enumerate(["2026", "2036", "2046", "2056"]):
        x = 40 + i * 100
        out.append(f'<circle cx="{x}" cy="150" r="6" style="fill:url(#gB)"/>')
        out.append(txt(x, 178, yr, 12, 700, "var(--ink-soft)", "middle", False))
        out.append(f'<rect x="{x-30}" y="{60 - i * 6}" width="60" height="70" rx="6" style="fill:var(--surface);stroke:var(--rule)"/>')
        out.append(f'<rect x="{x-24}" y="{68 - i * 6}" width="48" height="20" rx="3" style="fill:url(#gB)"/>')
        for k in range(3):
            out.append(f'<rect x="{x-24}" y="{94 - i * 6 + k * 10}" width="{48 - k * 10}" height="5" style="fill:var(--rule)"/>')
    out.append(txt(20, 30, "image + the decoder that reads it, in one file", 12, 600, "var(--ink-soft)", "start", False))
    return svg(380, 190, "".join(out), "An archive file carrying its own decoder, readable along a timeline of decades")


def art_zoom():
    """From the whole frame to the samples the sensor stored."""
    out = [GRADS, '<rect x="14" y="20" width="170" height="120" rx="8" style="fill:url(#gB);opacity:.85"/>',
           '<path d="M22 120l40-40l30 26l36-46l48 60z" style="fill:#ffffff;opacity:.35"/>',
           '<rect x="120" y="60" width="30" height="24" rx="2" style="fill:none;stroke:#ffffff;stroke-width:2.5"/>',
           '<path d="M150 72L236 40M150 84L236 150" style="stroke:var(--ink-soft);stroke-width:1.2;stroke-dasharray:4 4"/>']
    c = 22
    for y in range(5):
        for x in range(6):
            col = ("var(--r)", "var(--g)")[x % 2] if y % 2 == 0 else ("var(--g)", "var(--b)")[x % 2]
            op = 0.55 + 0.45 * (((x * 7 + y * 13) % 10) / 10)
            out.append(f'<rect x="{236 + x * c}" y="{40 + y * c}" width="{c - 3}" height="{c - 3}" rx="2" style="fill:{col};opacity:{op:.2f}"/>')
    out.append(txt(14, 166, "whole frame", 11, 600, "var(--ink-soft)", "start", False))
    out.append(txt(236, 166, "one number per site", 11, 600, "var(--ink-soft)", "start", False))
    return svg(380, 176, "".join(out), "A frame, a magnified spot, and the raw red, green and blue samples the sensor stored there")


def art_roundtrip():
    """Encode, decode, compare: the difference is all zero."""
    out = [GRADS]
    for i, (lab, fill) in enumerate([("source", "url(#gB)"), ("decoded", "url(#gB)"), ("difference", "#050d1b")]):
        x = 14 + i * 124
        out.append(f'<rect x="{x}" y="24" width="110" height="90" rx="8" style="fill:{fill};stroke:var(--rule)"/>')
        if i < 2:
            out.append(f'<path d="M{x+8} {104}l26-30l20 16l24-32l32 46z" style="fill:#ffffff;opacity:.35"/>')
        out.append(txt(x + 55, 136, lab, 12, 700, "var(--ink-soft)", "middle", False))
    out.append(txt(14 + 248 + 55, 76, "0 differ", 15, 800, "#55cf8a", "middle", False))
    out.append(txt(131, 18, "=", 18, 800, "var(--brand)", "middle", False))
    return svg(380, 150, "".join(out), "Source, decoded and difference panels; the difference panel reads 0 differ")


def motif(seed=0):
    """Page-head motif: a wide field of tiles (one pattern), a few lit, the odd one refused."""
    c, out = 46, []
    for y in range(9):
        for x in range(28):
            h = (x * 31 + y * 17 + seed * 7) % 23
            if h == 0:
                fill, op = "url(#gB)", 0.9
            elif h == 11 and (x + y + seed) % 3 == 0:
                fill, op = "#ff5a5f", 0.7
            else:
                continue
            out.append(f'<rect class="tile-hi" x="{x * c}" y="{y * c}" width="{c - 6}" height="{c - 6}" rx="4" style="fill:{fill};opacity:{op}"/>')
    grid = (f'<pattern id="pg{seed}" width="{c}" height="{c}" patternUnits="userSpaceOnUse">'
            f'<rect width="{c - 6}" height="{c - 6}" rx="4" style="fill:none;stroke:rgba(143,211,255,.16)"/></pattern>')
    return (f'<div class="motif" aria-hidden="true"><svg viewBox="0 0 1288 414" preserveAspectRatio="xMaxYMid slice" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>{grid}</defs><rect width="1288" height="414" style="fill:url(#pg{seed})"/>{"".join(out)}</svg></div>')


# ------------------------------------------------------------------ applications: what the layer is for, with honest status
VID = "Video: our own animation of a recorded simulation run. " + OAM


def video(k, label):
    return (f'<video controls muted playsinline preload="none" poster="video/{k}-poster.webp" width="1280" height="720" aria-label="{label}">'
            f'<source src="video/{k}.webm" type="video/webm"><source src="video/{k}.mp4" type="video/mp4">'
            f'<track kind="captions" src="video/{k}.vtt" srclang="en" label="English" default></video>')


STATUS = {"sim": ("sim", "Demonstrated in simulation"), "dev": ("prog", "In development"), "plan": ("later", "Planned"), "ready": ("ready", "Released")}
APPS = {
    "swarm": ("sim", lambda: video("swarm-share", "Animation: aircraft share region tiles first over a narrow link"),
              "Aircraft sharing imagery over limited links",
              "Several aircraft and a ground station hold one shared picture. The tiles of the region that matters go first, each with its own checksum, so a useful picture arrives long before a whole frame would.", VID),
    "selfcorrect": ("sim", lambda: video("self-correct", "Animation: a damaged tile is refused and requested again"),
                    "Damaged tiles caught and sent again",
                    "Every tile is checked on arrival. A damaged tile is refused, never shown, and requested again, so the receiver ends with exactly the original pixels.", VID),
    "collab": ("plan", lambda: art_collab(), "Aircraft and ground analysing together",
               "Aircraft and the ground link work from the same tiles, so every party can show that it is looking at the same picture.", ""),
    "downlink": ("dev", lambda: video("downlink", "Animation: a satellite pass sends the region first, then the rest"),
                 "Space downlink, region first",
                 "During a pass, the region of interest comes down first and the rest when the pass allows; a damaged tile is set aside, not used. Decoders released; on-board encoder in development.", VID),
    "archive": ("plan", lambda: art_decades(), "Archives that last decades",
                "Files that carry the decoder that reads them, so a picture stored today opens when the software that wrote it is gone.", ""),
    "medical": ("dev", lambda: pic("phantom", "A generated CT test phantom in 16 tiles, one tile marked as refused"), "Medical archives",
                "Studies stored exactly, opened region by region, with a damaged tile refused by number. Version 1.2.0 includes a decoder for single-channel and multi-plane images; no DICOM support yet; medical measurements are not yet published.", PHANTOM + DECODED),
}


def apps(keys, wide_first=False):
    out = []
    for i, k in enumerate(keys):
        st, media, h, p, cr = APPS[k]
        cls, lab = STATUS[st]
        crd = f'<p class="credit">{cr}</p>' if cr else ""
        w = " wide" if wide_first and i == 0 else ""
        m = media()
        kind = "vid" if "<video" in m else ("pic" if m.startswith("<img") else "svg")
        out.append(f'<article class="app{w}"><div class="media {kind}">{m}</div><div class="body"><span class="state {cls}">{lab}</span><h3>{h}</h3><p>{p}</p>{crd}</div></article>')
    return f'<div class="apps">{"".join(out)}</div>'


LOGO = open(os.path.join(HERE, "brand", "wordmark-inline.svg")).read()   # from tools/brand.py



# ------------------------------------------------------------------ the edge points, in plain words
PLAIN_POINTS = [
    ("Every dot is kept",
     "Like packing crayons so carefully that none ever breaks: when you open the box, every crayon is exactly as it was.",
     {"defence": "Every pixel the camera captured arrives exactly as it was taken.",
      "space": "Every value the satellite's sensor recorded reaches the ground unchanged.",
      "medical": "Every value in a scan is kept, so nothing a clinician might need is thrown away."}),
    ("A small program you can check",
     "The program that opens the pictures is short, like a picture book instead of a phone book, so a grown-up can read every page.",
     {"defence": "At about 27 KiB (code and data; its stack is reserved, not stored), your security team can review all of it, not trust a black box.",
      "space": "About 27 KiB (code and data; its stack is reserved, not stored): small enough for a review team to read in full before it goes anywhere near a mission.",
      "medical": "About 27 KiB (code and data; its stack is reserved, not stored): small enough for your security and regulatory reviewers to read in full."}),
    ("It says no to broken files",
     "If a picture arrives broken, or someone has tampered with it, the program does not guess. It says \u201cthis one is broken\u201d and gives the reason as a number.",
     {"defence": "Crafted image files are a known way to attack computers. In our tests, every damaged or hostile file was either read exactly or turned away.",
      "space": "A file damaged on the way down is flagged, not quietly used as if it were good.",
      "medical": "A damaged study is refused with a reason, instead of being shown as a picture that looks right but is not."}),
    ("Same answer on every computer",
     "Like a sum that gives the same answer on every calculator: it uses whole numbers only, so different machines cannot drift apart.",
     {"defence": "Measured on laptop, ARM, RISC-V and browser chips: the same picture, so a receiver can prove it got what was sent.",
      "space": "The flight computer and every ground computer can agree on the exact same image.",
      "medical": "Two viewers on two different computers show exactly the same pixels."}),
    ("Open just one piece",
     "Like opening one page of a book without reading the whole book. The picture is cut into tiles, and you open only the tile you need. If one tile is damaged, the others still open.",
     {"defence": "Send or decode just the region you care about over a narrow link.",
      "space": "Pull down only the region of interest from orbit, and lose only a tile, not the frame, if a packet is damaged.",
      "medical": "Large images can be opened region by region."}),
]


def plain(industry, note=""):
    cards = "".join(
        f'<div class="card" style="grid-template-rows:auto"><div class="body"><h3>{t}</h3><p>{kid}</p>'
        f'<p><strong>For you:</strong> {per[industry]}</p></div></div>' for t, kid, per in PLAIN_POINTS)
    extra = f'<p class="note">{note}</p>' if note else ""
    return f"""
<section class="alt" aria-labelledby="plain-h"><div class="wrap">
  <div class="head"><p class="label">In plain words</p><h2 id="plain-h">What 100on100 does, simply</h2></div>
  <div class="cards">{cards}</div>{extra}
</div></section>"""

# ------------------------------------------------------------------ shared chrome
NAV = [("defence.html", "Defence"), ("space.html", "Space"), ("medical.html", "Medical devices"), ("products.html", "Products"),
       ("evidence.html", "Evidence"), ("company.html", "Company")]


def page(fname, title, desc, body):
    nav = "\n      ".join(f'<a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{t}</a>' for h, t in NAV)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="site.css">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">{DEFS}</svg>
<div class="util"><div class="wrap">
  <a href="downloads.html">Downloads</a><a href="services.html">Services</a><a href="company.html#contact">Contact</a>
</div></div>
<div class="mast-bg"><div class="wrap">
  <header class="mast">
    <a class="mark" href="index.html" aria-label="100on100 home">{LOGO}<small>Lossless imaging you can audit</small></a>
    <nav aria-label="Main">
      {nav}
      <a class="btn primary" href="company.html#contact">Request a briefing</a>
    </nav>
  </header>
</div></div>
<main>
{body}
</main>
<footer><div class="wrap">
  <div class="cols">
    <div><h4>Solutions</h4><ul><li><a href="defence.html">Defence and edge sensing</a></li><li><a href="space.html">Space and Earth observation</a></li><li><a href="medical.html">Medical devices</a></li><li><a href="products.html#archive">Long-term archives</a></li></ul></div>
    <div><h4>Products</h4><ul><li><a href="products.html#sdk">100on100 SDK</a></li><li><a href="products.html#attest">100on100 Attest</a></li><li><a href="products.html#archive">100on100 Archive</a></li><li><a href="services.html">Services</a></li></ul></div>
    <div><h4>Evidence</h4><ul><li><a href="evidence.html">Measurements</a></li><li><a href="evidence.html#compression">Compression</a></li><li><a href="downloads.html">Downloads</a></li></ul></div>
    <div><h4>Company</h4><ul><li><a href="company.html">About</a></li><li><a href="company.html#contact">Contact</a></li><li><a href="privacy.html">Privacy</a></li><li><a href="legal.html">Legal notice</a></li></ul></div>
  </div>
  <div class="base"><span>© 2026 FastBuilder.AI · 100on100 · Columbus, Ohio, USA</span><span>Binaries free for evaluation; production use licensed · no cookies, no analytics, nothing loaded from other servers</span></div>
</div></footer>
</body>
</html>
"""
    open(os.path.join(HERE, fname), "w").write(html)


def pagehead(crumb, h1, lead, photo=None, seed=0):
    if photo:
        return f"""<div class="pagehead photo" style="--img:url(img/{photo}.webp)"><div class="wrap">
  <p class="crumbs"><a href="index.html">Home</a> / {crumb}</p>
  <h1>{h1}</h1>
  <p>{lead}</p>
  <p class="credit">{credit(photo)}</p>
</div></div>"""
    return f"""<div class="pagehead">{motif(seed)}<div class="wrap">
  <p class="crumbs"><a href="index.html">Home</a> / {crumb}</p>
  <h1>{h1}</h1>
  <p>{lead}</p>
</div></div>"""


DEMO = f"""<div class="demo"><div class="wrap">
  <div>
    <p class="label">Briefing and demonstration</p>
    <h2>Come and see for yourself</h2>
    <p>We show 100on100 on your own data, at your site or in a remote session: the decoder, the refusals, the matching results, and where other codecs are smaller.</p>
    <a class="btn" href="company.html#contact">Request a briefing</a>
  </div>
  <div class="art">{art_hashes(fg="#ffffff", soft="#dbeaff", box="rgba(255,255,255,.06)", stroke="rgba(255,255,255,.55)", val="#9ff0c4")}</div>
</div></div>"""

STRIP = """<div class="strip">
  <div><span class="fig num">27,272</span><p>octets: the whole RISC-V decoder image, code and data (stack and heap reserved, not stored), for format versions 1 to 4 (original v4 image)</p></div>
  <div><span class="fig num">1</span><p>decoded result on x86-64, ARM, RISC-V and WebAssembly for a test stream</p></div>
  <div><span class="fig num">43 / 43</span><p>hard and hostile files decoded exactly or refused by number</p></div>
  <div><span class="fig num">284 / 284</span><p>corpus files where the C99 decoder matched the reference byte for byte (97 of 97 test vectors also)</p></div>
</div>
<p class="cite" style="margin-top:10px">Details on the <a href="evidence.html">evidence page</a>. Test records are available to evaluators under NDA.</p>"""

# ------------------------------------------------------------------ home (v3, 2026-10-09: performance first, then integrity, then other benefits; every figure from research/claims-register.md)
STRIP_PERF = """<div class="strip">
  <div><span class="fig num">10.01%</span><p>smaller than JPEG-LS on 67 raw camera sensors (pooled, untiled files); 4.81% smaller than FFV1</p></div>
  <div><span class="fig num">0.82%</span><p>larger than JPEG XL on the same sensors: we publish where others are ahead</p></div>
  <div><span class="fig num">9,075</span><p>octets: the original version 4 C99 decoder library (small build), with no allocation and no global state</p></div>
  <div><span class="fig num">256 × 256</span><p>tiles: decode a region alone, with every tile decoded alone equal to the whole decode</p></div>
</div>"""

STRIP_SEC = """<div class="strip">
  <div><span class="fig num">0 of 9,600</span><p>damaged files decoded wrong or went undetected. Every one was decoded exactly or refused by number</p></div>
  <div><span class="fig num">29.7 M</span><p>fuzzed inputs under AddressSanitizer and UBSan, with determinism and tile-consistency oracles: 0 issues</p></div>
  <div><span class="fig num">284 / 284</span><p>corpus files where the C99 decoder library equals the reference decoder octet for octet (97 of 97 test vectors too)</p></div>
  <div><span class="fig num">9,600</span><p>damaged files per codec, 48,000 in all: one bit flipped, 4 octets overwritten, 16 octets zeroed, cut short</p></div>
</div>
<p class="cite" style="margin-top:10px">Details on the <a href="evidence.html">evidence page</a>. Test records are available to evaluators under NDA.</p>"""

page("index.html", "100on100",
     "Lossless raw imaging: files smaller than JPEG-LS and FFV1, a 9,075-octet decoder library, and damaged files decoded exactly or refused by number.",
     f"""<div class="heroband photo" style="--img:url(img/hero-coast.webp)"><div class="wrap">
  <div>
    <p class="label">Lossless raw imaging</p>
    <h1 style="margin-top:14px">Raw images kept exactly, in smaller files, with a decoder small enough to read.</h1>
    <p class="lead">On 67 raw camera sensors, 100on100 files are smaller than JPEG-LS and FFV1 and slightly larger than JPEG XL. The original version 4 C99 decoder library (small build) is 9,075 octets, and a region of a frame decodes on its own. Every damaged file in our test was decoded exactly or refused with a numbered reason.</p>
    <div class="ctas"><a class="btn primary" href="company.html#contact">Request a briefing</a><a class="btn light" href="evidence.html">See the evidence</a></div>
  </div>
  <figure class="hero-art">{hero_art()}<figcaption>Region first over a narrow link; a damaged tile is refused and sent again. <span class="credit">Background: {credit("hero-coast")}</span></figcaption></figure>
</div></div>

<section aria-labelledby="perf-h"><div class="wrap">
  <div class="head"><p class="label">1 · Performance</p><h2 id="perf-h">Smaller files. A decoder that fits anywhere you can read it.</h2><p>Every figure comes from our own test records and can be checked by your engineers. Every raw sensor sample is kept, bit for bit, before demosaicing.</p></div>
  {STRIP_PERF}
</div></section>

<div class="wrap" style="padding-block:0 8px">{part("size.html")}</div>

<section class="alt" aria-labelledby="foot-h"><div class="wrap">
  <div class="head"><p class="label">Footprint and regions</p><h2 id="foot-h">Small to ship, and a region at a time</h2>
    <p>Decoder code and data, measured the same way for each codec. 256 × 256 tiles, each with its own checksum: decode a region alone, and tiles decoded alone equal the whole decode. We publish where others are smaller, too.</p></div>
  <figure class="ops">{chart_size()}<figcaption><strong>9,075 octets (original version 4 C99 library, small build): 79× smaller than JPEG XL, 19× smaller than JPEG 2000, 9× smaller than JPEG-LS.</strong> CCSDS 121 is smaller still at 6,435 octets: a simpler coder, which 100on100 out-compresses.</figcaption></figure>
</div></section>

<section aria-labelledby="v5-h"><div class="wrap">
  <div class="head"><p class="label">Colour pictures · format version 5</p><h2 id="v5-h">The colour decoder, and where it stands</h2>
    <p>For colour pictures the format is locked and a reference decoder is built. This release includes a decoder for colour pictures.</p></div>
  <div class="cards">
    <div class="card"><div class="body"><h3>Footprint</h3><p>35,344 octets: the whole RISC-V decoder image, code and data (stack and heap reserved, not stored).</p></div></div>
    <div class="card"><div class="body"><h3>Density</h3><p>Pooled bits per sample, version 5 colour coder: 3.5913 on 120 COCO pictures (8-bit), 3.5131 on 35 CC0 camera pictures (8-bit sRGB), 9.2552 on the same 35 pictures (16-bit linear), 2.6962 on 120 Wikimedia Commons pictures (8-bit); every file decoded exactly by the C library.</p></div></div>
    <div class="card"><div class="body"><h3>Among small decoders</h3><p>Among coders whose decoder is at most 98,304 octets, the version 5 colour coder is the smallest in size on COCO-120, the CC0 cameras and Commons-120. Against JPEG-LS (CharLS, whole picture) its files are smaller by 21.0% / 6.2% / 9.9% on COCO / cameras 8-bit / cameras 16-bit and by 20.8% on Commons.</p></div></div>
  </div>
  <p class="note"><strong>Where others are ahead:</strong> JPEG XL (effort 9) produces smaller files than the version 5 colour coder: by 9.5% on COCO-120, 7.9% on the CC0 cameras (8-bit sRGB), 1.6% (16-bit linear) and 20.9% on Commons-120. JPEG XL's decoder is 713,139 octets and does not meet the 98,304 cap. Commons-120 is a quality-filtered pool (selection bias). Decoder sizes are x86-64 builds, not RISC-V.</p>
  <p class="note"><strong>Hyperspectral, measured:</strong> On imaging-spectrometer scenes from NASA open data (EMIT, 5 scenes; AVIRIS-NG, orthocorrected, 3 scenes; 2 of 10 dropped for no-data fill), the version 5 coder's rate is larger than CCSDS 123's (untuned default settings): pooled by 13.7% (EMIT) and 8.1% (AVIRIS-NG) at one quantisation scale, and by 14.6% and 7.1% at a four-times finer scale; not within 5% on this data. Formula rates, not written files; one 512 x 256 window per scene; radiance scaled and rounded to 16-bit integers (not the sensors' native form); small scene counts; one very dark EMIT window is smaller at both scales. Data openly shared (LP DAAC, ORNL DAAC).</p>
</div></section>

<section class="alt" aria-labelledby="sec-h"><div class="wrap">
  <div class="head"><p class="label">2 · Security and integrity</p><h2 id="sec-h">Damaged files are never passed off as good</h2><p>In our test sets, every damaged or hostile file was either decoded exactly or refused with a numbered reason. The original decoder (format version 4) was tested against four standard lossless codecs, damaging the same files the same ways for each.</p></div>
  {STRIP_SEC}
  <figure class="ops" style="margin-top:22px">{chart_damage()}<figcaption><strong>0 of 9,600 damaged files produced undetected corruption: every one was refused.</strong> JPEG XL 0.3%, JPEG-LS 9.3%, CCSDS 121 47%, JPEG 2000 75% decoded to a wrong image and reported success.</figcaption></figure>
  <p class="note">{FAIR}</p>
  <p class="cite">{METHOD} <a href="evidence.html#h2h-h">Full results</a>.</p>
</div></section>

<section aria-labelledby="apps-home"><div class="wrap">
  <div class="head"><p class="label">Applications</p><h2 id="apps-home">Where it goes next</h2><p>Each scenario carries its status: demonstrated in simulation, in development, or planned. Nothing is shown as shipped unless it is.</p></div>
  {apps(['swarm', 'selfcorrect', 'downlink', 'collab', 'archive', 'medical'])}
</div></section>

<section class="alt" aria-labelledby="why-h"><div class="wrap">
  <div class="head"><p class="label">Why now</p><h2 id="why-h">Image decoders are being exploited in the wild</h2><p>An image arrives from outside, and the decoder is the first code that touches it. Both of these are in the US government's catalogue of exploited vulnerabilities.</p></div>
  {part("cves.html")}
  <div class="prose" style="margin-top:22px"><p class="label">What the test covers</p>
  <p>Our damaged-file test covers one bit flipped, 4 octets overwritten, 16 octets zeroed and truncation, on 24 camera crops. It does not cover larger images or every kind of damage, and we make no claim beyond the figures on this page.</p></div>
</div></section>

<section aria-labelledby="more-h"><div class="wrap">
  <div class="head"><p class="label">3 · More benefits</p><h2 id="more-h">The same result on every machine, and a decoder you can review</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>One result on every machine</h3><p>Integer-only decoding; a test stream decodes identically on x86-64, ARM, RISC-V and WebAssembly.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><h3>A decoder your team can review</h3><p>27,272 octets: the whole RISC-V decoder image, code and data (stack and heap reserved, not stored), under a hard cap of 98,304.</p></div></div>
    <div class="card">{img_art("aerial-tiles", "Aerial frame with its tile grid, one tile highlighted")}<div class="body"><h3>Damage stays local</h3><p>A damaged tile is refused while the others decode, so one bad region does not cost the frame.</p></div></div>
  </div>
</div></section>

<section class="alt" aria-labelledby="who-h"><div class="wrap">
  <div class="head"><p class="label">Solutions</p><h2 id="who-h">Where an exact image matters</h2></div>
  <div class="cards two">
    <a class="card" href="defence.html">{img_art("aerial-tiles", "Aerial drone frame with a 256 by 256 tile grid, one tile highlighted")}<div class="body"><span class="state ready">Available to pilot</span><h3>Defence and edge sensing</h3><p>Raw sensor frames kept exactly, moved over narrow links and decoded on any machine, with a damaged tile refused while the others still decode.</p><span class="more">More →</span></div></a>
    <a class="card" href="space.html">{img_art("space-band", "Landsat 8 view of the Nile delta, the Suez Canal and the Gulf of Suez in natural colour")}<div class="body"><span class="state prog">Decoders released; payload encoder in development</span><h3>Space and Earth observation</h3><p>Raw samples kept exactly over narrow downlinks, with measured results against the space standards on open data.</p><span class="more">More →</span></div></a>
    <a class="card" href="medical.html"><div class="art">{art_refuse()}</div><div class="body"><span class="state later">In development</span><h3>Medical devices</h3><p>A decoder inside your device that refuses a malformed study instead of showing a wrong image.</p><span class="more">More →</span></div></a>
    <a class="card" href="products.html#archive"><div class="art">{art_archive()}</div><div class="body"><span class="state later">Planned</span><h3>Long-term archives</h3><p>Files that carry their own decoder, so an image stored today can still be read when the software that wrote it is gone.</p><span class="more">More →</span></div></a>
  </div>
</div></section>

<section aria-labelledby="buy-h"><div class="wrap">
  <div class="head"><p class="label">Working with us</p><h2 id="buy-h">Start with your own data</h2></div>
  <div class="cards">
    <div class="card"><div class="body"><h3>1. Briefing</h3><p>Thirty minutes: the risk 100on100 removes, the evidence your engineers can check, and what is ready today versus planned.</p></div></div>
    <div class="card"><div class="body"><h3>2. Evaluation</h3><p>Compiled decoder binaries for Linux, macOS, Windows and WebAssembly are free for evaluation, with checksums on the releases page. Test records are available under NDA.</p></div></div>
    <div class="card"><div class="body"><h3>3. Pilot, then licence</h3><p>A pilot on your own frames, with the refusal test run on your data. Production use is licensed under a commercial licence, and 100on100 is distributed as compiled binaries.</p></div></div>
  </div>
</div></section>

{DEMO}""")

# ------------------------------------------------------------------ defence
page("defence.html", "100on100 for Defence",
     "Lossless raw sensor imaging for defence research: an auditable decoder, bit-exact on every tested machine, refusing hostile files by number.",
     pagehead("Solutions / Defence", "Keep every raw frame, and prove it arrived intact",
              "For programme managers and office directors whose systems capture raw sensor data at the edge and must keep it exactly.", "aerial-plain") + plain("defence", "") + head2head("For ISR data, a picture that is quietly wrong is worse than no picture. We damaged the same files the same ways for five codecs: 100on100 refused every one (version 4 files); the others let 0.3% to 75% through undetected. Its original version 4 C99 decoder (small build) is 9 to 79 times smaller than the JPEG-LS, JPEG 2000 and JPEG XL decoders.") +
     f"""
<section aria-labelledby="d-problem"><div class="wrap">
  <div class="cards two">
    <div><div class="head"><p class="label">The problem</p><h2 id="d-problem">Large data, narrow links, fragile decoders</h2></div>
      <ul class="steps">
        <li>Raw frames are large and links are narrow, but analysis needs every bit.</li>
        <li>Image decoders are large C and C++ libraries: a proven attack path, and the first code to touch data from outside.</li>
        <li>Decoders that use floating point do not give identical output on different machines, so a hash of a decoded image proves nothing.</li>
      </ul></div>
    <div class="card">{svg_art(art_zoom())}<div class="body"><h3>Raw, before colour</h3><p>100on100 stores the sensor's own mosaic, before demosaicing, so nothing is interpolated away.</p></div></div>
  </div>
</div></section>

<section aria-labelledby="apps-def"><div class="wrap">
  <div class="head"><p class="label">Applications</p><h2 id="apps-def">From the edge to the ground</h2><p>Status shown on each scenario.</p></div>
  {apps(['swarm', 'selfcorrect', 'collab'], True)}
</div></section>

<section class="alt" aria-labelledby="d-offer"><div class="wrap">
  <div class="head"><p class="label">What you get</p><h2 id="d-offer">What 100on100 gives your programme</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><h3>A decoder your team can review</h3><p>27,272 octets: the whole RISC-V decoder image, code and data (stack and heap reserved, not stored), under a hard cap of 98,304. The original version 4 C99 library (small build), 9,075 octets of code and data, matches it byte for byte.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><h3>Hostile files turned away</h3><p>A damaged or crafted file is refused with a numbered reason. In our tests, none became a plausible wrong picture.</p></div></div>
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>One result on every machine</h3><p>Integer-only decoding. A test stream gives one result on x86-64, ARM, RISC-V and WebAssembly, so a receiver can prove what it decoded.</p></div></div>
    <div class="card">{img_art("aerial-tiles", "Aerial frame with its tile grid, one tile highlighted")}<div class="body"><h3>Region decode</h3><p>256 × 256 tiles. Decode only the region you need, or spread one frame across machines with identical results.</p></div></div>
    <div class="card"><div class="art">{art_archive()}</div><div class="body"><h3>Built to outlast</h3><p>Planned: archive files that carry their own decoder.</p></div></div>
    <div class="card">{svg_art(art_mosaic())}<div class="body"><h3>Binary evaluation</h3><p>Compiled binaries are free to evaluate, and production use is licensed. The decoder is small enough for your engineers to review the evidence for themselves; test records are available to evaluators under NDA.</p></div></div>
  </div>
</div></section>

<section aria-labelledby="d-how"><div class="wrap">
  <div class="head"><p class="label">Working together</p><h2 id="d-how">How we work with your programme</h2></div>
  <ol class="steps">
    <li>A briefing for your programme office and its technical lead.</li>
    <li>A pilot on your own sensor data: we report rate, decode time and refusal behaviour, including where we lose.</li>
    <li>Integration through the decode SDK (C99 and WebAssembly), with the fuzzing and attestation results attached.</li>
  </ol>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ space
page("space.html", "100on100 for Space",
     "Lossless raw imaging for space and Earth observation: exact samples over narrow downlinks, per-tile checksums, region decode, and one result on every ground machine.",
     pagehead("Solutions / Space", "Every sample from orbit, kept exactly",
              "For payload and ground-segment leaders at space agencies, satellite makers and Earth-observation operators.", "space-band") + plain("space", "") +
     f"""
<section aria-labelledby="s-why"><div class="wrap">
  <div class="cards two">
    <div><div class="head"><p class="label">Why it matters</p><h2 id="s-why">Downlinks are narrow, and science needs the raw data</h2></div>
      <ul class="steps">
        <li>Bandwidth from orbit or deep space is scarce, but a lossy or demosaiced image throws away what later analysis may need.</li>
        <li>Ground processing runs on many machines. With floating-point decoders, they need not agree to the last bit.</li>
        <li>Damaged downlink data must be detected and set aside, not used as if it were good.</li>
      </ul></div>
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><h3>Region by region</h3><p>Images are cut into 256 × 256 tiles. A region of interest decodes without the rest of the frame.</p></div></div>
  </div>
</div></section>

<section aria-labelledby="apps-space"><div class="wrap">
  <div class="head"><p class="label">Applications</p><h2 id="apps-space">From orbit to the ground segment</h2><p>Status shown on each scenario.</p></div>
  {apps(['downlink', 'selfcorrect'])}
</div></section>

<section class="alt" aria-labelledby="s-offer"><div class="wrap">
  <div class="head"><p class="label">What you get</p><h2 id="s-offer">What 100on100 gives a payload and its ground segment</h2></div>
  <div class="cards">
    <div class="card">{svg_art(art_mosaic())}<div class="body"><h3>Raw, before processing</h3><p>The sensor's own samples, stored losslessly before demosaicing or calibration, so the ground team works from what the detector recorded.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><h3>Damage contained to a tile</h3><p>Each tile carries its own checksum, so a damaged tile is identified and refused with a numbered reason, and the other tiles can still be decoded on their own.</p></div></div>
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>One result on every ground machine</h3><p>Integer-only decoding. A test stream decodes identically on x86-64, ARM, RISC-V and WebAssembly.</p></div></div>
  </div>
</div></section>

<section aria-labelledby="s-road"><div class="wrap">
  <div class="head"><p class="label">Roadmap</p><h2 id="s-road">Where it stands for space</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><span class="state ready">Ready</span><h3>Format and decoder</h3><p>Format version 4 with tiles and checksums; a 27,272-octet complete decoder image, code and data (stack and heap reserved, not stored); a 9,075-octet original version 4 C99 decoder (small build) matching the reference byte for byte.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><span class="state prog">In development</span><h3>An encoder for the payload</h3><p>On board, the encoder is what flies. A C99 encoder for colour pictures is built; the payload encoder (raw and multispectral) in C99 is in development, then an FPGA or RISC-V soft-core encoder with measured power and area.</p></div></div>
    <div class="card"><div class="art">{art_mosaic()}</div><div class="body"><span class="state ready">Colour decoder released</span><h3>Colour pictures first, then beyond colour cameras</h3><p>For colour pictures the format is locked and a reference decoder is built. This release includes a decoder for colour pictures. Version 1.2.0 includes a decoder for single-channel and multi-plane images (greyscale, unsigned or signed, 1 to 16 bits): 1 to 255 separate planes, or the four phases of a raw sensor mosaic as one array. The format is locked.</p></div></div>
  </div>
  <p class="note"><strong>Measured on open Landsat 8, Sentinel-2 and AVIRIS data with format version 5 inter-plane prediction (the generic-plane decoder is in version 1.2.0; these are formula rates):</strong> level with CCSDS 123 on multispectral (Sentinel-2 −0.1%, Landsat +1.4%, pooled); about 12–13% behind on hyperspectral (stateless). Each tile decodes from its own stream and the tiles at the same position in at most two declared reference planes; no adaptive state. A damaged tile also blocks the tiles at the same position in the planes that reference it: one column of planes, not the file. Coded band by band, as today, 100on100 is smaller than the CCSDS 121 lossless standard on multispectral data (preliminary rates, before tiling).</p>
  <p class="note"><strong>Hyperspectral, measured:</strong> On imaging-spectrometer scenes from NASA open data (EMIT, 5 scenes; AVIRIS-NG, orthocorrected, 3 scenes; 2 of 10 dropped for no-data fill), the version 5 coder's rate is larger than CCSDS 123's (untuned default settings): pooled by 13.7% (EMIT) and 8.1% (AVIRIS-NG) at one quantisation scale, and by 14.6% and 7.1% at a four-times finer scale; not within 5% on this data. Formula rates, not written files; one 512 x 256 window per scene; radiance scaled and rounded to 16-bit integers (not the sensors' native form); small scene counts; one very dark EMIT window is smaller at both scales. Data openly shared (LP DAAC, ORNL DAAC).</p>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ medical
page("medical.html", "100on100 for Medical Devices",
     "An auditable, refusing image decoder for makers of medical imaging devices and software. In development; version 1.2.0 includes a decoder for single-channel and multi-plane images (greyscale, unsigned or signed, 1 to 16 bits).",
     pagehead("Solutions / Medical devices", "The decoder inside your device should refuse, not guess",
              "For CEOs, CTOs and heads of engineering at makers of imaging devices and imaging software: modalities, PACS and archives.", None, 1) + plain("medical", "Version 1.2.0 includes a decoder for single-channel and multi-plane images (greyscale, unsigned or signed, 1 to 16 bits); medical results are not yet published, and the points above describe how the format works.") +
     f"""
<section aria-labelledby="m-see"><div class="wrap">
  <div class="head"><p class="label">How it would work in your product</p><h2 id="m-see">One study, cut into tiles, each one checked</h2>
    <p>A study is stored in 256 × 256 tiles, each with its own checksum. A viewer can open just the region a clinician is looking at. If a tile is damaged in storage or on the network, that tile is refused with a numbered reason and is never drawn as a picture that looks right but is not.</p></div>
  <div class="cards two">
    {shot("phantom", "A CT test phantom divided into 16 tiles, one tile marked as refused", "Illustration on a generated CT test phantom: one damaged tile refused, the other fifteen still open.")}
    <div>
      <ul class="steps">
        <li><strong>Exact:</strong> the viewer shows the values the scanner wrote, not an approximation.</li>
        <li><strong>The same everywhere:</strong> whole-number decoding leaves no rounding for two workstations to disagree on.</li>
        <li><strong>Honest about damage:</strong> a broken tile is a refusal with a number your service team can look up.</li>
      </ul>
      <p class="note">Version 1.2.0 includes a decoder for single-channel and multi-plane images (greyscale, unsigned or signed, 1 to 16 bits); no DICOM support yet; medical results are not yet published. The phantom is generated; no patient data appears on this site.</p>
    </div>
  </div>
  <figure class="ops" style="margin-top:28px">{OPS_MED}<figcaption>Where the decoder sits: from the modality, through the archive, to every viewer.</figcaption></figure>
</div></section>

{head2head("In a clinic, an image that is subtly wrong but decodes as if it were fine is the dangerous case. We damaged the same files the same ways for five codecs: 100on100 refused every one (version 4 files); the others let 0.3% to 75% through undetected. (Measured on raw camera images; medical results are not yet published.)")}

<section class="alt" aria-labelledby="m-why"><div class="wrap">
  <div class="cards two">
    <div><div class="head"><p class="label">Why it matters</p><h2 id="m-why">In a regulated product, a wrong image is worse than none</h2></div>
      <ul class="steps">
        <li>Your decoder opens files from outside your control. A malformed study must be refused with a reason, never shown as a plausible wrong image.</li>
        <li>Viewers must agree pixel for pixel, whatever hardware they run on.</li>
        <li>Imaging records are kept for decades. A format must stay readable after the software that wrote it is gone.</li>
        <li>Your security review and regulatory file are easier with a decoder small enough to read in full.</li>
      </ul></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><h3>Refused by number</h3><p>Each refusal has a code your viewer can show and your auditors can test.</p></div></div>
  </div>
</div></section>

<section aria-labelledby="apps-med"><div class="wrap">
  <div class="head"><p class="label">Applications</p><h2 id="apps-med">Archives that stay exact</h2><p>Status shown on each scenario.</p></div>
  {apps(['medical', 'archive'])}
</div></section>

<section class="alt" aria-labelledby="m-status"><div class="wrap">
  <div class="head"><p class="label">Roadmap</p><h2 id="m-status">Where it stands</h2><p>The decoder, its refusal codes and its C99 version are ready today. Medical images need one more step: the DICOM bridge.</p></div>
  <div class="cards">
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><span class="state ready">Ready</span><h3>Refusal and exactness</h3><p>Damaged files refused by number; one result across machines; byte-identical C99 decoder.</p></div></div>
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><span class="state ready">Version 1.2.0</span><h3>Single-channel and multi-plane images, signed or unsigned</h3><p>Single or multiple planes (up to 255) of 1 to 16 bits, unsigned or signed. The format is locked. No DICOM support yet.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><span class="state later">Planned</span><h3>DICOM bridge</h3><p>Planned; no DICOM support yet. Pixel data in and out of DICOM, with its own fuzz-testing gate.</p></div></div>
  </div>
  <p class="note">Medical measurements are not yet published.</p>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ products
def product(pid, name, state, art, rows):
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    cls = {"In progress": "prog", "Planned": "later", "Ready": "ready"}[state]
    return f"""<div class="product" id="{pid}">
    <div><div class="art">{art}</div><p class="name">100on100 <b>{name}</b></p><span class="state {cls}">{state}</span></div>
    <dl>{dl}</dl>
  </div>"""

page("products.html", "100on100 Products",
     "The 100on100 product line: the decode SDK, decode attestation, and the self-decoding archive.",
     pagehead("Products", "One format, one decoder, three ways to use it",
              "Every product wraps the same decoder, so there is one implementation of the codec to audit, not one per product.", None, 2) +
     f"""
<section aria-label="Product line"><div class="wrap">
  {product("sdk", "SDK", "Ready", art_sdk(), [
      ("What", "The decoder as a library: a C interface over the C99 decoder, and a WebAssembly build of the same source."),
      ("Does", "Open a file, read its geometry and tiles, decode one tile or the whole frame. Every error returns its refusal code."),
      ("Released", "Version 1.2.0: the C interface and the WebAssembly build.")])}
  {product("attest", "Attest", "Planned", art_hashes(), [
      ("What", "Decode attestation: a receiver publishes the hash of what it decoded, and anyone can check it against the sender's."),
      ("Why it works", "Integer-only decoding gives the same bits on every architecture, so equal hashes mean equal images."),
      ("Today", "One result on x86-64, ARM, RISC-V and WebAssembly for a test stream.")])}
  {product("archive", "Archive", "Planned", art_archive(), [
      ("What", "Self-decoding files: each archive carries the decoder that reads it."),
      ("For", "Records that must outlive the software that wrote them: medical, defence, legal.")])}
</div></section>

<section class="alt" aria-labelledby="keep-h"><div class="wrap">
  <div class="head"><p class="label">What we keep</p><h2 id="keep-h">The sensor's own samples, not a processed picture</h2>
    <p>A camera does not see colour pictures. Each site on its sensor records one number through a red, green or blue filter. Most formats throw that away and keep a processed picture. 100on100 keeps the numbers themselves, every one of them, so any later processing starts from what the sensor actually recorded.</p></div>
  <figure class="ops">{art_zoom()}<figcaption>From the whole frame to the samples the sensor stored: each square is one number, shown in its filter colour.</figcaption></figure>
</div></section>

<section aria-labelledby="ops-h"><div class="wrap">
  <div class="head"><p class="label">In operation</p><h2 id="ops-h">Where the decoder sits in a real system</h2>
    <p>The same small decoder runs at every step that opens an image, so every step can check what it received.</p></div>
  <div class="opsrow">
    <figure class="ops">{OPS_FIELD}<figcaption><strong>Defence and edge sensing.</strong> Keep every raw frame at the edge, send what the link allows, and decode the region an analyst needs first.</figcaption></figure>
    <figure class="ops">{OPS_SPACE}<figcaption><strong>Space and Earth observation.</strong> Tiles with their own checksums come down the link; a damaged tile is set aside instead of being used as good data.</figcaption></figure>
    <figure class="ops">{OPS_MED}<figcaption><strong>Medical devices.</strong> From scanner to archive to every viewer, one decoder and one answer, or a numbered refusal. Decoder for single-channel and multi-plane images in version 1.2.0.</figcaption></figure>
  </div>
</div></section>

<section class="alt" aria-labelledby="fmt-h"><div class="wrap">
  <div class="head"><p class="label">The format</p><h2 id="fmt-h">What is in the box today</h2></div>
  <div class="cards">
    <div class="card">{img_art("aerial-tiles", "Aerial frame with its tile grid")}<div class="body"><span class="state ready">Ready</span><h3>Format version 4</h3><p>256 × 256 tiles, a header checksum, a declared bit depth up to 16, and a checksum on every tile.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><span class="state ready">Ready</span><h3>The decoder</h3><p>27,272 octets: the whole RISC-V decoder image, code and data (stack and heap reserved, not stored), reading versions 1 to 4, under a hard cap of 98,304.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><span class="state ready">Ready</span><h3>The C99 decoder</h3><p>No dependencies. Byte-identical to the reference on 284 of 284 corpus files and 97 of 97 test vectors.</p></div></div>
  </div>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ evidence
page("evidence.html", "100on100 Evidence",
     "The measurements behind 100on100: decoder size, cross-machine result, hostile-file handling, the C99 decoder gate, refusal codes and compression.",
     pagehead("Evidence", "Four claims, each with its measurement",
              "Every figure comes from our own test records, which your engineers can review under NDA. Where another codec does better, we say so.", None, 3) +
     f"""
<section aria-labelledby="see-h"><div class="wrap">
  <div class="head"><p class="label">See it for yourself</p><h2 id="see-h">A real round trip: 24 million samples in, the same 24 million out</h2>
    <p>We took one raw camera frame, compressed it with our encoder, decoded it with our decoder, and compared the result with the original, sample by sample. Not one of the 24,064,000 samples changed. That is what lossless means here: not "looks the same", but is the same.</p></div>
  <figure class="ops">{art_roundtrip()}<figcaption>A real run (5 October 2026), using the C99 encoder and decoder, compared sample by sample: 0 of 24,064,000 samples differ. Every photograph on this site went through a round trip through our decoder before it was shown.</figcaption></figure>
</div></section>

{head2head("We built four widely used lossless decoders the same way as ours and measured them, then damaged the same files the same ways for every codec. These are the results, including where a competitor is smaller.", EVX)}

<section class="alt" aria-labelledby="dmg-h"><div class="wrap">
  <div>
    <div><div class="head"><p class="label">How damage is handled</p><h2 id="dmg-h">A broken tile is refused; the rest still opens</h2>
      <p>Every 256 × 256 tile carries its own checksum. A tile that does not match is refused with a numbered reason, never drawn as a plausible wrong picture, and the other tiles still decode on their own. A region can be opened without decoding the rest of the frame.</p>
      <p class="note">The animation is drawn from a recorded simulation run. The measurements behind the refusal are listed below.</p></div>
    <div style="margin-top:20px">{apps(["selfcorrect"])}</div>
  </div>
</div></section>

<section aria-label="Claims"><div class="wrap">{part("ledger.html")}</div></section>
<div id="compression"><div class="wrap">{part("size.html")}<div style="padding-bottom:64px"></div></div></div>
<section class="alt" aria-labelledby="src-h"><div class="wrap">
  <div class="head"><h2 id="src-h">Sources</h2></div>
  <ol class="steps cite">
    <li>100on100 test records: decoder size, cross-architecture results, hostile-file set, C99 decoder gate, compression. Available to evaluators under NDA.</li>
    <li>Camera corpus: raw.pixls.us, one raw file per camera model, CC0.</li>
    <li>CISA Known Exploited Vulnerabilities catalog (version 2026.10.04): CVE-2023-4863, CVE-2025-43300.</li>
    <li>Google Chrome Releases, “Stable Channel Update for Desktop”, 2023-09-11 (CVE-2023-4863).</li>
    <li>Apple, “About the security content of iOS 18.6.2 and iPadOS 18.6.2”, 2025-08-20 (CVE-2025-43300).</li>
    <li>Quarkslab, “Reverse engineering of Apple’s iOS 0-click CVE-2025-43300”, 2025-09-04.</li>
  </ol>
</div></section>""")

# ------------------------------------------------------------------ services
page("services.html", "100on100 Services",
     "Pilots on your own data, integration support, and support for your security review.",
     pagehead("Services", "From briefing to integration",
              "We work with your team on your data, and report what we find, including where 100on100 is not the best fit.", None, 4) +
     f"""
<section aria-label="Services"><div class="wrap">
  <div class="cards">
    <div class="card">{svg_art(art_roundtrip())}<div class="body"><h3>Pilot on your data</h3><p>We run 100on100 on a sample of your own images and report size, decode time and refusal behaviour beside the codecs you use today.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><h3>Integration support</h3><p>Help linking the decode SDK into your product, in C or in the browser, and wiring refusal codes into your error handling.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><h3>Security review support</h3><p>We walk your reviewers through the decoder, its refusal codes and its test results, so your own review can conclude.</p></div></div>
  </div>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ downloads
page("downloads.html", "100on100 Downloads",
     "Documents about 100on100: evidence, technical brief, format specification.",
     pagehead("Downloads", "Documents", "Technical documents for your team. Items marked “on request” are sent after a briefing.") + """
<section aria-label="Documents"><div class="wrap"><div class="dl-list">
  <div><div><h3>Decoder binaries, version 1.2.0</h3><p>Current release: Linux (x86-64, aarch64), macOS (Apple silicon and Intel, macOS 11 or later), Windows (arm64, x86-64) and WebAssembly builds, with C headers and static libraries. The small original builds remain the recommended choice where footprint matters. New in 1.2.0: fast builds of the original and colour decoders beside the small ones, and a decoder for single-channel and multi-plane images (greyscale, unsigned or signed, 1 to 16 bits). The colour decoder is also offered as a RISC-V reference image: 35,344 octets: the whole RISC-V decoder image, code and data (stack and heap reserved, not stored). On non-conforming files (a list plane with a bad index and an out-of-range value), the image reports 40 where the C decoders report 31. Free for evaluation under the evaluation licence. The fast builds are larger than the small originals. Checksums are published with the release.</p></div><a class="btn ghost" href="https://github.com/100on100/releases/releases/tag/v1.2.0">Release 1.2.0</a></div>
  <div><div><h3>Evidence summary</h3><p>Every measured claim with its source.</p></div><a class="btn ghost" href="evidence.html">Read online</a></div>
  <div><div><h3>Technical brief</h3><p>How the decoder works, its refusal codes, and its test regime.</p></div><a class="btn ghost" href="company.html#contact">On request</a></div>
  <div><div><h3>Format specification (version 5)</h3><p>The file format and its refusal codes. Under NDA.</p></div><a class="btn ghost" href="company.html#contact">On request</a></div>
  <div><div><h3>Medical imaging measurements</h3><p>Results on openly licensed medical images.</p></div><span class="state later">Planned</span></div>
</div></div></section>""")

# ------------------------------------------------------------------ company
page("company.html", "100on100 Company",
     "Who builds 100on100, how we work, and how to request a briefing.",
     pagehead("Company", "We build image infrastructure you can check",
              "100on100 builds its own lossless codec; the decoder runs on x86-64, ARM, RISC-V and in the browser.", None, 5) +
     f"""
<section aria-labelledby="c-how"><div class="wrap">
  <div class="head"><p class="label">How we work</p><h2 id="c-how">Three rules</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>Measured before stated</h3><p>No figure goes on this site without the measurement and the section that records it.</p></div></div>
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><h3>Losses published</h3><p>When another codec is smaller, the table says so.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><h3>Binary evaluation</h3><p>Binaries are free for evaluation and licensed for production. No source is distributed; test records are available to evaluators under NDA.</p></div></div>
  </div>
</div></section>

<section class="alt" id="contact" aria-labelledby="contact-h"><div class="wrap">
  <div class="cards two">
    <div class="head" style="margin:0"><p class="label">Contact</p><h2 id="contact-h">Request a briefing</h2>
      <p>Thirty minutes: the risk 100on100 removes, the evidence your engineers can check, and what a pilot on your own data would take.</p></div>
    <div class="card" style="grid-template-rows:auto"><div class="body">
      <h3>100on100</h3>
      <p><a class="btn primary" href="mailto:100on100@fastbuilder.ai?subject=Briefing%20request">Email us</a></p>
      <p><strong>100on100@fastbuilder.ai</strong></p>
      <address>400 East View St<br>Columbus, Ohio<br>USA</address>
      <p class="cite">Organisation: <a href="https://github.com/100on100">github.com/100on100</a></p>
    </div></div>
  </div>
</div></section>""")

# ------------------------------------------------------------------ privacy, legal
page("privacy.html", "100on100 Privacy",
     "What this website collects: nothing of its own.",
     pagehead("Privacy", "Privacy", "This website collects nothing of its own.") + """
<section><div class="wrap prose">
  <p>This site sets no cookies, runs no analytics or tracking, and loads nothing from any other server. It has no forms.</p>
  <p>The site is hosted on GitHub Pages. GitHub may record visitors' IP addresses for security, under GitHub's own privacy statement.</p>
  <p>If you write to us, we use your message only to answer it.</p>
</div></section>""")

page("legal.html", "100on100 Legal Notice",
     "Who operates this website.",
     pagehead("Legal notice", "Legal notice", "Who operates this website.") + """
<section><div class="wrap prose">
  <p>100on100 is a trade name of FastBuilder.AI.</p>
  <address>100on100<br>400 East View St<br>Columbus, Ohio<br>USA<br>100on100@fastbuilder.ai</address>
  <p>The 100on100 software is distributed as compiled binaries under the 100on100 licence: free for evaluation, licensed for production use.</p>
  <p>Figures on this site are measurements from our test records. They are not warranties.</p>
  <h2 style="font-size:1.2rem;margin-top:12px">Image credits</h2>
  <p>Every photograph on this site is open-licence imagery that we encoded and decoded with 100on100 and compared sample by sample (0 samples differ) before rendering it for display. Full sources, windows and licences are in the <a href="NOTICE.txt">NOTICE</a> file.</p>
  <ul>
    <li>Alps, Sentinel-2: contains modified Copernicus Sentinel data 2026.</li>
    <li>Nile delta and Suez, Landsat 8: courtesy of the U.S. Geological Survey (public domain).</li>
    <li>Aerial imagery and the scenes in the animations: International Organization for Migration (IOM), via OpenAerialMap, CC BY 4.0 (<a href="https://creativecommons.org/licenses/by/4.0/">licence</a>); cropped, downsampled, and overlaid with tile grids.</li>
    <li>CT test phantom: generated by us (Shepp–Logan); no patient data.</li>
  </ul>
  <p>The diagrams and animations are our own. Measurement corpora (raw.pixls.us camera files, CC0) are listed on the <a href="evidence.html">evidence page</a>.</p>
</div></section>""")

print("built", ["index.html"] + [n for n, _ in NAV] + ["services.html", "downloads.html", "privacy.html", "legal.html"])
