# R K Packers & Movers — website

Modern, fast, SEO-friendly static website for **R K Packers & Movers, Kolkata**.

## How it's built

The site is plain static HTML/CSS/JS (no server needed). To keep the shared header,
footer, floating buttons and `<head>` consistent across all pages, the HTML pages are
**generated** from small content fragments by a tiny Python script.

```
build.py            # generator: wraps content in the shared shell, emits *.html + sitemap.xml
_content/*.html     # per-page body content (edit these, then re-run build.py)
assets/css/style.css# design system (brand blue, responsive, light theme)
assets/js/site.js   # nav, form->WhatsApp/email, gallery lightbox, FAQ accordion, counters
assets/img/         # images
```

Service detail pages (Household Shifting, Office Relocation, Car/Bike Transport,
Packing & Unpacking, Storage) are generated from the `SERVICE_DETAIL` data in `build.py`.

### Build

```
python3 build.py
```

This regenerates all `*.html` at the repo root and `sitemap.xml`. The output is fully
static — just upload the repo to any host (GitHub Pages, Netlify, cPanel, etc.).

## Google reviews (auto-fetched at build time)

The Reviews page and home slider are populated from **real Google reviews** pulled via the
Google **Places API** during `build.py` — the API key is used only at build time and never
ships to the browser.

**One-time setup:**
1. In Google Cloud Console, create an API key and enable the **Places API** (and enable billing).
2. Give the key to the build in either way:
   - env var: `export GOOGLE_PLACES_API_KEY="AIza...."`, or
   - a file named `.places_key` in the repo root containing just the key (already gitignored).
3. Rebuild: `python3 build.py` — you'll see `reviews: fetched N from Google`.

Each rebuild refreshes the reviews. Results are cached to `_data/reviews.json` so builds
without the key (or offline) still show the last-fetched reviews. With no key and no cache,
the site falls back to the built-in `SAMPLE_REVIEWS` in `build.py`.

Notes:
- The Places API returns **up to 5 reviews** (Google's limit) and the overall rating/count.
- Place ID is set in `build.py` (`BIZ["place_id"]`). Per-star distribution isn't provided by
  the API, so the little distribution bars on the home page stay static/decorative.

## Things to fill in (search for `TODO`)

- **Google Analytics** — replace `G-XXXXXXXXXX` (the `ga` value in `build.py`) with your GA4 Measurement ID.
- **Google Maps** — replace the `map` embed URL in `build.py` with your exact business location embed.
- **Google reviews link** — set `google_reviews` in `build.py` to your Google Business Profile review URL.
- **Gallery** — replace placeholder images and demo YouTube IDs in `_content/gallery.html` with real photos/videos.
- **Reviews** — the review cards in `_content/reviews.html` are sample text; swap in real customer quotes.

## Features

Responsive design · WhatsApp chat + click-to-call (floating + inline) · enquiry forms that
open a prefilled WhatsApp message or email (no backend) · Google Maps · Google reviews section ·
photo & video gallery with lightbox · FAQ accordion · blog · on-page SEO (meta, Open Graph,
canonical, JSON-LD LocalBusiness + FAQ schema, sitemap, robots.txt).

## Pages

Home, About, Services (+ 6 service detail pages), Gallery, Reviews, Blog (+ sample post),
FAQ, Contact, Privacy, Terms.

---
Business: 102, Netaji Subhash Chandra Bose Rd, Kolkata 700047 · +91 70038 27993 · rkpackers6613@gmail.com

SSL, Google Search Console and Google Analytics activation are done in your hosting/Google
dashboards; the `google*.html` verification file and GA snippet are already wired in.
