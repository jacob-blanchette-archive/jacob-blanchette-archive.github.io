# Jacob Blanchette Jr. Photography Archive — draft website

This repository hosts the working website for the Jacob Blanchette Jr. Photography Archive. The site is **not ready for public launch**: the biography contains family-reported information under verification, the portrait is a placeholder, and the gallery uses nine clearly labeled demonstration records.

## Website files
- `index.html`: homepage and portrait placeholder
- `biography.html`: preliminary biography
- `collections.html`: collections index
- `bfhf.html`: Black Filmmakers Hall of Fame introduction
- `gallery.html?collection=bfhf-pilot`: searchable tiled gallery and slideshow
- `about.html`: archival project description
- `assets/css/site.css`: responsive design
- `assets/js/gallery.js`: search, pagination, image viewer
- `data/collections.json` and `data/photos.json`: public collection metadata

## View locally
Run `python3 -m http.server 8000` in the repository folder, then open `http://localhost:8000/`. Loading the gallery data requires HTTP rather than opening the file directly.

## Add the actual portrait
Save an approved web derivative to `assets/images/jacob-portrait.jpg` and update `index.html` and `biography.html` to reference it instead of `assets/images/portrait-placeholder.svg`. Preserve the original capture separately.

## Add photographs
Replace the nine `DEMO-...` records in `data/photos.json` with real catalog records only after checking identification, provenance, and publication rights. Place approved resized display JPEGs in `assets/images/photos/` and set each record's `image` field to its relative path. Do **not** put original phone photographs, TIFF masters, confidential archival metadata, or unreleased photographs in this public repository. Keep those in appropriately backed-up private storage.

Records can include `id`, `collection_id`, `order`, `title`, `caption`, `description`, `people`, `date`, `place`, `original_group`, `image`, `identification_status`, `digitization_tier`, and `published`. Review any original storage-location metadata before releasing it publicly.

## Publication
This repository is public, but Pages should remain disabled until the draft is approved. HTML files contain `noindex,nofollow` to discourage search indexing; this does **not** provide privacy. After review, configure GitHub Pages with `main` and `/(root)` to publish at `https://jacob-blanchette-archive.github.io/`. Remove noindex metadata when the site is ready for discovery.

## Historical sources
- [Oakland Public Library — Black Filmmakers Hall of Fame collection](https://oaklandlibrary.org/archival_post/black-filmmakers-hall-of-fame-collection-1974-2015/)
- [Indiana University Black Film Center & Archive](https://www.bfca.iu.edu/)

These institutional sources provide general context, not verification for particular photo captions or every family-reported biographical detail.
