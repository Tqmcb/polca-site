"""Build static guides from an editorial catalog entry and its Markdown article."""
from datetime import date, datetime, time
from html import escape
import json
import re
from zoneinfo import ZoneInfo

from lxml import html
from markdown import Markdown


ORIGIN = "https://polca.org.pl"


def timestamp(value):
    return datetime.combine(date.fromisoformat(value[:10]), time.min, ZoneInfo("Europe/Warsaw")).isoformat()


def markdown_source(entry, source):
    md = Markdown(extensions=["meta", "tables", "attr_list", "toc"],
                  extension_configs={"toc": {"toc_depth": "2-2"}})
    content = md.convert(source)
    fields = md.Meta
    image = fields.get("image", [None])[0]
    published = entry["published_at"]
    updated = fields.get("updated", [published])[0]
    title = entry["title"]
    url = ORIGIN + entry["href"]
    graph = [
        {"@type": "BlogPosting", "@id": url, "url": url, "headline": title,
         "description": entry["description"], "inLanguage": "pl-PL",
         **({"image": ORIGIN + image} if image else {}),
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
    image_url = escape(ORIGIN + image) if image else ""
    og_image = f'<meta property="og:image" content="{image_url}">' if image else ""
    twitter_image = f'<meta name="twitter:image" content="{image_url}">' if image else ""
    head = f'''<meta property="og:locale" content="pl_PL">{og_image}
<meta property="article:published_time" content="{timestamp(published)}"><meta property="article:modified_time" content="{timestamp(updated)}">
<meta name="twitter:card" content="{'summary_large_image' if image else 'summary'}"><meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(entry['description'])}">{twitter_image}
<script type="application/ld+json">{schema}</script>'''
    article = html.Element("body")
    article.append(html.fragment_fromstring(f"<h1>{escape(title)}</h1>"))
    prose = html.fragment_fromstring(content, create_parent="div")
    prose.set("class", "article-prose")
    lead = prose.find("p")
    lead.set("class", "article-lead")
    article.append(lead)
    if image:
        article.append(html.fragment_fromstring(
            f'<figure class="article-figure"><img src="{escape(image)}" alt="" loading="lazy"></figure>'))
    findings = html.Element("ol", {"class": "article-findings"})
    excerpts = fields.get("findings")
    if not excerpts:
        paragraphs = [lead, *reversed(prose.xpath(".//p"))]
        sentences = [sentence for p in paragraphs for sentence in
                     re.split(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ])", p.text_content().strip()) if sentence]
        excerpts = list(dict.fromkeys(sentences))[:3]
    for sentence in excerpts:
        item = html.Element("li")
        item.text = sentence
        findings.append(item)
    article.extend([findings, prose])
    return article, head, updated
