---
name: update-shop
description: Rebuild and deploy the Craft Something Clever item site after items.csv changes — regenerates item pages and QR codes, pushes to GitHub Pages, and verifies the live URLs. Use when Bridget adds, removes, edits, or renames a crochet item, or asks to update/rebuild/redeploy the shop site.
---

# Update the Craft Something Clever shop site

Regenerates the static item pages and QR codes from `items.csv`, deploys them to
GitHub Pages, and confirms the live URLs work.

Live site: https://bridgetleanne.github.io/craft-something-clever/
Repo: https://github.com/bridgetleanne/craft-something-clever

## How it fits together

`items.csv` is the single source of truth. `generate_site.py` reads it and writes
`index.html`, `items/<slug>.html`, and `qr/<slug>.png` — one page and one QR code
per row. Each QR code encodes that item's live URL. Nothing updates on the live
site until the generator runs *and* the result is committed and pushed.

Slugs come from the Item Name, so **renaming an item changes its URL**.

## Steps

1. **Read `items.csv`** and check the new or changed rows before building.
   Columns: ID, Item Name, Description, Yarn, Fiber Content, Colorway, Hook Size,
   Quality Tester, Notes, Pattern Link, Year Made, Care Instructions.

   Watch for:
   - **ID** is the primary key for each row. It's never shown on the item page —
     just keep it unique when adding a new item (highest existing ID + 1).
   - **Pattern Link must be a real URL** (starts with `http`). Anything else is
     rendered as a "One of a kind" freehand note instead of a pattern button —
     correct for her handmade-freehand pieces, wrong if she meant to paste a link.
     Never invent or guess a pattern URL; ask her for it.
   - **Quality Tester** should be George, Winston, or Josie (her dogs).
   - **Year Made** and **Care Instructions** are shown on the item page. Blank
     Year Made just omits that row. Blank Care Instructions falls back to the
     shared `DEFAULT_CARE_BLURB` in `generate_site.py` — most items use the
     default, so only fill this cell in when an item needs different care.
   - Blank cells are fine — those sections are omitted from the page.

2. **Run the generator:**
   ```bash
   python generate_site.py
   ```
   It prints each item's live URL, then reports any orphaned files it removed.

3. **Check for renamed items.** If the generator removed an orphaned file, an
   item's URL changed. Tell her explicitly which one, because **any already-printed
   QR label for that item now points at a dead page** and needs reprinting. This is
   the one failure mode that costs her physical work, so never let it pass silently.

4. **Review, commit, and push:**
   ```bash
   git status --short
   git add -A
   git commit -m "<what changed>"
   git push
   ```

5. **Verify the live pages** (GitHub Pages takes ~30-60s to deploy):
   ```bash
   for f in items/*.html; do
     slug=$(basename "$f")
     code=$(curl -s -o /dev/null -w "%{http_code}" \
       "https://bridgetleanne.github.io/craft-something-clever/items/$slug")
     echo "$code  $slug"
   done
   ```
   Poll until they return 200 rather than reporting success on a 404.

6. **Tell her which QR files are new or changed** and where to get them:
   https://github.com/bridgetleanne/craft-something-clever/tree/main/qr
   She prints her own labels with a Cricut and thermal label maker — provide the
   PNGs and the item mapping, don't build label layouts unless she asks.

## Gotchas

- **`items.csv` is often open in Excel**, which locks the file. Edits fail with
  `EPERM` or `Device or resource busy`. Ask her to close it; don't retry in a loop.
- **Editing design/content** (colors, care blurb, thank-you note, layout) means
  editing the templates in `generate_site.py`, not the generated HTML — generated
  files are overwritten on every run.
- **Shared content** lives in constants at the top of `generate_site.py`:
  `DEFAULT_CARE_BLURB`, `THANK_YOU_HTML`, `ETSY_URL`, `SITE_BASE_URL`.
- Pages are styled for phones first — buyers scan these at a market table.

## If she wants to switch to Supabase

She has a Supabase account and has considered moving the data there for phone-based
editing. Only `main()` in `generate_site.py` reads the CSV — swap that for a
Supabase fetch and everything downstream is unchanged. Keep the published pages
static: free-tier Supabase projects pause after inactivity, and these QR codes are
attached to physical objects that need to keep working years from now.
