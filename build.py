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


def art_hashes(fg="var(--ink)", soft="var(--ink-soft)", box="var(--ground)", stroke="var(--rule)"):
    """One stream, four instruction sets, one result."""
    out = []
    for k, isa in enumerate(["x86-64", "ARM aarch64", "RISC-V RV64", "WebAssembly"]):
        y = 8 + k * 44
        out.append(f'<rect x="8" y="{y}" width="300" height="36" rx="3" style="fill:{box};stroke:{stroke}"/>')
        out.append(txt(20, y + 23, isa, 13, 700, fg))
        out.append(txt(296, y + 23, "1267710892", 13, 700, "var(--g)", "end"))
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
           txt(79, 112, "94,336 octets", 11, 600, "var(--brand-ink)", "middle")]
    for k in range(6):
        out.append(f'<rect x="148" y="{52 + k * 15}" width="{136 - (k * 13) % 40}" height="9" style="fill:var(--rule)"/>')
    out.append(txt(148, 146, "image data", 11, 600, "var(--ink-soft)"))
    return svg(310, 170, "".join(out), "An archive file that carries its own decoder")


def art_sdk():
    """The SDK surface, illustrative until the interface is agreed with the codec's owners."""
    lines = ["img100 *f = img100_open(buf, len);", "img100_geometry(f, &w, &h, &tiles);",
             "rc = img100_decode_tile(f, 0, 7, out);", "if (rc) puts(img100_reason(rc));"]
    out = ['<rect x="8" y="8" width="304" height="150" rx="4" style="fill:var(--ground);stroke:var(--rule)"/>']
    for k, l in enumerate(lines):
        out.append(txt(22, 42 + k * 28, l.replace("&", "&amp;").replace("<", "&lt;"), 12, 500))
    out.append(txt(22, 150, "illustrative; the interface is being agreed", 10, 500, "var(--ink-soft)"))
    return svg(320, 166, "".join(out), "Illustration of a decode SDK call sequence")


def credit(k):
    return f"Raw frame: {CREDIT[k]}, raw.pixls.us (CC0)"


CREDIT = {'hero-aerial': 'Yuneec CGO3 drone', 'aerial-tiles': 'FIMI X8SE drone', 'drone-mountain': 'Autel Robotics XB015 drone', 'field-vehicle': 'Leaf AFi-II 12', 'city': 'Google Pixel 2 XL', 'bridge': 'Nikon 1 AW1', 'desert': 'OnePlus A3003', 'mosaic-zoom': 'FIMI X8SE drone', 'cameras-sheet': '65 cameras'}


def img_art(k, alt):
    return f'<div class="art img"><img src="img/{k}.jpg" alt="{alt}" loading="lazy"></div>'


def shot(k, alt, caption):
    return f'<figure class="shot"><img src="img/{k}.jpg" alt="{alt}" loading="lazy"><figcaption>{caption} <span class="credit">{credit(k)}</span></figcaption></figure>'


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
     {"defence": "At about 92 KiB, your security team can review all of it, not trust a black box.",
      "space": "About 92 KiB: small enough for a review team to read in full before it goes anywhere near a mission.",
      "medical": "About 92 KiB: small enough for your security and regulatory reviewers to read in full."}),
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
  <div class="base"><span>© 2026 100on100 · Columbus, Ohio, USA</span><span>Binaries free for evaluation; production use licensed · no cookies, no analytics, nothing loaded from other servers</span></div>
</div></footer>
</body>
</html>
"""
    open(os.path.join(HERE, fname), "w").write(html)


def pagehead(crumb, h1, lead, photo=None):
    if photo:
        return f"""<div class="pagehead photo" style="--img:url(img/{photo}.jpg)"><div class="wrap">
  <p class="crumbs"><a href="index.html">Home</a> / {crumb}</p>
  <h1>{h1}</h1>
  <p>{lead}</p>
  <p class="credit">{credit(photo)}</p>
</div></div>"""
    return f"""<div class="pagehead"><div class="wrap">
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
  <div class="art">{art_hashes(fg="var(--brand-ink)", soft="var(--brand-ink)", box="transparent", stroke="var(--brand-ink)")}</div>
</div></div>"""

STRIP = """<div class="strip">
  <div><span class="fig num">94,336</span><p>octets: the entire decoder, for format versions 1 to 4</p></div>
  <div><span class="fig num">1</span><p>decoded result on x86-64, ARM, RISC-V and WebAssembly for a test stream</p></div>
  <div><span class="fig num">43 / 43</span><p>hard and hostile files decoded exactly or refused by number</p></div>
  <div><span class="fig num">3,442</span><p>files where the C99 decoder matched the reference byte for byte</p></div>
</div>
<p class="cite" style="margin-top:10px">Details on the <a href="evidence.html">evidence page</a>. Test records are available to evaluators under NDA.</p>"""

# ------------------------------------------------------------------ home
page("index.html", "100on100",
     "Lossless imaging with a decoder small enough to audit: the same pixels on every tested machine, and damaged files refused by number.",
     f"""<div class="heroband photo" style="--img:url(img/hero-aerial.jpg)"><div class="wrap">
  <div>
    <p class="label">Lossless imaging · auditable decoder</p>
    <h1 style="margin-top:14px">Every pixel back, exactly, from a decoder small enough to read.</h1>
    <p class="lead">100on100 stores raw sensor images without losing a bit. Its decoder is one program of 94,336 octets. It gives the same pixels on every machine we have tested, and refuses a damaged or hostile file with a numbered reason instead of guessing.</p>
    <div class="ctas"><a class="btn primary" href="company.html#contact">Request a briefing</a><a class="btn light" href="evidence.html">See the evidence</a></div>
  </div>
  {shot("mosaic-zoom", "Magnified raw sensor samples, each in its red, green or blue filter colour", "What a sensor actually stores: 16 × 24 raw samples, one colour each, magnified. 100on100 keeps every one.")}
</div></div>
<div class="callouts">
  <a class="callout" href="defence.html"><span class="label">Defence</span><h3>Keep every raw frame, and prove it arrived intact</h3><p>Lossless sensor data over narrow links, decoded identically anywhere.</p><span class="more">More →</span></a>
  <a class="callout" href="medical.html"><span class="label">Medical devices</span><h3>A decoder that refuses, not guesses</h3><p>Malformed files turned away with a numbered reason.</p><span class="more">More →</span></a>
  <a class="callout" href="evidence.html"><span class="label">Evidence</span><h3>Measured, not claimed</h3><p>Every figure with the section that records it, and our losses too.</p><span class="more">More →</span></a>
</div>

<div class="wrap statement">
  <p class="label">100on100</p>
  <h2>We make every image provable</h2>
  <p>An image is worth keeping only if you can trust what comes back out. 100on100 is a lossless image format and a decoder small enough for your own team to review. Decoding uses integers only, so there is no floating-point rounding for machines to disagree on. In our test sets, every damaged or hostile file was either decoded exactly or refused by number.</p>
</div>

<section aria-labelledby="corpus-h"><div class="wrap feature">
  <div class="head" style="margin:0"><p class="label">Real sensor data</p><h2 id="corpus-h">Measured on raw frames from 67 cameras</h2>
    <p>Drones, phones, action cameras and medium-format backs: one raw file per camera model, 1.22 billion samples, every one decoded back and compared bit for bit. These are the frames behind our compression figures.</p>
    <a class="more" href="evidence.html#compression">See the figures →</a></div>
  {shot("cameras-sheet", "Thumbnails of 65 raw camera frames", "65 of the 67 frames, rendered from their raw mosaics.")}
</div></section>

<section class="alt" aria-labelledby="sol-h"><div class="wrap">
  <div class="head"><p class="label">Solutions</p><h2 id="sol-h">Where an exact image matters</h2></div>
  <div class="cards two">
    <a class="card" href="defence.html">{img_art("aerial-tiles", "Aerial drone frame with a 256 by 256 tile grid, one tile highlighted")}<div class="body"><span class="state ready">Available to pilot</span><h3>Defence and edge sensing</h3><p>Raw sensor frames kept exactly, moved over narrow links, decoded on any machine, with proof that nothing changed on the way.</p><span class="more">More →</span></div></a>
    <a class="card" href="space.html">{img_art("hero-aerial", "Aerial view of a river and dam from a drone camera")}<div class="body"><span class="state prog">In development</span><h3>Space and Earth observation</h3><p>Raw sensor samples kept exactly over narrow downlinks, a damaged tile refused by number while the rest of the frame still decodes, and one result on every ground machine.</p><span class="more">More →</span></div></a>
    <a class="card" href="medical.html"><div class="art">{art_refuse()}</div><div class="body"><span class="state later">In development</span><h3>Medical devices</h3><p>A decoder inside your device that refuses a malformed study instead of showing a wrong image, and gives every viewer the same pixels.</p><span class="more">More →</span></div></a>
    <a class="card" href="products.html#archive"><div class="art">{art_archive()}</div><div class="body"><span class="state later">Planned</span><h3>Long-term archives</h3><p>Files that carry their own decoder, so an image stored today can still be read when the software that wrote it is gone.</p><span class="more">More →</span></div></a>
  </div>
</div></section>

<section aria-labelledby="proof-h"><div class="wrap">
  <div class="head"><p class="label">Proof</p><h2 id="proof-h">Measured, not claimed</h2><p>Every figure comes from the codec's own records and can be checked by your engineers.</p></div>
  {STRIP}
</div></section>

<section class="alt" aria-labelledby="why-h"><div class="wrap">
  <div class="head"><p class="label">Why now</p><h2 id="why-h">Image decoders are being exploited in the wild</h2><p>An image arrives from outside, and the decoder is the first code that touches it. Both of these are in the US government's catalogue of exploited vulnerabilities.</p></div>
  {part("cves.html")}
</div></section>

{DEMO}""")

# ------------------------------------------------------------------ defence
page("defence.html", "100on100 for Defence",
     "Lossless raw sensor imaging for defence research: an auditable decoder, bit-exact on every tested machine, refusing hostile files by number.",
     pagehead("Solutions / Defence", "Keep every raw frame, and prove it arrived intact",
              "For programme managers and office directors whose systems capture raw sensor data at the edge and must keep it exactly.", "drone-mountain") + plain("defence", "") +
     f"""
<section aria-labelledby="d-problem"><div class="wrap">
  <div class="cards two">
    <div><div class="head"><p class="label">The problem</p><h2 id="d-problem">Large data, narrow links, fragile decoders</h2></div>
      <ul class="steps">
        <li>Raw frames are large and links are narrow, but analysis needs every bit.</li>
        <li>Image decoders are large C and C++ libraries: a proven attack path, and the first code to touch data from outside.</li>
        <li>Decoders that use floating point do not give identical output on different machines, so a hash of a decoded image proves nothing.</li>
      </ul></div>
    <div class="card">{img_art("field-vehicle", "Off-road vehicle on open ground, from a raw frame")}<div class="body"><h3>Raw, before colour</h3><p>100on100 stores the sensor's own mosaic, before demosaicing, so nothing is interpolated away.</p></div></div>
  </div>
</div></section>

<section class="alt" aria-labelledby="d-offer"><div class="wrap">
  <div class="head"><p class="label">What you get</p><h2 id="d-offer">What 100on100 gives your programme</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><h3>A decoder your team can review</h3><p>94,336 octets for the whole decoder, under a hard cap of 98,304. A plain C99 version for linking matches it byte for byte.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><h3>Hostile files turned away</h3><p>A damaged or crafted file is refused with a numbered reason. In our tests, none became a plausible wrong picture.</p></div></div>
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>One result on every machine</h3><p>Integer-only decoding. A test stream gives one result on x86-64, ARM, RISC-V and WebAssembly, so a receiver can prove what it decoded.</p></div></div>
    <div class="card">{img_art("aerial-tiles", "Aerial frame with its tile grid, one tile highlighted")}<div class="body"><h3>Region decode</h3><p>256 × 256 tiles. Decode only the region you need, or spread one frame across machines with identical results.</p></div></div>
    <div class="card"><div class="art">{art_archive()}</div><div class="body"><h3>Built to outlast</h3><p>Planned: archive files that carry their own decoder.</p></div></div>
    <div class="card">{img_art("mosaic-zoom", "Magnified raw sensor samples")}<div class="body"><h3>Open to inspection</h3><p>The decoder is small enough to read in full, and its source is available to your evaluators for review.</p></div></div>
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
              "For payload and ground-segment leaders at space agencies, satellite makers and Earth-observation operators.", "aerial-tiles") + plain("space", "") +
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

<section class="alt" aria-labelledby="s-offer"><div class="wrap">
  <div class="head"><p class="label">What you get</p><h2 id="s-offer">What 100on100 gives a payload and its ground segment</h2></div>
  <div class="cards">
    <div class="card">{img_art("mosaic-zoom", "Magnified raw sensor samples")}<div class="body"><h3>Raw, before processing</h3><p>The sensor's own samples, stored losslessly before demosaicing or calibration, so the ground team works from what the detector recorded.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><h3>Damage contained to a tile</h3><p>Each tile carries its own checksum, so a damaged tile is identified and refused with a numbered reason, and the other tiles can still be decoded on their own.</p></div></div>
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>One result on every ground machine</h3><p>Integer-only decoding. A test stream decodes identically on x86-64, ARM, RISC-V and WebAssembly.</p></div></div>
  </div>
</div></section>

<section aria-labelledby="s-road"><div class="wrap">
  <div class="head"><p class="label">Roadmap</p><h2 id="s-road">Where it stands for space</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><span class="state ready">Ready</span><h3>Format and decoder</h3><p>Format version 4 with tiles and checksums; a 94,336-octet decoder; a C99 decoder matching the reference byte for byte.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><span class="state prog">In development</span><h3>An encoder for the payload</h3><p>On board, the encoder is what flies. A C99 encoder is next, then an FPGA or RISC-V soft-core encoder with measured power and area.</p></div></div>
    <div class="card"><div class="art">{art_mosaic()}</div><div class="body"><span class="state later">Version 5</span><h3>Beyond colour cameras</h3><p>Single-plane greyscale and infrared, signed samples, and multispectral planes.</p></div></div>
  </div>
  <p class="note"><strong>Measured on open Landsat 8, Sentinel-2 and AVIRIS data</strong> (preliminary rates, before tiling): coded band by band, 100on100 is smaller than the CCSDS 121 lossless standard on multispectral data and level on hyperspectral. It is within 4–11% of CCSDS 123 on multispectral data, with a larger gap on hyperspectral, because CCSDS 123 predicts each band from its neighbours. Inter-band prediction is in development.</p>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ medical
page("medical.html", "100on100 for Medical Devices",
     "An auditable, refusing image decoder for makers of medical imaging devices and software. In development; greyscale and signed CT values arrive in format version 5.",
     pagehead("Solutions / Medical devices", "The decoder inside your device should refuse, not guess",
              "For CEOs, CTOs and heads of engineering at makers of imaging devices and imaging software: modalities, PACS and archives.") + plain("medical", "Greyscale and CT support arrive in format version 5; the points above describe how the format works today.") +
     f"""
<section aria-labelledby="m-why"><div class="wrap">
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

<section class="alt" aria-labelledby="m-status"><div class="wrap">
  <div class="head"><p class="label">Roadmap</p><h2 id="m-status">Where it stands</h2><p>The decoder, its refusal codes and its C99 version are ready today. Medical images need two more things, both scheduled for format version 5.</p></div>
  <div class="cards">
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><span class="state ready">Ready</span><h3>Refusal and exactness</h3><p>Damaged files refused by number; one result across machines; byte-identical C99 decoder.</p></div></div>
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><span class="state later">Version 5</span><h3>Greyscale and signed CT</h3><p>Single-channel images, and CT values below zero stored with an offset.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><span class="state later">After version 5</span><h3>DICOM bridge</h3><p>Pixel data in and out of DICOM, with its own fuzz-testing gate.</p></div></div>
  </div>
  <p class="note">We have measured 100on100 on 1,864 openly licensed CT, X-ray, MR and mammography images. The results will be published here after review, including where other codecs are smaller.</p>
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
              "Every product wraps the same decoder, so there is one implementation of the codec to audit, not one per product.") +
     f"""
<section aria-label="Product line"><div class="wrap">
  {product("sdk", "SDK", "In progress", art_sdk(), [
      ("What", "The decoder as a library: a C interface over the C99 decoder, and a WebAssembly build of the same source."),
      ("Does", "Open a file, read its geometry and tiles, decode one tile or the whole frame. Every error returns its refusal code."),
      ("Ready when", "The WebAssembly build matches the reference decoder byte for byte on the full test set.")])}
  {product("attest", "Attest", "Planned", art_hashes(), [
      ("What", "Decode attestation: a receiver publishes the hash of what it decoded, and anyone can check it against the sender's."),
      ("Why it works", "Integer-only decoding gives the same bits on every architecture, so equal hashes mean equal images."),
      ("Today", "One result on x86-64, ARM, RISC-V and WebAssembly for a test stream.")])}
  {product("archive", "Archive", "Planned", art_archive(), [
      ("What", "Self-decoding files: each archive carries the decoder that reads it."),
      ("For", "Records that must outlive the software that wrote them: medical, defence, legal.")])}
</div></section>

<section class="alt" aria-labelledby="fmt-h"><div class="wrap">
  <div class="head"><p class="label">The format</p><h2 id="fmt-h">What is in the box today</h2></div>
  <div class="cards">
    <div class="card">{img_art("aerial-tiles", "Aerial frame with its tile grid")}<div class="body"><span class="state ready">Ready</span><h3>Format version 4</h3><p>256 × 256 tiles, a header checksum, a declared bit depth up to 16, and a checksum on every tile.</p></div></div>
    <div class="card"><div class="art">{art_refuse()}</div><div class="body"><span class="state ready">Ready</span><h3>The decoder</h3><p>94,336 octets, reading versions 1 to 4, under a hard cap of 98,304 octets.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><span class="state ready">Ready</span><h3>The C99 decoder</h3><p>No dependencies. Byte-identical to the reference on 3,442 of 3,442 files and mutants.</p></div></div>
  </div>
</div></section>
{DEMO}""")

# ------------------------------------------------------------------ evidence
page("evidence.html", "100on100 Evidence",
     "The measurements behind 100on100: decoder size, cross-machine result, hostile-file handling, the C99 decoder gate, refusal codes and compression.",
     pagehead("Evidence", "Four claims, each with its measurement",
              "Every figure comes from our own test records, which your engineers can review under NDA. Where another codec does better, we say so.") +
     f"""
<section aria-label="Claims"><div class="wrap">{part("ledger.html")}</div></section>
<div id="compression"><div class="wrap">{part("size.html")}
  <div style="padding-bottom:64px">{shot("cameras-sheet", "Thumbnails of 65 raw camera frames", "The corpus: 65 of the 67 raw frames, one per camera model.")}</div></div></div>
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
              "We work with your team on your data, and report what we find, including where 100on100 is not the best fit.", "desert") +
     f"""
<section aria-label="Services"><div class="wrap">
  <div class="cards">
    <div class="card">{img_art("bridge", "Suspension bridge over an estuary, from a raw frame")}<div class="body"><h3>Pilot on your data</h3><p>We run 100on100 on a sample of your own images and report size, decode time and refusal behaviour beside the codecs you use today.</p></div></div>
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
  <div><div><h3>Decoder binaries</h3><p>Linux, macOS and WebAssembly builds of the decoder, free for evaluation. The first release is pending verification.</p></div><a class="btn ghost" href="https://github.com/100on100/releases">Releases</a></div>
  <div><div><h3>Evidence summary</h3><p>Every measured claim with its source.</p></div><a class="btn ghost" href="evidence.html">Read online</a></div>
  <div><div><h3>Technical brief</h3><p>How the decoder works, its refusal codes, and its test regime.</p></div><a class="btn ghost" href="company.html#contact">On request</a></div>
  <div><div><h3>Format specification (version 4)</h3><p>The file format and its refusal codes. Under NDA.</p></div><a class="btn ghost" href="company.html#contact">On request</a></div>
  <div><div><h3>Medical imaging measurements</h3><p>Results on 1,864 openly licensed CT, X-ray, MR and mammography images.</p></div><span class="state later">After review</span></div>
</div></div></section>""")

# ------------------------------------------------------------------ company
page("company.html", "100on100 Company",
     "Who builds 100on100, how we work, and how to request a briefing.",
     pagehead("Company", "We build image infrastructure you can check",
              "100on100 builds its own lossless codec and the toolchain that compiles its decoder for RISC-V and runs it on x86-64, ARM and in the browser.", "city") +
     f"""
<section aria-labelledby="c-how"><div class="wrap">
  <div class="head"><p class="label">How we work</p><h2 id="c-how">Three rules</h2></div>
  <div class="cards">
    <div class="card"><div class="art">{art_hashes()}</div><div class="body"><h3>Measured before stated</h3><p>No figure goes on this site without the measurement and the section that records it.</p></div></div>
    <div class="card"><div class="art">{art_tiles()}</div><div class="body"><h3>Losses published</h3><p>When another codec is smaller or faster, the table says so.</p></div></div>
    <div class="card"><div class="art">{art_sdk()}</div><div class="body"><h3>Open to inspection</h3><p>Binaries are free for evaluation and licensed for production. The decoder's source is available to evaluators for review.</p></div></div>
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
  <p>Every photograph on this site is rendered by us from a raw camera file published at raw.pixls.us under CC0 (public domain dedication). Cameras: Yuneec CGO3, FIMI X8SE, Autel Robotics XB015, Leaf AFi-II 12, Google Pixel 2 XL, Nikon 1 AW1, OnePlus A3003, and the 65-camera contact sheet. The diagrams are our own.</p>
</div></section>""")

print("built", ["index.html"] + [n for n, _ in NAV] + ["services.html", "downloads.html", "privacy.html", "legal.html"])
