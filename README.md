# RealRisks — Breast Cancer Screening module

A static educational website for women at high risk for breast cancer. This
repository contains **Module 2: Breast Cancer Screening**, built as 25
individual slide pages across 3 chapters, styled to match the existing
RealRisks design.

There is no server and no build step at request time — GitHub Pages serves the
committed HTML directly.

## Before you publish

Read [`LICENSING.md`](LICENSING.md). The images came from the source slide deck
and have no documented licences; three carry visible copyright or credit lines.
Clear them before making the repository public.

## Structure

```
index.html                Module home: 3 chapters, progress sidebar
chapter-1/slide-N.html    Overview (5 slides)
chapter-2/slide-N.html    Types of Screening Tests (11 slides)
chapter-3/slide-N.html    Screening Recommendations (9 slides)
content/screening.json    All slide text and image references — edit this
build.py                  Generates the HTML from the JSON
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
be overwritten. Edit `content/screening.json` instead, then rebuild.

## Editing content

```bash
# 1. Edit content/screening.json
# 2. Regenerate the pages (Python 3, no dependencies)
python3 build.py
# 3. Preview locally
python3 -m http.server 8000   # then open http://localhost:8000
# 4. Commit both the JSON and the regenerated HTML
```

`build.py` deletes and recreates the `chapter-*/` directories on every run, so
removing a slide from the JSON removes its page.

### Slide schema

Each slide has a `title`, an optional `subtitle`, an optional `media` array
(images shown in a right-hand column), and a list of `blocks`. Available block
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

All slide text is transcribed verbatim from the source deck
(`RR Usability Testing - Screening`). Only typographic artifacts from the PDF
were corrected. This site is for education and does not provide medical advice.
