# Jacob Blanchette Photography Archive — draft website

This public repository contains the working website for the Jacob Blanchette Photography Archive. The collection steward has approved provisional public presentation of the BFHF images. Historical identifications, rights documentation, and higher-quality digitization are still under review; a public repository makes all committed assets accessible even if GitHub Pages is not enabled. The biography contains family-reported information under verification, and the portrait has an explicitly labeled AI-enhanced presentation image alongside a documentary phone capture.

## New: Black Repertory Group 1990 album

- `brg-1990.html`: introduction to the album's documented 25th anniversary title page (July 20–22, 1990), original cover and opening-page photographs.
- `gallery.html?collection=brg-1990`: tiled gallery and slideshow, with text search and filter by provisional album page P09–P14.
- `data/photos.json`: 21 provisional photographs, identifiers `JB-000002` through `JB-000023`, excluding private business card `JB-000021`. The BFHF gallery is separately cataloged with 35 actual collection objects.
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

## Black Filmmakers Hall of Fame — provisional gallery

- `bfhf.html`: BFHF history and collection introduction.
- `gallery.html?collection=bfhf-pilot`: gallery of 35 cataloged binder objects (one printed awards announcement, 27 mounted photographic prints, seven provisional film/contact assemblies).
- `assets/images/bfhf/`: reduced-resolution, non-generative presentation crops; `assets/images/bfhf/as-found/`: 17 documentary binder-page reproductions for comparison.
- The expanded viewer switches between the cropped image and the binder page as photographed. The latter is **not a preservation-grade scan of an individual print**. Item IDs are displayed in the expanded viewer, not beneath thumbnails.
- These are provisional exhibition images; no new AI restoration was applied to the BFHF gallery, and the image-treatment review has not yet been carried out as an image replacement campaign. Preserve source captures and master files in private storage.
- The 1987 printed program and the Chicago June 1987 contact frames do not individually date all items. Attribution to Jacob Blanchette is family-reported; individual people, exposure dates, and rights documentation remain under research.

## View locally
Run `python3 -m http.server 8000` in the repository folder, then open `http://localhost:8000/`. Loading the gallery data requires HTTP rather than opening the file directly.

## First cataloged portrait — JB-000001
The homepage displays `assets/images/JB-000001_enhanced_web.webp`, derived by generative AI from a phone photograph of a print. The biography provides a comparison with `assets/images/JB-000001_phone_web.webp`. `data/portrait.json` provides public-facing metadata. Both files are resized derivatives for web display. The original phone capture and full-resolution AI result are retained outside the public repository, and the underlying physical print's date, photographer, and original container are not yet documented. Do not mistake generative restoration for archival reproduction.

## Add photographs
Use cataloged IDs and approved web-resolution derivatives in `data/photos.json`. The BFHF demonstration entries have already been replaced by 35 provisional gallery records. Place subsequent approved display files in collection-specific image directories and point each record's `image` field to its relative path. Do **not** put original phone photographs, TIFF masters, confidential archival metadata, or unreleased photographs in this public repository. Keep those in appropriately backed-up private storage.

Records can include `id`, `collection_id`, `order`, `title`, `caption`, `description`, `people`, `date`, `place`, `original_group`, `image`, `identification_status`, `digitization_tier`, and `published`. Review any original storage-location metadata before releasing it publicly.

## Publication
This repository is public, and provisional public display of the BFHF collection has been approved by the collection steward. GitHub Pages deployment has **not been verified in this repository review**. HTML pages retain `noindex,nofollow` because the site is a working historical archive, not yet approved for search-engine discovery. This does **not** provide privacy. Pages can be configured in repository settings using `main` and `/(root)`; remove `noindex` only after a separate discovery-readiness review.

## Historical sources
- [Oakland Public Library — Black Filmmakers Hall of Fame collection](https://oaklandlibrary.org/archival_post/black-filmmakers-hall-of-fame-collection-1974-2015/)
- [Indiana University Black Film Center & Archive](https://www.bfca.iu.edu/)

These institutional sources provide general context, not verification for particular photo captions or every family-reported biographical detail.

## Gallery consistency check

Before publishing a change to an event/occasion gallery card, gallery title, `data/collections.json`, `data/bfhf-events.json`, or the shared gallery layout, run:

```bash
python3 scripts/check_gallery_contract.py
```

This standard-library check verifies that the BFHF and BRG event/occasion card titles match their destination gallery headings and that the shared `gallery-source-note` stays below the photographic grid rather than under the Back link. It also checks the gallery's field fallbacks and responsive hidden state. Historical verification, copyright review, and browser/mobile inspection remain separate requirements. The skill's `references/site-presentation.md` documents the editorial rule.
