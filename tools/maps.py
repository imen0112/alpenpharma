#!/usr/bin/env python3
"""Generate the inline SVG market maps in src/maps/ from Natural Earth data.

Source: world-atlas 2.0.2 (Natural Earth 1:50m, public domain), downloaded
to tools/countries-50m.json on first run.
Run: python3 tools/maps.py   then   python3 build.py
"""
import json
import math
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "src" / "maps"
DATA = HERE / "countries-50m.json"
URL = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json"

FOCUS = {"tunisia": "Tunisia", "algeria": "Algeria", "libya": "Libya"}

# (name, lon, lat, capital, label side)
CITIES = {
    "tunisia": [("Tunis", 10.18, 36.81, True, "r"), ("Sousse", 10.64, 35.83, False, "r"), ("Sfax", 10.76, 34.74, False, "r")],
    "algeria": [("Algiers", 3.06, 36.75, True, "t"), ("Oran", -0.63, 35.70, False, "tl"), ("Constantine", 6.61, 36.37, False, "tr")],
    "libya": [("Tripoli", 13.19, 32.89, True, "tl"), ("Benghazi", 20.07, 32.12, False, "t")],
}
KX = math.cos(math.radians(30))  # equirectangular, standard parallel 30°N


def load():
    if not DATA.exists():
        urllib.request.urlretrieve(URL, DATA)
    topo = json.loads(DATA.read_text())
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a[1:] if pts else a)
        return pts

    shapes = {}
    for g in topo["objects"]["countries"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]] if g["type"] == "Polygon" else []
        shapes[g["properties"]["name"]] = [[ring(r) for r in poly] for poly in polys]
    return shapes


class View:
    """Fit a lon/lat box into a pixel box."""

    def __init__(self, lon0, lat0, lon1, lat1, px0, py0, px1, py1):
        w, h = (lon1 - lon0) * KX, lat1 - lat0
        self.s = min((px1 - px0) / w, (py1 - py0) / h)
        self.ox = px0 + ((px1 - px0) - w * self.s) / 2 - lon0 * KX * self.s
        self.oy = py0 + ((py1 - py0) - h * self.s) / 2 + lat1 * self.s

    def p(self, lon, lat):
        return self.ox + lon * KX * self.s, self.oy - lat * self.s


def path(view, polys, W, H, tol=1.6):
    out = []
    for poly in polys:
        for r in poly:
            raw = [view.p(*q) for q in r]
            xs, ys = [q[0] for q in raw], [q[1] for q in raw]
            if max(xs) < -50 or min(xs) > W + 50 or max(ys) < -50 or min(ys) > H + 50:
                continue
            # clamp to a margin around the frame: keeps fills correct, drops off-screen detail
            pts = [(min(max(x, -20), W + 20), min(max(y, -20), H + 20)) for x, y in raw]
            keep = [pts[0]]
            for q in pts[1:]:
                if abs(q[0] - keep[-1][0]) + abs(q[1] - keep[-1][1]) >= tol:
                    keep.append(q)
            if len(keep) < 3:
                continue
            out.append("M" + " ".join(f"{x:.0f} {y:.0f}" if tol >= 1.5 else f"{x:.1f} {y:.1f}" for x, y in keep) + "Z")
    return "".join(out)


def bbox(polys):
    pts = [q for poly in polys for r in poly for q in r]
    return min(q[0] for q in pts), min(q[1] for q in pts), max(q[0] for q in pts), max(q[1] for q in pts)


def graticule(view, W, H, step=5):
    d = []
    for lon in range(-30, 50, step):
        x, _ = view.p(lon, 0)
        if 0 < x < W:
            d.append(f"M{x:.1f} 0V{H}")
    for lat in range(0, 60, step):
        _, y = view.p(0, lat)
        if 0 < y < H:
            d.append(f"M0 {y:.1f}H{W}")
    return f'<path class="map__grid" d="{"".join(d)}"/>'


def cities(view, key, labels=True):
    out = []
    for name, lon, lat, cap, side in CITIES[key]:
        x, y = view.p(lon, lat)
        cls = "map__city map__city--cap" if cap else "map__city"
        out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{5 if cap else 3.5}"/>')
        if cap:
            out.append(f'<circle class="map__pulse" cx="{x:.1f}" cy="{y:.1f}" r="11"/>')
        if labels:
            dx, dy, anchor = {"r": (12, 4, "start"), "l": (-12, 4, "end"), "b": (0, 22, "middle"), "t": (0, -14, "middle"), "tl": (-6, -12, "end"), "tr": (6, -12, "start")}[side]
            out.append(f'<text class="map__label{" map__label--cap" if cap else ""}" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{name}</text>')
    return "".join(out)


def svg(W, H, cls, label, body, slice_=True):
    par = ' preserveAspectRatio="xMidYMid slice"' if slice_ else ""
    return (f'<svg class="map {cls}" viewBox="0 0 {W} {H}"{par} role="img" aria-label="{label}">'
            f'<rect class="map__sea" width="{W}" height="{H}"/>{body}</svg>\n')


def country_map(shapes, key, W, H, box, cls, labels):
    name = FOCUS[key]
    lon0, lat0, lon1, lat1 = bbox(shapes[name])
    pad = max(lon1 - lon0, lat1 - lat0) * 0.08
    view = View(lon0 - pad, lat0 - pad, lon1 + pad, lat1 + pad, *box)
    land = "".join(path(view, polys, W, H) for n, polys in shapes.items() if n != name)
    focus = path(view, shapes[name], W, H, 0.9)
    _, lon, lat, _, _ = CITIES[key][0]
    coords = f"{lat:.2f}°N  {lon:.2f}°E"
    body = (graticule(view, W, H) + f'<path class="map__land" d="{land}"/>'
            + f'<path class="map__shadow" d="{focus}" transform="translate(0 6)"/>'
            + f'<path class="map__focus" d="{focus}"/>' + cities(view, key, labels)
            + (f'<text class="map__coord" x="24" y="{H - 22}">{CITIES[key][0][0].upper()}  ·  {coords}</text>' if labels else ""))
    return svg(W, H, cls, f"Map of {name} showing key cities", body)


def region_map(shapes):
    W, H = 1600, 900
    view = View(-3, 19, 26, 38.5, 700, 230, 1540, 820)
    land = "".join(path(view, polys, W, H) for n, polys in shapes.items() if n not in FOCUS.values())
    focus = "".join(f'<path class="map__focus" d="{path(view, shapes[n], W, H, 1.2)}"/>' for n in FOCUS.values())
    caps = {k: view.p(*CITIES[k][0][1:3]) for k in CITIES}
    (ax, ay), (tx, ty), (lx, ly) = caps["algeria"], caps["tunisia"], caps["libya"]
    links = (f'<path class="map__link" d="M{ax:.1f} {ay:.1f}Q{(ax + tx) / 2:.1f} {min(ay, ty) - 60:.1f} {tx:.1f} {ty:.1f}'
             f'M{tx:.1f} {ty:.1f}Q{(tx + lx) / 2 + 40:.1f} {(ty + ly) / 2 - 30:.1f} {lx:.1f} {ly:.1f}"/>')
    dots = "".join(cities(view, k, labels=False) for k in CITIES)
    names = "".join(
        f'<text class="map__country" x="{x:.0f}" y="{y:.0f}" text-anchor="middle">{n}</text>'
        for n, (x, y) in (("ALGERIA", view.p(2.5, 27.5)), ("LIBYA", view.p(17.5, 27)), ("TUNISIA", view.p(9.4, 33.6))))
    caps_lbl = "".join(
        f'<text class="map__label map__label--cap" x="{x + dx:.0f}" y="{y + dy:.0f}" text-anchor="{a}">{CITIES[k][0][0]}</text>'
        for k, dx, dy, a in (("algeria", 0, -18, "middle"), ("tunisia", 16, -8, "start"), ("libya", 0, -18, "middle"))
        for x, y in [caps[k]])
    body = graticule(view, W, H) + f'<path class="map__land" d="{land}"/>' + focus + names + links + dots + caps_lbl
    return svg(W, H, "map--dark", "Map of Tunisia, Algeria and Libya", body)


def main():
    shapes = load()
    OUT.mkdir(parents=True, exist_ok=True)
    for key in FOCUS:
        # detail figure on the Markets page (5:4, light)
        (OUT / f"{key}.svg").write_text(country_map(shapes, key, 500, 400, (40, 30, 460, 370), "map--light", True))
        # home market card (3:4 portrait, dark; text sits over the lower part)
        (OUT / f"{key}-card.svg").write_text(country_map(shapes, key, 600, 800, (90, 70, 510, 420), "map--dark", False))
    (OUT / "region.svg").write_text(region_map(shapes))
    for f in sorted(OUT.glob("*.svg")):
        print(f.name, f.stat().st_size)


if __name__ == "__main__":
    main()
