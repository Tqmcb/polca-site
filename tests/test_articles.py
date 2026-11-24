"""Article layout, source fidelity and optional comparison to a pre-migration HTML directory."""
import json
import os
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

from lxml import html
from markdown import Markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from concrete_portal import worked_example


def text(nodes):
    # Normalize HTML whitespace, including line breaks between adjacent table cells.
    return " ".join(" ".join(t.split()) for node in nodes for t in node.itertext() if t.strip())


class ArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = sorted(ROOT.glob("blog-*.html"))
        cls.editorial = json.loads((ROOT / "data/portal-editorial.json").read_text())
        cls.records = {r["href"]: r for r in cls.editorial["resources"]}
        cls.catalog = json.loads((ROOT / "data/portal-catalog.json").read_text())

    def test_layout_for_every_post(self):
        self.assertEqual({"/" + p.name for p in self.pages},
                         {url for url in self.records if url.startswith("/blog-")})
        for path in self.pages:
            with self.subTest(page=path.name):
                doc = html.fromstring(path.read_text())
                article, = doc.xpath('//main/article')
                header, = article.xpath('./header')
                title, = header.xpath('./h1')
                crumbs, = doc.find_class("portal-breadcrumbs")
                self.assertEqual(crumbs.xpath('a/@href'), ["/", "/blog.html"])
                self.assertEqual(crumbs.xpath('a/text()'), ["Strona główna", "Artykuły i wyjaśnienia"])
                self.assertEqual(crumbs.xpath('string(*[@aria-current="page"])'), title.text_content())
                meta, = header.find_class("article-meta")
                self.assertEqual(meta.xpath('string(strong)'), "Zespół poLCA")
                self.assertRegex(meta.xpath('string(time)'), r'^(Opublikowano|Zaktualizowano) \d{1,2}\.\d{2}\.\d{4}$')
                self.assertRegex(meta.text_content(), r'[1-9]\d* min czytania$')
                self.assertTrue(header.find_class("article-category")[0].text_content().strip())
                self.assertTrue(header.find_class("article-lead")[0].text_content().strip())
                summary, = article.find_class("article-summary")
                n = len(summary.xpath('./ol/li'))
                self.assertGreater(n, 0)
                self.assertIn(f'W skrócie · {n} ', summary.xpath('string(p)'))
                mobile, = article.find_class("article-mobile-toc")
                self.assertIs(mobile.getprevious(), summary)
                self.assertEqual(mobile.tag, "details")
                self.assertEqual(mobile.xpath('string(summary)'), "W tym artykule")

                sidebar, = article.xpath('.//aside[@class="article-sidebar"]')
                self.assertIn("Multicert, operator programu EPD Polska", text(sidebar.find_class("article-author")))
                self.assertTrue(sidebar.find_class("article-resource")[0].xpath('.//a[@href]'))
                sections = [(h.get("id"), text([h])) for h in article.iter("h2")]
                self.assertGreater(len(sections), 0)
                self.assertEqual(len({anchor for anchor, _ in sections}), len(sections))
                for toc in (mobile, sidebar.find_class("article-desktop-toc")[0]):
                    self.assertEqual([(a.get("href"), text([a])) for a in toc.iter("a")],
                                     [("#" + anchor, title) for anchor, title in sections])
                related = sidebar.find_class("article-related")[0].xpath('.//a/@href')
                self.assertIn(len(set(related)), (2, 3))
                self.assertNotIn("/" + path.name, related)
                self.assertTrue(all(self.records[url]["kind"] == "article" for url in related))

                share, = article.find_class("article-share")
                canonical = doc.xpath('string(//link[@rel="canonical"]/@href)')
                self.assertEqual(share.xpath('string(button/@data-copy-url)'), canonical)
                linkedin, email = (urlsplit(url) for url in share.xpath('a/@href'))
                self.assertEqual(linkedin.hostname, "www.linkedin.com")
                self.assertEqual(parse_qs(linkedin.query)["url"], [canonical])
                self.assertEqual(email.scheme, "mailto")
                self.assertEqual(parse_qs(email.query)["body"], [canonical])
                self.assertEqual(article.find_class("article-return")[0].xpath('string(a/@href)'), "/blog.html")
                self.assertEqual(article.xpath('.//table[not(parent::div[@class="article-table"])]'), [])
                for faq in article.find_class("faq-item"):
                    self.assertEqual((faq.tag, faq[0].tag), ("details", "summary"))
                self.assertEqual(len(doc.find_class("portal-header")), 1)
                self.assertEqual(len(doc.find_class("portal-footer")), 1)

    def test_published_text_matches_article_sources(self):
        for path in self.pages:
            with self.subTest(page=path.name):
                doc = html.fromstring(path.read_text())
                source = ROOT / "content/articles" / (path.name + ".tpl")
                if source.exists():
                    raw = source.read_text()
                    if "<!-- concrete-example -->" in raw:
                        raw = raw.replace("<!-- concrete-example -->", worked_example(self.catalog))
                    before = html.fromstring(raw)
                    for field in ("article-lead", "article-prose", "article-findings",
                                  "article-values", "legacy-note"):
                        self.assertEqual(text(before.find_class(field)), text(doc.find_class(field)), field)
                    for selector in ('//head/meta', '//head/link[@rel="canonical"]',
                                     '//head/script[@type="application/ld+json"]'):
                        self.assertEqual([(n.attrib, n.text) for n in before.xpath(selector)],
                                         [(n.attrib, n.text) for n in doc.xpath(selector)])
                else:
                    md = Markdown(extensions=["meta", "tables", "attr_list", "toc"])
                    before = html.fragment_fromstring(md.convert(source.with_suffix("").with_suffix(".md").read_text()),
                                                      create_parent="div")
                    self.assertEqual(text([before]), text(doc.find_class("article-lead") + doc.find_class("article-prose")))

    @unittest.skipUnless(os.getenv("POLCA_ARTICLE_BASELINE"), "Optional pre-migration directory")
    def test_against_original_html(self):
        """Compare the original editorial blocks in order, excluding replaced navigation."""
        baseline = Path(os.environ["POLCA_ARTICLE_BASELINE"])
        for path in self.pages:
            with self.subTest(page=path.name):
                old = html.fromstring((baseline / path.name).read_text())
                new = html.fromstring(path.read_text())
                if old.find_class("guide-prose"):
                    blocks = old.find_class("guide-prose")
                    lead = blocks[0].find("p")
                    self.assertEqual(text([lead]), text(new.find_class("article-lead")))
                    blocks[0].remove(lead)
                elif old.find_class("blog-post-content"):
                    blocks = old.find_class("blog-post-content")
                else:
                    blocks = [n for n in old.find_class("polca-page")[0]
                              if hasattr(n, "classes") and
                              not set(n.classes).isdisjoint({"blog-post-body", "card-lg", "callout"})]
                if path.stem == "blog-alokacja-metan-kopalniany":
                    notes = old.find_class("margin-note")
                    self.assertEqual(text(notes), text(new.find_class("article-findings")))
                    for note in notes:
                        note.drop_tree()
                # Bibliography labels became section headings. Semicolons now terminate list items.
                def tokens(value):
                    value = re.sub(r'\bźródła( wskaźników)?:?', lambda m: "Źródła" + (m[1] or ""),
                                   value, flags=re.I)
                    return re.findall(r'\w+|[^\w\s]', value)
                self.assertEqual(tokens(text(blocks)), tokens(text(new.find_class("article-prose"))))
                for cls in ("vcol-label", "vcol-value", "comp-bar-fill", "faq-q", "faq-a"):
                    self.assertEqual(text(old.find_class(cls)), text(new.find_class(cls)), cls)
                summary = tokens(text(new.find_class("article-summary")))
                for row in old.find_class("key-stat") + old.find_class("sidebar-stat") + old.find_class("sidebar-stat-label"):
                    self.assertIn(" ".join(tokens(text([row]))), " ".join(summary))
                for li in old.xpath('//div[contains(@class,"tldr-box")]/ul/li'):
                    self.assertIn(" ".join(tokens(text([li]))), " ".join(summary))
