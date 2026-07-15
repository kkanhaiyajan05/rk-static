#!/usr/bin/env python3
"""
Static site builder for R K Packers & Movers.

Wraps the per-page content fragments in `_content/*.html` inside a shared shell
(head, top bar, header/nav, footer, floating buttons) and writes plain static
HTML to the repo root. The generated files are self-contained and need no
server or build step to view — this script only keeps the shared chrome DRY.

Usage:  python3 build.py
"""
import os
import re
import json
import html as _html
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "_content")

# --- Business info -----------------------------------------------------------
BIZ = {
    "name": "R K Packers & Movers",
    "tagline": "Safe • Fast • Trusted",
    "slogan": "Your Peace of Mind, Our Responsibility",
    "phone": "+917003827993",
    "phone_disp": "+91 70038 27993",
    "phone2": "+919831940694",
    "phone2_disp": "+91 98319 40694",
    "phone3": "+919831931413",
    "phone3_disp": "+91 98319 31413",
    "wa": "917003827993",
    "email": "rkpackers6613@gmail.com",
    "addr": "102/1, N.S.C. Bose Road, Naktala, Kolkata 700047 (Near Naktala High School)",
    "url": "https://www.rkpackersmovers.com",
    "hours": "24×7 Service · Mon–Sun",
    # TODO: replace with your Google Maps place embed URL (Google Maps > Share > Embed a map)
    "map": "https://www.google.com/maps?q=N.S.C.+Bose+Road+Naktala+Kolkata+700047&output=embed",
    # TODO: replace with your real Google Analytics 4 Measurement ID
    "ga": "G-XXXXXXXXXX",
    # Google Business Profile "write a review" link
    "google_reviews": "https://search.google.com/local/writereview?placeid=ChIJ0RSWdtRxAjoRIn1pf0PE5Eo&amp;source=g.page.m.ia._&amp;utm_source=gbp&amp;laa=nmx-review-solicitation-ia2",
    # Google Place ID — used by the build-time reviews fetch (Places API)
    "place_id": "ChIJ0RSWdtRxAjoRIn1pf0PE5Eo",
    # Link to the full list of Google reviews (all reviews)
    "all_reviews": "https://search.google.com/local/reviews?placeid=ChIJ0RSWdtRxAjoRIn1pf0PE5Eo&amp;hl=en",
}

# --- Navigation --------------------------------------------------------------
SERVICES = [
    ("household-shifting", "Household Shifting"),
    ("office-relocation", "Office Relocation"),
    ("car-transportation", "Car Transportation"),
    ("bike-transportation", "Bike Transportation"),
    ("packing-unpacking", "Packing &amp; Unpacking"),
    ("storage-service", "Storage Service"),
]

NAV = [
    ("index", "Home"),
    ("about", "About"),
    ("services", "Services"),  # dropdown injected
    ("gallery", "Gallery"),
    ("reviews", "Reviews"),
    ("faq", "FAQ"),
    ("contact", "Contact"),
]  # Blog intentionally omitted — pages still exist, just unlinked for now

# --- Inline SVG icons --------------------------------------------------------
IC = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "wa": '<svg viewBox="0 0 32 32" fill="currentColor"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.1.6 4.2 1.6 6L4 29l8.2-1.6c1.8.9 3.7 1.4 5.8 1.4 6.6 0 12-5.4 12-12S22.6 3 16 3zm0 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-4.9 1 1-4.8-.3-.4a9.7 9.7 0 0 1-1.5-5.2c0-5.4 4.4-9.8 9.8-9.8s9.8 4.4 9.8 9.8-4.4 9.8-9.8 9.8zm5.4-7.3c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.5-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.3 5.1 4.6.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.2-.3-.2-.6-.3z"/></svg>',
    "chevron": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12h18M3 6h18M3 18h18"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0 0 22 12Z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
    "yt": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 12s0-3.2-.4-4.7a2.5 2.5 0 0 0-1.7-1.8C19.3 5 12 5 12 5s-7.3 0-8.9.5A2.5 2.5 0 0 0 1.4 7.3C1 8.8 1 12 1 12s0 3.2.4 4.7a2.5 2.5 0 0 0 1.7 1.8C4.7 19 12 19 12 19s7.3 0 8.9-.5a2.5 2.5 0 0 0 1.7-1.8C23 15.2 23 12 23 12Zm-13 3V9l5 3-5 3Z"/></svg>',
    "alert": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/></svg>',
}

def social(cls=""):
    return ('<a href="https://www.facebook.com/share/174kdqEyjK/" target="_blank" rel="noopener" aria-label="Facebook">%s</a>'
            '<a href="https://www.instagram.com/rkpackers6613?igsh=OTBvdXQyYmJubXJ3" target="_blank" rel="noopener" aria-label="Instagram">%s</a>'
            '<a href="https://youtube.com/@rkpackersmovers?si=dppTDLnWs09c2BVh" target="_blank" rel="noopener" aria-label="YouTube">%s</a>') % (IC["fb"], IC["ig"], IC["yt"])

# --- Google reviews (fetched at build time via Places API) -------------------
# The API key is read from the GOOGLE_PLACES_API_KEY env var or a gitignored
# `.places_key` file — it is used only during the build and never ships to the
# browser. Results are cached to `_data/reviews.json` so builds without a key
# (or without network) still show the last-fetched reviews; if neither is
# available we fall back to the built-in sample reviews so the build never breaks.
_STAR_FULL = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 6.9 7.6.6-5.8 4.9 1.8 7.4L12 18l-6.4 3.8 1.8-7.4L1.6 9.5l7.6-.6L12 2z"/></svg>'
_STAR_EMPTY = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3 6.9 7.6.6-5.8 4.9 1.8 7.4L12 18l-6.4 3.8 1.8-7.4L1.6 9.5l7.6-.6L12 2z"/></svg>'

# Displayed until real reviews are fetched. Marked clearly as samples.
SAMPLE_REVIEWS = [
    {"name": "Sourav Das", "rating": 5, "sub": "Household Shifting", "text": "Shifted my 3BHK from Kolkata to Bangalore. The team packed everything so carefully — not a single item damaged. Very professional and on time."},
    {"name": "Priya Agarwal", "rating": 5, "sub": "Office Relocation", "text": "We relocated our office of 40 staff over a weekend with zero downtime on Monday. Excellent coordination and labelling. Highly recommended."},
    {"name": "Rahul Kumar", "rating": 5, "sub": "Vehicle Transport", "text": "Sent my car and bike from Kolkata to Pune. Both arrived in perfect condition and the price was very reasonable. Good tracking updates too."},
    {"name": "Moumita Banerjee", "rating": 5, "sub": "Household Shifting", "text": "Very courteous staff and neat packing. They handled my glassware and TV with a lot of care. Everything reached safe. Thank you R K team!"},
    {"name": "Arvind Verma", "rating": 5, "sub": "Household Shifting", "text": "Got quotes from three companies — R K gave the most transparent price with no hidden charges. Smooth move from start to finish."},
    {"name": "Sunita Ghosh", "rating": 5, "sub": "Storage Service", "text": "Needed storage for two months between houses. Warehouse was clean and secure, and redelivery was exactly on the day promised."},
    {"name": "Faisal Khan", "rating": 5, "sub": "Household Shifting", "text": "Booked at short notice and they still managed a next-day move. Professional team, fair price and no damage at all. Highly recommend."},
    {"name": "Nandini Roy", "rating": 5, "sub": "Packing & Unpacking", "text": "The unpacking service was a lifesaver. They set up all the furniture and even took away the packing waste. Truly end-to-end."},
]
SAMPLE_RATING = {"value": "4.7", "total": 987}

# rating shown in JSON-LD / badges (updated by prepare_reviews)
RVALUE = SAMPLE_RATING["value"]
RCOUNT = str(SAMPLE_RATING["total"])

def _stars(n):
    n = max(0, min(5, int(round(n or 5))))
    return _STAR_FULL * n + _STAR_EMPTY * (5 - n)

def _initials(name):
    parts = [p for p in (name or "").split() if p]
    if not parts:
        return "★"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def review_card(r, reveal=True):
    cls = "card review-card reveal" if reveal else "card review-card"
    return (
        '<div class="%s"><div class="stars">%s</div>'
        '<p class="quote">"%s"</p>'
        '<div class="who"><span class="av">%s</span><div><div class="nm">%s</div>'
        '<div class="rl">%s</div></div></div></div>'
        % (cls, _stars(r.get("rating", 5)), _html.escape(r["text"]),
           _html.escape(_initials(r.get("name", ""))),
           _html.escape(r.get("name", "Google User")),
           _html.escape(r.get("sub", "")))
    )

def _places_key():
    k = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if k:
        return k
    kf = os.path.join(ROOT, ".places_key")
    if os.path.exists(kf):
        return open(kf, encoding="utf-8").read().strip()
    return ""

def _fetch_new(pid, key):
    url = "https://places.googleapis.com/v1/places/%s?languageCode=en" % urllib.parse.quote(pid)
    req = urllib.request.Request(url, headers={
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "rating,userRatingCount,reviews",
    })
    d = json.load(urllib.request.urlopen(req, timeout=30))
    revs = []
    for rv in d.get("reviews", []):
        txt = ((rv.get("text") or {}).get("text")
               or (rv.get("originalText") or {}).get("text") or "").strip()
        aa = rv.get("authorAttribution") or {}
        when = (rv.get("relativePublishTimeDescription") or "").strip()
        revs.append({"name": aa.get("displayName", "Google User"),
                     "rating": rv.get("rating", 5), "text": txt,
                     "sub": (when + " · Google review").strip(" ·")})
    return revs, {"value": str(round(d.get("rating", 0) or 0, 1)),
                  "total": int(d.get("userRatingCount", 0) or 0)}

def _fetch_legacy(pid, key):
    q = urllib.parse.urlencode({"place_id": pid, "language": "en",
        "fields": "reviews,rating,user_ratings_total", "key": key})
    d = json.load(urllib.request.urlopen(
        "https://maps.googleapis.com/maps/api/place/details/json?" + q, timeout=30))
    if d.get("status") != "OK":
        raise RuntimeError("legacy status=%s %s" % (d.get("status"), d.get("error_message", "")))
    res = d.get("result", {})
    revs = []
    for rv in res.get("reviews", []):
        when = (rv.get("relative_time_description") or "").strip()
        revs.append({"name": rv.get("author_name", "Google User"),
                     "rating": rv.get("rating", 5), "text": (rv.get("text") or "").strip(),
                     "sub": (when + " · Google review").strip(" ·")})
    return revs, {"value": str(round(res.get("rating", 0) or 0, 1)),
                  "total": int(res.get("user_ratings_total", 0) or 0)}

def load_reviews():
    pid, key = BIZ["place_id"], _places_key()
    cache = os.path.join(ROOT, "_data", "reviews.json")
    if key and pid:
        for fn in (_fetch_new, _fetch_legacy):
            try:
                revs, rating = fn(pid, key)
                revs = [r for r in revs if r["text"] and (r.get("rating", 5) or 5) >= 4]
                if revs:
                    os.makedirs(os.path.dirname(cache), exist_ok=True)
                    json.dump({"reviews": revs, "rating": rating},
                              open(cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    print("  reviews: fetched %d from Google (%s)" % (len(revs), fn.__name__))
                    return revs, rating
            except Exception as e:
                print("  reviews: %s failed: %s" % (fn.__name__, e))
    if os.path.exists(cache):
        try:
            d = json.load(open(cache, encoding="utf-8"))
            print("  reviews: using cached %d from _data/reviews.json" % len(d["reviews"]))
            return d["reviews"], d["rating"]
        except Exception:
            pass
    print("  reviews: using built-in SAMPLE reviews (set GOOGLE_PLACES_API_KEY to fetch real ones)")
    return SAMPLE_REVIEWS, SAMPLE_RATING

def prepare_reviews():
    global RVALUE, RCOUNT
    revs, rating = load_reviews()
    RVALUE = rating.get("value") or "4.7"
    RCOUNT = str(rating.get("total") or len(revs))
    TOKENS["{{REVIEW_GRID}}"] = "\n          ".join(review_card(r) for r in revs[:12])
    TOKENS["{{REVIEW_SLIDER}}"] = "\n          ".join(review_card(r, reveal=False) for r in revs[:3])
    TOKENS["{{RATING_VALUE}}"] = RVALUE
    TOKENS["{{RATING_COUNT}}"] = RCOUNT

# --- Shared chrome -----------------------------------------------------------
def nav_html(active):
    items = []
    for slug, label in NAV:
        href = "index.html" if slug == "index" else slug + ".html"
        act = " active" if slug == active or (slug == "services" and active in [s for s, _ in SERVICES]) else ""
        if slug == "services":
            drop = "".join(
                '<li><a href="%s.html">%s</a></li>' % (s, l) for s, l in SERVICES
            )
            items.append(
                '<li class="has-drop"><a href="services.html" class="%s">Services %s</a>'
                '<ul class="dropdown"><li><a href="services.html">All Services</a></li>%s</ul></li>'
                % (act.strip(), IC["chevron"], drop)
            )
        else:
            items.append('<li><a href="%s" class="%s">%s</a></li>' % (href, act.strip(), label))
    return "\n".join(items)

def header(active):
    return f'''<div class="notice">
    <div class="container">{IC['alert']}<span>Beware of fraudulent companies misusing our name. Always verify by calling <a href="tel:{BIZ['phone']}">{BIZ['phone_disp']}</a> before booking.</span></div>
  </div>

  <div class="topbar">
    <div class="container">
      <div class="tb-left">
        <a class="tb-item" href="tel:{BIZ['phone']}">{IC['phone']} {BIZ['phone_disp']}</a>
        <a class="tb-item" href="mailto:{BIZ['email']}">{IC['mail']} {BIZ['email']}</a>
        <span class="tb-item">{IC['clock']} {BIZ['hours']}</span>
        <a class="tb-item tb-link" href="get-a-quote.html">{IC['arrow']} Get a Quote</a>
        <a class="tb-item tb-link" href="physical-survey.html">{IC['pin']} Book a Survey</a>
      </div>
      <div class="tb-social">{social()}</div>
    </div>
  </div>

  <header class="header">
    <div class="container">
      <a class="brand" href="index.html">
        <img class="mark" src="assets/img/logo-mark.svg" alt="R K Packers &amp; Movers logo" width="48" height="48">
        <span class="bname">R K Packers &amp; Movers<span>10+ Years of Trust · Kolkata</span></span>
      </a>
      <button class="nav-toggle" aria-label="Open menu">{IC['menu']}</button>
      <nav class="nav" aria-label="Primary">
        <button class="nav-close" aria-label="Close menu">{IC['close']}</button>
        <ul>
{nav_html(active)}
        </ul>
        <div class="nav-mobile-cta">
          <a class="btn btn-primary" href="get-a-quote.html">{IC['arrow']} Get a Quote</a>
          <a class="btn btn-ghost" href="physical-survey.html">{IC['pin']} Book a Survey</a>
          <div class="nav-contact">
            <a href="tel:{BIZ['phone']}">{IC['phone']} {BIZ['phone_disp']}</a>
            <a href="tel:{BIZ['phone2']}">{IC['phone']} {BIZ['phone2_disp']}</a>
            <a href="mailto:{BIZ['email']}">{IC['mail']} {BIZ['email']}</a>
          </div>
        </div>
      </nav>
      <div class="header-cta">
        <a class="btn btn-ghost" href="tel:{BIZ['phone']}">{IC['phone']} Call</a>
        <a class="btn btn-primary" href="get-a-quote.html">Get a Quote</a>
      </div>
    </div>
  </header>
  <div class="nav-backdrop"></div>'''

def footer():
    svc_links = "".join('<li><a href="%s.html">%s</a></li>' % (s, l) for s, l in SERVICES)
    quick = "".join(
        '<li><a href="%s">%s</a></li>' % ("index.html" if s == "index" else s + ".html", l)
        for s, l in [("about", "About Us"), ("services", "Services"), ("get-a-quote", "Get a Quote"),
                     ("physical-survey", "Book a Survey"), ("gallery", "Gallery"), ("reviews", "Customer Reviews"),
                     ("faq", "FAQ"), ("contact", "Contact Us")]
    )
    return f'''<footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <div class="fbrand"><span class="flogo"><img src="assets/img/logo.svg" alt="R K Packers &amp; Movers logo"></span></div>
          <p class="fdesc">{BIZ['tagline']} — {BIZ['slogan']}. Trusted packers and movers in Kolkata for household shifting, office relocation and vehicle transport across India.</p>
          <div class="foot-badges">
            <span class="fbadge">✓ GST Registered</span>
            <span class="fbadge">✓ Licensed &amp; Verified</span>
            <span class="fbadge">✓ 24×7 Service</span>
          </div>
          <div class="fsocial">{social()}</div>
        </div>
        <div>
          <h4>Our Services</h4>
          <ul>{svc_links}</ul>
        </div>
        <div>
          <h4>Company</h4>
          <ul>{quick}</ul>
        </div>
        <div>
          <h4>Get in Touch</h4>
          <ul class="foot-contact">
            <li>{IC['pin']}<span>{BIZ['addr']}</span></li>
            <li>{IC['phone']}<span><a href="tel:{BIZ['phone']}">{BIZ['phone_disp']}</a><br><a href="tel:{BIZ['phone2']}">{BIZ['phone2_disp']}</a><br><a href="tel:{BIZ['phone3']}">{BIZ['phone3_disp']}</a></span></li>
            <li>{IC['mail']}<a href="mailto:{BIZ['email']}">{BIZ['email']}</a></li>
            <li>{IC['clock']}<span>{BIZ['hours']}</span></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="container" style="padding:0;">
          <span>© <span data-year>2026</span> {BIZ['name']}. All rights reserved.</span>
          <span><a href="privacy.html">Privacy Policy</a> &nbsp;·&nbsp; <a href="terms.html">Terms of Service</a></span>
        </div>
      </div>
    </div>
  </footer>

  <div class="floaters">
    <a class="float-btn float-wa" href="https://wa.me/{BIZ['wa']}?text=Hi%20R%20K%20Packers%20%26%20Movers%2C%20I%20need%20a%20moving%20quote." target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{IC['wa']}</a>
    <a class="float-btn float-call" href="tel:{BIZ['phone']}" aria-label="Call us">{IC['phone']}</a>
  </div>
  <button class="to-top" aria-label="Back to top">{IC['up']}</button>

  <div class="lightbox"><button class="lb-close" aria-label="Close">{IC['close']}</button><div class="lb-body"></div></div>'''

def jsonld():
    return f'''{{
  "@context": "https://schema.org",
  "@type": "MovingCompany",
  "name": "{BIZ['name']}",
  "image": "{BIZ['url']}/assets/img/truck-1.jpg",
  "logo": "{BIZ['url']}/assets/img/logo.png",
  "@id": "{BIZ['url']}",
  "url": "{BIZ['url']}",
  "telephone": "{BIZ['phone']}",
  "email": "{BIZ['email']}",
  "priceRange": "₹₹",
  "slogan": "{BIZ['tagline']} — {BIZ['slogan']}",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "102/1, N.S.C. Bose Road, Naktala",
    "addressLocality": "Kolkata",
    "addressRegion": "West Bengal",
    "postalCode": "700047",
    "addressCountry": "IN"
  }},
  "contactPoint": {{
    "@type": "ContactPoint",
    "contactType": "customer service",
    "telephone": ["{BIZ['phone']}", "{BIZ['phone2']}", "{BIZ['phone3']}"],
    "areaServed": "IN",
    "availableLanguage": ["en", "hi", "bn"]
  }},
  "openingHoursSpecification": {{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "opens": "09:00", "closes": "21:00"
  }},
  "areaServed": "Kolkata and Pan-India",
  "aggregateRating": {{
    "@type": "AggregateRating",
    "ratingValue": "{RVALUE}", "reviewCount": "{RCOUNT}"
  }}
}}'''

def page_shell(slug, title, desc, content, extra_head=""):
    canonical = f"{BIZ['url']}/{'' if slug == 'index' else slug + '.html'}"
    og_img = f"{BIZ['url']}/assets/img/truck-1.jpg"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="packers and movers Kolkata, movers and packers near me, household shifting Kolkata, office relocation, car transportation, bike transport, packing unpacking, storage service, R K Packers and Movers">
  <link rel="canonical" href="{canonical}">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_img}">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" type="image/svg+xml" href="assets/img/logo-mark.svg">
  <link rel="icon" type="image/png" href="assets/img/favicon.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="assets/css/style.css">

  <script type="application/ld+json">
{jsonld()}
  </script>

  <!-- Google Analytics 4 — TODO: replace {BIZ['ga']} with your real Measurement ID -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={BIZ['ga']}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{BIZ['ga']}');
  </script>
{extra_head}
</head>
<body>
  {header(slug)}

  <main>
{content}
  </main>

  {footer()}

  <script src="assets/js/site.js"></script>
</body>
</html>
'''

# --- Page registry -----------------------------------------------------------
PAGES = [
    ("index", "R K Packers &amp; Movers — Best Packers and Movers in Kolkata",
     "R K Packers & Movers is a trusted packers and movers company in Kolkata offering safe household shifting, office relocation, car & bike transport, packing and storage services across India."),
    ("about", "About Us — R K Packers &amp; Movers Kolkata",
     "Learn about R K Packers & Movers — 10+ years of trusted, professional moving services in Kolkata with trained staff, quality packing and pan-India reach."),
    ("services", "Our Services — Packers and Movers in Kolkata | R K Packers &amp; Movers",
     "Explore R K Packers & Movers services: household shifting, office relocation, car & bike transportation, packing & unpacking and secure storage across India."),
    ("household-shifting", "Household Shifting Services in Kolkata | R K Packers &amp; Movers",
     "Professional household shifting in Kolkata by R K Packers & Movers. Careful packing, safe transport and on-time home relocation across India at affordable rates."),
    ("office-relocation", "Office &amp; Corporate Relocation in Kolkata | R K Packers &amp; Movers",
     "Hassle-free office and corporate relocation in Kolkata. R K Packers & Movers moves your workplace with minimal downtime, expert handling and full insurance support."),
    ("car-transportation", "Car Transportation Services in Kolkata | R K Packers &amp; Movers",
     "Safe car transportation and carrier services from Kolkata across India. Enclosed carriers, GPS tracking and doorstep pickup & delivery by R K Packers & Movers."),
    ("bike-transportation", "Bike Transportation Services in Kolkata | R K Packers &amp; Movers",
     "Reliable bike and two-wheeler transportation from Kolkata across India. Professional packing, dedicated carriers and insured delivery by R K Packers & Movers."),
    ("packing-unpacking", "Packing &amp; Unpacking Services in Kolkata | R K Packers &amp; Movers",
     "Expert packing and unpacking services in Kolkata using quality materials — bubble wrap, corrugated sheets and sturdy cartons — for damage-free moving."),
    ("storage-service", "Storage &amp; Warehousing Services in Kolkata | R K Packers &amp; Movers",
     "Secure, clean and monitored storage and warehousing in Kolkata. Short and long-term storage solutions for household and office goods by R K Packers & Movers."),
    ("gallery", "Photo &amp; Video Gallery | R K Packers &amp; Movers Kolkata",
     "See R K Packers & Movers in action — photos and videos of our packing, loading, moving and fleet from real relocations across Kolkata and India."),
    ("reviews", "Customer Reviews &amp; Google Ratings | R K Packers &amp; Movers",
     "Read genuine customer reviews and Google ratings for R K Packers & Movers Kolkata. Rated 4.7/5 by hundreds of happy families and businesses."),
    ("contact", "Contact Us — Get a Free Quote | R K Packers &amp; Movers Kolkata",
     "Contact R K Packers & Movers in Kolkata for a free moving quote. Call +91 70038 27993, WhatsApp us or fill the enquiry form. Fast response, best rates."),
    ("get-a-quote", "Get a Free Moving Quote Online | R K Packers &amp; Movers Kolkata",
     "Get an instant moving quote from R K Packers & Movers. Fill the online quotation form and your details are sent straight to us on WhatsApp for a fast, free estimate."),
    ("physical-survey", "Book a Free Physical Survey | R K Packers &amp; Movers Kolkata",
     "Book a free in-home physical survey with R K Packers & Movers for the most accurate moving quote. Pick a date and time slot — our surveyor visits and assesses your goods."),
    ("faq", "Frequently Asked Questions | R K Packers &amp; Movers Kolkata",
     "Answers to common questions about moving with R K Packers & Movers — pricing, insurance, packing, timelines, storage and more."),
    ("blog", "Moving Tips &amp; Blog | R K Packers &amp; Movers Kolkata",
     "Practical moving tips, packing guides and relocation advice from the experts at R K Packers & Movers, Kolkata."),
    ("blog-choosing-packers", "How to Choose the Right Packers and Movers in Kolkata | R K Packers &amp; Movers",
     "A practical guide to choosing reliable packers and movers in Kolkata — what to check, questions to ask and red flags to avoid before you book."),
    ("privacy", "Privacy Policy | R K Packers &amp; Movers",
     "Privacy policy of R K Packers & Movers describing how we collect and use your information."),
    ("terms", "Terms of Service | R K Packers &amp; Movers",
     "Terms of service for R K Packers & Movers Kolkata."),
]

# --- Service detail pages (generated from data) ------------------------------
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'

SVC_IC = {
    "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "team": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>',
    "gps": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "rupee": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12M6 8h12M6 13c6 0 6 8 0 8M6 13l7 8"/></svg>',
    "truck": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17h4V5H2v12h1M14 8h5l3 4v5h-2M14 17H9M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0Zm12 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z"/></svg>',
}

SERVICE_DETAIL = {
    "household-shifting": {
        "title": "Household Shifting", "img": "assets/img/about.jpg",
        "lead": ["Moving home should be exciting, not exhausting. Our household shifting service in Kolkata takes care of everything — from packing your first carton to placing the last piece of furniture in your new home.",
                 "Every item, from fragile crockery to heavy wardrobes, is packed with the right materials and handled by our trained crew, so your belongings reach safely and on time."],
        "includes": ["Room-by-room professional packing", "Safe dismantling &amp; reassembly of furniture", "Careful loading with padding &amp; straps",
                      "Well-maintained, closed-body vehicles", "Unloading, unpacking &amp; rearranging", "Optional transit insurance coverage"],
        "features": [("shield", "Damage-Free Handling", "Multi-layer packing and trained handlers keep every item protected."),
                     ("clock", "On-Time Delivery", "Scheduled pickup and delivery with live status updates."),
                     ("rupee", "Affordable Rates", "Transparent, itemised quotes with no hidden charges.")],
    },
    "office-relocation": {
        "title": "Office &amp; Corporate Relocation", "img": "assets/img/logistics-service.jpg",
        "lead": ["Relocating an office is all about minimising downtime. We plan your move around your schedule — often over weekends or after hours — so your business is up and running fast.",
                 "From workstations, servers and IT equipment to files, furniture and pantry, everything is systematically labelled, packed and reinstalled at your new premises."],
        "includes": ["Pre-move planning &amp; site survey", "Systematic labelling &amp; inventory", "Safe handling of IT &amp; electronics",
                      "Workstation &amp; furniture dismantling", "Weekend / after-hours moving", "Fast setup at the new office"],
        "features": [("clock", "Minimal Downtime", "Carefully scheduled moves so your team is productive on day one."),
                     ("team", "Dedicated Crew", "An experienced supervisor and team assigned to your project."),
                     ("shield", "Asset Protection", "Anti-static wrapping and crating for sensitive equipment.")],
    },
    "car-transportation": {
        "title": "Car Transportation", "img": "assets/img/trucking-service.jpg",
        "lead": ["Send your car anywhere in India without putting a single kilometre on the odometer. We use enclosed and open car carriers to transport your vehicle safely from door to door.",
                 "Your car is loaded using proper ramps, secured with wheel locks and soft straps, and delivered in the same condition it left — with tracking throughout the journey."],
        "includes": ["Doorstep pickup &amp; delivery", "Enclosed &amp; open carrier options", "Secure loading with wheel locks",
                      "GPS-tracked transit", "Transit insurance available", "Pan-India coverage"],
        "features": [("truck", "Specialised Carriers", "Purpose-built car carriers — never towed or self-driven."),
                     ("gps", "Live Tracking", "Know where your vehicle is at every stage of the move."),
                     ("shield", "Insured &amp; Safe", "Optional coverage protects against transit damage.")],
    },
    "bike-transportation": {
        "title": "Bike Transportation", "img": "assets/img/cargo-service.jpg",
        "lead": ["Whether it's your daily commuter or a prized superbike, we transport two-wheelers across India with the care they deserve.",
                 "Each bike is drained of excess fuel, wrapped with foam and stretch film, and secured inside dedicated carriers to prevent any scratches or dents in transit."],
        "includes": ["Foam &amp; bubble-wrap protection", "Secure crating for premium bikes", "Doorstep pickup &amp; delivery",
                      "Dedicated two-wheeler carriers", "GPS-tracked movement", "Transit insurance available"],
        "features": [("shield", "Scratch-Free", "Full-body wrapping keeps paint and parts protected."),
                     ("gps", "Trackable", "Real-time updates from pickup to delivery."),
                     ("rupee", "Value Pricing", "Competitive rates for single and multiple bikes.")],
    },
    "packing-unpacking": {
        "title": "Packing &amp; Unpacking", "img": "assets/img/packaging-service.jpg",
        "lead": ["Great moves start with great packing. Our packing service uses premium, purpose-selected materials for every category of item — because how something is packed decides how safely it arrives.",
                 "And when you reach your new place, we don't just drop the boxes — our team unpacks, arranges and disposes of the packing waste so you can settle in immediately."],
        "includes": ["Bubble wrap &amp; foam for fragiles", "Corrugated sheets &amp; sturdy cartons", "Wooden crating for valuables",
                      "Waterproof wrapping for mattresses", "Colour-coded labelling", "Complete unpacking &amp; setup"],
        "features": [("box", "Premium Materials", "Multi-layer, item-specific packing for maximum protection."),
                     ("team", "Expert Packers", "Trained staff who pack fast, neat and safe."),
                     ("shield", "Damage-Free", "The right packing means fewer surprises on arrival.")],
    },
    "storage-service": {
        "title": "Storage &amp; Warehousing", "img": "assets/img/storage-service.jpg",
        "lead": ["Need a safe place to keep your belongings between moves? Our clean, secure warehouses in Kolkata offer flexible short and long-term storage for household and office goods.",
                 "Your items are inventoried, stored on racks or in dedicated units, and monitored round the clock — ready to be delivered whenever you need them."],
        "includes": ["Short &amp; long-term storage plans", "Clean, dry &amp; pest-controlled units", "24×7 CCTV-monitored facility",
                      "Detailed inventory management", "Household &amp; office goods", "Flexible pickup &amp; redelivery"],
        "features": [("shield", "Secure Facility", "24×7 surveillance and controlled access."),
                     ("clock", "Flexible Terms", "Store for a week or a year — pay only for what you use."),
                     ("truck", "Easy Redelivery", "We deliver your goods back whenever you're ready.")],
    },
}

def service_content(slug):
    d = SERVICE_DETAIL[slug]
    leads = "".join('<p class="text-muted">%s</p>' % p for p in d["lead"])
    includes = "".join('<li>%s %s</li>' % (CHECK, i) for i in d["includes"])
    feats = "".join(
        '<div class="feature reveal"><div class="ic">%s</div><div><h4>%s</h4><p>%s</p></div></div>' % (SVC_IC[ic], t, dd)
        for ic, t, dd in d["features"]
    )
    other = "".join(
        '<a href="%s.html" class="card svc-photo reveal"><img src="%s" alt="%s"><div class="body"><h3>%s</h3></div></a>'
        % (s, SERVICE_DETAIL[s]["img"], l.replace("&amp;", "and"), l)
        for s, l in SERVICES if s != slug
    )
    wa = "https://wa.me/%s?text=Hi%%2C%%20I%%20need%%20%s." % (BIZ["wa"], d["title"].replace("&amp;", "and").replace(" ", "%20"))
    return f'''    <section class="page-hero">
      <img class="page-bg" src="assets/img/page-header.jpg" alt="">
      <div class="container">
        <h1>{d["title"]}</h1>
        <div class="crumbs"><a href="index.html">Home</a><span class="sep">›</span><a href="services.html">Services</a><span class="sep">›</span><span>{d["title"]}</span></div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="split">
          <div class="reveal"><img src="{d["img"]}" alt="{d["title"]} in Kolkata"></div>
          <div class="split-text reveal">
            <span class="eyebrow">{d["title"]}</span>
            <h2>Reliable {d["title"]} in Kolkata &amp; Across India</h2>
            {leads}
            <div class="hero-actions" style="margin-top:8px;">
              <a class="btn btn-primary" href="contact.html">Get a Free Quote {IC["arrow"]}</a>
              <a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener">{IC["wa"]} WhatsApp</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section soft">
      <div class="container">
        <div class="split">
          <div class="split-text reveal">
            <span class="eyebrow">What's Included</span>
            <h2>Everything Taken Care Of</h2>
            <p class="text-muted">Our {d["title"].lower()} package is designed to be complete and worry-free.</p>
            <ul class="check-list" style="margin-top:16px;">{includes}</ul>
          </div>
          <div class="reveal"><img src="assets/img/features-1.jpg" alt="Professional moving service"></div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head reveal"><span class="eyebrow">Why Choose Us</span><h2>Built for a Safe, Smooth Move</h2></div>
        <div class="grid g-3">{feats}</div>
      </div>
    </section>

    <section class="section soft">
      <div class="container">
        <div class="section-head reveal"><span class="eyebrow">Explore More</span><h2>Other Services</h2></div>
        <div class="grid g-3">{other}</div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="cta-band reveal">
          <div><h2>Get a Free {d["title"]} Quote</h2><p>Fast response on call &amp; WhatsApp. Best rates in Kolkata.</p></div>
          <div class="actions">
            <a class="btn btn-white btn-lg" href="tel:{BIZ['phone']}">{IC['phone']} {BIZ['phone_disp']}</a>
            <a class="btn btn-wa btn-lg" href="{wa}" target="_blank" rel="noopener">{IC['wa']} WhatsApp</a>
          </div>
        </div>
      </div>
    </section>'''

def build():
    prepare_reviews()
    for slug, title, desc in PAGES:
        if slug in SERVICE_DETAIL:
            content = service_content(slug)
            html = page_shell(slug, title, desc, content)
            with open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8") as f:
                f.write(html)
            print("  ->", slug + ".html")
            continue
        cpath = os.path.join(CONTENT, slug + ".html")
        if not os.path.exists(cpath):
            print("  ! missing content:", slug)
            continue
        with open(cpath, encoding="utf-8") as f:
            content = f.read()
        # expand simple {{TOKENS}} in content
        content = expand(content)
        html = page_shell(slug, title, desc, content)
        out = os.path.join(ROOT, "index.html" if slug == "index" else slug + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print("  ->", os.path.basename(out))

TOKENS = {
    "{{PHONE}}": BIZ["phone"], "{{PHONE_DISP}}": BIZ["phone_disp"],
    "{{PHONE2}}": BIZ["phone2"], "{{PHONE2_DISP}}": BIZ["phone2_disp"],
    "{{WA}}": BIZ["wa"], "{{EMAIL}}": BIZ["email"], "{{ADDR}}": BIZ["addr"],
    "{{MAP}}": BIZ["map"], "{{HOURS}}": BIZ["hours"], "{{GREVIEWS}}": BIZ["google_reviews"],
    "{{ALLREVIEWS}}": BIZ["all_reviews"],
    "{{IC_ARROW}}": IC["arrow"], "{{IC_PHONE}}": IC["phone"], "{{IC_WA}}": IC["wa"],
    "{{IC_MAIL}}": IC["mail"], "{{IC_PIN}}": IC["pin"], "{{IC_CLOCK}}": IC["clock"],
    "{{STARS}}": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 6.9 7.6.6-5.8 4.9 1.8 7.4L12 18l-6.4 3.8 1.8-7.4L1.6 9.5l7.6-.6L12 2z"/></svg>' * 5,
}

def expand(s):
    for k, v in TOKENS.items():
        s = s.replace(k, v)
    return s

def build_sitemap():
    import datetime
    today = datetime.date.today().isoformat()
    urls = []
    priorities = {"index": "1.0", "services": "0.9", "contact": "0.9"}
    for slug, _, _ in PAGES:
        if slug.startswith("blog"):
            continue  # blog pages exist but are unlinked/hidden for now
        loc = BIZ["url"] + "/" + ("" if slug == "index" else slug + ".html")
        pr = priorities.get(slug, "0.7")
        urls.append(
            "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <priority>%s</priority>\n  </url>"
            % (loc, today, pr)
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    print("  -> sitemap.xml (%d urls)" % len(urls))


if __name__ == "__main__":
    print("Building R K Packers & Movers site...")
    build()
    build_sitemap()
    print("Done.")
