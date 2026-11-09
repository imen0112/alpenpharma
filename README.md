# Alpen Health — website

Static multi-page site (HTML/CSS/JS) + `contact.php` for the partnership enquiry form.

## Pages
Home · About · What We Do · Therapeutic Areas · Markets · Partnerships · Contact · Privacy · Legal · 404

## Editing
Page content lives in `src/pages/*.html` (English) and `src/pages-fr/*.html` (French, built into `fr/`); the shared header/footer/logo and their translations are in `build.py`.
After editing, rebuild the root HTML files:

    python3 build.py

## Deploy
The site is served by Railway (www.alpen-health.com). `contact.php` is not run there: it lives on the Ooredoo cPanel hosting (public_html) and the form posts to https://alpen-health.com/contact.php (PHP 7.0, `mail()`; enquiries go to info@alpen-health.com).

## Brand
Navy #082B4C · Cyan #59C4D1 · Ice #CDEBF0 · Coral #E54B4B · Off-white #F7F9FA · Graphite #17212B
Montserrat (headings) · Inter (body). Photography: Unsplash (Unsplash License).
