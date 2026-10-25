"""Verify the report against its source, download and frozen consultation package."""
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("report_under_test", ROOT / "scripts/report_portal.py")
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def normalize(text):
    return " ".join(text.split())


def inline_text(text):
    return text.replace("**", "").replace("*", "").replace("`", "")


def source_text(source):
    """Independent plain-text reading of the formatting used by this source."""
    result = []
    for line in source.splitlines():
        if re.fullmatch(r"[|:\-\s]+", line):
            continue
        line = re.sub(r"^#{1,6}\s+|^\s*(?:[-+*]|\d+\.)\s+", "", line)
        if line.startswith("|"):
            line = " ".join(cell.strip() for cell in line.strip("|").split("|"))
        result.append(inline_text(line))
    return normalize("\n".join(result))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / REPORT.PAGE
        cls.doc = html.parse(str(cls.path))
        cls.source = (ROOT / REPORT.SOURCE).read_text(encoding="utf-8")
        cls.content = cls.doc.xpath("//*[@class='consult-report-content']")[0]

    def test_page_exists_with_portal_shell_and_machine_metadata(self):
        self.assertTrue(self.path.is_file())
        self.assertEqual(self.doc.getroot().get("lang"), "pl")
        self.assertEqual(len(self.doc.xpath("//header[@class='portal-header']")), 1)
        self.assertEqual(len(self.doc.xpath("//footer[@class='portal-footer']")), 1)
        self.assertEqual(len(self.doc.xpath("//h1")), 1)
        url = "https://polca.org.pl/" + REPORT.PAGE
        self.assertEqual(self.doc.xpath("//link[@rel='canonical']/@href"), [url])
        self.assertEqual(self.doc.xpath("//meta[@property='og:url']/@content"), [url])
        self.assertTrue(self.doc.xpath("//meta[@property='og:title']/@content"))
        self.assertTrue(self.doc.xpath("//meta[@property='og:description']/@content"))
        self.assertTrue(self.doc.xpath("//meta[@property='og:type']/@content"))
        self.assertEqual(self.doc.xpath("//meta[@name='twitter:card']/@content"), ["summary"])
        for field in ("title", "description", "url"):
            self.assertTrue(self.doc.xpath(f"//meta[@name='twitter:{field}']/@content"))
        self.assertLessEqual(len(self.doc.xpath("//meta[@name='description']/@content")[0]), 160)
        report = json.loads(self.doc.xpath("//script[@type='application/ld+json']")[0].text)
        self.assertEqual(report["@type"], "Report")
        self.assertEqual(report["name"], self.doc.xpath("//h1")[0].text_content())
        self.assertEqual(report["datePublished"], "2026-10-26")
        self.assertEqual(report["publisher"]["name"], "Multicert Sp. z o.o.")
        self.assertEqual(report["inLanguage"], "pl")

    def test_exact_status_is_visible_above_toc_and_links_to_consultation_and_form(self):
        status = self.doc.xpath("//*[@id='status-raportu']")[0]
        expected = (
            "Projekt raportu, wersja 0.3 z 26.10.2026. "
            "Raport nie przeszedł jeszcze przeglądu krytycznego przez niezależnego eksperta. "
            "Kontrole wykonane narzędziami sztucznej inteligencji (Claude, Codex) nie zastępują tego przeglądu. "
            "Dane nie zostały przyjęte do wydawanych deklaracji w programie EPD Polska."
        )
        self.assertEqual(normalize(status.xpath("./p")[0].text_content()), expected)
        self.assertFalse(status.xpath("ancestor-or-self::*[@hidden or @aria-hidden='true']"))
        toc = self.doc.xpath("//nav[@class='consult-report-toc']")[0]
        self.assertIs(status.getparent(), toc.getparent())
        self.assertLess(status.getparent().index(status), toc.getparent().index(toc))
        self.assertIn(REPORT.CONSULTATION_PAGE, status.xpath(".//a/@href"))
        self.assertIn(REPORT.CONSULTATION_PAGE + "#zglos-uwage", status.xpath(".//a/@href"))

    def test_all_source_sentences_and_numbers_are_preserved_in_order(self):
        visible = self.doc.xpath("//h1")[0].text_content() + "\n" + self.content.text_content()
        self.assertEqual(normalize(visible), source_text(self.source))
        # Check visible text, never attributes or embedded metadata, including exponents.
        numbers = set(re.findall(r"\d+(?:[.,]\d+)*(?:·10[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)?", self.source))
        for number in sorted(numbers):
            with self.subTest(number=number):
                self.assertIn(number, visible)

    def test_all_six_numbered_tables_and_every_cell_are_present(self):
        captions = self.content.xpath(".//p/strong")
        numbers = [int(match[1]) for item in captions
                   if (match := re.match(r"Tabela ([1-6])\.", item.text_content()))]
        self.assertCountEqual(numbers, range(1, 7))
        expected = []
        current = []
        for line in self.source.splitlines() + [""]:
            if line.startswith("|"):
                if not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", line):
                    current.append([inline_text(cell.strip()) for cell in line.strip("|").split("|")])
            elif current:
                expected.append(current)
                current = []
        tables = self.content.xpath(".//table")
        self.assertEqual(len(tables), len(expected))
        for index, (table, rows) in enumerate(zip(tables, expected), 1):
            actual = [[cell.text_content() for cell in row.xpath("./th|./td")]
                      for row in table.xpath("./thead/tr|./tbody/tr")]
            self.assertEqual(actual, rows, f"Table block {index}")
            wrapper = table.getparent()
            self.assertEqual(wrapper.get("class"), "consult-report-table-wrap")
            self.assertEqual(wrapper.get("tabindex"), "0")
            self.assertEqual(wrapper.get("role"), "region")
            self.assertIn("przewijana poziomo", wrapper.get("aria-label"))
        css = (ROOT / "assets/report.css").read_text()
        self.assertRegex(css, r"\.consult-report-table-wrap\s*\{[^}]*max-width:\s*100%[^}]*overflow-x:\s*auto")

    def test_toc_covers_all_second_level_headings_only(self):
        headings = self.content.xpath("./h2")
        expected = re.findall(r"^## (.+)$", self.source, re.M)
        self.assertEqual([heading.text_content() for heading in headings], expected)
        toc = self.doc.xpath("//nav[@class='consult-report-toc']")[0]
        self.assertEqual(toc.xpath(".//a/@href"), ["#" + heading.get("id") for heading in headings])
        self.assertEqual([item.text_content() for item in toc.xpath(".//a")], expected)

    def test_lists_bold_italic_and_inline_code_are_rendered_as_markup(self):
        self.assertTrue(self.content.xpath(".//ul/li"))
        self.assertEqual(len(self.content.xpath(".//ol/li")), 10)
        self.assertIn("available for final consumption", self.content.xpath(".//em/text()"))
        self.assertIn("PL2025_METHOD_CLOSURE_CANDIDATE", self.content.xpath(".//code/text()"))
        self.assertTrue(self.content.xpath(".//strong"))

    def test_markdown_download_is_byte_exact_and_matches_manifest(self):
        source = (ROOT / REPORT.SOURCE).read_bytes()
        directory = ROOT / REPORT.DATA
        self.assertEqual((directory / REPORT.DOWNLOAD).read_bytes(), source)
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertEqual(manifest["version"], "0.3")
        self.assertEqual(manifest["date"], "2026-10-26")
        self.assertEqual(manifest["hash_algorithm"], "SHA-256")
        self.assertEqual(manifest["files"], {
            REPORT.DOWNLOAD: {"sha256": hashlib.sha256(source).hexdigest(), "bytes": len(source)},
        })
        for filename in (REPORT.DOWNLOAD, "manifest.json"):
            self.assertIn("/" + REPORT.DATA + "/" + filename, self.doc.xpath("//a[@download]/@href"))

    def test_report_is_linked_and_indexed_without_claiming_expert_review(self):
        for name in ("energia-polska-2025.html", "energia-polska-2025-metoda.html"):
            doc = html.parse(str(ROOT / "konsultacje" / name))
            self.assertIn("/" + REPORT.PAGE, doc.xpath("//main//a/@href"))
        consultation = html.parse(str(ROOT / REPORT.CONSULTATION_PAGE.lstrip("/")))
        self.assertIn(
            "Raport z niezależnego krytycznego przeglądu eksperckiego nie jest jeszcze dostępny.",
            consultation.xpath("//*[@id='status']")[0].text_content(),
        )
        sitemap = etree.parse(str(ROOT / "sitemap.xml"))
        self.assertIn("https://polca.org.pl/" + REPORT.PAGE, sitemap.xpath("//*[local-name()='loc']/text()"))
        catalog = json.loads((ROOT / "data/portal-catalog.json").read_text())
        search = html.parse(str(ROOT / "szukaj.html"))
        search_records = json.loads(search.xpath("//*[@id='portal-search-data']")[0].text)
        for records in (catalog["resources"], search_records):
            matches = [row for row in records if row["href"] == "/" + REPORT.PAGE]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["status_id"], "consultation")

    def test_all_local_links_and_fragments_resolve(self):
        for href in self.doc.xpath("//@href|//@src"):
            url = urlsplit(href)
            if (url.scheme in ("mailto", "tel", "data", "javascript") or
                    url.netloc and url.netloc not in ("polca.org.pl", "www.polca.org.pl")):
                continue
            target = (ROOT / unquote(url.path).lstrip("/") if url.path.startswith("/") or url.netloc
                      else self.path.parent / unquote(url.path) if url.path else self.path)
            if target.is_dir():
                target /= "index.html"
            with self.subTest(href=href):
                self.assertTrue(target.is_file())
                if url.fragment and target.suffix == ".html":
                    self.assertIn(unquote(url.fragment), html.parse(str(target)).xpath("//@id|//@name"))

    def test_frozen_consultation_directory_is_byte_exact_including_manifest_and_zip(self):
        baseline = json.loads((ROOT / "tests/fixtures/consultation-energy-20261020-sha256.json").read_text())
        directory = ROOT / "data/konsultacje/energia-2025-20261020"
        current = {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(directory.rglob("*")) if path.is_file()}
        self.assertEqual(current, baseline)


if __name__ == "__main__":
    unittest.main()
