"""
Builds the Craft Something Clever GitHub Pages site + QR codes from items.csv.
Rerun after editing items.csv to regenerate everything.
"""
import csv
import os
import re
import qrcode

SITE_BASE_URL = "https://bridgetleanne.github.io/craft-something-clever"
ETSY_URL = "https://www.etsy.com/shop/CraftSomethingClever"

CARE_BLURB = (
    "Hand wash in cold water and lay flat to dry. Avoid the dryer &mdash; "
    "heat can cause shrinking or misshape crocheted pieces, especially "
    "cotton and acrylic blends. Reshape gently while damp if needed."
)

THANK_YOU_HTML = (
    'THANK YOU for contributing to my &ldquo;Bridget needs yarn money&rdquo; fund! '
    'To find out if I ever list items on Etsy, follow our shop: '
    f'<a href="{ETSY_URL}" target="_blank" rel="noopener">etsy.com/shop/craftsomethingclever</a>'
)

TESTER_EMOJI = {
    "George": "\U0001F436",
    "Winston": "\U0001F436",
    "Josie": "\U0001F436",
}

ROOT = os.path.dirname(os.path.abspath(__file__))
ITEMS_DIR = os.path.join(ROOT, "items")
QR_DIR = os.path.join(ROOT, "qr")
ASSETS_DIR = os.path.join(ROOT, "assets")

os.makedirs(ITEMS_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)


def slugify(name):
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CSS = """
:root {
  --bg: #fff7f0;
  --card: #ffffff;
  --ink: #2b2130;
  --muted: #7a6a78;
  --accent: #ff5d8f;
  --accent-soft: #ffe1ea;
  --accent2: #12b3a3;
  --accent2-soft: #d7f7f2;
  --border: #f3e2da;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #241b2e;
    --card: #2f2438;
    --ink: #f5eef2;
    --muted: #c9b8c5;
    --accent: #ff8fb0;
    --accent-soft: #4a2733;
    --accent2: #4fd9c7;
    --accent2-soft: #1f3a37;
    --border: #3d3145;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
  line-height: 1.5;
}
.wrap {
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1.25rem 3rem;
}
.eyebrow {
  color: var(--accent);
  font-weight: 600;
  font-size: 0.85rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin: 0 0 0.4rem;
}
h1 {
  margin: 0 0 0.75rem;
  font-size: 1.6rem;
  line-height: 1.25;
}
.desc {
  color: var(--muted);
  margin: 0 0 1.5rem;
  font-size: 1rem;
}
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.1rem;
}
.card h2 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  margin: 0 0 0.75rem;
}
dl { margin: 0; }
.row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.95rem;
}
.row:last-child { border-bottom: none; }
.row dt { color: var(--muted); }
.row dd { margin: 0; text-align: right; font-weight: 500; }
.tester {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--accent-soft);
  color: var(--accent);
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.9rem;
}
.notes {
  font-size: 0.95rem;
  margin: 0;
}
.care {
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0;
}
.actions {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  margin-top: 1.5rem;
}
.btn {
  display: block;
  text-align: center;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  border: 1px solid var(--border);
  color: var(--ink);
}
.btn.primary {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.thankyou {
  background: var(--accent2-soft);
  border: 1px solid var(--accent2);
  border-radius: 14px;
  padding: 1rem 1.15rem;
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
}
.thankyou a {
  color: var(--accent2);
}
.make-your-own {
  background: var(--accent-soft);
  border: 2px dashed var(--accent);
  border-radius: 16px;
  padding: 1.35rem 1.25rem;
  margin: 1.5rem 0;
  text-align: center;
}
.make-your-own h2 {
  margin: 0 0 0.3rem;
  font-size: 1.25rem;
  color: var(--accent);
  text-transform: none;
  letter-spacing: 0;
}
.make-your-own p {
  margin: 0 0 1rem;
  font-size: 0.92rem;
  color: var(--muted);
}
.make-your-own .btn {
  margin: 0;
}
.make-your-own.freehand {
  border-style: solid;
  background: transparent;
}
.make-your-own.freehand p {
  margin-bottom: 0;
}
.back {
  display: inline-block;
  margin-top: 2rem;
  color: var(--muted);
  text-decoration: none;
  font-size: 0.9rem;
}
.shop-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0 0;
  display: grid;
  gap: 0.75rem;
}
.shop-list a {
  display: block;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.1rem;
  text-decoration: none;
  color: var(--ink);
  font-weight: 600;
}
.shop-list a span {
  display: block;
  font-weight: 400;
  color: var(--muted);
  font-size: 0.88rem;
  margin-top: 0.2rem;
}
footer {
  margin-top: 2.5rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  line-height: 1.7;
}
.credit {
  font-size: 0.78rem;
  opacity: 0.8;
  font-style: italic;
}
"""

with open(os.path.join(ASSETS_DIR, "style.css"), "w", encoding="utf-8") as f:
    f.write(CSS)


def item_page_html(item):
    tester = item["Quality Tester"].strip()
    tester_html = ""
    if tester:
        emoji = TESTER_EMOJI.get(tester, "\U0001F43E")
        tester_html = f'<span class="tester">{emoji} Quality tested by {esc(tester)}</span>'

    detail_rows = ""
    for label, key in [
        ("Yarn", "Yarn"),
        ("Fiber content", "Fiber Content"),
        ("Colorway", "Colorway"),
        ("Hook size", "Hook Size"),
    ]:
        val = item[key].strip()
        if val:
            detail_rows += f'<div class="row"><dt>{esc(label)}</dt><dd>{esc(val)}</dd></div>\n'

    notes = item["Notes"].strip()
    notes_card = ""
    if notes:
        notes_card = f"""
    <div class="card">
      <h2>Notes</h2>
      <p class="notes">{esc(notes)}</p>
    </div>"""

    pattern_link = item["Pattern Link"].strip()
    if pattern_link.lower().startswith("http"):
        make_your_own = f"""<div class="make-your-own">
    <h2>Make your own!</h2>
    <p>Here&rsquo;s the exact pattern I used for this piece.</p>
    <a class="btn primary" href="{esc(pattern_link)}" target="_blank" rel="noopener">Get the pattern &rarr;</a>
  </div>"""
    else:
        make_your_own = f"""<div class="make-your-own freehand">
    <h2>One of a kind</h2>
    <p>{esc(pattern_link) or "Made freehand &mdash; no pattern for this one."}</p>
  </div>"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(item['Item Name'])} &middot; Craft Something Clever</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<div class="wrap">
  <p class="eyebrow">Craft Something Clever</p>
  <h1>{esc(item['Item Name'])}</h1>
  <p class="desc">{esc(item['Description'])}</p>

  <div class="thankyou">{THANK_YOU_HTML}</div>

  {tester_html}

  <div class="card" style="margin-top:1.25rem;">
    <h2>Details</h2>
    <dl>
      {detail_rows}
    </dl>
  </div>
  {notes_card}

  {make_your_own}

  <div class="card">
    <h2>Care</h2>
    <p class="care">{CARE_BLURB}</p>
  </div>

  <div class="actions">
    <a class="btn" href="{ETSY_URL}" target="_blank" rel="noopener">Visit the Etsy shop</a>
  </div>

  <a class="back" href="../index.html">&larr; Back to all items</a>
  <footer>Handmade by Craft Something Clever<br><span class="credit">Site built by Claude, items and patterns by people.</span></footer>
</div>
</body>
</html>
"""


def index_html(items):
    list_items = ""
    for item, slug in items:
        list_items += f"""<li><a href="items/{slug}.html">{esc(item['Item Name'])}<span>{esc(item['Description'])}</span></a></li>\n"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Craft Something Clever</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">
  <p class="eyebrow">Craft Something Clever</p>
  <h1>Handmade crochet, one skein at a time</h1>
  <p class="desc">Scan the tag on any item to land here, or browse everything below.</p>
  <ul class="shop-list">
    {list_items}
  </ul>
  <div class="actions">
    <a class="btn primary" href="{ETSY_URL}" target="_blank" rel="noopener">Visit the Etsy shop</a>
  </div>
  <footer>Handmade by Craft Something Clever<br><span class="credit">Site built by Claude, items and patterns by people.</span></footer>
</div>
</body>
</html>
"""


def make_qr(url, out_path):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)


def main():
    with open(os.path.join(ROOT, "items.csv"), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get("Item Name", "").strip()]

    items = []
    for row in rows:
        slug = slugify(row["Item Name"])
        items.append((row, slug))

    for item, slug in items:
        page = item_page_html(item)
        with open(os.path.join(ITEMS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(page)

        url = f"{SITE_BASE_URL}/items/{slug}.html"
        make_qr(url, os.path.join(QR_DIR, f"{slug}.png"))
        print(f"{item['Item Name']!s:45s} -> {url}")

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html(items))

    print(f"\nGenerated {len(items)} item pages, {len(items)} QR codes, and index.html")


if __name__ == "__main__":
    main()
