#!/usr/bin/env python3
"""Assemble the static site: src/pages/*.html + shared layout -> ./*.html

Each page starts with a metadata block:
<!--
title: About Alpen Health
description: ...
nav: about
overlay: yes        (transparent header over a dark hero)
-->
Run: python3 build.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SITE = "https://www.alpen-health.com"

ARROW = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M1 8h13M9 3l5 5-5 5"/></svg>'

MARK = (
    '<path fill="currentColor" d="M618 55 1052 738 940 652 680 278 565 382 110 705Z"/>'
    '<path fill="#59C4D1" d="M672 342 925 695Q790 612 665 601L497 607Z"/>'
    '<path fill="#E54B4B" d="M500 475 405 638 245 657Z"/>'
)

LOGO = (
    '<svg viewBox="0 0 520 172" role="img" aria-label="Alpen Health">'
    '<g transform="translate(-22 -6) scale(.222)">' + MARK + '</g>'
    '<text x="196" y="132" font-family="Montserrat, Arial, sans-serif" font-weight="600" font-size="140" letter-spacing="-5" fill="currentColor">lpen</text>'
    '<text class="health" x="276" y="166" font-family="Montserrat, Arial, sans-serif" font-weight="500" font-size="27" letter-spacing="13.2" fill="#59C4D1">HEALTH</text>'
    '</svg>'
)

NAV = [
    ("about", "about.html", "About"),
    ("what-we-do", "what-we-do.html", "What We Do"),
    ("therapeutic-areas", "therapeutic-areas.html", "Therapeutic Areas"),
    ("markets", "markets.html", "Markets"),
    ("partnerships", "partnerships.html", "Partnerships"),
]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Alpen Health">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#082B4C">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v=1">
{schema}
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="Alpen Health, home">{logo}</a>
    <nav class="nav" aria-label="Main">
      {nav}
      <a class="btn" href="contact.html"{contact_current}>Contact</a>
    </nav>
    <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<div class="footer-band">
  <div class="wrap">
    <p>Science connects possibilities. <span>People make them real.</span></p>
    <p class="r">Alpen Health &nbsp;|&nbsp; North Africa and beyond</p>
  </div>
</div>
<footer class="site-footer">
  <div class="wrap">
    <div class="f-top">
      <div>
        <a class="logo" href="index.html" aria-label="Alpen Health, home">{logo}</a>
        <p class="f-tag">Science. Access. Growth.</p>
        <p>Strategic partner to pharmaceutical and healthcare companies building their business across North Africa.</p>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About Alpen Health</a></li>
          <li><a href="about.html#values">Our Values</a></li>
          <li><a href="about.html#ecosystem">KETATA Group</a></li>
          <li><a href="partnerships.html">Partnerships</a></li>
        </ul>
      </div>
      <div>
        <h4>Expertise</h4>
        <ul>
          <li><a href="what-we-do.html">What We Do</a></li>
          <li><a href="therapeutic-areas.html">Therapeutic Areas</a></li>
          <li><a href="markets.html">Markets</a></li>
          <li><a href="contact.html">Partnership Enquiry</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:info@alpen-health.com">info@alpen-health.com</a></li>
          <li><a href="tel:+21654574587">+216 54 574 587</a></li>
          <li><a href="tel:+41788893647">+41 78 889 36 47</a></li>
          <li>Centre Urbain Nord<br>Ariana, Tunisia</li>
        </ul>
      </div>
    </div>
    <div class="f-bottom">
      <span>&copy; 2026 Alpen Health. Part of KETATA Group.</span>
      <nav aria-label="Legal">
        <a href="privacy.html">Privacy Policy</a>
        <a href="legal.html">Legal Notice</a>
      </nav>
    </div>
  </div>
</footer>
<script src="assets/js/site.js?v=1" defer></script>
</body>
</html>
"""

SCHEMA = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"Alpen Health","url":"https://www.alpen-health.com/","logo":"https://www.alpen-health.com/apple-touch-icon.png","slogan":"Science. Access. Growth.","email":"info@alpen-health.com","telephone":"+216 54 574 587","address":{"@type":"PostalAddress","streetAddress":"Centre Urbain Nord","addressLocality":"Ariana","addressCountry":"TN"},"areaServed":["Tunisia","Algeria","Libya"],"parentOrganization":{"@type":"Organization","name":"KETATA Group"}}
</script>"""


def parse(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def build():
    for src in sorted((ROOT / "src" / "pages").glob("*.html")):
        meta, body = parse(src.read_text(encoding="utf-8"))
        current = meta.get("nav", "")
        cur = ' aria-current="page"'
        nav = "\n      ".join(
            f'<a href="{href}"{cur if key == current else ""}>{label}</a>'
            for key, href, label in NAV
        )
        name = src.name
        url = SITE + "/" + ("" if name == "index.html" else name)
        html = HEAD.format(
            title=meta["title"],
            description=meta["description"],
            url=url,
            site=SITE,
            schema=SCHEMA if name in ("index.html", "contact.html") else "",
            body_class="is-overlay" if meta.get("overlay") == "yes" else "",
            logo=LOGO,
            nav=nav,
            contact_current=' aria-current="page"' if current == "contact" else "",
        )
        html += body.replace("{{arrow}}", ARROW) + FOOT.format(logo=LOGO)
        (ROOT / name).write_text(html, encoding="utf-8")
        print("built", name)


if __name__ == "__main__":
    build()
