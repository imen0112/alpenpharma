# Alpen Health — website

Static multi-page site (HTML/CSS/JS) + `contact.php` for the partnership enquiry form.

## Pages
Home · About · What We Do · Therapeutic Areas · Markets · Partnerships · Contact · Privacy · Legal · 404

## Editing
Page content lives in `src/pages/*.html`; the shared header/footer/logo are in `build.py`.
After editing, rebuild the root HTML files:

    python3 build.py

## Deploy
Upload the repository content (except `src/`, `docs/`, `build.py`) to the web root of alpen-health.com.
The server needs PHP `mail()` for `contact.php` (enquiries go to info@alpen-health.com).

## Brand
Navy #082B4C · Cyan #59C4D1 · Ice #CDEBF0 · Coral #E54B4B · Off-white #F7F9FA · Graphite #17212B
Montserrat (headings) · Inter (body). Photography: Unsplash (Unsplash License).
