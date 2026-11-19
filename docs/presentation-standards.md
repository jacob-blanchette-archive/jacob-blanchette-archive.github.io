# Public presentation standards

These are **role-based** design and editorial conventions. Reuse styles **within a card role**, not a single size or spacing rule for every page. The website CSS is the rendering authority; the Jacob Photo Archive skill records the editorial method.

| Role | Applies to | Rendering source | Intentional geometry |
| --- | --- | --- | --- |
| Collection preview | Home and Collections: BFHF, BRG, Politics & Activism, Community, Portraits, Environmental | `assets/css/collection-previews.css` | Same linked card, 16:10 crop, padding, heading weight, CTA, and credit **below** the card on both pages |
| Year index | BFHF organization overview | `assets/css/bfhf-years.css` (`.bfhf-year-*`) | Distinct three-column year cards, large year numerals, compact copy, different image and text spacing |
| Occasion/event index | BFHF years, BRG, Dellums, thematic introductions | `assets/css/bfhf-years.css` (`.bfhf-event-*` and `.archive-event-*`) | Shared two-column card grammar and action row; intentional padding and image-height differences from previews and year cards |
| Photographic gallery tiles | Individual galleries | `assets/css/site.css`, `assets/css/curatorial.css`, gallery viewer | Denser image-led browsing, archival metadata in the expanded viewer |

## Collection-preview contract

1. Both Home and Collections use `collection-card-wrap > a.collection-card + p.featured-photo-credit`; **the whole card** links to the introduction. No link is nested in that anchor.
2. The same collection uses the same photographic image, public subject title, destination and archival-record link on both pages; Home may have shorter text, and HTML heading levels appropriately differ.
3. The credit is a separate subdued line **after the closing card link**: `Photograph by Jacob Blanchette · View photo record and citation →`. The link points to that specific published photograph, not automatically to the card's collection. Do not attribute an unattributed image to Jacob by layout convention.
4. Every theme uses normal grid cells, even when only one collection is published. Portraiture now displays two published photographic collection cards, **Portraits** and **Environmental**, under the same preview-card contract as the other themes.
5. Load `assets/css/collection-previews.css` after the page and curatorial styles on both pages, so there is one preview design to maintain.

## Community & Civic Life grouping contract

Community & Civic Life uses two public **parent collection** previews on Home and Collections: **Politics & Activism** and **Community**. Their metadata and published subjects are maintained in `data/collection-groups.json`. Only published subjects belong on their index cards.

- Politics & Activism → `politics-activism.html` → Ronald V. Dellums (`dellums-1987.html`) → the existing 1987 gala gallery.
- Community → `community.html` → Community Baseball (`community-baseball.html`) → the existing ball-field gallery.
- The existing gallery identifiers, original subject pages, archival item IDs, and publication permissions remain unchanged. `data/subjects.json` records `parent_group_id` to keep group membership explicit.
- Continue reviewing the possible future titles **Sports**, **Gatherings & Parades**, and other reported political/community subjects before making additional public changes. No new unpublished photograph is exposed by creating these parent pages.
- Parent index cards use the same `archive-event` visual grammar for a published subject introduction as occasion cards use for gallery navigation. Preview credit lines stay outside the whole-card anchors; interior cards do not acquire duplicate credit lines.

## Interior-card contract

1. **BFHF year cards** are navigational indexes by year. Keep their own card proportions and spacing; do not force the preview-card image ratio or event-card typography onto them.
2. **Occasion/event cards** on BFHF year pages and BRG/Dellums introductions use the shared `bfhf-event` / `archive-event` rules in `assets/css/bfhf-years.css`. Within this role, match photograph height, padding, title scale, CTA alignment and mobile breakpoints. The event/occasion title must equal the destination gallery H1.
3. The primary photo and CTA open the corresponding gallery. An occasion-specific document is a separate action in the **same action row**, opening the shared document viewer. A schedule covering several events belongs under the broader year history instead. Do not add documents to photographic counts.
4. Preserve distinct page hierarchies: organization → year or occasion → gallery. A single published gallery remains one normal grid card, not a stretched horizontal hero.
5. Differences **between roles** are deliberate: the shared system is typography, photographic fidelity, attribution and action semantics, not an identical `padding` or `gap` value on every component.

## Gallery and writing contract

- A gallery title matches its incoming card; context such as organization/year belongs in an eyebrow when useful.
- Lead with the historic occasion and photographed activity. Keep counts, crop workflow and uncertain binder assignments out of public introductory prose.
- Put qualified dates, attribution/rights caveats and documentary provenance in a restrained `gallery_source_note` **after** the photographic grid; full evidence remains in item records.
- Preserve permanent `JB-######` IDs, approved publication scope, photo sources, rights and as-found arrangement.

## Shared vertical spacing contract

Spacing follows semantic roles, not page-by-page pixel choices. Define the
tokens once in `assets/css/curatorial.css` and reference them in page styles.

| Role | Desktop | Mobile (760px and below) | Application |
| --- | --- | --- | --- |
| Major content-section inset (`--space-major-section`) | 72px | 56px | Home's outer bands, Collections' first/last outer edges, Biography's lead/career/conclusion |
| Related-topic divider (`--space-internal-divider`) | 40px total | 32px total | Between homepage themes, Collections themes, biography passages; split equally before and after the divider |
| Stronger biography chapter divider (`--space-chapter-divider`) | 56px total | 44px total | Between distinct groups within the professional narrative |
| Interior collection/event section (`--space-section`) | 81px | 57px at 540px and below | BFHF, BRG, Dellums and other pages, intentionally separate from the three top-level page families |

The page-title/header region uses separate tokens; it is not a standard content
band. Card padding, text leading, and photo staging likewise do not inherit
section spacing.

- **Never double-pad Collections themes.** Their `.content.collection-themes`
  wrapper has zero vertical padding; the first and last theme supply 72px/56px
  exterior insets. Each shared theme boundary instead uses two half-dividers,
  creating 40px/32px total whitespace around the border.
- **Homepage theme separators** use the same two half-dividers; Biography
  internal passages also use the same related-topic divider. The stronger
  biography grouped sections use the chapter divider.
- **No ad-hoc last-child padding exceptions.** A terminal theme ends with the
  same major inset as another top-level section. A deliberate exception must
  have a named token and an explanation here before publication.
- Change the shared tokens rather than adding hardcoded `margin-top` or
  `padding` values to equivalent sections. Keep responsive breakpoints
  centralized; do not duplicate the values in page-specific media queries.

Run `python3 scripts/check_spacing_contract.py` after changing site spacing
or any of these CSS files. This guards the token references, wrapper geometry,
document inclusion, and mobile values. Check actual desktop/mobile rendering
separately: automated structure checks cannot prove visual balance.

## Review before publication

Run `python3 scripts/check_spacing_contract.py` for shared major-section and internal-divider rules. Run `python3 scripts/check_gallery_contract.py` for occasion titles, subject mapping and gallery-source-note placement. Run `python3 scripts/check_preview_contract.py` for Home/Collections preview alignment, credit position, Portraiture previews and role-specific interior-card styling. Both are structural checks; inspect desktop/mobile rendering, link behavior, image framing, alt text and documentary viewers separately. Do not change the indexing/rights policy during a presentation-only cleanup.
