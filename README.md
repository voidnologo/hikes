# Hike with Me

A personal static site for backpacking trip plans, routes, and photos.
Plain HTML/CSS/JS, no build step, hosted on GitHub Pages.

**Live:** https://voidnologo.github.io/hikes/ (once Pages is enabled)

## Structure

```
.
├── index.html                  # "Hike with Me" landing: hero, photo carousel, hike index
├── .nojekyll                   # serve files as-is (no Jekyll), matching the main site
├── assets/
│   ├── css/styles.css          # shared styles for the landing + all hike pages
│   ├── js/carousel.js          # dependency-free photo carousel
│   └── img/                    # landing/carousel images
└── hikes/                      # one self-contained folder per hike
    ├── hiwassee-river-bmt/     # Benton MacKaye Trail, Childers Creek → Unicoi Gap
    │   ├── index.html          # hike page
    │   ├── plan.md             # full written plan
    │   └── waypoints.gpx       # verified GPS waypoints
    └── 2026-smokies/           # Appalachian Trail, Great Smokies (merged from the 2026-hike repo)
```

## Adding a new hike

1. Create `hikes/<slug>/` with its own `index.html` (copy an existing hike page as a starting point).
2. Add the plan, GPX, and any scripts/data specific to that hike inside the same folder.
3. Add a `<a class="hike-card">` for it in the `#hikes` section of `/index.html`.

Each hike folder is self-contained, so a trip can carry its own plans, pages, scripts, and data.

## Adding carousel photos

See the instructions at the top of `assets/js/carousel.js` — drop images in `assets/img/`,
add `<div class="carousel__slide">` entries in `index.html`, remove the placeholders.

## Local preview

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```
