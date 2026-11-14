# Jacob Blanchette Jr. Photography Archive — draft website

This repository hosts the working website for the Jacob Blanchette Jr. Photography Archive. The site is **not ready for public launch**: the biography contains family-reported information under verification, the portrait is cataloged as JB-000001 with an AI-enhanced display image and a phone-capture comparison, and the BFHF gallery uses nine clearly labeled demonstration records.

## New: Black Repertory Group 1990 album

- `brg-1990.html`: introduction to the album's documented 25th anniversary title page (July 20–22, 1990), original cover and opening-page photographs.
- `gallery.html?collection=brg-1990`: tiled gallery and slideshow, with text search and filter by provisional album page P09–P14.
- `data/photos.json`: 21 provisional photographs, identifiers `JB-000002` through `JB-000023`, excluding private business card `JB-000021`. BFHF demo entries remain separate.
- `assets/images/brg-1990/`: small first-pass WebP derivatives made by conventional cropping and tonal adjustment, **not generative AI**; includes cover and title page.
- **Important:** Individual photograph dates, subject identifications, original photographer attribution, exact page order, crop boundaries, and publication rights require review. The printed title page establishes the album's stated celebration dates, not each print's date. Public GitHub repositories expose assets even if GitHub Pages is disabled.
- The authoritative item-level catalog and original-arrangement photographs remain in the **private** `archive-catalog` repository. Do not publish internal file metadata or unreviewed business-card contact information.

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

## First cataloged portrait — JB-000001
The homepage displays `assets/images/JB-000001_enhanced_web.webp`, derived by generative AI from a phone photograph of a print. The biography provides a comparison with `assets/images/JB-000001_phone_web.webp`. `data/portrait.json` provides public-facing metadata. Both files are resized derivatives for web display. The original phone capture and full-resolution AI result are retained outside the public repository, and the underlying physical print's date, photographer, and original container are not yet documented. Do not mistake generative restoration for archival reproduction.

## Add photographs
Replace the nine `DEMO-...` records in `data/photos.json` with real catalog records only after checking identification, provenance, and publication rights. Place approved resized display JPEGs in `assets/images/photos/` and set each record's `image` field to its relative path. Do **not** put original phone photographs, TIFF masters, confidential archival metadata, or unreleased photographs in this public repository. Keep those in appropriately backed-up private storage.

Records can include `id`, `collection_id`, `order`, `title`, `caption`, `description`, `people`, `date`, `place`, `original_group`, `image`, `identification_status`, `digitization_tier`, and `published`. Review any original storage-location metadata before releasing it publicly.

## Publication
This repository is public, but Pages should remain disabled until the draft is approved. HTML files contain `noindex,nofollow` to discourage search indexing; this does **not** provide privacy. After review, configure GitHub Pages with `main` and `/(root)` to publish at `https://jacob-blanchette-archive.github.io/`. Remove noindex metadata when the site is ready for discovery.

## Historical sources
- [Oakland Public Library — Black Filmmakers Hall of Fame collection](https://oaklandlibrary.org/archival_post/black-filmmakers-hall-of-fame-collection-1974-2015/)
- [Indiana University Black Film Center & Archive](https://www.bfca.iu.edu/)

These institutional sources provide general context, not verification for particular photo captions or every family-reported biographical detail.
