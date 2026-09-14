# RealRisks — Breast Cancer Screening module

A static educational website for women at high risk for breast cancer. This
repository contains **Module 2: Breast Cancer Screening** in **English and
Spanish**, built as 26 individual slide pages per language across 3 chapters,
styled to match the existing RealRisks design.

There is no server and no build step at request time — GitHub Pages serves the
committed HTML directly.

## Before you publish

Read [`LICENSING.md`](LICENSING.md). The images came from the source slide deck
and have no documented licences; three carry visible copyright or credit lines.
Clear them before making the repository public.

## Structure

```
index.html                English module home
chapter-1/slide-N.html    Overview (5 slides)
chapter-2/slide-N.html    Types of Screening Tests (11 slides)
chapter-3/slide-N.html    Screening Recommendations (10 slides)
es/…                      The same tree in Spanish
content/screening.en.json English slide text, image references and UI strings
content/screening.es.json The same, in Spanish
build.py                  Generates both language trees from the JSON
assets/css/styles.css     Styles
assets/js/progress.js     Progress tracking, accordion, arrow-key navigation
assets/img/               Images
assets/fonts/             Raleway, self-hosted (SIL OFL 1.1)
```

The site is set in **Raleway**, the same font as the source deck. It is
self-hosted rather than loaded from Google Fonts, so the site renders correctly
offline, makes no third-party requests, and never silently falls back to a
different font.

**The HTML files are generated. Don't edit them by hand** — your changes will
be overwritten. Edit the content file for the language you mean, then rebuild.

## Languages

English is served from the site root, Spanish from `/es/`, and a toggle in the
header links each page to the same page in the other language. Each page sets
its own `lang` attribute and declares the other via `hreflang`, so screen
readers pronounce it correctly and the pair is machine-discoverable.

Progress is deliberately **shared** between languages: slide ids do not carry a
language, so switching part-way through does not reset the reader's progress.

Both content files must describe the same chapters, the same number of slides,
and the same number of menu entries, or a toggle would land on a page that does
not exist. `build.py` refuses to build if they drift apart.

See [`TRANSLATION.md`](TRANSLATION.md) for what in the Spanish version still
needs a fluent review, and for the places where the two source decks state
different medical content.

## Editing content

```bash
# 1. Edit content/screening.en.json or content/screening.es.json
# 2. Regenerate the pages (Python 3, no dependencies)
python3 build.py
# 3. Preview locally
python3 -m http.server 8000   # then open http://localhost:8000
# 4. Commit both the JSON and the regenerated HTML
```

`build.py` recreates the generated pages on every run, so removing a slide
from a content file removes its page.

### Controlling the home-page menu

By default each slide gets its own entry in a chapter's dropdown. When a
chapter has many slides on a few topics, that menu gets long and repeats
titles. Adding a `"menu"` label to a slide groups the menu instead:

- A slide with a `"menu"` label starts an entry, and the entry links to it.
- Slides without one fold into the entry above, staying in the Next/Back flow
  but out of the menu.
- Slides before the first labelled slide join that first entry.
- A chapter with no `"menu"` labels lists every slide, as chapters 1 and 3 do.

Chapter 2 uses this: 11 slides collapse to 6 entries, so "Mammogram" appears
once and opens the mammogram slide, with the `~15 min` walkthrough following
on Next. An entry only shows its completion tick once **every** slide it
covers has been visited.

### Slide schema

Each slide has a `title`, an optional `subtitle`, an optional `menu` label
(see above), an optional `media` array (images shown in a right-hand column),
and a list of `blocks`. Available block
types, all defined in `build.py`:

| Type | Renders as |
| --- | --- |
| `text` | A paragraph |
| `bullets` | A bulleted list, with an optional heading |
| `numbered` | A numbered list, supporting lettered sub-items |
| `callout` | A highlighted "think of it like…" box |
| `takeaways` | The starred key-takeaways list |
| `compare` | Side-by-side benefits and harms |
| `twocol` | Two colour-coded columns (average vs. high risk) |
| `schedule` | Arrow-bulleted recommendation columns |
| `cards` | A row of captioned images |
| `steps` | Numbered preparation / positioning / imaging cards |
| `qablocks` | Question-and-answer pairs |
| `equation` | Two images joined by an `=` sign |
| `table` | The screening-methods comparison table |
| `birads` | The colour-coded BI-RADS table |
| `answer` | A large answer with explanatory notes |
| `factcards` | A row of short highlighted facts |

## Features

- **Every slide is its own page** with a real URL, so slides can be linked,
  bookmarked, and shared directly.
- **Progress tracking.** A slide is marked complete once visited; chapters tick
  when all their slides are done, and the Accomplishments bar shows the total.
  This is stored in `localStorage`, so it is per-browser and resets if the user
  clears their browser data. A static site cannot do better without a backend.
- **Keyboard navigation.** Left and right arrow keys move between slides.
- **Responsive** down to phone widths, and **accessible**: skip link, landmarks,
  visible focus, alt text on every image, and a progress bar exposed to screen
  readers.
- Content is readable with JavaScript disabled; only progress tracking needs it.

## Deploying to GitHub Pages

In the repository's **Settings → Pages**, set the source to **Deploy from a
branch** and pick the branch plus the `/ (root)` folder. The included
`.nojekyll` file stops Jekyll from processing the site.

## Content source

All slide text is transcribed verbatim from the source decks
(`RR Usability Testing - Screening` and `Copy Spanish Real Risk slides`). Only
typographic artifacts from the PDFs were corrected. This site is for education
and does not provide medical advice.
