"""Build static guides from an editorial catalog entry and its Markdown article."""
from datetime import date, datetime, time
from html import escape
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from markdown import Markdown


ORIGIN = "https://polca.org.pl"
MONTHS = "stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia".split()


def date_label(value):
    day = date.fromisoformat(value)
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def timestamp(value):
    return datetime.combine(date.fromisoformat(value), time.min, ZoneInfo("Europe/Warsaw")).isoformat()


def build(root, resources, page, crumb):
    directory = root / "content/articles"
    for entry in resources:
        source = directory / (Path(entry["href"]).stem + ".md")
        if entry["kind"] == "article" and source.is_file():
            render(entry, source.read_text(encoding="utf-8"), page, crumb)


def render(entry, source, page, crumb):
    md = Markdown(extensions=["meta", "tables", "attr_list", "toc"],
                  extension_configs={"toc": {"toc_depth": "2-2"}})
    content = md.convert(source)
    fields = md.Meta
    image = fields["image"][0]
    updated = fields["updated"][0]
    published = entry["published_at"]
    title = entry["title"]
    url = ORIGIN + entry["href"]
    toc = "".join(
        f'<li><a href="#{escape(token["id"])}">{escape(token["name"])}</a></li>'
        for token in md.toc_tokens
    )
    byline = "Redakcja poLCA"
    graph = [
        {"@type": "BlogPosting", "@id": url, "url": url, "headline": title,
         "description": entry["description"], "inLanguage": "pl-PL", "image": ORIGIN + image,
         "datePublished": timestamp(published), "dateModified": timestamp(updated),
         "author": {"@type": "Organization", "name": "poLCA — Polska Baza Danych LCA", "url": ORIGIN},
         "publisher": {"@type": "Organization", "name": "Multicert Sp. z o.o.", "url": ORIGIN,
                       "logo": {"@type": "ImageObject", "url": ORIGIN + "/favicon.svg"}},
         "isPartOf": {"@type": "Blog", "name": "Artykuły i wyjaśnienia", "url": ORIGIN + "/blog.html"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": link}
            for i, (name, link) in enumerate([
                ("Strona główna", ORIGIN + "/"), ("Artykuły i wyjaśnienia", ORIGIN + "/blog.html"),
                (title, url)], 1)]},
    ]
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", r"\u003c")
    head = f'''<link rel="stylesheet" href="/assets/article-guide.css?v=20261123">
<meta property="og:locale" content="pl_PL"><meta property="og:image" content="{escape(ORIGIN + image)}">
<meta property="article:published_time" content="{timestamp(published)}"><meta property="article:modified_time" content="{timestamp(updated)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(entry['description'])}"><meta name="twitter:image" content="{escape(ORIGIN + image)}">
<script type="application/ld+json">{schema}</script>'''
    body = f'''<article class="article-guide">
<header class="guide-cover"><img src="{escape(image)}" width="1280" height="853" alt="" fetchpriority="high">
<div class="guide-cover-inner">{crumb(fields['breadcrumb'][0], ("Artykuły i wyjaśnienia", "/blog.html"))}
<p class="guide-type">Przewodnik</p><h1>{escape(title)}</h1>
<div class="guide-byline"><span>{byline}</span><span>Opublikowano <time datetime="{published}">{date_label(published)}</time></span>
<span>Aktualizacja <time datetime="{updated}">{date_label(updated)}</time></span></div></div></header>
<div class="guide-layout">
<nav class="guide-toc guide-toc-mobile" aria-label="Spis treści artykułu"><details><summary>Spis treści</summary><ul>{toc}</ul></details></nav>
<div class="guide-prose">{content}</div>
<nav class="guide-toc guide-toc-desktop" aria-label="Spis treści artykułu"><p>Spis treści</p><ul>{toc}</ul></nav>
</div></article>'''
    page(entry["href"].lstrip("/"), title, entry["description"], body, head_extra=head,
         pagehead=False, main_class="guide-main", show_crumb=False, og_type="article")
