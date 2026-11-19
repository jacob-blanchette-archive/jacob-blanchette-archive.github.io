# Jacob Blanchette Photography Archive — public website

This repository contains the public website for the **Jacob Blanchette Photography Archive**. It presents selected photographs, historically grounded collection introductions and a biography of the photographer. The website is a working publication: identifications, historical context, rights, and digitization continue to be reviewed.

**This repository is public.** Committing an image here makes that file publicly accessible even when the website carries a search-engine `noindex` directive. Do not commit private research, unapproved images, unredacted contact information, full-resolution archival masters, or sensitive catalog fields.

## Public pages and editorial structure

| Page or route | Purpose |
| --- | --- |
| `index.html` | Home and selected collection previews |
| `collections.html` | Collection overview |
| `biography.html` | Jacob Blanchette's public biography |
| `bfhf.html`, `bfhf-1987.html`, `bfhf-1988.html`, `bfhf-1990.html` | Black Filmmakers Hall of Fame history and year/occasion navigation |
| `brg-1990.html` | Black Repertory Group organization-level introduction and gallery links, including 1985, building-campaign, and 1990 collections |
| `politics-activism.html` | Politics & Activism parent collection |
| `dellums-1987.html`, `political-gatherings.html` | Direct photographic presentations for the Dellums gala and provisional political gatherings |
| `community.html` | Recreation & Events parent collection |
| `community-sports.html`, `festivals-parades.html` | Direct community sports and festivals/parades galleries |
| `portraits.html` | Direct Portraits gallery |
| `gallery.html?collection=...` | Individual gallery and permanent-ID photographic records |
| `about.html` | Purpose and stewardship of the archive |

Some older routes, including `community-baseball.html`, `gatherings-parades.html` and `environmental.html`, are maintained as redirects; do not treat them as separate current collections.

## How the website is assembled

- `data/photos.json`: public, approved image and descriptive records. It is **not** the authoritative internal item catalog.
- `data/collections.json`, `data/subjects.json`, `data/collection-groups.json`: gallery, subject, and parent-category metadata.
- `data/bfhf-events.json`: BFHF year and documented occasion/program groupings.
- `data/direct-collection-pages.json`: historical and thematic text for direct photographic pages.
- `templates/direct-collection-page.html`, `scripts/build_direct_collection_pages.py`: shared rendering of direct collection pages.
- `assets/images/`: reduced-resolution public derivatives only.
- `assets/css/`, `assets/js/`: shared presentation and photographic viewer behavior.
- [`docs/presentation-standards.md`](docs/presentation-standards.md): **current** layout, navigation, card, spacing, and editorial interaction contract.

The museum-style introductory copy focuses on historical subjects and events. Item provenance, exposure-date qualifications, sources, and detailed image records stay in appropriate source notes and archival records. Published collection membership is not proof that an event, person, location or individual exposure date has been verified.

## Private source of truth and work continuity

Internal metadata, permanent `JB-######` identifiers, digital file IDs, original arrangement, source/claim registers, rights review and project coordination are managed in the separate **private** `jacob-blanchette-archive/archive-catalog` repository. It contains `documentation/PROJECT_STATUS.md`, `DECISIONS.md`, `RESEARCH_TODO.md` and `SESSION_WORKFLOW.md`, which are the handoff for new ChatGPT working conversations. Their contents are intentionally not copied into this public repository.

This public repository is the authority for **what the website code and public metadata currently display**. Publication approval, documentary evidence, and preservation status must be checked in the private repository and against original materials. Do not use this README as a live progress tracker.

## Work locally

Run a local HTTP server from the repository root:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/`; dynamic gallery data should be tested over HTTP, not through `file://`.

Before publishing relevant content or structural changes:

```bash
python3 scripts/build_direct_collection_pages.py --check
python3 scripts/check_preview_contract.py
python3 scripts/check_gallery_contract.py
python3 scripts/check_spacing_contract.py
```

When changing direct-page content, edit the manifest/template and generate the affected HTML with `python3 scripts/build_direct_collection_pages.py`, then run the checks. These checks verify structural conventions only; independently review images, references, links, credits, document interactions, responsiveness, and real browser rendering.

## Current operating safeguards

- Use **Jacob Blanchette** as the public name. His formal full name, **Jacob Samuel Blanchette Jr.**, belongs in appropriate biographical or authority-record context.
- Never infer photographic authorship or reproduction rights from possession of a print; photographic attribution and legal permission require separate evidence.
- Clearly distinguish faithful scans/crops from any AI-enhanced derivative. The public biography uses a non-generative portrait reproduction for JB-000001.
- Preserve the site's existing `noindex,nofollow` policy until the collection steward explicitly changes it. This is **not** access control.
- Do not imply that an internally cataloged object is approved for public display. Keep master files in separately backed-up, private preservation storage.
- Before declaring work complete, verify its GitHub commit and actual site behavior; a commit alone does not establish successful live-site or mobile-browser verification.

## Research context

For general historical context, consult institutional sources such as the [Oakland Public Library's Black Filmmakers Hall of Fame collection](https://oaklandlibrary.org/archival_post/black-filmmakers-hall-of-fame-collection-1974-2015/) and the [Indiana University Black Film Center & Archive](https://www.bfca.iu.edu/). These support background history, not the identification, authorship, or exposure date of each photograph.
