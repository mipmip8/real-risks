#!/usr/bin/env python3
"""Generate the static RealRisks Screening module from content/screening.json.

Run `python3 build.py` after editing the JSON, then commit the generated HTML.
GitHub Pages serves the generated files directly; nothing runs at request time.
"""

import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
# Each language is a parallel content file rendered into its own tree: English
# at the site root, Spanish under es/. The two files must describe the same
# chapters and the same number of slides, so every page has a counterpart to
# toggle to; build() asserts that.
LANGUAGES = [
    {"code": "en", "root": "", "content": "screening.en.json"},
    {"code": "es", "root": "es/", "content": "screening.es.json"},
]

LOGO = (
    '<svg class="logo__mark" width="34" height="34" viewBox="0 0 24 24" '
    'fill="none" stroke="#b9a7e0" stroke-width="1.8" stroke-linecap="round" '
    'aria-hidden="true">'
    '<path d="M6 2c0 5 12 5 12 10S6 17 6 22"/>'
    '<path d="M18 2c0 5-12 5-12 10s12 5 12 10"/>'
    '<path d="M7.5 6h9M6.2 10h11.6M6.2 14h11.6M7.5 18h9"/>'
    "</svg>"
)

CHAPTER_ICONS = {
    "lightbulb": (
        '<path d="M9 21h6M10 17h4M12 3a6 6 0 0 0-3.6 10.8c.5.4.8.9.9 1.5h5.4'
        'c.1-.6.4-1.1.9-1.5A6 6 0 0 0 12 3z"/>'
    ),
    "scan": (
        '<path d="M3 8V5a2 2 0 0 1 2-2h3M16 3h3a2 2 0 0 1 2 2v3M21 16v3a2 2 0 0'
        ' 1-2 2h-3M8 21H5a2 2 0 0 1-2-2v-3M7 12h10"/>'
    ),
    "calendar": (
        '<path d="M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H5'
        'a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>'
    ),
}

CHEVRON = (
    '<svg class="chapter__chevron" width="20" height="20" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"'
    ' stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
)


POSITIONS = 9      # notches on each slider
MIDDLE_POS = 5     # the neutral notch, and the default


def e(text):
    """Escape a string for use in HTML text content."""
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------------------
# Block renderers
# ---------------------------------------------------------------------------


def r_text(b, _ctx):
    return "<p>%s</p>" % e(b["text"])


def r_callout(b, _ctx):
    return '<p class="callout">%s</p>' % e(b["text"])


def r_bullets(b, _ctx):
    out = []
    if b.get("heading"):
        out.append('<h2 class="block-heading">%s</h2>' % e(b["heading"]))
    items = "".join("<li>%s</li>" % e(i) for i in b["items"])
    out.append('<ul class="bullets">%s</ul>' % items)
    return "<div>%s</div>" % "".join(out) if b.get("heading") else out[0]


def r_numbered(b, _ctx):
    out = []
    if b.get("heading"):
        out.append('<h2 class="block-heading">%s</h2>' % e(b["heading"]))
    items = []
    for item in b["items"]:
        if isinstance(item, str):
            items.append("<li>%s</li>" % e(item))
            continue
        sub = ""
        if item.get("sub"):
            sub = "<ol>%s</ol>" % "".join(
                "<li>%s</li>" % e(s) for s in item["sub"]
            )
        items.append("<li>%s%s</li>" % (e(item["text"]), sub))
    out.append('<ol class="numbered">%s</ol>' % "".join(items))
    return "<div>%s</div>" % "".join(out)


def _compare_items(items, mark):
    rows = []
    for item in items:
        rows.append(
            '<li><p class="compare__title">'
            '<span class="compare__mark" aria-hidden="true">%s</span>%s</p>'
            "<p>%s</p></li>" % (mark, e(item["title"]), e(item["text"]))
        )
    return "".join(rows)


def r_compare(b, ctx):
    """Benefits and harms as staggered panels with a balance scale between,
    matching the source slide. The column headings are visually hidden: the
    slide does not show them, but screen readers need the two lists labelled.
    """
    benefits, harms = b["benefits"], b["harms"]
    return (
        '<div class="compare">'
        '<section class="compare__col compare__col--benefits">'
        '<h2 class="visually-hidden">%s</h2><ul>%s</ul></section>'
        '<div class="compare__scale">'
        '<img src="%sassets/img/balance-scale.jpg" alt="" width="342"'
        ' height="360" loading="lazy"></div>'
        '<section class="compare__col compare__col--harms">'
        '<h2 class="visually-hidden">%s</h2><ul>%s</ul></section>'
        "</div>"
        % (
            e(benefits["heading"]),
            _compare_items(benefits["items"], "✓"),
            ctx["assets"],
            e(harms["heading"]),
            _compare_items(harms["items"], "⚠"),
        )
    )


def r_equation(b, ctx):
    def fig(side):
        return (
            '<figure><img src="%sassets/img/%s" alt="%s" loading="lazy">'
            "<figcaption>%s</figcaption></figure>"
            % (ctx["assets"], e(side["src"]), e(side["alt"]), e(side["label"]))
        )

    return (
        '<div><div class="equation">%s'
        '<div class="equation__sign" aria-hidden="true">=</div>%s</div>'
        '<p class="equation__caption">%s</p></div>'
        % (fig(b["left"]), fig(b["right"]), e(b["caption"]))
    )


def r_takeaways(b, _ctx):
    items = "".join(
        '<li><span class="star" aria-hidden="true">★</span>'
        "<span>%s</span></li>" % e(i)
        for i in b["items"]
    )
    return '<ul class="takeaways">%s</ul>' % items


def r_cards(b, ctx):
    """Captioned image cards, each optionally linking to the slide it names.

    The whole card is one link rather than the image and caption being two, so
    there is a single tab stop and a single target. Its accessible name is the
    caption; the alt text stays for anyone reading the image itself.
    """
    items = []
    for i in b["items"]:
        figure = (
            '<figure><img src="%sassets/img/%s" alt="%s" loading="lazy">'
            "<figcaption>%s</figcaption></figure>"
            % (ctx["assets"], e(i["src"]), e(i["alt"]), e(i["title"]))
        )
        if i.get("href"):
            figure = (
                '<a class="cards__link" href="%s%s" aria-label="%s">%s</a>'
                % (ctx["assets"], e(i["href"]), e(i["title"]), figure)
            )
        items.append("<li>%s</li>" % figure)
    return '<ul class="cards">%s</ul>' % "".join(items)


def r_steps(b, ctx):
    items = []
    for step in b["items"]:
        bullets = "".join("<li>%s</li>" % e(x) for x in step["items"])
        items.append(
            '<li><h2>%s</h2><img src="%sassets/img/%s" alt="%s" loading="lazy">'
            "<ul>%s</ul></li>"
            % (e(step["title"]), ctx["assets"], e(step["src"]), e(step["alt"]), bullets)
        )
    return '<ol class="steps">%s</ol>' % "".join(items)


def r_qablocks(b, _ctx):
    items = "".join(
        "<div><dt>%s</dt><dd>%s</dd></div>" % (e(i["q"]), e(i["a"]))
        for i in b["items"]
    )
    return '<dl class="qablocks">%s</dl>' % items


def r_table(b, _ctx):
    head = "".join("<th scope='col'>%s</th>" % e(h) for h in b["headers"])
    rows = []
    for row in b["rows"]:
        cells = "<th scope='row'>%s</th>" % e(row[0])
        cells += "".join("<td>%s</td>" % e(c) for c in row[1:])
        rows.append("<tr>%s</tr>" % cells)
    return (
        '<div class="table-scroll"><table class="data-table">'
        "<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>"
        % (head, "".join(rows))
    )


def r_birads(b, _ctx):
    head = "".join("<th scope='col'>%s</th>" % e(h) for h in b["headers"])
    rows = []
    for row in b["rows"]:
        tone = e(row["tone"])
        cell = (
            '<td class="tone-%s"><span class="mark" aria-hidden="true">%s</span>'
            "%s</td>" % (tone, e(row["mark"]), e(row["category"]))
        )
        if "meaning" in row:
            span = int(row.get("span", 1))
            attr = ' rowspan="%d"' % span if span > 1 else ""
            cell += '<td class="tone-%s"%s>%s</td>' % (tone, attr, e(row["meaning"]))
        rows.append("<tr>%s</tr>" % cell)
    return (
        '<div class="table-scroll"><table class="data-table birads">'
        "<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>"
        % (head, "".join(rows))
    )


def r_answer(b, ctx):
    notes = "".join("<p>%s</p>" % e(n) for n in b["notes"])
    body = '<p class="answer__value">%s</p><div class="answer__notes">%s</div>' % (
        e(b["answer"]),
        notes,
    )

    if not b.get("reveal"):
        return '<div class="answer">%s</div>' % body

    # A <details> disclosure rather than a scripted button: it reveals on
    # click or keyboard without JavaScript, and a reader with JS disabled
    # still gets to the answer instead of a dead control. The notes hide with
    # the answer because they reference it ("before age 40").
    return (
        '<div class="answer"><details class="reveal">'
        '<summary class="reveal__toggle">'
        '<span class="reveal__show">%s</span>'
        '<span class="reveal__hide">%s</span>'
        "</summary>"
        '<div class="reveal__body">%s</div>'
        "</details></div>"
        % (e(ctx["ui"]["revealShow"]), e(ctx["ui"]["revealHide"]), body)
    )


def r_twocol(b, _ctx):
    cols = []
    for col in b["columns"]:
        sub = (
            '<p class="subtitle">%s</p>' % e(col["subtitle"])
            if col.get("subtitle")
            else ""
        )
        items = "".join("<li>%s</li>" % e(i) for i in col["items"])
        cols.append(
            '<section class="twocol__col twocol__col--%s"><h2>%s</h2>%s'
            "<ul>%s</ul></section>" % (e(col["tone"]), e(col["title"]), sub, items)
        )
    return '<div class="twocol">%s</div>' % "".join(cols)


def r_schedule(b, _ctx):
    """Recommendation columns with arrow bullets, one column per age group."""
    cols = []
    for col in b["columns"]:
        title = "<h2>%s</h2>" % e(col["title"]) if col.get("title") else ""
        items = "".join("<li>%s</li>" % e(i) for i in col["items"])
        cols.append(
            '<section class="schedule__col">%s<ul>%s</ul></section>' % (title, items)
        )
    return '<div class="schedule">%s</div>' % "".join(cols)


def r_factcards(b, _ctx):
    items = []
    for i in b["items"]:
        title = "<strong>%s</strong>" % e(i["title"]) if i.get("title") else ""
        items.append("<li>%s%s</li>" % (title, e(i["text"])))
    return '<ul class="factcards">%s</ul>' % "".join(items)


def r_sliders(b, ctx):
    cards = []
    for item in b["items"]:
        framings = "".join(
            '<p class="slider__framing" data-framing="%d"%s>%s</p>'
            % (i, "" if i == MIDDLE_POS else ' hidden=""', e(text))
            for i, text in enumerate(item["framings"], 1)
        )
        # The middle position renders as the default so the slide is still
        # readable, and still says something true, with JavaScript unavailable.
        cards.append(
            """<li class="slider-card" data-pos="{mid}" data-id="{id}">
  <h2 class="slider__title">{title}</h2>
  <div class="slider__control">
    <span class="slider__end slider__end--left" aria-hidden="true">{left}</span>
    <span class="slider__end slider__end--right" aria-hidden="true">{right}</span>
    <input type="range" id="slider-{id}" min="1" max="{max}" step="1" value="{mid}"
           class="slider__input" list="slider-ticks" aria-describedby="framing-{id}"
           aria-label="{title}. 1 means: {left}. {max} means: {right}."
           data-summary="{summaries}">
    <span class="slider__notches" aria-hidden="true">{notches}</span>
  </div>
  <div class="slider__framings" id="framing-{id}" aria-live="polite">{framings}</div>
</li>""".format(
                id=e(item["id"]),
                title=e(item["title"]),
                left=e(item["left"]),
                right=e(item["right"]),
                max=POSITIONS,
                mid=MIDDLE_POS,
                notches='<span class="notch"></span>' * POSITIONS,
                summaries=e("|".join(item["summary"])),
                framings=framings,
            )
        )

    ticks = "".join('<option value="%d"></option>' % n
                    for n in range(1, POSITIONS + 1))
    ui = ctx["ui"]
    return """<div class="sliders"
     data-copied="{s_copied}" data-copy-fail="{s_fail}"
     data-copy-unsupported="{s_unsupported}" data-reset="{s_reset}"
     data-clipboard-title="{s_title}" data-clipboard-footer="{s_footer}">
  <datalist id="slider-ticks">{ticks}</datalist>
  <p class="sliders__intro">{intro}</p>
  <p class="sliders__disclaimer">{disclaimer}</p>
  <ol class="slider-list">{cards}</ol>
  <section class="sliders__summary" id="slider-summary">
    <h2>{sh}</h2>
    <p>{si}</p>
    <ul class="sliders__summary-list"></ul>
    <div class="sliders__actions">
      <button type="button" class="btn btn--primary" data-slider-print>Print or save as PDF</button>
      <button type="button" class="btn" data-slider-copy>Copy to clipboard</button>
      <button type="button" class="btn" data-slider-reset>Reset sliders</button>
      <span class="sliders__status" role="status"></span>
    </div>
  </section>
</div>""".format(
        ticks=ticks,
        s_copied=e(ui["sliderCopied"]),
        s_fail=e(ui["sliderCopyFail"]),
        s_unsupported=e(ui["sliderCopyUnsupported"]),
        s_reset=e(ui["sliderReset"]),
        s_title=e(ui["sliderClipboardTitle"]),
        s_footer=e(ui["sliderClipboardFooter"]),
        intro=e(b["intro"]),
        disclaimer=e(b["disclaimer"]),
        cards="".join(cards),
        sh=e(b["summaryHeading"]),
        si=e(b["summaryIntro"]),
    )


RENDERERS = {
    "sliders": r_sliders,
    "text": r_text,
    "callout": r_callout,
    "bullets": r_bullets,
    "numbered": r_numbered,
    "compare": r_compare,
    "equation": r_equation,
    "takeaways": r_takeaways,
    "cards": r_cards,
    "steps": r_steps,
    "qablocks": r_qablocks,
    "table": r_table,
    "birads": r_birads,
    "answer": r_answer,
    "twocol": r_twocol,
    "schedule": r_schedule,
    "factcards": r_factcards,
}


def render_blocks(blocks, ctx):
    """ctx carries `assets` (prefix to the site root) and `ui` (localised
    strings), since some blocks need one, some the other."""
    out = []
    for block in blocks:
        renderer = RENDERERS.get(block["type"])
        if renderer is None:
            raise SystemExit("Unknown block type: %s" % block["type"])
        out.append(renderer(block, ctx))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------


def shell(ui, title, assets, links, toggle, body_attrs, breadcrumb, main,
          description):
    """One page.

    `assets` steps up to the site root (stylesheet, fonts, images are shared
    across languages); `links` steps up to the language root (every in-page
    link stays inside its own language). `toggle` is the same page in the
    other language.
    """
    return """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preload" href="{assets}assets/fonts/raleway-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{assets}assets/css/styles.css">
<link rel="icon" href="{assets}assets/img/favicon.svg" type="image/svg+xml">
<link rel="alternate" hreflang="{other_lang}" href="{toggle}">
</head>
<body {body_attrs}>
<a class="skip-link" href="#main">{skip}</a>
<header class="site-header">
  <div class="site-header__inner">
    <a class="logo" href="{links}index.html">
      {logo}<span><span class="logo__real">REAL</span>RISKS</span>
    </a>
    <nav class="site-nav" aria-label="Main">
      <a href="{links}index.html">{module_home}</a>
      <a class="lang-toggle" href="{toggle}" lang="{other_lang}"
         hreflang="{other_lang}">{switch_to}</a>
    </nav>
  </div>
</header>
{breadcrumb}
<div class="page">
<main id="main">
{main}
</main>
</div>
<footer class="site-footer">
  <div>
    <p><strong>{disclaimer}</strong>{disclaimer_rest}</p>
    <p>{progress_note}</p>
  </div>
</footer>
<script src="{assets}assets/js/progress.js"></script>
<script src="{assets}assets/js/sliders.js"></script>
</body>
</html>
""".format(
        lang=e(ui["lang"]),
        other_lang=e(ui["switchToLang"]),
        title=e(title),
        description=e(description),
        assets=assets,
        links=links,
        toggle=e(toggle),
        body_attrs=body_attrs,
        logo=LOGO,
        skip=e(ui["skipToContent"]),
        module_home=e(ui["moduleHome"]),
        switch_to=e(ui["switchTo"]),
        breadcrumb=breadcrumb,
        main=main,
        disclaimer=e(ui["footerDisclaimer"]),
        disclaimer_rest=e(ui["footerDisclaimerRest"]),
        progress_note=e(ui["footerProgress"]),
    )


def crumbs(depth, trail):
    items = []
    for i, (label, href) in enumerate(trail):
        last = i == len(trail) - 1
        if last or href is None:
            items.append('<li aria-current="page">%s</li>' % e(label))
        else:
            items.append('<li><a href="%s%s">%s</a></li>' % (depth, href, e(label)))
    return (
        '<nav class="breadcrumb" aria-label="Breadcrumb"><ol>%s</ol></nav>'
        % "".join(items)
    )


def menu_entries(chapter):
    """Group a chapter's slides into the entries shown in the home-page menu.

    A slide carrying a "menu" label starts an entry, and that entry links
    straight to it. Slides without one fold into the entry above, so detail
    slides stay in the Next/Back flow without cluttering the menu — and a
    topic spread over several slides appears once rather than repeating its
    title. Slides before the first labelled one join that first entry.

    A chapter with no labels at all lists every slide, which is the plain
    behaviour chapters 1 and 3 rely on.
    """
    slug = chapter["slug"]
    labelled = any(s.get("menu") for s in chapter["slides"])
    entries = []
    pending = []  # slides seen before the first labelled one

    for index, slide in enumerate(chapter["slides"], 1):
        sid = "%s-%d" % (slug, index)

        if labelled:
            label = slide.get("menu")
        else:
            label = slide["title"]
            if slide.get("subtitle"):
                label += " (%s)" % slide["subtitle"]

        if label:
            entries.append(
                {"label": label, "index": index, "ids": pending + [sid]}
            )
            pending = []
        elif entries:
            entries[-1]["ids"].append(sid)
        else:
            pending.append(sid)

    return entries


def sidebar(ui, total):
    return """<aside class="sidebar">
  <h2>{heading}</h2>
  <div class="accomplishments">
    <div class="progress-track"><div class="progress-fill"></div></div>
    <p class="progress-count">0 / {total}</p>
    <p>{hint}</p>
    <button type="button" class="reset-progress"
            data-confirm="{confirm}">{reset}</button>
  </div>
</aside>""".format(
        heading=e(ui["accomplishments"]),
        total=total,
        hint=e(ui["progressHint"]),
        confirm=e(ui["resetConfirm"]),
        reset=e(ui["resetProgress"]),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def progress_attrs(ui):
    """Localised strings progress.js needs, carried on <body>."""
    return (
        'data-i18n-completed="%s" data-i18n-not-completed="%s" '
        'data-i18n-progress="%s"'
        % (e(ui["completed"]), e(ui["notCompleted"]), e(ui["progressAria"]))
    )


def toggle_href(lang_root, inner, other_root):
    """Relative link from a page to the same page in the other language."""
    depth = "../" * (lang_root + inner).count("/")
    return depth + other_root + inner


def build_language(lang, other_root):
    with open(os.path.join(ROOT, "content", lang["content"]), encoding="utf-8") as fh:
        data = json.load(fh)

    ui = data["ui"]
    module = data["module"]
    chapters = data["chapters"]
    lang_root = lang["root"]

    flat = []
    for chapter in chapters:
        for index, slide in enumerate(chapter["slides"], 1):
            flat.append(
                {
                    "id": "%s-%d" % (chapter["slug"], index),
                    "path": "%s/slide-%d.html" % (chapter["slug"], index),
                    "chapter": chapter,
                    "index": index,
                    "slide": slide,
                }
            )

    total = len(flat)
    all_ids = ",".join(s["id"] for s in flat)
    module_label = "%s %d: %s" % (
        "Module" if ui["lang"] == "en" else "Módulo",
        module["number"],
        module["title"],
    )

    out_root = os.path.join(ROOT, *[p for p in lang_root.split("/") if p])
    if lang_root and os.path.isdir(out_root):
        shutil.rmtree(out_root)
    for chapter in chapters:
        os.makedirs(os.path.join(out_root, chapter["slug"]), exist_ok=True)
    for chapter in chapters:
        out_dir = os.path.join(out_root, chapter["slug"])
        for name in os.listdir(out_dir):
            os.remove(os.path.join(out_dir, name))

    # --- Home page --------------------------------------------------------
    chapter_html = []
    for chapter in chapters:
        ids = [s["id"] for s in flat if s["chapter"] is chapter]
        links = []
        for entry in menu_entries(chapter):
            links.append(
                '<li><span class="check" data-check-all="%s"></span>'
                '<a href="%s/slide-%d.html">%s</a></li>'
                % (
                    ",".join(entry["ids"]),
                    chapter["slug"],
                    entry["index"],
                    e(entry["label"]),
                )
            )
        chapter_html.append(
            """<li class="chapter" data-open="{open}">
  <h2>
    <button type="button" class="chapter__header" aria-expanded="{open}"
            aria-controls="panel-{slug}">
      <svg class="chapter__icon" width="26" height="26" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8"
           stroke-linecap="round" stroke-linejoin="round"
           aria-hidden="true">{icon}</svg>
      <span class="chapter__title">{chapter_word} {num}: {title}</span>
      <span class="check" data-check-all="{ids}"></span>
      {chevron}
    </button>
  </h2>
  <div class="chapter__panel" id="panel-{slug}">
    <ul class="slide-list">{links}</ul>
  </div>
</li>""".format(
                open="true" if chapter["number"] == 1 else "false",
                slug=chapter["slug"],
                icon=CHAPTER_ICONS[chapter["icon"]],
                chapter_word=e(ui["chapter"]),
                num=chapter["number"],
                title=e(chapter["title"]),
                ids=",".join(ids),
                chevron=CHEVRON,
                links="".join(links),
            )
        )

    home_main = """<div class="layout">
<div>
  <div class="intro-panel">
    <h1>{label}</h1>
    <p>{intro}</p>
  </div>
  <ul class="chapter-list">
{chapters}
  </ul>
</div>
{sidebar}
</div>""".format(
        label=e(module_label),
        intro=e(module["intro"]),
        chapters="\n".join(chapter_html),
        sidebar=sidebar(ui, total),
    )

    assets = "../" * lang_root.count("/")
    with open(os.path.join(out_root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(
            shell(
                ui,
                title="%s | RealRisks" % module_label,
                assets=assets,
                links="",
                toggle=toggle_href(lang_root, "index.html", other_root),
                body_attrs='data-total-slides="%d" data-all-slide-ids="%s" %s'
                % (total, all_ids, progress_attrs(ui)),
                breadcrumb=crumbs("", [(module["title"], None)]),
                main=home_main,
                description=module["intro"],
            )
        )

    # --- Slide pages ------------------------------------------------------
    for position, entry in enumerate(flat):
        slide = entry["slide"]
        chapter = entry["chapter"]
        links = "../"
        assets = "../" * (lang_root + entry["path"]).count("/")

        blocks = render_blocks(slide["blocks"], {"assets": assets, "ui": ui})
        media = slide.get("media") or []
        if media:
            figures = []
            for m in media:
                caption = (
                    "<figcaption>%s</figcaption>" % e(m["caption"])
                    if m.get("caption")
                    else ""
                )
                figures.append(
                    '<figure><img src="%sassets/img/%s" alt="%s">%s</figure>'
                    % (assets, e(m["src"]), e(m["alt"]), caption)
                )
            body = (
                '<div class="slide__body is-split">'
                '<div class="slide__col">%s</div>'
                '<div class="slide__col slide__media">%s</div></div>'
                % (blocks, "".join(figures))
            )
        else:
            body = '<div class="slide__body">%s</div>' % blocks

        subtitle = (
            '<span class="slide__subtitle">%s</span>' % e(slide["subtitle"])
            if slide.get("subtitle")
            else ""
        )

        prev_entry = flat[position - 1] if position > 0 else None
        next_entry = flat[position + 1] if position < total - 1 else None

        prev_link = (
            '<a class="btn" rel="prev" href="%s%s">%s</a>'
            % (links, prev_entry["path"], e(ui["back"]))
            if prev_entry
            else '<a class="btn" rel="prev" href="%sindex.html">%s</a>'
            % (links, e(ui["back"]))
        )
        next_link = (
            '<a class="btn btn--next btn--primary" rel="next" href="%s%s">%s</a>'
            % (links, next_entry["path"], e(ui["next"]))
            if next_entry
            else '<a class="btn btn--next btn--primary" rel="next" '
            'href="%sindex.html">%s</a>' % (links, e(ui["finish"]))
        )

        count_text = ui["slideCount"].format(
            n=entry["index"], total=len(chapter["slides"]), ch=chapter["number"]
        )

        slide_main = """<div class="slide">
  <h1 class="slide__title">{title}{subtitle}</h1>
  {body}
  <nav class="slide-nav" aria-label="Slide navigation">
    {prev}
    <p class="slide-nav__count">{count_text}</p>
    {next}
  </nav>
</div>""".format(
            title=e(slide["title"]),
            subtitle=subtitle,
            body=body,
            prev=prev_link,
            next=next_link,
            count_text=e(count_text),
        )

        trail = [
            (ui["home"], "index.html"),
            (module["title"], "index.html"),
            ("%s %d: %s" % (ui["chapter"], chapter["number"], chapter["title"]), None),
        ]

        with open(os.path.join(out_root, entry["path"]), "w", encoding="utf-8") as fh:
            fh.write(
                shell(
                    ui,
                    title="%s | %s | RealRisks" % (slide["title"], chapter["title"]),
                    assets=assets,
                    links=links,
                    toggle=toggle_href(lang_root, entry["path"], other_root),
                    body_attrs='data-slide-id="%s" data-total-slides="%d" '
                    'data-all-slide-ids="%s" %s'
                    % (entry["id"], total, all_ids, progress_attrs(ui)),
                    breadcrumb=crumbs(links, trail),
                    main=slide_main,
                    description="%s — %s" % (slide["title"], module_label),
                )
            )

    return total


def build():
    # Every language must offer the same pages, or a toggle would 404.
    shapes = {}
    for lang in LANGUAGES:
        with open(os.path.join(ROOT, "content", lang["content"]), encoding="utf-8") as fh:
            data = json.load(fh)
        shapes[lang["code"]] = [
            (c["slug"], len(c["slides"])) for c in data["chapters"]
        ]
    reference = shapes[LANGUAGES[0]["code"]]
    for code, shape in shapes.items():
        if shape != reference:
            raise SystemExit(
                "Language %r has a different slide structure: %r vs %r"
                % (code, shape, reference)
            )

    # The home-page menus must also line up, or one language quietly offers
    # fewer entries than the other and some slides drop out of its menu.
    menus = {}
    for lang in LANGUAGES:
        with open(os.path.join(ROOT, "content", lang["content"]), encoding="utf-8") as fh:
            data = json.load(fh)
        menus[lang["code"]] = [
            (c["slug"], len(menu_entries(c))) for c in data["chapters"]
        ]
    reference_menu = menus[LANGUAGES[0]["code"]]
    for code, shape in menus.items():
        if shape != reference_menu:
            raise SystemExit(
                "Language %r has a different menu shape: %r vs %r"
                % (code, shape, reference_menu)
            )

    for lang in LANGUAGES:
        other = next(l for l in LANGUAGES if l["code"] != lang["code"])
        total = build_language(lang, other["root"])
        print("Built %s: %d slide pages + index.html" % (lang["code"], total))


if __name__ == "__main__":
    build()
