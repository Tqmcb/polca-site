"""Render the same poLCA article layout for editorial HTML and Markdown sources."""
from datetime import date
from html import escape
import json
from math import ceil
from pathlib import Path
from urllib.parse import quote

from lxml import html
from markdown.extensions.toc import slugify

from article_guides import markdown_source
from concrete_portal import worked_example

ASSETS = '''<link rel="stylesheet" href="/assets/article.css?v=20261124c">
<script src="/assets/article.js?v=20261124b" defer></script>'''
AUTHOR = "Zespół poLCA"
ROLE = "Multicert, operator programu EPD Polska"


def markup(node):
    return html.tostring(node, encoding="unicode", with_tail=False)


def contents(node):
    return escape(node.text or "") + "".join(html.tostring(child, encoding="unicode") for child in node)


def normalized(node):
    return " ".join(node.text_content().split())


def related_articles(entry, resources):
    others = [r for r in resources if r["kind"] == "article" and r["href"] != entry["href"]]
    others.sort(key=lambda r: (r["href"].startswith("/blog-"),
                              r.get("reviewed_at") or r.get("published_at") or ""), reverse=True)
    matches = [r for r in others if r["category_id"] == entry["category_id"]]
    # Cement and asphalt have fewer than two other articles in their own categories.
    if len(matches) < 2 and entry["category_id"] in {"cement", "mma"}:
        matches.extend(r for r in others if r["category_id"] == "materialy")
    return matches[:3]


def prepare_prose(prose):
    used = set(prose.xpath('.//*[@id]/@id'))
    toc = []
    for heading in prose.iter("h2"):
        title = normalized(heading)
        if not heading.get("id"):
            stem = slugify(title.replace("ł", "l").replace("Ł", "L"), "-") or "sekcja"
            anchor = stem
            index = 2
            while anchor in used:
                anchor = f"{stem}-{index}"
                index += 1
            heading.set("id", anchor)
            used.add(anchor)
        toc.append(f'<li><a href="#{escape(heading.get("id"))}">{escape(title)}</a></li>')
    for table in prose.iter("table"):
        wrapper = table.getparent()
        if set(wrapper.classes).isdisjoint({"portal-table-wrap", "table-wrap", "article-table"}):
            wrapper = html.Element("div")
            table.addprevious(wrapper)
            wrapper.append(table)
        wrapper.set("class", "article-table")
        wrapper.set("tabindex", "0")
        wrapper.set("role", "region")
        label = table.xpath('string(caption)') or table.xpath('string(preceding::*[@class="card-title" or self::h2][1])')
        wrapper.set("aria-label", "Tabela" + (" — " + " ".join(label.split()) if label else ""))
    return "<ol>" + "".join(toc) + "</ol>"


def article_date(published, updated):
    day = date.fromisoformat((updated or published)[:10])
    label = "Zaktualizowano" if day.isoformat() != published[:10] else "Opublikowano"
    return f'<time datetime="{day.isoformat()}">{label} {day.day}.{day.month:02}.{day.year}</time>'


def article_layout(source, entry, editorial, crumb, published, updated):
    """The source contains editorial fields only. All navigation derives from the current content."""
    title = normalized(source.find("h1"))
    lead, = source.find_class("article-lead")
    prose, = source.find_class("article-prose")
    findings, = source.find_class("article-findings")
    count = len(findings.findall("li"))
    if not count:
        raise ValueError(f'Brak wniosków we wpisie {entry["href"]}')
    noun = "wniosków"
    if count == 1:
        noun = "wniosek"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        noun = "wnioski"
    values = "".join(map(markup, source.find_class("article-values")))
    notices = "\n".join(map(markup, source.find_class("legacy-note")))
    figure = "".join(map(markup, source.find_class("article-figure")))
    minutes = source.get("data-minutes") or max(1, ceil(len(normalized(prose).split()) / 200))
    category = editorial["categories"][entry["category_id"]]
    date_html = article_date(published, updated)
    toc = prepare_prose(prose)
    related = related_articles(entry, editorial["resources"])
    related_links = "".join(f'<li><a href="{escape(r["href"])}">{escape(r["title"])}</a></li>' for r in related)
    tools = source.find_class("article-tools")
    resource = contents(tools[0]) if tools else '<a href="/datasety.html">Katalog danych</a>'
    url = "https://polca.org.pl" + entry["href"]
    encoded = quote(url, safe="")
    email = f'mailto:?subject={quote(title, safe="")}&amp;body={encoded}'
    return f'''{crumb(title, ("Artykuły i wyjaśnienia", "/blog.html"))}
<div class="reading-progress" aria-hidden="true"></div>
<article class="portal-post">
<header class="article-header">
<p class="article-category">{escape(category)}</p>
<h1>{escape(title)}</h1>
{markup(lead)}
<div class="article-meta"><strong>{AUTHOR}</strong><span aria-hidden="true">|</span>{date_html}<span aria-hidden="true">|</span><span>{minutes} min czytania</span></div>
</header>
{notices}
<div class="article-grid">
<div class="article-main">
<section class="article-summary" aria-label="W skrócie">
<p class="article-label">W skrócie · {count} {noun}</p>
{markup(findings)}
{values}
</section>
<details class="article-mobile-toc"><summary>W tym artykule</summary><nav aria-label="W tym artykule">{toc}</nav></details>
{figure}
{markup(prose)}
<footer class="article-end">
<div class="article-share" role="group" aria-label="Udostępnij artykuł">
<strong>Udostępnij artykuł</strong>
<a href="https://www.linkedin.com/sharing/share-offsite/?url={encoded}" rel="nofollow noopener" target="_blank">LinkedIn</a>
<a href="{email}">E-mail</a><button type="button" data-copy-url="{escape(url)}" hidden>Kopiuj link</button>
<span role="status"></span></div>
<div class="article-return"><a href="/blog.html">← Wszystkie artykuły</a>{date_html}</div>
</footer>
</div>
<aside class="article-sidebar" aria-label="Informacje o artykule">
<nav class="article-desktop-toc" aria-label="W tym artykule"><p class="article-label">W tym artykule</p>{toc}</nav>
<div class="article-author"><span class="article-initials" aria-hidden="true">ZP</span><div><p class="article-label">Autor</p><strong>{AUTHOR}</strong><p>{ROLE}</p></div></div>
<div class="article-resource">{resource}</div>
<nav class="article-related" aria-label="Powiązane artykuły"><p class="article-label">Powiązane artykuły</p><ul>{related_links}</ul></nav>
</aside>
</div>
</article>'''


def build(root, catalog, page, crumb):
    editorial = json.loads((root / "data/portal-editorial.json").read_text())
    directory = root / "content/articles"
    for entry in editorial["resources"]:
        path = entry["href"].removeprefix("/")
        if entry["kind"] != "article" or not path.startswith("blog-"):
            continue
        md = directory / Path(path).with_suffix(".md")
        template = directory / (path + ".tpl")
        if md.is_file():
            source, extra, updated = markdown_source(entry, md.read_text())
            head = None
        else:
            raw = template.read_text()
            if "<!-- concrete-example -->" in raw:
                raw = raw.replace("<!-- concrete-example -->", worked_example(catalog))
            doc = html.document_fromstring(raw)
            source = doc.find("body")
            head = contents(doc.find("head"))
            extra = ""
            updated = None
            for script in doc.xpath('//head/script[@type="application/ld+json"]'):
                schema = json.loads(script.text)
                for node in schema.get("@graph", [schema]):
                    if node.get("@type") == "BlogPosting":
                        updated = node.get("dateModified")
        body = article_layout(source, entry, editorial, crumb, entry["published_at"], updated)
        page(path, normalized(source.find("h1")), entry["description"], body, head_extra=extra + ASSETS,
             head_metadata=head, pagehead=False, show_crumb=False, og_type="article",
             main_class="portal-shell portal-main article-page")
