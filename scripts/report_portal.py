"""Render the public LCA report and its byte-exact Markdown download."""
from __future__ import annotations

import hashlib
import html
import json
import re

from lxml import etree, html as document
from markdown import Markdown


PAGE = "konsultacje/energia-polska-2025-raport-lca.html"
CONSULTATION_PAGE = "/konsultacje/energia-polska-2025.html"
SOURCE = "content/raport-lca-energia-2025.md"
DATA = "data/konsultacje/raport-lca-2025"
DOWNLOAD = "RAPORT-LCA-PL2025-0.3.md"
VERSION = "0.3"
PUBLISHED = "2026-10-26"
DESCRIPTION = (
    "Projekt raportu oceny cyklu życia energii elektrycznej w Polsce w 2025 r. "
    "Wersja 0.3, wyniki, metoda i ograniczenia do konsultacji."
)
STATUS = (
    "Projekt raportu, wersja 0.3 z 26.10.2026. "
    "Raport nie przeszedł jeszcze przeglądu krytycznego przez niezależnego eksperta. "
    "Kontrole wykonane narzędziami sztucznej inteligencji (Claude, Codex) nie zastępują tego przeglądu. "
    "Dane nie zostały przyjęte do wydawanych deklaracji w programie EPD Polska."
)


def render_markdown(source):
    """Keep source text intact; accept lists immediately following a paragraph."""
    lines = []
    for line in source.splitlines():
        if (re.match(r"^(?:[-+*]|\d+\.)\s+", line) and lines and lines[-1].strip()
                and not re.match(r"^(?:[-+*]|\d+\.)\s+", lines[-1])):
            lines.append("")
        lines.append(line)
    renderer = Markdown(
        extensions=["tables", "toc", "sane_lists"],
        extension_configs={"toc": {"toc_depth": "2-2"}},
    )
    body = document.fragment_fromstring(renderer.convert("\n".join(lines)), create_parent="div")
    headings = body.xpath("./h1")
    if len(headings) != 1 or body[0] is not headings[0]:
        raise ValueError("Raport musi zaczynać się jednym nagłówkiem pierwszego poziomu")
    heading = headings[0]
    title = heading.text_content()
    heading_html = etree.tostring(heading, encoding="unicode", method="html", with_tail=False)
    body.remove(heading)
    for index, table in enumerate(body.xpath(".//table"), 1):
        wrapper = etree.Element(
            "div", {"class": "consult-report-table-wrap", "tabindex": "0", "role": "region",
                    "aria-label": f"Tabela w raporcie — przewijana poziomo (obszar {index})"},
        )
        table.addprevious(wrapper)
        wrapper.append(table)
        for cell in table.xpath("./thead/tr/th"):
            cell.set("scope", "col")
    content = "".join(
        etree.tostring(node, encoding="unicode", method="html") for node in body
    )
    return title, heading_html, renderer.toc, content


def build(api):
    root, page = api["ROOT"], api["page"]
    payload = (root / SOURCE).read_bytes()
    title, heading, toc, content = render_markdown(payload.decode("utf-8"))
    destination = root / DATA
    destination.mkdir(parents=True, exist_ok=True)
    (destination / DOWNLOAD).write_bytes(payload)
    manifest = {
        "version": VERSION,
        "date": PUBLISHED,
        "hash_algorithm": "SHA-256",
        "files": {DOWNLOAD: {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}},
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    report = {
        "@context": "https://schema.org",
        "@type": "Report",
        "name": title,
        "description": DESCRIPTION,
        "datePublished": PUBLISHED,
        "publisher": {"@type": "Organization", "name": "Multicert Sp. z o.o."},
        "inLanguage": "pl",
        "version": VERSION,
        "url": "https://polca.org.pl/" + PAGE,
    }
    head = (
        '<link rel="stylesheet" href="/assets/report.css?v=20261026">'
        '<meta property="og:locale" content="pl_PL">'
        '<meta name="twitter:card" content="summary">'
        f'<meta name="twitter:title" content="{html.escape(title, quote=True)} — poLCA">'
        f'<meta name="twitter:description" content="{html.escape(DESCRIPTION, quote=True)}">'
        f'<meta name="twitter:url" content="https://polca.org.pl/{PAGE}">'
        '<script type="application/ld+json">'
        + json.dumps(report, ensure_ascii=False).replace("<", "\\u003c") + "</script>"
    )
    body = f'''<article class="consult-report">
<header class="portal-pagehead">{heading}</header>
<aside class="consult-report-status" id="status-raportu" aria-label="Status raportu">
  <p><strong>{html.escape(STATUS.split('. ', 1)[0])}.</strong> {html.escape(STATUS.split('. ', 1)[1])}</p>
  <p><a href="{CONSULTATION_PAGE}">Przejdź do konsultacji modelu</a> · <a href="{CONSULTATION_PAGE}#zglos-uwage">Zgłoś uwagę przez formularz</a></p>
</aside>
<ul class="consult-report-downloads">
  <li><a href="/{DATA}/{DOWNLOAD}" download>Pobierz raport — Markdown, wersja 0.3</a></li>
  <li><a href="/{DATA}/manifest.json" download>Pobierz manifest — SHA-256 i rozmiar pliku (JSON)</a></li>
</ul>
<nav class="consult-report-toc" aria-label="Spis treści raportu"><h2>Spis treści</h2>{toc}</nav>
<p class="consult-report-hint">Na małym ekranie tabele można przewijać w poziomie. Obszary tabel są dostępne także z klawiatury.</p>
<div class="consult-report-content">{content}</div>
</article>'''
    page(
        PAGE, title, DESCRIPTION, body,
        parent=("Konsultacje modelu", CONSULTATION_PAGE),
        head_extra=head, pagehead=False,
    )
