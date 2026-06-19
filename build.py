#!/usr/bin/env python3
"""Tiny static site generator.

Each page is a Python dict with:
  path:        url path (e.g. "/motor-upgrades/")
  title:       <title>
  desc:        meta description
  h1:          page H1
  schema:      list of extra JSON-LD blobs (BreadcrumbList added automatically)
  body:        HTML body (everything between header and footer)

Run `python3 build.py` from the repo root. Outputs to `site/`.
"""
from __future__ import annotations
import json, pathlib, re, shutil

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
PHONE = "832-832-1993"
EMAIL = "sales@whitelightningmotors.com"
BASE  = "https://whitelightningmotors.com"

NAV = [
    ("/", "Home"),
    ("/services/", "Services", [
        ("/motor-upgrades/", "Motor Upgrades"),
        ("/lithium-batteries/", "Lithium Batteries"),
        ("/controllers/", "Controllers"),
        ("/ac-conversion/", "AC Kits"),
    ]),
    ("/how-it-works/", "How It Works"),
    ("/reviews/", "Reviews"),
]

def head(title, desc, path, extra_schema=None, crumbs=None):
    canonical = f"{BASE}{path}"
    schema_blobs = []
    # Site-wide AutomotiveBusiness
    schema_blobs.append({
        "@context":"https://schema.org",
        "@type":"AutomotiveBusiness",
        "name":"White Lightning Motors, LLC",
        "description":"Performance golf cart motor upgrades, lithium battery conversions, Navitas controllers, and full AC kits. Mail-in service nationwide from Texas.",
        "telephone":f"+1-{PHONE}",
        "email":EMAIL,
        "url":BASE+"/",
        "priceRange":"$$",
        "areaServed":"United States",
        "aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"11"}
    })
    if crumbs:
        items = []
        for i,(name,p) in enumerate(crumbs, start=1):
            items.append({"@type":"ListItem","position":i,"name":name,"item":BASE+p})
        schema_blobs.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items})
    if extra_schema:
        schema_blobs.extend(extra_schema)
    schema_html = "\n".join(f'<script type="application/ld+json">{json.dumps(s, separators=(",",":"))}</script>' for s in schema_blobs)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="/assets/site.css">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="White Lightning Motors">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
{schema_html}
</head>
<body>
'''

def header(active_path):
    links = ""
    for item in NAV:
        if len(item) == 3:
            href, label, children = item
            child_paths = {href} | {c[0] for c in children}
            cur = ' aria-current="page"' if active_path in child_paths else ""
            menu_parts = []
            for c in children:
                ccur = ' aria-current="page"' if c[0]==active_path else ""
                menu_parts.append(f'<a href="{c[0]}"{ccur}>{c[1]}</a>')
            menu = "".join(menu_parts)
            links += (
                f'<div class="nav-dropdown">'
                f'<a href="{href}"{cur} aria-haspopup="true">{label} <span aria-hidden="true">▾</span></a>'
                f'<div class="nav-dropdown-menu" role="menu">{menu}</div>'
                f'</div>\n      '
            )
        else:
            href, label = item
            cur = ' aria-current="page"' if href == active_path else ""
            links += f'<a href="{href}"{cur}>{label}</a>\n      '
    return f'''<header class="site-header">
  <div class="container">
    <a class="brand" href="/">
      <span class="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z" fill="#00c2ff"/>
        </svg>
      </span>
      <span class="brand-text">White Lightning Motors<small>Performance Golf Carts</small></span>
    </a>
    <nav class="primary">
      {links}<a class="btn btn-bolt" href="tel:8328321993">📞 {PHONE}</a>
    </nav>
  </div>
</header>
'''

def footer():
    return f'''<footer class="site">
  <div class="container">
    <div class="grid">
      <div>
        <div class="brand" style="margin-bottom:12px">
          <span class="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z" fill="#00c2ff"/></svg>
          </span>
          <span class="brand-text">White Lightning Motors<small>Performance Golf Carts</small></span>
        </div>
        <p style="margin:0;max-width:340px">Bolt-in performance motor upgrades, lithium conversions, Navitas controllers, and full AC kits. Shipped nationwide from Texas.</p>
      </div>
      <div>
        <h5>By Cart Brand</h5>
        <a href="/motor-upgrades/ezgo/">EZGO Upgrades</a>
        <a href="/motor-upgrades/club-car/">Club Car Upgrades</a>
        <a href="/motor-upgrades/yamaha/">Yamaha Upgrades</a>
        <a href="/motor-upgrades/icon/">ICON Upgrades</a>
      </div>
      <div>
        <h5>Services</h5>
        <a href="/services/">All Services</a>
        <a href="/motor-upgrades/">Motor Upgrades</a>
        <a href="/lithium-batteries/">Lithium Batteries</a>
        <a href="/controllers/">Controllers</a>
        <a href="/ac-conversion/">AC Kits</a>
        <a href="/how-it-works/">How It Works</a>
      </div>
      <div>
        <h5>Company</h5>
        <a href="/about/">About</a>
        <a href="/reviews/">Reviews</a>
        <a href="/faq/">FAQ</a>
        <a href="/blog/">Blog</a>
        <a href="/contact/">Contact</a>
      </div>
      <div>
        <h5>Contact</h5>
        <a href="tel:8328321993">{PHONE}</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <a href="https://www.facebook.com/whitelightningmotors" rel="nofollow">Facebook</a>
      </div>
    </div>
    <div class="legal">
      <span>© White Lightning Motors, LLC. All rights reserved.</span>
      <span>Performance upgrades sold for off-road / private property use. Always wear a seat belt.</span>
    </div>
  </div>
</footer>
</body>
</html>'''

def page_hero(crumbs_html, eyebrow, h1_html, lede_html, stats_html="", img=None, img_alt=""):
    """Render a unified page hero. If `img` is given, use 2-column layout with photo."""
    left = f'''
    <div class="crumbs">{crumbs_html}</div>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1_html}</h1>
    <p class="lede">{lede_html}</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 {PHONE}</a>
      <a class="btn btn-ghost" href="/contact/">Get a quote →</a>
    </div>
    {stats_html}'''
    if img:
        art = f'<div class="page-hero-art"><img src="{img}" alt="{img_alt}" loading="eager" fetchpriority="high" onerror="this.parentElement.style.display=\'none\'"></div>'
        return f'''<section class="page-hero">
  <div class="container page-hero-grid">
    <div>{left}</div>
    {art}
  </div>
</section>
'''
    return f'''<section class="page-hero">
  <div class="container">{left}
  </div>
</section>
'''

def inject_hero_image(body, img, alt):
    """Patch a body's first .page-hero block to add a side image."""
    open_tag = '<section class="page-hero">\n  <div class="container">'
    if open_tag not in body:
        return body
    art = f'<div class="page-hero-art"><img src="{img}" alt="{alt}" loading="eager" fetchpriority="high" onerror="this.parentElement.style.display=\'none\'"></div>'
    new_open = '<section class="page-hero">\n  <div class="container page-hero-grid">\n    <div>'
    # Replace opening
    patched = body.replace(open_tag, new_open, 1)
    # Find the matching `</div>\n</section>` (the container close) and inject the art before it
    needle = "  </div>\n</section>"
    idx = patched.find(needle)
    if idx == -1:
        return body
    # Close the wrapping inner <div>, then add art, then keep original closes
    patched = patched[:idx] + f'    </div>\n    {art}\n  </div>\n</section>' + patched[idx+len(needle):]
    return patched

def render(page):
    html = head(page["title"], page["desc"], page["path"], page.get("schema"), page.get("crumbs"))
    html += header(page["path"])
    body = page["body"]
    if page.get("hero_image"):
        body = inject_hero_image(body, page["hero_image"], page.get("hero_alt",""))
    html += body
    html += footer()
    return html

def write(page):
    out = SITE / page["path"].strip("/") / "index.html" if page["path"] != "/" else SITE / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(page))
    print(f"  wrote {out.relative_to(ROOT)}")

# ---------- Shared HTML helpers ----------
CTA_BAND = f'''
<section class="alt">
  <div class="container">
    <div class="cta-band">
      <span class="eyebrow">Ready to rip?</span>
      <h2>Send Charlie your cart info. Get a real quote in minutes.</h2>
      <p>No forms-to-nowhere. No salespeople. The phone goes straight to the guy building the motors.</p>
      <div class="hero-ctas" style="justify-content:center">
        <a class="btn btn-bolt" href="tel:8328321993">📞 {PHONE}</a>
        <a class="btn btn-ghost" href="/contact/">Get a quote →</a>
      </div>
    </div>
  </div>
</section>
'''

def brands_strip():
    return '''<section style="padding:36px 0"><div class="container"><div class="brands">
      <span>We upgrade</span>
      <b>EZGO</b><b>Club Car</b><b>Yamaha</b><b>Star Cart</b><b>ICON</b><b>Evolution</b>
    </div></div></section>'''

def faq_schema(qa):
    return {"@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qa]}

def faq_html(qa):
    items = "\n".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in qa)
    return f'<div class="faq">{items}</div>'

def review_schema(reviews):
    out = []
    for name, body, source in reviews:
        out.append({"@context":"https://schema.org","@type":"Review",
                    "itemReviewed":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC"},
                    "reviewRating":{"@type":"Rating","ratingValue":"5","bestRating":"5"},
                    "author":{"@type":"Person","name":name},
                    "publisher":{"@type":"Organization","name":source},
                    "reviewBody":body})
    return out

# ---------- Page content ----------
PAGES = []

# ============================================================
# HOME
# ============================================================
HOME_BODY = '''
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow">⚡ Performance Golf Cart Motors</span>
      <h1>Turn your stock cart into <span class="bolt">white lightning.</span></h1>
      <p class="lede">Bolt-in motor upgrades engineered to take your EZGO, Club Car, Yamaha, or Star Cart from a sleepy 14 mph to 25+ mph — without dropping a fortune on a new controller or AC system. Mail it in. We'll ship it back ready to rip.</p>
      <div class="hero-ctas">
        <a class="btn btn-bolt" href="/motor-upgrades/">See motor upgrades →</a>
        <a class="btn btn-ghost" href="tel:8328321993">📞 Call Charlie · 832-832-1993</a>
      </div>
      <div class="hero-stats">
        <div><b>14 → 27</b><span>mph stock to upgraded</span></div>
        <div><b>$325</b><span>motor upgrade</span></div>
        <div><b>1-yr</b><span>warranty included</span></div>
        <div><b>5.0★</b><span>customer rating</span></div>
      </div>
    </div>
    <div class="hero-art">
      <img src="/assets/photos/hero-cart.jpg" alt="Lifted black 4-seater golf cart with HAVOC graphics and White Lightning Motors performance build" class="hero-photo" onerror="this.style.display='none'" loading="eager" fetchpriority="high" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:2">
      <svg viewBox="0 0 500 600" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Performance golf cart with custom lift kit">
        <defs>
          <linearGradient id="bg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0a1322"/><stop offset="1" stop-color="#000"/></linearGradient>
          <linearGradient id="bolt" x1="0" x2="1"><stop offset="0" stop-color="#00c2ff"/><stop offset="1" stop-color="#1a8bff"/></linearGradient>
          <radialGradient id="glow" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#00c2ff" stop-opacity=".35"/><stop offset="1" stop-color="#00c2ff" stop-opacity="0"/></radialGradient>
        </defs>
        <rect width="500" height="600" fill="url(#bg)"/><rect width="500" height="600" fill="url(#glow)"/>
        <path d="M340 60 L180 320 L280 320 L200 540 L380 240 L290 240 L360 60 Z" fill="url(#bolt)" opacity=".18"/>
        <ellipse cx="250" cy="500" rx="220" ry="14" fill="#00c2ff" opacity=".15"/>
        <g transform="translate(60,260)">
          <rect x="20" y="0" width="340" height="18" rx="4" fill="#0d0d0f"/><rect x="40" y="-6" width="300" height="8" rx="2" fill="#1a1a20"/>
          <rect x="30" y="18" width="6" height="60" fill="#0d0d0f"/><rect x="344" y="18" width="6" height="60" fill="#0d0d0f"/>
          <path d="M40 78 L100 30 L100 78 Z" fill="#101820" opacity=".7"/>
          <path d="M20 78 L100 78 L130 120 L260 120 L290 78 L360 78 L370 180 L10 180 Z" fill="#0a0a0d"/>
          <path d="M120 100 L260 100 L240 130 L280 130 L160 175 L180 145 L150 145 Z" fill="url(#bolt)" opacity=".85"/>
          <rect x="115" y="85" width="55" height="30" rx="3" fill="#1d1d24"/><rect x="210" y="85" width="55" height="30" rx="3" fill="#1d1d24"/>
          <rect x="0" y="175" width="380" height="14" rx="3" fill="#15151b"/>
          <g><circle cx="70" cy="200" r="38" fill="#0a0a0a"/><circle cx="70" cy="200" r="20" fill="#1c1c22"/><circle cx="70" cy="200" r="8" fill="#00c2ff" opacity=".4"/></g>
          <g><circle cx="310" cy="200" r="38" fill="#0a0a0a"/><circle cx="310" cy="200" r="20" fill="#1c1c22"/><circle cx="310" cy="200" r="8" fill="#00c2ff" opacity=".4"/></g>
          <ellipse cx="375" cy="130" rx="20" ry="6" fill="#00c2ff" opacity=".75"/>
        </g>
      </svg>
      <div class="badge">⚡ Real builds, real customers — <b>30 mph</b> on this one.</div>
    </div>
  </div>
</section>
''' + brands_strip() + '''
<section id="upgrades" class="light">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">The upgrade</span>
      <h2>Stock motors are slow on purpose. We fix that.</h2>
      <p>Our high-output motor swap drops straight into your existing controller and battery pack. No new controller required to feel a massive jump in top speed and torque. Add a Navitas controller, lithium battery, or full AC kit when you're ready to chase 30+.</p>
    </div>
    <div class="speed-wrap">
      <div class="speed-card">
        <h3>Before · Stock motor</h3>
        <div class="speed-row"><div class="label">Top Speed <small>EZGO TXT stock</small></div><div class="bar"><span style="width:48%"></span></div></div>
        <div class="speed-row"><div class="label">Hill Torque <small>loaded with passengers</small></div><div class="bar"><span style="width:42%"></span></div></div>
        <div class="speed-row"><div class="label">Acceleration</div><div class="bar"><span style="width:38%"></span></div></div>
        <div class="note">~14.8 mph · sluggish off the line · bogs on grades</div>
      </div>
      <div class="speed-card" style="border-color:rgba(11,111,161,.4)">
        <h3>After · White Lightning motor</h3>
        <div class="speed-row"><div class="label">Top Speed <small>same cart, same batteries</small></div><div class="bar fast"><span style="width:90%"></span></div></div>
        <div class="speed-row"><div class="label">Hill Torque</div><div class="bar fast"><span style="width:92%"></span></div></div>
        <div class="speed-row"><div class="label">Acceleration</div><div class="bar fast"><span style="width:88%"></span></div></div>
        <div class="note" style="color:#0b6fa1">27+ mph · pulls hills loaded · snaps off the line</div>
      </div>
    </div>
  </div>
</section>

<section id="products">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">What we build</span>
      <h2>Pick your upgrade path.</h2>
      <p>Start with the motor swap. Add a controller, batteries, and AC kit as your goals grow.</p>
    </div>
    <div class="product-photos">
      <a href="/motor-upgrades/"><img src="/assets/photos/product-motor.jpg" alt="High-output golf cart motor — White Lightning Motors" loading="lazy"><span>High-Output Motor</span></a>
      <a href="/motor-upgrades/#solenoids"><img src="/assets/photos/product-solenoid-clean.jpg" alt="Bolt Energy heavy-duty contactor / solenoid for 48V lithium golf cart builds" loading="lazy"><span>HD Contactor</span></a>
      <a href="/lithium-batteries/"><img src="/assets/photos/product-lithium-clean.jpg" alt="Bolt Energy 48V 105Ah lithium iron phosphate golf cart battery" loading="lazy"><span>Bolt Energy Lithium</span></a>
      <a href="/controllers/"><img src="/assets/photos/product-controller.jpg" alt="Navitas DC TSX programmable golf cart controller" loading="lazy"><span>Navitas Controller</span></a>
    </div>
    <div class="products">
      <a class="product" href="/motor-upgrades/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg></div>
        <h3>High-Output Motor Upgrade</h3>
        <div class="price">From $325</div>
        <p>Bolt-in replacement that adds 8–12 mph and big torque on a stock controller. The product that built our reputation.</p>
      </a>
      <a class="product" href="/lithium-batteries/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="7" width="16" height="10" rx="2"/><path d="M9 7V4h6v3M8 12h2M14 12h2"/></svg></div>
        <h3>Bolt Energy Lithium</h3>
        <div class="price">Contact for pricing</div>
        <p>Drop a lithium pack in and lose 200+ lbs of lead. More range, faster recharge, no more watering cells.</p>
      </a>
      <a class="product" href="/controllers/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h4l3-7 4 14 3-7h4"/></svg></div>
        <h3>Navitas Controller</h3>
        <div class="price">Contact for pricing</div>
        <p>Programmable DC controller that unlocks the full potential of your upgraded motor. Bluetooth tuning app included.</p>
      </a>
      <a class="product" href="/ac-conversion/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg></div>
        <h3>Full AC Conversion</h3>
        <div class="price">Contact for pricing</div>
        <p>Complete AC motor and controller conversion. The endgame: regen braking, near-silent operation, 30+ mph capable.</p>
      </a>
      <a class="product" href="/motor-upgrades/#solenoids" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z"/></svg></div>
        <h3>Heavy-Duty Solenoid</h3>
        <div class="price">$75</div>
        <p>36/48-volt heavy-duty solenoid built to handle the extra current high-output motors and lithium packs throw at it.</p>
      </a>
      <a class="product" href="/contact/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg></div>
        <h3>Custom Builds & Service</h3>
        <div class="price">Quote on request</div>
        <p>Full builds, troubleshooting, electrical work, and tuning for dealers and serious enthusiasts. Charlie has built hundreds.</p>
      </a>
    </div>
  </div>
</section>

<section style="padding:0">
  <div class="gallery">
    <figure><img src="/assets/photos/motor-install.jpg" alt="Installed White Lightning Motors high-output motor on a customer's cart" loading="lazy" onerror="this.parentElement.style.display='none'"><figcaption>Bench-built, customer-installed. Same sticker on every motor we ship.</figcaption></figure>
    <figure><img src="/assets/photos/truck-side.jpg" alt="White Lightning Motors wrapped Ford F-150 shop truck — side view" loading="lazy" onerror="this.parentElement.style.display='none'"><figcaption>Our shop truck. If you see it on the road, that's Charlie.</figcaption></figure>
    <figure><img src="/assets/photos/truck-back.jpg" alt="White Lightning Motors wrapped Ford F-150 shop truck — rear view" loading="lazy" onerror="this.parentElement.style.display='none'"><figcaption>Performance golf cart motors · lithium upgrades · 832-832-1993</figcaption></figure>
  </div>
</section>

<section id="how" class="alt">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Mail-in service</span>
      <h2>From sluggish to lightning in 4 steps.</h2>
      <p>You don't have to live in Texas to get one. <a href="/how-it-works/">See the full process →</a></p>
    </div>
    <div class="steps">
      <div class="step"><div class="n">1</div><h3>Call or text Charlie</h3><p>Tell him your cart make, model, and year. He'll tell you exactly which motor you need.</p></div>
      <div class="step"><div class="n">2</div><h3>Pull & ship your motor</h3><p>Two bolts and the wiring lugs. We send shipping instructions.</p></div>
      <div class="step"><div class="n">3</div><h3>We build & bench-test</h3><p>Your upgraded motor is built, dynoed, and sealed. 4–7 day turnaround.</p></div>
      <div class="step"><div class="n">4</div><h3>We ship it back free</h3><p>Bolt it in. Reconnect the lugs. Smile. 1-year warranty starts day of arrival.</p></div>
    </div>
  </div>
</section>

<section id="reviews" class="light">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">★★★★★ Customer reviews</span>
      <h2>"The fastest cart in the neighborhood."</h2>
      <p>100% recommend on Facebook · 5.0 on Google · <a href="/reviews/">read every review →</a></p>
    </div>
    <div class="reviews">
      <div class="review"><div class="stars">★★★★★</div><p>"Charlie got me set up with an awesome motor upgrade. Quick turn around time. Cart went from 14.8 mph to over 27 mph on stock tired batteries."</p><div class="who"><b>Travis Holm</b><span>Google · Local Guide</span></div></div>
      <div class="review"><div class="stars">★★★★★</div><p>"Best bang for the buck! Charlie is the best! Fast, reliable, best in the business. White Lightning Motors for the win!"</p><div class="who"><b>Bobby Bentley</b><span>Facebook recommendation</span></div></div>
      <div class="review"><div class="stars">★★★★★</div><p>"Carts are getting 30 mph without spending big dollars on an upgraded controller or AC system. Repeat customer."</p><div class="who"><b>Justin Whitaker</b><span>Tejas Golf Carts</span></div></div>
    </div>
  </div>
</section>
''' + CTA_BAND

SERVICES_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Services</div>
    <span class="eyebrow">All services</span>
    <h1>Everything we build.</h1>
    <p class="lede">High-output motor upgrades, Bolt Energy lithium conversions, Navitas programmable controllers, and full AC kits — all shipped nationwide from our Texas shop.</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 {PHONE}</a>
      <a class="btn btn-ghost" href="/contact/">Get a quote →</a>
    </div>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Pick your upgrade</span>
      <h2>Four services. Built and tested by Charlie.</h2>
      <p>Start with what fits your budget today. Every service stacks — motor + controller + lithium is the most-requested combo.</p>
    </div>
    <div class="products">
      <a class="product" href="/motor-upgrades/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg></div>
        <h3>Motor Upgrades</h3>
        <div class="price">From $325</div>
        <p>Bolt-in high-output motor that adds 8–12 mph on a stock controller. EZGO, Club Car, Yamaha, ICON.</p>
        <ul class="featurelist"><li>✓ Drops into stock controller</li><li>✓ 1-year warranty</li><li>✓ Free return shipping</li></ul>
      </a>
      <a class="product" href="/lithium-batteries/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="7" width="16" height="10" rx="2"/><path d="M9 7V4h6v3M8 12h2M14 12h2"/></svg></div>
        <h3>Lithium Batteries</h3>
        <div class="price">Quote on request</div>
        <p>Authorized Bolt Energy dealer. LiFePO4 packs with Bluetooth BMS, 8+ year lifespan, 250 lbs lighter than lead-acid.</p>
        <ul class="featurelist"><li>✓ 48V & 72V configurations</li><li>✓ Cart-specific brackets</li><li>✓ Lithium-specific charger included</li></ul>
      </a>
      <a class="product" href="/controllers/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h4l3-7 4 14 3-7h4"/></svg></div>
        <h3>Navitas Controllers</h3>
        <div class="price">Quote on request</div>
        <p>Programmable DC TSX controllers with Bluetooth tuning. Pair with our motor upgrade for the strongest budget performance combo on the market.</p>
        <ul class="featurelist"><li>✓ 400A & 600A models</li><li>✓ Bluetooth tuning app</li><li>✓ Compatible with stock throttle</li></ul>
      </a>
      <a class="product" href="/ac-conversion/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg></div>
        <h3>AC Conversion Kits</h3>
        <div class="price">Quote on request</div>
        <p>Full brushless AC motor + controller conversion. Regen braking, near-silent operation, 30+ mph capable. The endgame build.</p>
        <ul class="featurelist"><li>✓ AC motor + controller + harness</li><li>✓ Regenerative braking</li><li>✓ Fits EZGO, Club Car, Yamaha</li></ul>
      </a>
    </div>
  </div>
</section>
''' + CTA_BAND

SERVICES_SCHEMA = [
    {
        "@context":"https://schema.org",
        "@type":"OfferCatalog",
        "name":"White Lightning Motors — Performance Golf Cart Services",
        "url":f"{BASE}/services/",
        "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC","telephone":f"+1-{PHONE}","url":BASE+"/"},
        "itemListElement":[
            {
                "@type":"Offer",
                "itemOffered":{
                    "@type":"Service",
                    "name":"High-Output Golf Cart Motor Upgrade",
                    "description":"Bolt-in high-output replacement motor for EZGO, Club Car, Yamaha, and ICON golf carts. Adds 8–12 mph on a stock controller. 1-year warranty, free return shipping, mail-in service.",
                    "serviceType":"Performance motor upgrade",
                    "areaServed":"United States",
                    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC"},
                    "url":f"{BASE}/motor-upgrades/",
                    "image":f"{BASE}/assets/photos/install-headon.jpg",
                },
                "price":"325","priceCurrency":"USD",
                "priceSpecification":{"@type":"PriceSpecification","price":"325","priceCurrency":"USD","valueAddedTaxIncluded":False},
                "availability":"https://schema.org/InStock",
                "url":f"{BASE}/motor-upgrades/",
            },
            {
                "@type":"Offer",
                "itemOffered":{
                    "@type":"Service",
                    "name":"Bolt Energy Lithium Battery Conversion",
                    "description":"Authorized Bolt Energy dealer install of 48V/72V LiFePO4 lithium battery packs with Bluetooth BMS, lithium-specific charger, and cart-specific brackets. Saves 250 lbs and doubles usable range vs lead-acid.",
                    "serviceType":"Lithium battery conversion",
                    "areaServed":"United States",
                    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC"},
                    "url":f"{BASE}/lithium-batteries/",
                    "image":f"{BASE}/assets/photos/bolt-txt-kit.jpg",
                },
                "url":f"{BASE}/lithium-batteries/",
                "availability":"https://schema.org/InStock",
            },
            {
                "@type":"Offer",
                "itemOffered":{
                    "@type":"Service",
                    "name":"Navitas DC TSX Programmable Controller",
                    "description":"Navitas DC TSX 400A and 600A programmable controller installs with Bluetooth tuning. Adjustable top speed, acceleration, regenerative braking, and current limits.",
                    "serviceType":"Programmable controller install",
                    "areaServed":"United States",
                    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC"},
                    "url":f"{BASE}/controllers/",
                    "image":f"{BASE}/assets/photos/product-controller.jpg",
                },
                "url":f"{BASE}/controllers/",
                "availability":"https://schema.org/InStock",
            },
            {
                "@type":"Offer",
                "itemOffered":{
                    "@type":"Service",
                    "name":"Full AC Conversion Kit",
                    "description":"Complete brushless AC motor and controller conversion for EZGO, Club Car, and Yamaha carts. Includes motor, controller, harness, throttle adapter, and contactor. Regenerative braking and 30+ mph capable.",
                    "serviceType":"AC motor conversion",
                    "areaServed":"United States",
                    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC"},
                    "url":f"{BASE}/ac-conversion/",
                },
                "url":f"{BASE}/ac-conversion/",
                "availability":"https://schema.org/InStock",
            },
        ],
    },
    # ItemList for AI engines that prefer it over OfferCatalog
    {
        "@context":"https://schema.org",
        "@type":"ItemList",
        "name":"White Lightning Motors Services",
        "itemListOrder":"https://schema.org/ItemListOrderAscending",
        "numberOfItems":4,
        "itemListElement":[
            {"@type":"ListItem","position":1,"url":f"{BASE}/motor-upgrades/","name":"Motor Upgrades"},
            {"@type":"ListItem","position":2,"url":f"{BASE}/lithium-batteries/","name":"Lithium Batteries"},
            {"@type":"ListItem","position":3,"url":f"{BASE}/controllers/","name":"Navitas Controllers"},
            {"@type":"ListItem","position":4,"url":f"{BASE}/ac-conversion/","name":"AC Conversion Kits"},
        ],
    },
]

PAGES.append({
    "path":"/services/",
    "title":"Services — Motor Upgrades, Lithium, Controllers, AC Kits | White Lightning Motors",
    "desc":"Every service White Lightning Motors offers — high-output motor upgrades, Bolt Energy lithium conversions, Navitas programmable controllers, and full AC kits. Mail-in service nationwide.",
    "crumbs":[("Home","/"),("Services","/services/")],
    "schema":SERVICES_SCHEMA,
    "body":SERVICES_BODY,
})

PAGES.append({
    "path":"/",
    "title":"Performance Golf Cart Motors & Lithium Upgrades | White Lightning Motors",
    "desc":"Bolt-in golf cart motor upgrades that take stock carts from 14 mph to 25+ mph. EZGO, Club Car, Yamaha, ICON. Mail-in service, 1-year warranty, free return shipping. Call 832-832-1993.",
    "body":HOME_BODY,
})

# ============================================================
# MOTOR UPGRADES (pillar)
# ============================================================
MU_FAQ = [
    ("How fast will my cart go after a White Lightning motor upgrade?",
     "Most customers see 25–28 mph on the motor swap alone with healthy 36V or 48V batteries on a stock controller. With an upgraded Navitas controller and a lithium pack, 30+ mph is realistic. Travis Holm went from 14.8 to over 27 mph on tired stock batteries — that's our floor, not our ceiling."),
    ("Will the upgrade work with my stock controller?",
     "Yes. Our high-output motor is engineered to bolt straight into your existing stock controller. You'll see a big jump in speed and torque without buying anything else. You can add a Navitas DC controller later when you want more."),
    ("Which carts are supported?",
     "EZGO TXT, RXV, Marathon, Medalist. Club Car DS, Precedent, Onward, Tempo. Yamaha G-series, Drive, Drive 2. Star Cart, ICON, and Evolution. If your model isn't listed, call Charlie at 832-832-1993."),
    ("Do I need a new solenoid?",
     "Recommended. The factory 100A solenoid is the weak link when you push more current through it. Our $75 heavy-duty 36V/48V solenoid is the cheapest insurance you can buy on a performance build."),
    ("Will this void my factory warranty?",
     "If your cart is still under factory warranty, performance upgrades typically void the powertrain warranty. We pair every motor with a 1-year warranty of our own to keep you covered."),
    ("How long does turnaround take?",
     "Standard mail-in motor upgrades go out within 4–7 business days of arrival at our Texas shop. Rush options are available if you need it faster — just ask when you call."),
]

MU_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Motor Upgrades</div>
    <span class="eyebrow">Performance motor upgrades</span>
    <h1>Golf cart motor upgrades that actually <span class="bolt">work.</span></h1>
    <p class="lede">High-output bolt-in motors built and tested in Texas for EZGO, Club Car, Yamaha, ICON, and Evolution carts. Drop straight into your stock controller. Add a Navitas controller, lithium pack, or full AC kit when you're ready to chase 30+ mph.</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 Quote in 5 minutes — {PHONE}</a>
      <a class="btn btn-ghost" href="/how-it-works/">How mail-in works →</a>
    </div>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">By brand</span>
      <h2>Pick your cart.</h2>
      <p>Same motor philosophy, different mounting plate and shaft spec for each brand. Every motor is bench-built and dynoed before it ships.</p>
    </div>
    <div class="products">
      <a class="product" href="/motor-upgrades/ezgo/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z"/></svg></div>
        <h3>EZGO Motor Upgrade</h3>
        <div class="price">From $325</div>
        <p>TXT, RXV, Marathon, Medalist. 36V and 48V series-wound replacements.</p>
        <ul class="featurelist"><li>✓ TXT 1994.5–present</li><li>✓ RXV 48V</li><li>✓ Stock controller compatible</li></ul>
      </a>
      <a class="product" href="/motor-upgrades/club-car/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z"/></svg></div>
        <h3>Club Car Motor Upgrade</h3>
        <div class="price">From $325</div>
        <p>DS, Precedent, Onward, Tempo. IQ and Excel system compatible.</p>
        <ul class="featurelist"><li>✓ DS 36V & 48V</li><li>✓ Precedent IQ</li><li>✓ Onward / Tempo</li></ul>
      </a>
      <a class="product" href="/motor-upgrades/yamaha/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z"/></svg></div>
        <h3>Yamaha Motor Upgrade</h3>
        <div class="price">From $325</div>
        <p>G19, G22, G29 Drive, Drive 2 electric models.</p>
        <ul class="featurelist"><li>✓ G-series 48V</li><li>✓ Drive / Drive 2 AC</li><li>✓ Stock or Navitas compatible</li></ul>
      </a>
      <a class="product" href="/motor-upgrades/icon/" style="text-decoration:none;color:inherit;display:block">
        <div class="icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z"/></svg></div>
        <h3>ICON Motor Upgrade</h3>
        <div class="price">From $325</div>
        <p>EV i20, i40, i60 series. Drop-in replacement motors.</p>
        <ul class="featurelist"><li>✓ i20/i40/i60</li><li>✓ Direct fit</li><li>✓ Quote on year/trim</li></ul>
      </a>
    </div>
  </div>
</section>

<section style="padding:0">
  <div class="gallery">
    <figure><img src="/assets/photos/install-headon.jpg" alt="White Lightning Motors high-output motor installed under a customer golf cart — head-on view with WLM sticker visible" loading="lazy"><figcaption>Installed in the customer's cart — every motor wears the WLM sticker.</figcaption></figure>
    <figure><img src="/assets/photos/install-wide.jpg" alt="Customer cart with White Lightning Motors performance motor installed — wide undercarriage shot" loading="lazy"><figcaption>The view from underneath after a 4-bolt swap.</figcaption></figure>
    <figure><img src="/assets/photos/motor-install.jpg" alt="Installed White Lightning Motors high-output motor on a customer's cart" loading="lazy"><figcaption>Bench-built. Customer-installed. Texas-shipped.</figcaption></figure>
  </div>
</section>

<section id="solenoids">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Don't forget</span>
      <h2>The $75 part that saves a $325 motor.</h2>
      <p>The factory solenoid is rated for stock current. The second you push more amps through it — high-output motor, lithium pack, performance controller — it becomes the weak link. Our heavy-duty 36V/48V solenoid is the cheapest insurance on a performance build.</p>
    </div>
    <div style="text-align:center">
      <a class="btn btn-bolt" href="tel:8328321993">📞 Add a solenoid to your build</a>
    </div>
    <div style="margin-top:48px;text-align:center">
      <img src="/assets/photos/product-lineup.jpg" alt="White Lightning Motors product lineup — high-output motor, heavy-duty solenoid, Bolt Energy lithium battery, Navitas controller" style="max-width:900px;width:100%;border-radius:14px;border:1px solid var(--rule)" loading="lazy" onerror="this.style.display='none'">
    </div>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">FAQ</span>
      <h2>Motor upgrade questions, answered.</h2>
    </div>
    {faq_html(MU_FAQ)}
  </div>
</section>
''' + CTA_BAND

MOTOR_SERVICE_SCHEMA = {
    "@context":"https://schema.org","@type":"Service",
    "name":"Golf Cart Motor Upgrade Service",
    "serviceType":"Performance motor upgrade",
    "description":"High-output bolt-in motor upgrade for EZGO, Club Car, Yamaha, ICON, and Evolution golf carts. Takes stock 14 mph carts to 25+ mph on a stock controller. Mail-in service nationwide.",
    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC","telephone":f"+1-{PHONE}","url":BASE+"/"},
    "areaServed":{"@type":"Country","name":"United States"},
    "audience":{"@type":"Audience","audienceType":"Golf cart owners, dealers, and performance enthusiasts"},
    "image":f"{BASE}/assets/photos/install-headon.jpg",
    "url":f"{BASE}/motor-upgrades/",
    "offers":{
        "@type":"Offer","price":"325","priceCurrency":"USD",
        "availability":"https://schema.org/InStock",
        "url":f"{BASE}/motor-upgrades/",
        "priceValidUntil":"2027-12-31",
    },
    "hasOfferCatalog":{
        "@type":"OfferCatalog","name":"Motor upgrades by cart brand",
        "itemListElement":[
            {"@type":"Offer","itemOffered":{"@type":"Service","name":"EZGO motor upgrade","url":f"{BASE}/motor-upgrades/ezgo/"}, "price":"325","priceCurrency":"USD"},
            {"@type":"Offer","itemOffered":{"@type":"Service","name":"Club Car motor upgrade","url":f"{BASE}/motor-upgrades/club-car/"}, "price":"325","priceCurrency":"USD"},
            {"@type":"Offer","itemOffered":{"@type":"Service","name":"Yamaha motor upgrade","url":f"{BASE}/motor-upgrades/yamaha/"}, "price":"325","priceCurrency":"USD"},
            {"@type":"Offer","itemOffered":{"@type":"Service","name":"ICON motor upgrade","url":f"{BASE}/motor-upgrades/icon/"}, "price":"325","priceCurrency":"USD"},
        ],
    },
    "aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"11"},
}
PAGES.append({
    "path":"/motor-upgrades/",
    "title":"Golf Cart Motor Upgrades — EZGO, Club Car, Yamaha | White Lightning Motors",
    "desc":"High-output bolt-in golf cart motor upgrades from $325. EZGO, Club Car, Yamaha, ICON. 14 mph stock to 25+ mph with stock controller. 1-year warranty. Mail-in service.",
    "crumbs":[("Home","/"),("Motor Upgrades","/motor-upgrades/")],
    "schema":[MOTOR_SERVICE_SCHEMA, faq_schema(MU_FAQ)],
    "body":MU_BODY,
})

# ---- Per-brand pages ----
def brand_page(slug, brand, models, top_speed, hero_intro, model_table):
    crumbs=[("Home","/"),("Motor Upgrades","/motor-upgrades/"),(f"{brand} Upgrades",f"/motor-upgrades/{slug}/")]
    qa = [
        (f"What's the top speed of a {brand} cart with the White Lightning motor?",
         f"Customers regularly hit {top_speed} on a {brand} with our high-output motor, stock controller, and healthy 48V batteries. Add a Navitas controller and lithium pack and 30+ mph is realistic."),
        (f"Which {brand} models do you support?",
         f"We build motors for: {', '.join(models)}. If your year or trim isn't listed, call Charlie at 832-832-1993 — five minutes on the phone and you'll know."),
        (f"Will this work with my {brand} stock controller?",
         "Yes. The motor is designed to drop in and run on the factory controller. You'll see a major top-speed and torque bump immediately. Pair it with a Navitas DC controller later when you want full programmability."),
        ("How fast can I get it back?",
         "4–7 business days for standard turnaround once your motor lands at the shop. Rush options available."),
    ]
    schema=[faq_schema(qa), {
        "@context":"https://schema.org","@type":"Product",
        "name":f"{brand} Golf Cart High-Output Motor Upgrade",
        "description":f"Bolt-in high-output motor upgrade for {brand} golf carts. Drops into stock controller, takes top speed to {top_speed} mph.",
        "brand":{"@type":"Brand","name":"White Lightning Motors"},
        "offers":{"@type":"Offer","priceCurrency":"USD","price":"325","availability":"https://schema.org/InStock","url":f"{BASE}/motor-upgrades/{slug}/"},
        "aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"11"},
    }]
    rows = "".join(f'<tr><td>{m}</td><td>{y}</td><td>{notes}</td></tr>' for m,y,notes in model_table)
    body = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / <a href="/motor-upgrades/">Motor Upgrades</a> / {brand}</div>
    <span class="eyebrow">{brand.upper()} performance motors</span>
    <h1>{brand} golf cart motor upgrade.</h1>
    <p class="lede">{hero_intro}</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 {PHONE}</a>
      <a class="btn btn-ghost" href="/contact/">Get a quote →</a>
    </div>
    <div class="hero-stats">
      <div><b>{top_speed}</b><span>typical top speed</span></div>
      <div><b>$325</b><span>starting price</span></div>
      <div><b>1-yr</b><span>warranty</span></div>
      <div><b>4–7d</b><span>turnaround</span></div>
    </div>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <h2>Supported {brand} models</h2>
    <p>Every motor is built to the exact mounting plate and shaft spec for your model. If the table below doesn't include your year, call us — most of the time we can still build for it.</p>
    <div style="overflow-x:auto;background:#fff;border:1px solid #e7eaf0;border-radius:12px;margin:24px 0">
      <table style="width:100%;border-collapse:collapse;font-size:15px">
        <thead style="background:#0c1018;color:#fff"><tr><th style="text-align:left;padding:14px 18px">Model</th><th style="text-align:left;padding:14px 18px">Years</th><th style="text-align:left;padding:14px 18px">Notes</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <h2>What you get</h2>
    <ul>
      <li>High-output series-wound motor, bench-built and dynoed</li>
      <li>White Lightning sticker (mandatory 🙃)</li>
      <li>1-year warranty from day of arrival</li>
      <li>Free return shipping inside the continental US</li>
      <li>Phone support from Charlie if you hit anything during install</li>
    </ul>
    <h2>How the install goes</h2>
    <p>Two bolts on the mounting plate, two lugs on the motor terminals. Most {brand} owners pull and replace it themselves in under 30 minutes. We send detailed shipping instructions when you book.</p>
    <p><a href="/how-it-works/">See the full mail-in process →</a></p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">FAQ</span>
      <h2>{brand} motor upgrade questions.</h2>
    </div>
    {faq_html(qa)}
  </div>
</section>
''' + CTA_BAND
    return {
        "path":f"/motor-upgrades/{slug}/",
        "title":f"{brand} Golf Cart Motor Upgrade — From $325 | White Lightning Motors",
        "desc":f"High-output bolt-in motor upgrade for {brand} golf carts. Hit {top_speed} on stock controller. Models supported: {', '.join(models[:3])} and more. 1-year warranty.",
        "crumbs":crumbs,
        "schema":schema,
        "body":body,
    }

PAGES.append(brand_page(
    "ezgo","EZGO",
    ["TXT","RXV","Marathon","Medalist","Express"],
    "25–28 mph",
    "EZGO TXT, RXV, Marathon, and Medalist carts are our most-built platform. The factory series-wound motor is plenty reliable — it's just geared and wound for sleepy 14 mph operation. Our drop-in replacement uses a higher-flux winding and better brush geometry to get you 25–28 mph on the same controller and batteries.",
    [("TXT 36V","1994.5–2009","Most common build — drops straight in"),
     ("TXT 48V","2009.5–present","48V series-wound, our highest-volume motor"),
     ("RXV 48V","2008–present","AC system — pair with Navitas or factory controller"),
     ("Medalist","1994.5–2001","Same physical motor as early TXT"),
     ("Marathon","1989–1994","Older 36V — call to confirm spec")],
))

PAGES.append(brand_page(
    "club-car","Club Car",
    ["DS","Precedent","Onward","Tempo","XRT"],
    "25–27 mph",
    "Club Car DS and Precedent carts are the second-most-common build on our bench. The IQ system from 2000+ is happy to run a higher-output motor. Excel and PowerDrive Plus carts pick up the same gains. Onward and Tempo platforms share the Precedent driveline.",
    [("DS 36V","1981–1996","Older 36V — PowerDrive or PowerDrive Plus"),
     ("DS 48V","1996–2014","IQ system — high-volume build"),
     ("Precedent IQ","2004–present","Most popular — pairs perfectly with Navitas"),
     ("Onward / Tempo","2017–present","Same driveline as Precedent"),
     ("XRT utility","various","Call to confirm — usually compatible")],
))

PAGES.append(brand_page(
    "yamaha","Yamaha",
    ["G19","G22","G29 Drive","Drive 2","YDRE"],
    "23–26 mph",
    "Yamaha electric carts use a slightly different mounting plate and shaft spec than the EZGO / Club Car world, but the upgrade philosophy is the same. The G19 and G22 cars love the swap. Newer Drive and Drive 2 AC systems can be upgraded too — usually paired with a Navitas controller for full effect.",
    [("G19","1995–2002","Original Drive-style platform"),
     ("G22","2003–2006","Series motor, classic upgrade candidate"),
     ("G29 Drive","2007–2016","DC and AC versions — call to confirm"),
     ("Drive 2 (AC)","2017–present","Best paired with Navitas controller"),
     ("YDRE","various","Yamaha electric — call to confirm motor spec")],
))

PAGES.append(brand_page(
    "icon","ICON",
    ["i20","i40","i60","i40L","i60L"],
    "25–28 mph",
    "ICON's i-series carts have grown into the value pick of the LSV world. We build drop-in replacement motors for the i20, i40, and i60 lineup that take stock 19 mph street-legal carts up to 25–28 mph for off-road / private property use.",
    [("i20","all years","2-passenger — common upgrade"),
     ("i40","all years","4-passenger — highest volume"),
     ("i60","all years","6-passenger — pair with HD solenoid"),
     ("i40L / i60L","limo models","Call to confirm motor spec")],
))

# ============================================================
# LITHIUM BATTERIES
# ============================================================
LITHIUM_FAQ = [
    ("How much weight does a lithium swap save?",
     "About 200–250 lbs out of an EZGO TXT or Club Car DS. You're replacing six 60-lb lead-acid batteries (~360 lbs) with one ~120-lb lithium pack. The weight loss alone improves acceleration, range, and ride."),
    ("How much more range does lithium give me?",
     "Lithium delivers usable capacity all the way down — lead-acid sags hard below 50%. Real-world range usually doubles, and you can fully discharge a lithium pack without damaging it."),
    ("Does lithium work with my existing controller?",
     "On most 48V EZGO, Club Car, and Yamaha carts, yes. The Bolt Energy packs we install include a BMS that talks to the cart's charger and meter. Some early-2000s carts need a meter adapter — we'll tell you up front."),
    ("How long does a lithium pack last?",
     "8–10 years of normal recreational use. Lithium batteries are rated for 3,000+ charge cycles vs ~500 for flooded lead-acid. You'll likely sell the cart before you replace the pack."),
    ("Can I keep my lead-acid charger?",
     "Sometimes, but we recommend pairing lithium with a lithium-specific charger to maximize pack life. Quote includes the right charger if you need one."),
]

LITHIUM_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Lithium Batteries</div>
    <span class="eyebrow">Bolt Energy lithium</span>
    <h1>Drop 250 lbs. <span class="bolt">Double your range.</span></h1>
    <p class="lede">Lithium battery conversions for EZGO, Club Car, Yamaha, ICON, and Evolution carts. Bluetooth BMS, 8+ year lifespan, no more watering cells, no more voltage sag halfway through the day. Sized for your cart and your real-world use.</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 Quote my lithium swap</a>
      <a class="btn btn-ghost" href="/blog/lithium-vs-lead-acid-golf-cart/">Lithium vs lead-acid →</a>
    </div>
    <div class="hero-stats">
      <div><b>250 lb</b><span>weight saved</span></div>
      <div><b>2×</b><span>usable range</span></div>
      <div><b>8+ yr</b><span>pack lifespan</span></div>
      <div><b>3,000+</b><span>charge cycles</span></div>
    </div>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <h2>Why lithium changes everything</h2>
    <p>Lead-acid batteries are heavy, slow to charge, lose capacity in cold weather, and start dying the day you buy them. Lithium iron phosphate (LiFePO4) packs don't have any of those problems. The day we install a lithium pack is usually the day the customer texts back asking why they didn't do this five years ago.</p>
    <div class="key-takeaway"><b>The short version</b>Lithium = lighter cart, more range, faster recharge, longer life, zero maintenance. Higher upfront cost is offset by the pack outlasting two lead-acid replacements.</div>
    <h2>What's in a Bolt Energy lithium kit</h2>
    <p>Not just a battery — every kit ships with every component you need to swap from lead-acid to lithium in an afternoon. Authorized Bolt Energy dealer pricing.</p>
  </div>

  <div class="container" style="margin-top:32px">
    <div class="product-photos" style="grid-template-columns:repeat(4,1fr)">
      <div style="background:#fff;border-radius:14px;padding:14px;text-align:center;border:1px solid #e7eaf0">
        <img src="/assets/photos/product-lithium-clean.jpg" alt="Bolt Energy 48V 105Ah LiFePO4 lithium battery" style="width:100%;height:160px;object-fit:contain" loading="lazy">
        <b style="display:block;margin-top:8px;color:#0c1018">LiFePO4 Battery</b>
        <span style="color:#566070;font-size:13px">48V · 60/105/160Ah</span>
      </div>
      <div style="background:#fff;border-radius:14px;padding:14px;text-align:center;border:1px solid #e7eaf0">
        <img src="/assets/photos/product-solenoid-clean.jpg" alt="Heavy-duty contactor" style="width:100%;height:160px;object-fit:contain" loading="lazy">
        <b style="display:block;margin-top:8px;color:#0c1018">HD Contactor</b>
        <span style="color:#566070;font-size:13px">High-current rated</span>
      </div>
      <div style="background:#fff;border-radius:14px;padding:14px;text-align:center;border:1px solid #e7eaf0">
        <img src="/assets/photos/product-bms.jpg" alt="Bolt Energy Bluetooth BMS unit" style="width:100%;height:160px;object-fit:contain" loading="lazy">
        <b style="display:block;margin-top:8px;color:#0c1018">Bluetooth BMS</b>
        <span style="color:#566070;font-size:13px">App monitoring</span>
      </div>
      <div style="background:#fff;border-radius:14px;padding:14px;text-align:center;border:1px solid #e7eaf0">
        <img src="/assets/photos/product-charger.jpg" alt="Bolt Energy 48V lithium charger" style="width:100%;height:160px;object-fit:contain" loading="lazy">
        <b style="display:block;margin-top:8px;color:#0c1018">48V Charger</b>
        <span style="color:#566070;font-size:13px">Lithium-specific</span>
      </div>
    </div>
  </div>

  <div class="container prose" style="margin-top:42px">
    <h2>Pair it with a motor upgrade</h2>
    <p>Lithium and a <a href="/motor-upgrades/">high-output motor</a> are made for each other. The pack delivers usable voltage all the way down, so the motor pulls hard from full to empty instead of getting weaker as the batteries sag. Add a <a href="/controllers/">Navitas controller</a> and you have a 30+ mph build that runs all day.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">FAQ</span>
      <h2>Lithium golf cart questions.</h2>
    </div>
    {faq_html(LITHIUM_FAQ)}
  </div>
</section>
''' + CTA_BAND

LITHIUM_SERVICE_SCHEMA = {
    "@context":"https://schema.org","@type":"Service",
    "name":"Bolt Energy Lithium Battery Conversion",
    "serviceType":"Lithium battery conversion and install",
    "description":"Authorized Bolt Energy dealer install of 48V and 72V LiFePO4 lithium battery packs for golf carts. Includes battery, Bluetooth BMS, heavy-duty contactor, lithium-specific charger, and cart-specific brackets. Saves 250+ lbs vs lead-acid and doubles usable range.",
    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC","telephone":f"+1-{PHONE}","url":BASE+"/"},
    "areaServed":{"@type":"Country","name":"United States"},
    "audience":{"@type":"Audience","audienceType":"Golf cart owners and dealers upgrading from lead-acid"},
    "image":f"{BASE}/assets/photos/bolt-txt-kit.jpg",
    "url":f"{BASE}/lithium-batteries/",
    "brand":{"@type":"Brand","name":"Bolt Energy USA"},
    "offers":{"@type":"Offer","availability":"https://schema.org/InStock","url":f"{BASE}/lithium-batteries/","priceSpecification":{"@type":"PriceSpecification","priceCurrency":"USD","description":"Quote on request — varies by cart and pack capacity"}},
    "aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"11"},
}
PAGES.append({
    "path":"/lithium-batteries/",
    "title":"Lithium Golf Cart Battery Conversions | White Lightning Motors",
    "desc":"Lithium battery upgrades for EZGO, Club Car, Yamaha, ICON. 48V/72V Bolt Energy LiFePO4 packs with Bluetooth BMS. 250 lb weight savings, 2× range, 8+ year lifespan.",
    "crumbs":[("Home","/"),("Lithium Batteries","/lithium-batteries/")],
    "schema":[LITHIUM_SERVICE_SCHEMA, faq_schema(LITHIUM_FAQ)],
    "body":LITHIUM_BODY,
})

# ============================================================
# CONTROLLERS
# ============================================================
CTRL_FAQ = [
    ("What does a Navitas controller actually do?",
     "It replaces the factory DC controller and unlocks programmable speed, acceleration, regen, and current limits. Pair it with our motor upgrade and you go from a fast cart to a tunable cart — adjust top speed, snap, and battery save mode from your phone."),
    ("400A vs 600A — which one do I need?",
     "400A is the right call for most recreational and neighborhood-cruise builds. 600A is for serious performance builds with lithium packs, AC kits, or off-road duty where you want maximum current available at all times."),
    ("Can I install a Navitas controller myself?",
     "Most customers do. The wiring is well-documented and the Bluetooth tuning app makes initial setup straightforward. If you'd rather we install it on your motor before we ship, just ask — we'll wire it up."),
    ("Will the Navitas work with my factory throttle and accelerator?",
     "Yes. Navitas DC controllers are designed to drop in and use your factory ITS (Inductive Throttle Sensor) or hall-effect throttle without modification."),
]

CTRL_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Navitas Controllers</div>
    <span class="eyebrow">Programmable performance</span>
    <h1>Navitas controllers — <span class="bolt">tune it from your phone.</span></h1>
    <p class="lede">Programmable DC controllers that turn a fast cart into a customizable performance machine. Adjust speed, acceleration, regen braking, and current limits over Bluetooth. Pair with our motor upgrade for the strongest budget performance combo on the market.</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 Quote a Navitas build</a>
      <a class="btn btn-ghost" href="/motor-upgrades/">+ Add a motor upgrade →</a>
    </div>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <h2>Why Navitas, why now</h2>
    <p>Stock golf cart controllers are tuned for safety and battery life — which is code for "slow." A Navitas DC programmable controller hands the dial back to you. Want a snappy 27 mph daily-driver? Done. Want a 20 mph speed limit when the grandkids are driving? Toggle in the app. Want maximum regen so you barely use the brakes? Two taps.</p>
    <h2>What we sell</h2>
    <ul>
      <li><b>Navitas DC TSX 400A</b> — the daily-driver pick, perfect with our motor upgrade and stock batteries</li>
      <li><b>Navitas DC TSX 600A</b> — for serious performance and lithium-powered builds</li>
      <li><b>Bluetooth tuning module</b> — included with both, talks to the Navitas app on iOS and Android</li>
      <li><b>Compatible carts</b> — EZGO TXT/RXV, Club Car DS/Precedent, Yamaha G-series, ICON, Evolution</li>
    </ul>
    <h2>Best paired with</h2>
    <p><a href="/motor-upgrades/">Our high-output motor upgrade</a> — the controller and motor are designed to work together. <a href="/lithium-batteries/">A lithium pack</a> — full voltage all the way down means the controller can actually use the headroom you paid for.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">FAQ</span>
      <h2>Navitas controller questions.</h2>
    </div>
    {faq_html(CTRL_FAQ)}
  </div>
</section>
''' + CTA_BAND

CTRL_SERVICE_SCHEMA = {
    "@context":"https://schema.org","@type":"Service",
    "name":"Navitas DC TSX Programmable Controller Install",
    "serviceType":"Programmable golf cart controller install and tuning",
    "description":"Navitas DC TSX 400A and 600A programmable controller installs with Bluetooth tuning over the Navitas iOS/Android app. Adjustable top speed, acceleration profile, regen aggressiveness, and current limits. Compatible with EZGO TXT/RXV, Club Car DS/Precedent, Yamaha G-series, ICON, and Evolution.",
    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC","telephone":f"+1-{PHONE}","url":BASE+"/"},
    "areaServed":{"@type":"Country","name":"United States"},
    "audience":{"@type":"Audience","audienceType":"Golf cart performance enthusiasts and dealers"},
    "image":f"{BASE}/assets/photos/product-controller.jpg",
    "url":f"{BASE}/controllers/",
    "brand":{"@type":"Brand","name":"Navitas Vehicle Systems"},
    "offers":{"@type":"Offer","availability":"https://schema.org/InStock","url":f"{BASE}/controllers/","priceSpecification":{"@type":"PriceSpecification","priceCurrency":"USD","description":"Quote on request — varies by controller model and install scope"}},
    "aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"11"},
}
PAGES.append({
    "path":"/controllers/",
    "title":"Navitas Golf Cart Controllers — DC TSX 400A & 600A | White Lightning Motors",
    "desc":"Navitas DC TSX programmable controllers for EZGO, Club Car, Yamaha. Bluetooth tuning, adjustable speed/regen/current limits. 400A and 600A models. Paired with motor upgrades.",
    "crumbs":[("Home","/"),("Controllers","/controllers/")],
    "schema":[CTRL_SERVICE_SCHEMA, faq_schema(CTRL_FAQ)],
    "body":CTRL_BODY,
})

# ============================================================
# AC CONVERSION
# ============================================================
AC_FAQ = [
    ("What's the difference between DC and AC golf cart motors?",
     "DC motors use brushes and a commutator — simpler, cheaper, easier to upgrade. AC motors are brushless, more efficient, and support regenerative braking. AC kits are the endgame: quieter operation, recovered energy on deceleration, and the highest top-end potential."),
    ("Is an AC conversion worth it?",
     "If you want 30+ mph, regen braking, and the quietest cart on the block, yes. For most customers a high-output DC motor + Navitas controller + lithium pack hits 90% of the AC kit's performance at half the price. We'll tell you straight up which path makes sense for your goals."),
    ("Which carts are good AC conversion candidates?",
     "EZGO TXT and RXV, Club Car DS and Precedent, Yamaha G-series. Newer AC-equipped carts (Drive 2, RXV) can be upgraded with higher-output AC components instead of a full conversion."),
    ("What's included in a full AC conversion kit?",
     "AC motor, AC controller, wiring harness, throttle adapter, and contactor. We can pre-wire the kit before shipping so you're closer to plug-and-play."),
]

AC_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / AC Conversion Kits</div>
    <span class="eyebrow">The endgame build</span>
    <h1>Full AC conversion kits.</h1>
    <p class="lede">Brushless AC motor, programmable AC controller, regenerative braking. Built for customers who want the quietest, most efficient, highest-performance golf cart possible. Not the cheap path — the right path if you know you want it.</p>
    <div class="hero-ctas">
      <a class="btn btn-bolt" href="tel:8328321993">📞 Talk through an AC build</a>
      <a class="btn btn-ghost" href="/motor-upgrades/">Or start with DC →</a>
    </div>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <h2>What an AC conversion gives you</h2>
    <ul>
      <li><b>Regen braking</b> — energy recovered every time you let off. Brake pads last 5× longer.</li>
      <li><b>Whisper quiet</b> — no brush hiss, no commutator click. Cart hum only.</li>
      <li><b>Higher top end</b> — 30+ mph on the right battery setup</li>
      <li><b>Lighter motor</b> — modern AC motors are physically smaller than the brushed DC they replace</li>
      <li><b>Programmable</b> — same Bluetooth tuning workflow as our Navitas DC controllers</li>
    </ul>
    <h2>Be honest about what you need</h2>
    <p>An AC conversion is a $1,500+ investment when you add it all up. For 80% of customers, our <a href="/motor-upgrades/">high-output DC motor</a> + <a href="/controllers/">Navitas controller</a> + <a href="/lithium-batteries/">lithium pack</a> gets you 90% of the AC experience for half the money. Call Charlie — he'll talk you through both paths and tell you which one fits your actual use case.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">FAQ</span>
      <h2>AC conversion questions.</h2>
    </div>
    {faq_html(AC_FAQ)}
  </div>
</section>
''' + CTA_BAND

AC_SERVICE_SCHEMA = {
    "@context":"https://schema.org","@type":"Service",
    "name":"Full AC Conversion Kit Install",
    "serviceType":"Brushless AC motor and controller conversion",
    "description":"Complete brushless AC motor and AC controller conversion for EZGO, Club Car, and Yamaha golf carts. Includes AC motor, AC controller, wiring harness, throttle adapter, and contactor. Adds regenerative braking, near-silent operation, and 30+ mph top-end capability.",
    "provider":{"@type":"AutomotiveBusiness","name":"White Lightning Motors, LLC","telephone":f"+1-{PHONE}","url":BASE+"/"},
    "areaServed":{"@type":"Country","name":"United States"},
    "audience":{"@type":"Audience","audienceType":"Serious golf cart performance builders"},
    "image":f"{BASE}/assets/photos/motor-install.jpg",
    "url":f"{BASE}/ac-conversion/",
    "offers":{"@type":"Offer","availability":"https://schema.org/InStock","url":f"{BASE}/ac-conversion/","priceSpecification":{"@type":"PriceSpecification","priceCurrency":"USD","description":"Quote on request — typically $1,500+ depending on cart and components"}},
    "aggregateRating":{"@type":"AggregateRating","ratingValue":"5.0","reviewCount":"11"},
}
PAGES.append({
    "path":"/ac-conversion/",
    "title":"Golf Cart AC Conversion Kits | White Lightning Motors",
    "desc":"Full AC motor + controller conversion kits for EZGO, Club Car, Yamaha. Regenerative braking, near-silent operation, 30+ mph capable. Compare AC vs high-output DC with Charlie.",
    "crumbs":[("Home","/"),("AC Conversion","/ac-conversion/")],
    "schema":[AC_SERVICE_SCHEMA, faq_schema(AC_FAQ)],
    "body":AC_BODY,
})

# ============================================================
# HOW IT WORKS
# ============================================================
HOW_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / How It Works</div>
    <span class="eyebrow">Mail-in service</span>
    <h1>How the mail-in upgrade works.</h1>
    <p class="lede">You're not within driving distance of our Texas shop — and that's fine. 90% of our customers ship us a motor, we build it, we ship it back. Here's every step, with no surprises.</p>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="steps">
      <div class="step"><div class="n">1</div><h3>Call or text Charlie</h3><p>Tell him your cart make, model, year, and what you're trying to do. He'll tell you exactly which motor you need and quote it on the phone. 832-832-1993.</p></div>
      <div class="step"><div class="n">2</div><h3>Pay & get shipping label</h3><p>We invoice you. Once paid, we send detailed instructions for pulling the motor + a return shipping label. Two bolts and the wiring lugs — most customers do it themselves in 20 minutes.</p></div>
      <div class="step"><div class="n">3</div><h3>Ship your motor to Texas</h3><p>Drop it at any UPS or FedEx counter. We track it from there. Average transit is 2–4 business days from anywhere in the lower 48.</p></div>
      <div class="step"><div class="n">4</div><h3>We build & bench-test</h3><p>Your motor is rewound, rebuilt with our high-output components, and dyno-tested before it leaves the shop. Standard turnaround is 4–7 business days from arrival.</p></div>
      <div class="step"><div class="n">5</div><h3>We ship it back free</h3><p>Free return shipping inside the continental US. We send tracking. Most customers get their motor back in under two weeks total.</p></div>
      <div class="step"><div class="n">6</div><h3>Bolt in. Smile. Send video.</h3><p>Reverse of the removal. Reconnect the two motor lugs. Pull the throttle. Send Charlie a video — we love seeing the builds. 1-year warranty starts the day it arrives.</p></div>
    </div>
  </div>
</section>

<section class="container" style="padding-top:0">
  <div class="warranty">
    <div class="item">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L4 5v6c0 5 3.5 9.5 8 11 4.5-1.5 8-6 8-11V5l-8-3z"/></svg>
      <div><h4>1-year warranty</h4><p>If something fails inside the first year, we make it right. Period.</p></div>
    </div>
    <div class="item">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="13" rx="2"/><path d="M16 7V4H8v3M6 12h12"/></svg>
      <div><h4>Free return shipping</h4><p>You pay to ship in. We pay to ship back. No surprises at checkout.</p></div>
    </div>
    <div class="item">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>
      <div><h4>4–7 day turnaround</h4><p>Most standard upgrades ship back inside a week. Rush options available.</p></div>
    </div>
  </div>
</section>
''' + CTA_BAND

HOWTO_SCHEMA = {
    "@context":"https://schema.org","@type":"HowTo",
    "name":"How to upgrade a golf cart motor with White Lightning Motors mail-in service",
    "description":"The complete 6-step mail-in process — from quote to install — for upgrading a golf cart motor with White Lightning Motors. Average total turnaround is under 2 weeks.",
    "image":f"{BASE}/assets/photos/install-headon.jpg",
    "estimatedCost":{"@type":"MonetaryAmount","currency":"USD","value":"325"},
    "totalTime":"P14D",
    "supply":[
        {"@type":"HowToSupply","name":"Existing golf cart motor (to ship in)"},
        {"@type":"HowToSupply","name":"Shipping box and packing material"},
    ],
    "tool":[
        {"@type":"HowToTool","name":"Socket wrench"},
        {"@type":"HowToTool","name":"Cart-specific motor mount bolts (factory)"},
    ],
    "step":[
        {"@type":"HowToStep","position":1,"name":"Call or text Charlie","text":"Call 832-832-1993 with your cart make, model, year, and goal. Charlie quotes you on the phone and tells you exactly which motor specs you need.","url":f"{BASE}/how-it-works/#step-1"},
        {"@type":"HowToStep","position":2,"name":"Pay and receive shipping instructions","text":"Pay the invoice. We send shipping instructions plus a return shipping label. Most customers pull the motor themselves in 20 minutes with two bolts and the wiring lugs.","url":f"{BASE}/how-it-works/#step-2"},
        {"@type":"HowToStep","position":3,"name":"Ship your motor to Texas","text":"Drop the boxed motor at any UPS or FedEx counter. Average transit is 2-4 business days from anywhere in the continental United States.","url":f"{BASE}/how-it-works/#step-3"},
        {"@type":"HowToStep","position":4,"name":"We rebuild and bench-test","text":"Your motor is rewound with high-output components, bench-built, and dyno-tested before it leaves the shop. Standard turnaround is 4-7 business days from arrival.","url":f"{BASE}/how-it-works/#step-4"},
        {"@type":"HowToStep","position":5,"name":"We ship it back free","text":"Free return shipping inside the continental United States. We send tracking. Most customers get their motor back in under two weeks total.","url":f"{BASE}/how-it-works/#step-5"},
        {"@type":"HowToStep","position":6,"name":"Bolt it back in","text":"Reverse of the removal. Reconnect the two motor lugs. Pull the throttle. The 1-year warranty starts the day the motor arrives at your door.","url":f"{BASE}/how-it-works/#step-6"},
    ],
}
PAGES.append({
    "path":"/how-it-works/",
    "title":"How Our Mail-In Golf Cart Motor Service Works | White Lightning Motors",
    "desc":"Step-by-step: how to ship your golf cart motor to our Texas shop, what we do to it, and how fast it comes back. Free return shipping, 4–7 day turnaround, 1-year warranty.",
    "crumbs":[("Home","/"),("How It Works","/how-it-works/")],
    "schema":[HOWTO_SCHEMA],
    "body":HOW_BODY,
})

# ============================================================
# ABOUT
# ============================================================
ABOUT_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / About</div>
    <span class="eyebrow">About the shop</span>
    <h1>Charlie builds the motors.</h1>
    <p class="lede">White Lightning Motors is a small Texas shop run by Charlie Stout — performance golf cart builder, motor rebuilder, and the guy who picks up the phone. No call centers, no offshore support, no chatbot.</p>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <h2>The pitch</h2>
    <p>Most golf cart performance shops are either dealers who sell you a $25,000 finished cart or online stores that drop-ship a motor with zero support. We're neither. We build motors. We answer the phone. We talk you through the install. And we back every motor we ship with a 1-year warranty.</p>
    <h2>How we got here</h2>
    <p>Charlie started building performance carts as a side gig — friends and neighbors wanted faster carts, and the price gap between a stock cart and a dealer-built performance build was crazy. Word spread. Texas neighbors became Texas dealers. Texas dealers became out-of-state customers. The shop now ships motors to all 50 states, and the business is still run by the same one builder. Pricing reflects that — no middlemen, no overhead, no sales floor.</p>
    <h2>What we believe</h2>
    <ul>
      <li><b>Honest quotes.</b> If you don't need a $1,500 AC conversion, we'll tell you. Most customers are better served by a $325 motor + $75 solenoid.</li>
      <li><b>Phone-first support.</b> The contact form works, but call. You'll get answers faster and you'll get them from the guy who built your motor.</li>
      <li><b>Real warranties.</b> 1-year on every motor. If it fails, we fix it. No drama.</li>
      <li><b>Dealer-friendly.</b> If you run a cart shop, we have dealer pricing and bulk motor orders. Polk County Golf Carts and Tejas Golf Carts source from us.</li>
    </ul>
    <h2>Where we are</h2>
    <p>The shop is in the Houston, TX area. The truck (the wrapped F-150 you might've seen on Facebook) is at every local install. Mail-in customers, doesn't matter — your motor comes back free.</p>
  </div>
</section>

<section style="padding:0">
  <img src="/assets/photos/cart-glow.jpg" alt="Lifted custom golf cart with green underglow lights at night — built and tuned by White Lightning Motors" style="width:100%;display:block;max-height:560px;object-fit:cover" loading="lazy" onerror="this.style.display='none'">
</section>

<section>
  <div class="container">
    <div class="brands">
      <span>Dealer partners</span>
      <b>Polk County Golf Carts</b><b>Tejas Golf Carts</b>
    </div>
  </div>
</section>
''' + CTA_BAND

PAGES.append({
    "path":"/about/",
    "title":"About White Lightning Motors — Charlie Stout's Texas Performance Cart Shop",
    "desc":"White Lightning Motors is a small Texas shop run by Charlie Stout. We build high-output golf cart motors and ship them nationwide. 1-year warranty, free return shipping, phone-first support.",
    "crumbs":[("Home","/"),("About","/about/")],
    "body":ABOUT_BODY,
})

# ============================================================
# REVIEWS
# ============================================================
REVIEWS = [
    ("Travis Holm","Charlie got me set up with an awesome motor upgrade. Quick turn around time. Very very happy with the results. Cart went from 14.8 mph to over 27 mph (stock tired batteries). Do not hesitate to send your motor to White Lightning Motors! I'll be sending another to him soon.","Google · Local Guide"),
    ("Bobby Bentley","Best bang for the buck! Charlie is the best! Fast reliable best in the business!!! His motors are definitely on top of the market. Thanks for your normal way of going far and beyond! White lightning motors for the win!!!","Facebook recommendation"),
    ("Kobe Torres-Adams","The night and day difference with this upgrade is amazing. My family and I love it. Thank you.","Facebook recommendation"),
    ("Justin Whitaker","I have installed several of these motors and am very pleased with the service, turnaround time, and performance. Carts are getting 30mph without spending big dollars for an upgraded high output controller or ac system. I am a repeat customer and will continue to use White Lightning motors for builds in the future.","Tejas Golf Carts"),
    ("John Long","I'm the owner of Polk County Golf Carts. We have used White lightening services on rebuilding customers motors. Fast turn around, great service and quality. Customers were very pleased with the speed upgrade! Charlie is highly recommended.","Polk County Golf Carts"),
    ("Corey Haynes Garcia","Excellent customer service and speedy response time. Bringing a drive motor back to life!","Facebook recommendation"),
    ("Shawn Adams","Thanks for the hook up. Grandson is going crazy!!! We have the fastest cart in the neighborhood. Also thanks for sending me the link to all your accessories. The seat belt kit and flip seat are awesome.","Google review"),
    ("Mary Adams","Thanks for helping me out with my motor. Super fast. Much more fun to drive. I was nervous being a lady and thinking I would get taken advantage of but Charlie did me right. Thank you so much.","Google · Local Guide"),
    ("Corey Haynes","Great customer service and didn't think it was possible to swap out my cart motor! Capabilities to go even faster? Very satisfied with purchase!","Google review"),
    ("John Long","Fast service! Quality product! Speed your slow cart up today.","Google · Local Guide"),
    ("Travis Holm","Repeat customer. Sent in a second motor and it came back even faster than the first. Charlie knows what he's doing.","Google · Local Guide"),
]
review_cards = "\n".join(f'<div class="review"><div class="stars">★★★★★</div><p>"{body}"</p><div class="who"><b>{name}</b><span>{source}</span></div></div>' for name,body,source in REVIEWS)

REVIEWS_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Reviews</div>
    <span class="eyebrow">★★★★★ Every single one</span>
    <h1>11 reviews. 5.0 average. Zero complaints.</h1>
    <p class="lede">Pulled verbatim from Google, Facebook, and dealer testimonials. We didn't curate the highlights — these are every review we have.</p>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="reviews">{review_cards}</div>
  </div>
</section>
''' + CTA_BAND

PAGES.append({
    "path":"/reviews/",
    "title":"Reviews — 5.0 Average on Google + Facebook | White Lightning Motors",
    "desc":"Every customer review for White Lightning Motors from Google and Facebook — 11 reviews, 5.0 average, including dealer testimonials from Polk County Golf Carts and Tejas Golf Carts.",
    "crumbs":[("Home","/"),("Reviews","/reviews/")],
    "schema":review_schema(REVIEWS),
    "body":REVIEWS_BODY,
})

# ============================================================
# FAQ
# ============================================================
ALL_FAQ = MU_FAQ + LITHIUM_FAQ + CTRL_FAQ + AC_FAQ + [
    ("Do you offer dealer pricing?",
     "Yes. Polk County Golf Carts, Tejas Golf Carts, and other shops resell our work. Call to get on dealer pricing and bulk motor orders."),
    ("Can I order parts only, without sending in my motor?",
     "Yes. Solenoids, batteries, controllers, and AC components can all be sold standalone. The motor upgrade specifically needs your existing motor to rebuild — that's how we keep the price at $325."),
    ("What's the warranty if I install it myself?",
     "Same 1-year warranty. We trust you with two bolts and two lugs. If something fails inside the warranty window, ship it back and we make it right."),
]
FAQ_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / FAQ</div>
    <span class="eyebrow">Every question we get</span>
    <h1>Frequently asked questions.</h1>
    <p class="lede">The full list — motor upgrades, lithium, controllers, AC, warranty, dealer pricing. If your question isn't here, call Charlie at <a href="tel:8328321993">{PHONE}</a>.</p>
  </div>
</section>

<section class="light">
  <div class="container">
    {faq_html(ALL_FAQ)}
  </div>
</section>
''' + CTA_BAND

PAGES.append({
    "path":"/faq/",
    "title":"Golf Cart Motor Upgrade FAQ | White Lightning Motors",
    "desc":"Every common question about White Lightning Motors golf cart upgrades — top speeds, supported carts, lithium, Navitas controllers, AC conversions, warranty, dealer pricing.",
    "crumbs":[("Home","/"),("FAQ","/faq/")],
    "schema":[faq_schema(ALL_FAQ)],
    "body":FAQ_BODY,
})

# ============================================================
# CONTACT
# ============================================================
CONTACT_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Contact</div>
    <span class="eyebrow">Talk to Charlie</span>
    <h1>Get a real quote in 5 minutes.</h1>
    <p class="lede">Phone is fastest — you'll talk to the guy building the motors, not a salesperson. Email and form work too.</p>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="contact-grid">
      <div class="contact-box">
        <h3>Get in touch</h3>
        <p>Most customers are quoted on the first phone call. Have your cart make, model, and year ready.</p>
        <div class="row">
          <span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span>
          <div><b>832-832-1993</b><span>Charlie answers — call or text</span></div>
        </div>
        <div class="row">
          <span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/></svg></span>
          <div><b>{EMAIL}</b><span>Quotes, dealer inquiries, support</span></div>
        </div>
        <div class="row">
          <span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg></span>
          <div><b>Mail-in service nationwide</b><span>USA shipping. Free return on every build.</span></div>
        </div>
      </div>
      <div class="contact-box">
        <h3>Tell us about your cart</h3>
        <p>The more detail you give Charlie, the faster he can quote you.</p>
        <form class="cf" action="mailto:{EMAIL}" method="post" enctype="text/plain">
          <label for="name">Your name</label><input id="name" name="name" required>
          <label for="phone">Phone</label><input id="phone" name="phone" type="tel" required>
          <label for="cart">Cart make / model / year</label><input id="cart" name="cart" placeholder="e.g. EZGO TXT 48V 2018">
          <label for="goal">What are you trying to do?</label>
          <textarea id="goal" name="goal" placeholder="Top speed I want, batteries I'm running, any controller or AC plans…"></textarea>
          <button class="btn btn-bolt" type="submit">⚡ Send to Charlie</button>
        </form>
      </div>
    </div>
  </div>
</section>
'''

PAGES.append({
    "path":"/contact/",
    "title":"Contact — Talk to Charlie at White Lightning Motors | 832-832-1993",
    "desc":"Get a real quote in 5 minutes. Call or text Charlie at 832-832-1993, email sales@whitelightningmotors.com, or fill out the form. Mail-in service nationwide.",
    "crumbs":[("Home","/"),("Contact","/contact/")],
    "body":CONTACT_BODY,
})

# ============================================================
# BLOG INDEX + ARTICLES
# ============================================================
ARTICLES = [
    ("how-fast-will-my-golf-cart-go-after-a-motor-upgrade",
     "How fast will my golf cart go after a motor upgrade?",
     "Real-world top speeds after a White Lightning motor upgrade by cart brand, battery condition, and controller. Plus what it takes to get to 30+ mph.",
     "2026-06-19"),
    ("ezgo-vs-club-car-motor-upgrade",
     "EZGO vs Club Car: which motor upgrade is better?",
     "Side-by-side comparison of EZGO TXT and Club Car DS/Precedent motor upgrades — what's different, what's the same, which is faster, and which one to buy if you're shopping for a cart.",
     "2026-06-19"),
    ("lithium-vs-lead-acid-golf-cart",
     "Lithium vs lead-acid for golf carts: the honest comparison",
     "When lithium is worth the upfront cost, when lead-acid is fine, and how to think about range, weight, lifespan, and total cost across both options.",
     "2026-06-19"),
]

BLOG_INDEX_CARDS = "\n".join(f'''<a class="product" href="/blog/{slug}/" style="text-decoration:none;color:inherit;display:block">
  <span class="eyebrow" style="font-size:11px">{date}</span>
  <h3 style="margin-top:10px">{title}</h3>
  <p>{desc}</p>
  <span style="color:var(--bolt);font-weight:700">Read article →</span>
</a>''' for slug,title,desc,date in ARTICLES)

BLOG_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / Blog</div>
    <span class="eyebrow">Resources</span>
    <h1>Articles, comparisons, & how-tos.</h1>
    <p class="lede">Straight answers to the questions we get on the phone every day. No fluff, no SEO word-salad — just what we'd tell you if you called.</p>
  </div>
</section>

<section class="light">
  <div class="container">
    <div class="products">{BLOG_INDEX_CARDS}</div>
  </div>
</section>
'''

PAGES.append({
    "path":"/blog/",
    "title":"Golf Cart Performance Blog | White Lightning Motors",
    "desc":"Articles, comparisons, and how-tos for golf cart performance upgrades — top speed expectations, EZGO vs Club Car, lithium vs lead-acid, and more from Charlie at White Lightning Motors.",
    "crumbs":[("Home","/"),("Blog","/blog/")],
    "body":BLOG_BODY,
})

# Article: How fast will my golf cart go
ART1_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a> / How fast will my golf cart go</div>
    <span class="eyebrow">{ARTICLES[0][3]} · 6 min read</span>
    <h1>{ARTICLES[0][1]}</h1>
    <p class="lede">The short answer most customers want: 25–28 mph on a White Lightning motor swap alone, 30+ with a controller and lithium pack. The longer answer depends on your cart, your batteries, and your controller. Here's how to think about it.</p>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <div class="key-takeaway"><b>The TL;DR</b>A bolt-in White Lightning motor takes a stock 14–16 mph cart to 25–28 mph with no other changes. Add a Navitas controller, get to 27–29. Add lithium batteries on top, and 30+ is realistic. Beyond 30 mph requires a full AC conversion.</div>

    <h2>The stock baseline</h2>
    <p>Most factory 48V electric golf carts top out around 14–17 mph from the dealer. Some are software-limited to that speed for liability reasons; some are mechanically geared and motor-wound for it. Either way, the gap between "stock" and "actually fun" is enormous, and you can close most of it for under $400.</p>

    <h2>The motor swap alone — 25–28 mph</h2>
    <p>Our most common build is the motor swap by itself. The customer's stock controller stays. The stock batteries stay. We just rebuild the motor with higher-flux windings and better brush geometry. The result is more torque at every RPM and a higher unloaded top speed.</p>
    <ul>
      <li>EZGO TXT 48V: typically 26–28 mph</li>
      <li>Club Car Precedent IQ: typically 25–27 mph</li>
      <li>Yamaha G22/G29: typically 23–26 mph</li>
      <li>ICON i40: typically 25–28 mph</li>
    </ul>
    <p>One real-world data point: <a href="/reviews/">Travis Holm</a> took his cart from 14.8 to over 27 mph on stock, tired batteries. That's the floor of what's possible — not the ceiling.</p>

    <h2>Add a Navitas controller — 27–29 mph</h2>
    <p>A <a href="/controllers/">Navitas DC TSX controller</a> hands you the dials the factory locked. Top speed limit, current limit, acceleration profile, regen aggressiveness — all programmable over Bluetooth. The controller alone adds 2–3 mph to a motor-swap-only build because it stops capping the current you can push through the motor.</p>

    <h2>Add lithium — 28–32 mph</h2>
    <p><a href="/lithium-batteries/">Lithium packs</a> hold voltage all the way down. Lead-acid batteries sag — meaning a "48V" pack delivers maybe 46V at half-charge and 42V near empty. Lithium delivers 48V from full to empty, which means your motor and controller get the headroom they were designed for. The combination of fresh motor + Navitas + lithium consistently hits 30+ mph in real-world testing.</p>

    <h2>The 30+ mph ceiling</h2>
    <p>To break clean of 30 mph and stay there at speed under load, you're entering AC territory — the <a href="/ac-conversion/">full AC conversion kit</a> route. AC motors are brushless, more efficient, support regenerative braking, and have a higher top-end ceiling than even our highest-output DC motors. 90% of customers don't need it. The 10% who do, know who they are.</p>

    <blockquote>The fastest motor in the world won't help if your batteries are sagging or your controller is choking the current. Spec the whole system, not just the part.</blockquote>

    <h2>What about gas carts?</h2>
    <p>Gas-cart performance is a different sport — usually carb/intake/exhaust + governor work. We don't do gas. If you're thinking about a Yamaha G2 gas → electric conversion, we can help with the electric side.</p>

    <h2>The honest summary</h2>
    <ul>
      <li><b>Want fast and cheap?</b> Motor swap only. $325 + the cost of a heavy-duty solenoid. 25–28 mph.</li>
      <li><b>Want fast and tunable?</b> Motor + Navitas. ~$1,000. 27–29 mph + programmable everything.</li>
      <li><b>Want a daily-driver performance build?</b> Motor + Navitas + lithium. 30+ mph + 2× the range.</li>
      <li><b>Want the highest performance possible?</b> Full AC conversion. $1,500+. The endgame.</li>
    </ul>
    <p><a href="tel:8328321993">Call Charlie at {PHONE}</a> — five minutes on the phone and you'll know which path fits your cart and your goals.</p>
  </div>
</section>
''' + CTA_BAND

ART1_SCHEMA = [{
    "@context":"https://schema.org","@type":"Article",
    "headline":ARTICLES[0][1],
    "description":ARTICLES[0][2],
    "datePublished":ARTICLES[0][3],
    "author":{"@type":"Person","name":"Charlie Stout","url":f"{BASE}/about/"},
    "publisher":{"@type":"Organization","name":"White Lightning Motors","logo":{"@type":"ImageObject","url":f"{BASE}/assets/favicon.svg"}},
}]

PAGES.append({
    "path":f"/blog/{ARTICLES[0][0]}/",
    "title":f"{ARTICLES[0][1]} | White Lightning Motors",
    "desc":ARTICLES[0][2],
    "crumbs":[("Home","/"),("Blog","/blog/"),(ARTICLES[0][1],f"/blog/{ARTICLES[0][0]}/")],
    "schema":ART1_SCHEMA,
    "body":ART1_BODY,
})

# Article 2: EZGO vs Club Car
ART2_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a> / EZGO vs Club Car upgrade</div>
    <span class="eyebrow">{ARTICLES[1][3]} · 5 min read</span>
    <h1>{ARTICLES[1][1]}</h1>
    <p class="lede">We build motors for both EZGO and Club Car every week. They're more similar than the brand loyalty wars suggest — but there are a few real differences that matter when you're shopping or planning a performance build.</p>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <div class="key-takeaway"><b>The TL;DR</b>For pure performance upgrade ceiling: roughly a tie — EZGO TXT and Club Car Precedent both hit 27–28 mph with our motor swap. EZGO is slightly easier to work on. Club Car has the better factory suspension. Whichever one you already own is the right one to upgrade.</div>

    <h2>The platforms</h2>
    <p>EZGO TXT (and its successor the RXV) is the most common cart on golf courses in America. Club Car DS and Precedent are the second most common, with a stronger reputation in fleet and rental fleets thanks to the aluminum frame. Both platforms have been in production for 25+ years with massive aftermarket support.</p>

    <h2>What's the same</h2>
    <ul>
      <li><b>Motor philosophy</b> — both use series-wound DC motors as standard, both accept our high-output replacement</li>
      <li><b>Top speed potential</b> — 25–28 mph on motor swap alone, 30+ with the full performance stack</li>
      <li><b>Solenoid story</b> — both factory solenoids are the weak link on a performance build, both swap to our HD unit cleanly</li>
      <li><b>Pricing</b> — our motor upgrade is $325 for either platform</li>
    </ul>

    <h2>What's different</h2>
    <h3>Frame and suspension</h3>
    <p>EZGO uses a steel frame. Club Car uses aluminum. The Club Car aluminum frame is corrosion-resistant — a real win in coastal or wet climates. The EZGO steel frame is slightly stiffer, which some performance builders prefer.</p>
    <p>Club Car Precedent's factory suspension is generally regarded as more comfortable than EZGO TXT. RXV closes the gap.</p>
    <h3>Electrical system</h3>
    <p>EZGO TXT runs a series motor on a series controller — simple, reliable, easy to upgrade. EZGO RXV runs an AC system. Club Car DS is series. Club Car Precedent's IQ system is a sophisticated regen-capable DC drive. All four accept performance upgrades, but the install path is different.</p>
    <h3>Service & parts</h3>
    <p>EZGO TXT is a tinkerer's dream — everything is bolt-on, everything has a Hicks ID, every part is available aftermarket. Club Car's IQ system has more proprietary electronics, which means slightly more cost when something breaks but a more refined feel when everything's working.</p>

    <h2>Which one should you buy?</h2>
    <p>If you already own one, upgrade that one. The performance ceiling is similar enough that switching platforms isn't worth the cost.</p>
    <p>If you're shopping new or used:</p>
    <ul>
      <li>Buy <b>EZGO TXT</b> if you want the easiest, cheapest performance build path and don't mind doing your own wrenching.</li>
      <li>Buy <b>Club Car Precedent</b> if you want a slightly nicer ride out of the box, plan to use the cart on coastal or wet ground, and don't mind a small premium on parts.</li>
      <li>Buy <b>EZGO RXV</b> or <b>Club Car Onward</b> if you want a newer feature set (factory AC drive, better display, more comfort) and don't mind a higher entry price.</li>
    </ul>

    <h2>What we'd actually upgrade</h2>
    <p>For a $325 motor swap on either platform, you'll see 25–28 mph. Add an <a href="/controllers/">HD solenoid</a> and a <a href="/lithium-batteries/">lithium pack</a> and either platform becomes a 30 mph cart with 2× the range and 200+ pounds less weight.</p>

    <p><a href="tel:8328321993">Call Charlie</a> with your cart year and model — we'll quote it on the phone.</p>
  </div>
</section>
''' + CTA_BAND

ART2_SCHEMA = [{
    "@context":"https://schema.org","@type":"Article",
    "headline":ARTICLES[1][1],"description":ARTICLES[1][2],"datePublished":ARTICLES[1][3],
    "author":{"@type":"Person","name":"Charlie Stout","url":f"{BASE}/about/"},
    "publisher":{"@type":"Organization","name":"White Lightning Motors"},
}]

PAGES.append({
    "path":f"/blog/{ARTICLES[1][0]}/",
    "title":f"{ARTICLES[1][1]} | White Lightning Motors",
    "desc":ARTICLES[1][2],
    "crumbs":[("Home","/"),("Blog","/blog/"),(ARTICLES[1][1],f"/blog/{ARTICLES[1][0]}/")],
    "schema":ART2_SCHEMA,
    "body":ART2_BODY,
})

# Article 3: Lithium vs lead-acid
ART3_BODY = f'''
<section class="page-hero">
  <div class="container">
    <div class="crumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a> / Lithium vs lead-acid</div>
    <span class="eyebrow">{ARTICLES[2][3]} · 7 min read</span>
    <h1>{ARTICLES[2][1]}</h1>
    <p class="lede">Lithium is better than lead-acid on almost every dimension — except upfront cost. Whether that cost tradeoff makes sense for your cart depends on how often you use it, how heavy your build is, and how long you plan to own the cart.</p>
  </div>
</section>

<section class="light">
  <div class="container prose">
    <div class="key-takeaway"><b>The TL;DR</b>Lithium costs 2–3× more upfront, lasts 4–6× longer, weighs 60% less, holds voltage all the way down, and recharges twice as fast. If you use your cart more than once a week and plan to own it for more than 3 years, lithium is the right call. If you bought your cart for the occasional neighborhood cruise and don't mind the weight, lead-acid is still fine.</div>

    <h2>The dimensions that matter</h2>
    <h3>Lifespan</h3>
    <p>Flooded lead-acid: ~500 charge cycles before noticeable capacity loss. AGM: ~700 cycles. Lithium iron phosphate (LiFePO4): 3,000–5,000 cycles. In years of recreational use, that's roughly 3–5 years for lead-acid vs 8–10+ for lithium.</p>
    <h3>Weight</h3>
    <p>A 48V flooded pack (six 8V batteries) weighs about 360 lbs. The equivalent LiFePO4 pack weighs about 120 lbs. That 240 lbs comes off the back of your cart — better handling, more usable payload, and more range from less work for the motor.</p>
    <h3>Usable capacity</h3>
    <p>Lead-acid is rated at 50% depth of discharge — meaning if you discharge below 50% regularly, you destroy the pack. A "200Ah" lead-acid pack gives you 100Ah of real usable energy. Lithium can be discharged to ~90% without damage. That same 200Ah lithium pack gives you ~180Ah real usable energy.</p>
    <p>Net effect: lithium delivers roughly 2× the usable range from the same nameplate capacity.</p>
    <h3>Voltage curve</h3>
    <p>Lead-acid voltage sags as it discharges — your motor and controller see less power as the pack drains, which means the cart gets slower the longer you drive. Lithium holds nominal voltage from full to nearly empty. The motor pulls as hard at 20% state of charge as it does at 100%.</p>
    <p>This is the difference that's invisible on a spec sheet but huge in the driveway.</p>
    <h3>Charging speed</h3>
    <p>Lead-acid carts typically need 8–12 hours for a full charge. Lithium pulls full current straight through to ~95% state of charge — most customers get a full charge in 3–5 hours.</p>
    <h3>Maintenance</h3>
    <p>Flooded lead-acid needs distilled water topped off monthly. The terminals corrode. The cells can sulfate if you leave it discharged. Lithium needs zero maintenance — no water, no equalization charges, no terminal cleaning.</p>

    <h2>Upfront cost</h2>
    <p>A new set of decent 48V flooded lead-acid batteries runs about $700–$1,000 installed. A 48V lithium pack from us runs $2,500–$4,000 depending on capacity. So you're paying 3× the upfront cost — but for 6–10 years of use vs 3–4.</p>

    <h2>When lithium is the right call</h2>
    <ul>
      <li>You use the cart at least once a week</li>
      <li>You plan to own the cart for 4+ more years</li>
      <li>You've already done (or are planning) a <a href="/motor-upgrades/">motor upgrade</a> and want the performance to actually land</li>
      <li>You're sick of watering batteries and corroded terminals</li>
      <li>You live somewhere cold — lithium handles low temps far better than lead-acid</li>
    </ul>

    <h2>When lead-acid is still fine</h2>
    <ul>
      <li>You bought a $3,000 used cart and don't want to put another $3,000 into batteries</li>
      <li>You use the cart maybe once a month</li>
      <li>Your current pack is healthy and you don't have a specific reason to upgrade</li>
    </ul>

    <blockquote>The day after a customer texts that they did the lithium swap is usually the day they text again saying they should've done it five years ago.</blockquote>

    <h2>What we install</h2>
    <p>We install Bolt Energy LiFePO4 packs with Bluetooth BMS. You see pack health, cell-by-cell voltage, state of charge, and temperature from your phone. The pack ships with cart-specific brackets so it drops into the factory battery tray cleanly. Quote includes the lithium-specific charger if you need one. <a href="/lithium-batteries/">More on the lithium options →</a></p>

    <p><a href="tel:8328321993">Call Charlie at {PHONE}</a> with your cart and your use case — we'll tell you straight up whether lithium is worth it for you.</p>
  </div>
</section>
''' + CTA_BAND

ART3_SCHEMA = [{
    "@context":"https://schema.org","@type":"Article",
    "headline":ARTICLES[2][1],"description":ARTICLES[2][2],"datePublished":ARTICLES[2][3],
    "author":{"@type":"Person","name":"Charlie Stout","url":f"{BASE}/about/"},
    "publisher":{"@type":"Organization","name":"White Lightning Motors"},
}]

PAGES.append({
    "path":f"/blog/{ARTICLES[2][0]}/",
    "title":f"{ARTICLES[2][1]} | White Lightning Motors",
    "desc":ARTICLES[2][2],
    "crumbs":[("Home","/"),("Blog","/blog/"),(ARTICLES[2][1],f"/blog/{ARTICLES[2][0]}/")],
    "schema":ART3_SCHEMA,
    "body":ART3_BODY,
})

# ============================================================
# Build
# ============================================================

def write_favicon():
    SITE.joinpath("assets").mkdir(parents=True, exist_ok=True)
    SITE.joinpath("assets/favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="4" fill="#000"/><path d="M13 2L4 14h6l-2 8 9-12h-6l2-8z" fill="#00c2ff"/></svg>'
    )

def write_sitemap():
    urls = []
    for p in PAGES:
        urls.append(f'  <url><loc>{BASE}{p["path"]}</loc><changefreq>weekly</changefreq><priority>{"1.0" if p["path"]=="/" else "0.8"}</priority></url>')
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
    (SITE/"sitemap.xml").write_text(xml)
    print(f"  wrote site/sitemap.xml")

def write_robots():
    (SITE/"robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    print("  wrote site/robots.txt")

def write_llms_txt():
    lines = [
        "# White Lightning Motors",
        "",
        "> Performance golf cart motor upgrades and lithium battery conversions. Mail-in service nationwide from Texas. Built by Charlie Stout. 1-year warranty on every motor, free return shipping, 4–7 day turnaround.",
        "",
        "Phone: 832-832-1993",
        f"Email: {EMAIL}",
        "",
        "## Products",
    ]
    for p in PAGES:
        if any(p["path"].startswith(x) for x in ["/motor-upgrades/","/lithium-","/controllers/","/ac-"]):
            lines.append(f"- [{p['title'].split(' |')[0]}]({BASE}{p['path']}): {p['desc']}")
    lines.append("")
    lines.append("## Resources")
    for p in PAGES:
        if p["path"].startswith("/blog/"):
            lines.append(f"- [{p['title'].split(' |')[0]}]({BASE}{p['path']}): {p['desc']}")
    lines.append("")
    lines.append("## Company")
    for p in PAGES:
        if p["path"] in ("/about/","/how-it-works/","/reviews/","/faq/","/contact/"):
            lines.append(f"- [{p['title'].split(' |')[0]}]({BASE}{p['path']}): {p['desc']}")
    (SITE/"llms.txt").write_text("\n".join(lines)+"\n")
    print("  wrote site/llms.txt")

HERO_IMAGES = {
    "/motor-upgrades/": ("/assets/photos/install-headon.jpg","White Lightning Motors high-output motor installed in a customer cart — head-on under-cart view of the WLM-branded motor"),
    "/motor-upgrades/ezgo/": ("/assets/photos/hero-cart.jpg","EZGO performance golf cart upgrade — black 4-seater with lift kit and custom motor build"),
    "/motor-upgrades/club-car/": ("/assets/photos/cart-glow.jpg","Lifted custom golf cart with performance motor build by White Lightning Motors"),
    "/motor-upgrades/yamaha/": ("/assets/photos/motor-install.jpg","Installed Yamaha-compatible White Lightning high-output motor"),
    "/motor-upgrades/icon/": ("/assets/photos/hero-cart.jpg","Performance ICON golf cart with White Lightning motor upgrade"),
    "/lithium-batteries/": ("/assets/photos/bolt-txt-kit.jpg","Bolt Energy 48V 105Ah lithium kit — battery, contactor, BMS, charger, harnesses, display gauge"),
    "/controllers/": ("/assets/photos/product-controller.jpg","Navitas DC TSX programmable golf cart controller with throttle and contactor"),
    "/ac-conversion/": ("/assets/photos/motor-install.jpg","Performance AC motor installed on a customer golf cart"),
    "/how-it-works/": ("/assets/photos/truck-back.jpg","White Lightning Motors wrapped F-150 shop truck — rear view with phone number 832-832-1993"),
    "/about/": ("/assets/photos/truck-side.jpg","Charlie's White Lightning Motors wrapped Ford F-150 shop truck — driver-side view"),
    "/reviews/": ("/assets/photos/hero-cart.jpg","Customer-built lifted black HAVOC golf cart with White Lightning performance motor"),
    "/faq/": ("/assets/photos/motor-3d.png","White Lightning Motors high-output golf cart motor close-up"),
    "/contact/": ("/assets/photos/truck-side.jpg","White Lightning Motors shop truck — call Charlie at 832-832-1993"),
    "/blog/": ("/assets/photos/cart-glow.jpg","Custom lifted golf cart with underglow — built and tuned by White Lightning Motors"),
    "/blog/how-fast-will-my-golf-cart-go-after-a-motor-upgrade/": ("/assets/photos/hero-cart.jpg","Lifted black golf cart with HAVOC graphics and White Lightning performance motor build"),
    "/blog/ezgo-vs-club-car-motor-upgrade/": ("/assets/photos/product-lineup.jpg","EZGO and Club Car golf cart performance motor lineup — White Lightning Motors"),
    "/blog/lithium-vs-lead-acid-golf-cart/": ("/assets/photos/product-lineup.jpg","Bolt Energy lithium golf cart battery alongside White Lightning Motors performance components"),
}
for _p in PAGES:
    img = HERO_IMAGES.get(_p["path"])
    if img:
        _p["hero_image"], _p["hero_alt"] = img

def main():
    print(f"Building {len(PAGES)} pages to {SITE}/")
    # Clean only the generated subdirs (keep assets/ photos)
    for sub in SITE.iterdir():
        if sub.is_dir() and sub.name not in ("assets",):
            shutil.rmtree(sub)
    if (SITE/"index.html").exists():
        (SITE/"index.html").unlink()
    write_favicon()
    for page in PAGES:
        write(page)
    write_sitemap()
    write_robots()
    write_llms_txt()
    print(f"Done. {len(PAGES)} pages + sitemap + robots + llms.txt")

if __name__ == "__main__":
    main()
