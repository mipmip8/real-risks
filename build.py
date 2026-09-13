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
CONTENT = os.path.join(ROOT, "content", "screening.json")

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


def e(text):
    """Escape a string for use in HTML text content."""
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------------------
# Block renderers
# ---------------------------------------------------------------------------


def r_text(b, _):
    return "<p>%s</p>" % e(b["text"])


def r_callout(b, _):
    return '<p class="callout">%s</p>' % e(b["text"])


def r_bullets(b, _):
    out = []
    if b.get("heading"):
        out.append('<h2 class="block-heading">%s</h2>' % e(b["heading"]))
    items = "".join("<li>%s</li>" % e(i) for i in b["items"])
    out.append('<ul class="bullets">%s</ul>' % items)
    return "<div>%s</div>" % "".join(out) if b.get("heading") else out[0]


def r_numbered(b, _):
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
            '<li><span class="compare__mark" aria-hidden="true">%s</span>'
            "<span><strong>%s</strong>%s</span></li>"
            % (mark, e(item["title"]), e(item["text"]))
        )
    return "".join(rows)


def r_compare(b, _):
    benefits, harms = b["benefits"], b["harms"]
    return (
        '<div class="compare">'
        '<section class="compare__col compare__col--benefits"><h2>%s</h2>'
        "<ul>%s</ul></section>"
        '<section class="compare__col compare__col--harms"><h2>%s</h2>'
        "<ul>%s</ul></section>"
        "</div>"
        % (
            e(benefits["heading"]),
            _compare_items(benefits["items"], "✓"),
            e(harms["heading"]),
            _compare_items(harms["items"], "⚠"),
        )
    )


def r_equation(b, depth):
    def fig(side):
        return (
            '<figure><img src="%sassets/img/%s" alt="%s" loading="lazy">'
            "<figcaption>%s</figcaption></figure>"
            % (depth, e(side["src"]), e(side["alt"]), e(side["label"]))
        )

    return (
        '<div><div class="equation">%s'
        '<div class="equation__sign" aria-hidden="true">=</div>%s</div>'
        '<p class="equation__caption">%s</p></div>'
        % (fig(b["left"]), fig(b["right"]), e(b["caption"]))
    )


def r_takeaways(b, _):
    items = "".join(
        '<li><span class="star" aria-hidden="true">★</span>'
        "<span>%s</span></li>" % e(i)
        for i in b["items"]
    )
    return '<ul class="takeaways">%s</ul>' % items


def r_cards(b, depth):
    items = "".join(
        '<li><figure><img src="%sassets/img/%s" alt="%s" loading="lazy">'
        "<figcaption>%s</figcaption></figure></li>"
        % (depth, e(i["src"]), e(i["alt"]), e(i["title"]))
        for i in b["items"]
    )
    return '<ul class="cards">%s</ul>' % items


def r_steps(b, depth):
    items = []
    for step in b["items"]:
        bullets = "".join("<li>%s</li>" % e(x) for x in step["items"])
        items.append(
            '<li><h2>%s</h2><img src="%sassets/img/%s" alt="%s" loading="lazy">'
            "<ul>%s</ul></li>"
            % (e(step["title"]), depth, e(step["src"]), e(step["alt"]), bullets)
        )
    return '<ol class="steps">%s</ol>' % "".join(items)


def r_qablocks(b, _):
    items = "".join(
        "<div><dt>%s</dt><dd>%s</dd></div>" % (e(i["q"]), e(i["a"]))
        for i in b["items"]
    )
    return '<dl class="qablocks">%s</dl>' % items


def r_table(b, _):
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


def r_birads(b, _):
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


def r_answer(b, _):
    notes = "".join("<p>%s</p>" % e(n) for n in b["notes"])
    return (
        '<div class="answer"><p class="answer__value">%s</p>'
        '<div class="answer__notes">%s</div></div>' % (e(b["answer"]), notes)
    )


def r_twocol(b, _):
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


def r_schedule(b, _):
    cols = []
    for col in b["columns"]:
        title = "<h2>%s</h2>" % e(col["title"]) if col.get("title") else ""
        items = "".join("<li>%s</li>" % e(i) for i in col["items"])
        cols.append(
            '<section class="schedule__col">%s<ul>%s</ul></section>' % (title, items)
        )
    return '<div class="schedule">%s</div>' % "".join(cols)


def r_factcards(b, _):
    items = []
    for i in b["items"]:
        title = "<strong>%s</strong>" % e(i["title"]) if i.get("title") else ""
        items.append("<li>%s%s</li>" % (title, e(i["text"])))
    return '<ul class="factcards">%s</ul>' % "".join(items)


RENDERERS = {
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


def render_blocks(blocks, depth):
    out = []
    for block in blocks:
        renderer = RENDERERS.get(block["type"])
        if renderer is None:
            raise SystemExit("Unknown block type: %s" % block["type"])
        out.append(renderer(block, depth))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------


def shell(title, depth, body_attrs, breadcrumb, main, description):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,400;0,600;0,700;0,900;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{depth}assets/css/styles.css">
<link rel="icon" href="{depth}assets/img/favicon.svg" type="image/svg+xml">
</head>
<body {body_attrs}>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="site-header__inner">
    <a class="logo" href="{depth}index.html">
      {logo}<span><span class="logo__real">REAL</span>RISKS</span>
    </a>
    <nav class="site-nav" aria-label="Main">
      <a href="{depth}index.html">Module home</a>
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
    <p><strong>This website is for education only.</strong> It does not give
    medical advice and is not a substitute for talking with your own doctor
    about your breast cancer risk and screening plan.</p>
    <p>Your progress is saved only in this browser. Clearing your browser data
    will reset it.</p>
  </div>
</footer>
<script src="{depth}assets/js/progress.js"></script>
</body>
</html>
""".format(
        title=e(title),
        description=e(description),
        depth=depth,
        body_attrs=body_attrs,
        logo=LOGO,
        breadcrumb=breadcrumb,
        main=main,
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


def sidebar(module, total):
    return """<aside class="sidebar">
  <h2>Accomplishments</h2>
  <div class="accomplishments">
    <div class="progress-track"><div class="progress-fill"></div></div>
    <p class="progress-count">0 / {total}</p>
    <p>Work through each section to complete this module!</p>
    <button type="button" class="reset-progress">Reset my progress</button>
  </div>
</aside>""".format(total=total)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build():
    with open(CONTENT, encoding="utf-8") as fh:
        data = json.load(fh)

    module = data["module"]
    chapters = data["chapters"]

    # Flat, ordered list of every slide plus its neighbours.
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
    module_label = "Module %d: %s" % (module["number"], module["title"])

    # --- Clean previously generated chapter directories -------------------
    for chapter in chapters:
        out_dir = os.path.join(ROOT, chapter["slug"])
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

    # --- Home page --------------------------------------------------------
    chapter_html = []
    for chapter in chapters:
        ids = [s["id"] for s in flat if s["chapter"] is chapter]
        links = []
        for index, slide in enumerate(chapter["slides"], 1):
            sid = "%s-%d" % (chapter["slug"], index)
            label = slide["title"]
            if slide.get("subtitle"):
                label += " (%s)" % slide["subtitle"]
            links.append(
                '<li><span class="check" data-check-slide="%s"></span>'
                '<a href="%s/slide-%d.html">%s</a></li>'
                % (sid, chapter["slug"], index, e(label))
            )
        icon = CHAPTER_ICONS[chapter["icon"]]
        chapter_html.append(
            """<li class="chapter" data-open="{open}">
  <h2>
    <button type="button" class="chapter__header" aria-expanded="{open}"
            aria-controls="panel-{slug}">
      <svg class="chapter__icon" width="26" height="26" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8"
           stroke-linecap="round" stroke-linejoin="round"
           aria-hidden="true">{icon}</svg>
      <span class="chapter__title">Chapter {num}: {title}</span>
      <span class="check" data-check-chapter="{ids}"></span>
      {chevron}
    </button>
  </h2>
  <div class="chapter__panel" id="panel-{slug}">
    <ul class="slide-list">{links}</ul>
  </div>
</li>""".format(
                open="true" if chapter["number"] == 1 else "false",
                slug=chapter["slug"],
                icon=icon,
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
        sidebar=sidebar(module, total),
    )

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(
            shell(
                title="%s | RealRisks" % module_label,
                depth="",
                body_attrs='data-total-slides="%d" data-all-slide-ids="%s"'
                % (total, all_ids),
                breadcrumb=crumbs("", [(module["title"], None)]),
                main=home_main,
                description=module["intro"],
            )
        )

    # --- Slide pages ------------------------------------------------------
    for position, entry in enumerate(flat):
        slide = entry["slide"]
        chapter = entry["chapter"]
        depth = "../"

        blocks = render_blocks(slide["blocks"], depth)
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
                    % (depth, e(m["src"]), e(m["alt"]), caption)
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
            '<a class="btn" rel="prev" href="%s%s">Back</a>'
            % (depth, prev_entry["path"])
            if prev_entry
            else '<a class="btn" rel="prev" href="%sindex.html">Back</a>' % depth
        )
        next_link = (
            '<a class="btn btn--next btn--primary" rel="next" href="%s%s">Next</a>'
            % (depth, next_entry["path"])
            if next_entry
            else '<a class="btn btn--next btn--primary" rel="next" '
            'href="%sindex.html">Finish module</a>' % depth
        )

        slide_main = """<div class="slide">
  <h1 class="slide__title">{title}{subtitle}</h1>
  {body}
  <nav class="slide-nav" aria-label="Slide navigation">
    {prev}
    <p class="slide-nav__count">Slide {n} of {count} in Chapter {cnum}</p>
    {next}
  </nav>
</div>""".format(
            title=e(slide["title"]),
            subtitle=subtitle,
            body=body,
            prev=prev_link,
            next=next_link,
            n=entry["index"],
            count=len(chapter["slides"]),
            cnum=chapter["number"],
        )

        trail = [
            ("Home", "index.html"),
            (module["title"], "index.html"),
            ("Chapter %d: %s" % (chapter["number"], chapter["title"]), None),
        ]

        with open(os.path.join(ROOT, entry["path"]), "w", encoding="utf-8") as fh:
            fh.write(
                shell(
                    title="%s | %s | RealRisks" % (slide["title"], chapter["title"]),
                    depth=depth,
                    body_attrs='data-slide-id="%s" data-total-slides="%d" '
                    'data-all-slide-ids="%s"' % (entry["id"], total, all_ids),
                    breadcrumb=crumbs(depth, trail),
                    main=slide_main,
                    description="%s — %s" % (slide["title"], module_label),
                )
            )

    print("Built %d slide pages + index.html" % total)


if __name__ == "__main__":
    build()
