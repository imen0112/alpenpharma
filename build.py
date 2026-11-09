#!/usr/bin/env python3
"""Assemble the static site in two languages:
  src/pages/*.html    (English) -> ./*.html
  src/pages-fr/*.html (French)  -> ./fr/*.html

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

from PIL import Image

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

NAV = {
    "en": [
        ("about", "about.html", "About"),
        ("what-we-do", "what-we-do.html", "What We Do"),
        ("therapeutic-areas", "therapeutic-areas.html", "Therapeutic Areas"),
        ("markets", "markets.html", "Markets"),
        ("partnerships", "partnerships.html", "Partnerships"),
    ],
    "fr": [
        ("about", "about.html", "À propos"),
        ("what-we-do", "what-we-do.html", "Nos savoir-faire"),
        ("therapeutic-areas", "therapeutic-areas.html", "Domaines thérapeutiques"),
        ("markets", "markets.html", "Marchés"),
        ("partnerships", "partnerships.html", "Partenariats"),
    ],
}

T = {
    "en": {
        "locale": "en_US", "skip": "Skip to content", "home_label": "Alpen Health, home", "nav_label": "Main",
        "contact": "Contact", "menu": "Menu", "lang_label": "Language",
        "band": "Science connects possibilities. <span>People make them real.</span>",
        "band_r": "Alpen Health &nbsp;|&nbsp; North Africa and beyond",
        "tag": "Science. Access. Growth.",
        "intro": "Strategic partner to pharmaceutical and healthcare companies building their business across North Africa.",
        "company": "Company", "about": "About Alpen Health", "values": "Our Values", "group": "KETATA Group",
        "partnerships": "Partnerships", "expertise": "Expertise", "what": "What We Do", "areas": "Therapeutic Areas",
        "markets": "Markets", "enquiry": "Partnership Enquiry", "address": "Centre Urbain Nord<br>Ariana, Tunisia",
        "copy": "&copy; 2026 Alpen Health. Part of KETATA Group.", "legal_label": "Legal",
        "privacy": "Privacy Policy", "legal": "Legal Notice", "top": "Back to top", "home": "Home",
    },
    "fr": {
        "locale": "fr_FR", "skip": "Aller au contenu", "home_label": "Alpen Health, accueil", "nav_label": "Navigation principale",
        "contact": "Contact", "menu": "Menu", "lang_label": "Langue",
        "band": "La science ouvre des possibles. <span>Ce sont les gens qui les concrétisent.</span>",
        "band_r": "Alpen Health &nbsp;|&nbsp; L’Afrique du Nord et au-delà",
        "tag": "Science. Accès. Croissance.",
        "intro": "Partenaire stratégique des laboratoires et des entreprises de santé qui se développent en Afrique du Nord.",
        "company": "Entreprise", "about": "À propos d’Alpen Health", "values": "Nos valeurs", "group": "Groupe KETATA",
        "partnerships": "Partenariats", "expertise": "Expertise", "what": "Nos savoir-faire", "areas": "Domaines thérapeutiques",
        "markets": "Marchés", "enquiry": "Demande de partenariat", "address": "Centre Urbain Nord<br>Ariana, Tunisie",
        "copy": "&copy; 2026 Alpen Health. Membre du groupe KETATA.", "legal_label": "Informations légales",
        "privacy": "Politique de confidentialité", "legal": "Mentions légales", "top": "Revenir en haut", "home": "Accueil",
    },
}

# Map labels drawn inside the inline SVG maps
MAP_FR = {">ALGERIA<": ">ALGÉRIE<", ">LIBYA<": ">LIBYE<", ">TUNISIA<": ">TUNISIE<", ">Algiers<": ">Alger<"}

# Sends first-time visitors on English pages to French when their browser language is French
# or their time zone is in a French-speaking country (Tunisia, Algeria, Morocco, France, ...).
# A choice made with the language switch (stored as alpen-lang) always wins.
DETECT = """<script>(function(){var P=location.pathname;if(P==='/fr'){location.replace('/fr/'+location.search+location.hash);return}
if(/\\.html$/.test(P)&&history.replaceState)history.replaceState(null,'',P.replace(/(index)?\\.html$/,'')+location.search+location.hash);
var L='{lang}',K='alpen-lang',p=null;try{p=localStorage.getItem(K)}catch(e){}
if(!p&&L==='en'){var n=((navigator.languages&&navigator.languages[0])||navigator.language||'').toLowerCase(),z='';try{z=Intl.DateTimeFormat().resolvedOptions().timeZone||''}catch(e){}
if(n.indexOf('fr')===0||/^(Africa\\/(Tunis|Algiers|Casablanca|Dakar|Abidjan|Bamako|Niamey|Ouagadougou|Lome|Porto-Novo|Conakry|Nouakchott|Douala|Libreville|Brazzaville|Kinshasa|Bangui|Ndjamena)|Europe\\/(Paris|Brussels|Luxembourg|Monaco)|Indian\\/Reunion|America\\/(Martinique|Guadeloupe|Cayenne))$/.test(z))p='fr'}
if(p&&p!==L)location.replace('{alt_path}'+location.search+location.hash)})();</script>"""

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url_en}">
<link rel="alternate" hreflang="fr" href="{url_fr}">
<link rel="alternate" hreflang="x-default" href="{url_en}">
{detect}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Alpen Health">
<meta property="og:locale" content="{t[locale]}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#082B4C">
<link rel="icon" href="favicon.svg?v=2" type="image/svg+xml">
<link rel="icon" href="favicon-32.png?v=2" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v=8">
{preload}{schema}
</head>
<body class="{body_class}">
<a class="skip" href="#main">{t[skip]}</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="{t[home_label]}">{logo}</a>
    <nav class="nav" id="site-nav" aria-label="{t[nav_label]}">
      {nav}
      <a class="btn" href="contact.html"{contact_current}>{t[contact]}</a>
      <div class="nav__contact"><a href="mailto:info@alpen-health.com">info@alpen-health.com</a><br><a href="tel:+21654574587">+216 54 574 587</a></div>
    </nav>
    <div class="lang-switch" role="group" aria-label="{t[lang_label]}">{switch}</div>
    <button class="burger" aria-label="{t[menu]}" aria-controls="site-nav" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<div class="footer-band">
  <div class="wrap">
    <p>{t[band]}</p>
    <p class="r">{t[band_r]}</p>
  </div>
</div>
<footer class="site-footer">
  <div class="wrap">
    <div class="f-top">
      <div>
        <a class="logo" href="index.html" aria-label="{t[home_label]}">{logo}</a>
        <p class="f-tag">{t[tag]}</p>
        <p>{t[intro]}</p>
      </div>
      <div>
        <h4>{t[company]}</h4>
        <ul>
          <li><a href="about.html">{t[about]}</a></li>
          <li><a href="about.html#values">{t[values]}</a></li>
          <li><a href="about.html#ecosystem">{t[group]}</a></li>
          <li><a href="partnerships.html">{t[partnerships]}</a></li>
        </ul>
      </div>
      <div>
        <h4>{t[expertise]}</h4>
        <ul>
          <li><a href="what-we-do.html">{t[what]}</a></li>
          <li><a href="therapeutic-areas.html">{t[areas]}</a></li>
          <li><a href="markets.html">{t[markets]}</a></li>
          <li><a href="contact.html">{t[enquiry]}</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:info@alpen-health.com">info@alpen-health.com</a></li>
          <li><a href="tel:+21654574587">+216 54 574 587</a></li>
          <li><a href="tel:+41788893647">+41 78 889 36 47</a></li>
          <li>{t[address]}</li>
        </ul>
      </div>
    </div>
    <div class="f-bottom">
      <span>{t[copy]}</span>
      <nav aria-label="{t[legal_label]}">
        <a href="privacy.html">{t[privacy]}</a>
        <a href="legal.html">{t[legal]}</a>
      </nav>
    </div>
  </div>
</footer>
<button class="to-top" type="button" aria-label="{t[top]}"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M8 14V2M3 7l5-5 5 5"/></svg></button>
<script src="assets/js/site.js?v=9" defer></script>
</body>
</html>
"""

SCHEMA = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"Alpen Health","url":"https://www.alpen-health.com/","logo":"https://www.alpen-health.com/apple-touch-icon.png","slogan":"Science. Access. Growth.","email":"info@alpen-health.com","telephone":"+216 54 574 587","address":{"@type":"PostalAddress","streetAddress":"Centre Urbain Nord","addressLocality":"Ariana","addressCountry":"TN"},"areaServed":["Tunisia","Algeria","Libya"],"parentOrganization":{"@type":"Organization","name":"KETATA Group"}}
</script>"""


IMG_DIR = ROOT / "assets" / "img"
SIZES = {
    "mcard": "(max-width: 760px) 80vw, (max-width: 900px) 100vw, 33vw",
    "half": "(max-width: 900px) 100vw, 45vw",
}


def srcset(name):
    out = []
    for w in (640, 1024, 1600, 2200):
        if (IMG_DIR / f"{name}-{w}.webp").exists():
            out.append(f"assets/img/{name}-{w}.webp {w}w")
    master = IMG_DIR / f"{name}.webp"
    mw = Image.open(master).width
    if not any(o.endswith(f" {mw}w") for o in out):
        out.append(f"assets/img/{name}.webp {mw}w")
    return ", ".join(out), Image.open(master).size


def responsive(html):
    """Add srcset/sizes/width/height to every content image."""
    def fix(m):
        tag = m.group(0)
        name = m.group(1)
        if "srcset=" in tag:
            return tag
        ss, (w, h) = srcset(name)
        sizes = "100vw"
        ds = re.search(r'data-sizes="([^"]+)"', tag)
        if ds:
            sizes = SIZES.get(ds.group(1), ds.group(1))
            tag = tag.replace(ds.group(0), "")
        extra = f' srcset="{ss}" sizes="{sizes}" width="{w}" height="{h}" decoding="async"'
        return tag.replace(f'src="assets/img/{name}.webp"', f'src="assets/img/{name}.webp"{extra}')
    return re.sub(r'<img[^>]*src="assets/img/([a-z0-9-]+)\.webp"[^>]*>', fix, html)


def hero_preload(body):
    m = re.search(r'<img[^>]*src="assets/img/([a-z0-9-]+)\.webp"[^>]*fetchpriority="high"', body)
    if not m:
        return ""
    ss, _ = srcset(m.group(1))
    return f'<link rel="preload" as="image" type="image/webp" imagesrcset="{ss}" imagesizes="100vw">\n'


def breadcrumb(title, url, name, home="Home", home_url=SITE + "/"):
    if name == "index.html":
        return ""
    label = title.split("|")[0].strip()
    return ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
            f'{{"@type":"ListItem","position":1,"name":"{home}","item":"{home_url}"}},'
            f'{{"@type":"ListItem","position":2,"name":"{label}","item":"{url}"}}]}}</script>')


def maps(html):
    """Inline the SVG maps generated by tools/maps.py: {{map:tunisia}}."""
    return re.sub(r"\{\{map:([a-z-]+)\}\}", lambda m: (ROOT / "src" / "maps" / f"{m.group(1)}.svg").read_text().strip(), html)


def parse(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def up_one(html):
    """French pages live in /fr/: point shared files (assets, icons) one level up."""
    return re.sub(r'(?<=["\s,])(assets/|favicon|apple-touch-icon)', r'../\1', html)


def slug(name):
    """Clean URL for a page file: about.html -> about, index.html -> '' (the server maps both)."""
    return "" if name == "index.html" else name[:-5]


def page_url(lang, name):
    return SITE + ("/fr/" if lang == "fr" else "/") + slug(name)


def clean_links(html):
    """Drop .html from internal links: about.html#x -> about#x, index.html -> ./"""
    html = re.sub(r'href="index\.html"', 'href="./"', html)
    return re.sub(r'href="([a-z0-9-]+)\.html([#?][^"]*)?"', lambda m: f'href="{m.group(1)}{m.group(2) or ""}"', html)


def build_lang(lang):
    t = T[lang]
    src_dir = ROOT / "src" / ("pages" if lang == "en" else "pages-fr")
    out_dir = ROOT if lang == "en" else ROOT / "fr"
    out_dir.mkdir(exist_ok=True)
    pages = []
    for src in sorted(src_dir.glob("*.html")):
        meta, body = parse(src.read_text(encoding="utf-8"))
        current = meta.get("nav", "")
        cur = ' aria-current="page"'
        nav = "\n      ".join(
            f'<a href="{href}"{cur if key == current else ""}>{label}</a>'
            for key, href, label in NAV[lang]
        )
        name = src.name
        url, url_en, url_fr = page_url(lang, name), page_url("en", name), page_url("fr", name)
        other = "fr" if lang == "en" else "en"
        alt_path = url_fr if lang == "en" else url_en
        alt_path = alt_path[len(SITE):]
        other_href = ("fr/" if lang == "en" else "../") + slug(name)
        links = {lang: (slug(name) or "./", ' aria-current="true"'), other: (other_href, "")}
        switch = '<span aria-hidden="true">/</span>'.join(
            f'<a href="{links[code][0]}" hreflang="{code}" lang="{code}" data-lang="{code}"{links[code][1]}>{code.upper()}</a>'
            for code in ("en", "fr")
        )
        html = HEAD.format(
            lang=lang,
            t=t,
            title=meta["title"],
            description=meta["description"],
            url=url,
            url_en=url_en,
            url_fr=url_fr,
            detect=DETECT.replace("{lang}", lang).replace("{alt_path}", alt_path),
            site=SITE,
            schema=(SCHEMA if name in ("index.html", "contact.html") else "")
            + breadcrumb(meta["title"], url, name, t["home"], page_url(lang, "index.html")),
            preload=hero_preload(body),
            body_class="is-overlay" if meta.get("overlay") == "yes" else "",
            logo=LOGO,
            nav=nav,
            switch=switch,
            contact_current=' aria-current="page"' if current == "contact" else "",
        )
        content = maps(body.replace("{{arrow}}", ARROW))
        if lang == "fr":
            for a, b in MAP_FR.items():
                content = content.replace(a, b)
        html += responsive(content) + FOOT.format(logo=LOGO, t=t)
        html = clean_links(html)
        if lang == "fr":
            html = up_one(html)
        (out_dir / name).write_text(html, encoding="utf-8")
        if name != "404.html" and meta.get("nav") is not None:
            pages.append(name)
        print("built", lang, name)
    return pages


def build():
    en = build_lang("en")
    fr = build_lang("fr")
    sitemap(sorted(set(en) | set(fr)))


def sitemap(names):
    rows = []
    for name in names:
        alts = "".join(
            f'<xhtml:link rel="alternate" hreflang="{code}" href="{page_url(code, name)}"/>' for code in ("en", "fr")
        )
        for code in ("en", "fr"):
            rows.append(f"  <url><loc>{page_url(code, name)}</loc><lastmod>2026-11-09</lastmod>{alts}</url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    build()
