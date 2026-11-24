"""Check the published homepage against its catalogue, consultation and change register."""
import csv
import html as html_text
import json
import re
import sys
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from home_portal import article_items, build, counted, family_coverage
from consultation_portal import DATA


def read_json(path):
    return json.loads((ROOT / path).read_text())


class HomepageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = html.parse(str(ROOT / 'index.html'))
        cls.catalog = read_json('data/portal-catalog.json')

    def test_title_and_catalogue_count(self):
        self.assertEqual(self.home.xpath('//h1/text()'), ['Polskie dane do oceny cyklu życia wyrobów i budynków'])
        count = self.catalog['counts']['data_positions']
        lead = self.home.xpath('//p[@class="home-description"]/text()')
        self.assertEqual(lead, [
            f'Katalog zawiera {counted(count, "pozycję", "pozycje", "pozycji")} danych dla energii, paliw, '
            'transportu i materiałów budowlanych. Przy każdej wartości podajemy jednostkę, rok, źródło i status.'
        ])

    def test_polish_count_forms(self):
        forms = {0: 'pozycji', 1: 'pozycję', 2: 'pozycje', 4: 'pozycje', 5: 'pozycji',
                 12: 'pozycji', 13: 'pozycji', 14: 'pozycji', 21: 'pozycji', 22: 'pozycje', 112: 'pozycji'}
        for number, noun in forms.items():
            with self.subTest(number=number):
                self.assertEqual(counted(number, 'pozycję', 'pozycje', 'pozycji'), f'{number} {noun}')
        self.assertEqual(family_coverage([]), 'Wskaźniki liczbowe nie są jeszcze dostępne dla żadnej rodziny.')
        self.assertEqual(family_coverage(['Stal']), 'Wskaźniki liczbowe podajemy obecnie dla 1 rodziny. Jest to: stal.')
        self.assertEqual(family_coverage(['Stal i wyroby', 'Cement']), 'Wskaźniki liczbowe podajemy obecnie dla 2 rodzin. Są to: stal i wyroby; cement.')

    def test_families_with_current_data(self):
        families = read_json('data/cpr-families.json')['families']
        ids = {i for record in self.catalog['datasets'] for i in record['cpr_family_ids']}
        names = [f['label'] for f in families if f['id'] in ids]
        lead, = self.home.xpath('//*[@class="home-products-intro"]/p/text()')
        self.assertTrue(lead.startswith(f'Dla {len(families)} rodzin wyrobów według CPR 2024/3110 '))
        self.assertTrue(lead.endswith(' ' + family_coverage(names)), lead)
        self.assertIn(f'Przeglądaj {len(families)} rodzin wyrobów', self.home.xpath('//main//a/text()'))
        self.assertIn(f'({len(families)} rodzin według rozporządzenia CPR 2024/3110)', self.home.xpath('string(//*[@class="home-routes"])'))

    def test_build_updates_counts_and_ignores_withdrawn_families(self):
        families = read_json('data/cpr-families.json')['families']
        catalog = read_json('data/portal-catalog.json')
        catalog['counts']['data_positions'] = 12
        for record in catalog['datasets']:
            record['cpr_family_ids'] = []
        catalog['datasets'][0]['cpr_family_ids'] = [families[0]['id']]
        catalog['withdrawn_datasets'][0]['cpr_family_ids'] = [families[1]['id']]
        pages = []
        def capture(path, title, lead, body, **kwargs):
            pages.append(html.fromstring(body))
        build({'ROOT': ROOT, 'CAT': catalog, 'CHANGE_ENTRIES': [], 'page': capture,
               'e': lambda value: html_text.escape(str(value))}, families)
        self.assertIn('Katalog zawiera 12 pozycji', pages[0].text_content())
        label = families[0]['label']
        self.assertIn(f'dla 1 rodziny. Jest to: {label[:1].lower() + label[1:]}.', pages[0].text_content())

    def test_four_latest_changes_link_to_matching_entries(self):
        register = html.parse(str(ROOT / 'rejestr-zmian.html'))
        entries = sorted(read_json('data/rejestr-zmian.json')['wpisy'], key=lambda row: row['data'], reverse=True)
        items = self.home.xpath('//section[@class="home-updates"]/ol/li')
        self.assertEqual(len(items), 4)
        for item, entry in zip(items, entries[:4]):
            published = date.fromisoformat(entry['data'])
            self.assertEqual(item.xpath('time/@datetime'), [entry['data']])
            self.assertEqual(item.xpath('time/text()'), [f'{published.day}.{published:%m.%Y}'])
            self.assertEqual(item.xpath('a/text()'), [entry['tytul']])
            target = urlsplit(item.xpath('string(a/@href)'))
            self.assertEqual(target.path, '/rejestr-zmian.html')
            self.assertEqual(register.xpath('//article[@id=$id]//h3/text()', id=target.fragment), [entry['tytul']])

    def test_published_homepage_lists_current_editorial_articles(self):
        section, = self.home.xpath('//*[@id="home-updates-title"]/../following-sibling::section[1]')
        self.assertEqual(section.xpath('h2/text()'), ['Które artykuły opisują aktualne dane?'])
        self.assertEqual(section.xpath('a[@href="/blog.html"]/text()'), ['Wszystkie artykuły i wyjaśnienia'])
        articles = [r for r in read_json('data/portal-editorial.json')['resources']
                    if r['kind'] == 'article' and r['status_id'] != 'archive'
                    and (r.get('reviewed_at') or r.get('published_at'))]
        articles.sort(key=lambda r: (r.get('reviewed_at') or r['published_at'])[:10], reverse=True)
        items = section.xpath('ol/li')
        self.assertEqual([item.xpath('string(a/@href)') for item in items], [r['href'] for r in articles[:3]])
        for item, article in zip(items, articles):
            dt = date.fromisoformat((article.get('reviewed_at') or article['published_at'])[:10])
            self.assertEqual(item.xpath('a/text()'), [article['title']])
            self.assertEqual(item.xpath('.//time/@datetime'), [dt.isoformat()])
            self.assertEqual(item.xpath('.//time/text()'), [f'{dt.day}.{dt:%m.%Y}'])
            self.assertIn(article['description'], item.text_content())

    def test_article_limit_uses_review_or_publication_day(self):
        base = dict(kind='article', status_id='guide', description='Opis', href='/article.html')
        resources = [
            dict(base, title='Starszy wpis', published_at='2026-10-20'),
            dict(base, title='Przegląd', published_at='2025-12-01', reviewed_at='2026-11-03'),
            dict(base, title='Archiwum', published_at='2026-11-05', status_id='archive'),
            dict(base, title='Kalkulator', kind='tool', published_at='2026-11-06'),
            dict(base, title='Wpis z godziną', published_at='2026-11-04T10:00:00+01:00'),
            dict(base, title='Trzeci wpis', published_at='2026-11-01'),
        ]
        items = html.fragment_fromstring(article_items(resources, html_text.escape), create_parent='ol')
        self.assertEqual(items.xpath('li/a/text()'), ['Wpis z godziną', 'Przegląd', 'Trzeci wpis'])
        self.assertEqual(items.xpath('.//time/text()'), ['4.11.2026', '3.11.2026', '1.11.2026'])

    def test_consultation_figures_come_from_the_consultation_package(self):
        package = ROOT / DATA.lstrip('/')
        indicators = read_json(package / 'profil-37.json')['indicators']
        with (package / 'wrazliwosc-37.csv').open(encoding='utf-8-sig', newline='') as stream:
            variants = {(row['q_hardcoal'], row['q_lignite']) for row in csv.DictReader(stream, delimiter=';')}
        expected = read_json('content/consultation-energy.json')['home_description'].format(
            indicator_count=len(indicators), variant_count=len(variants))
        self.assertEqual(self.home.xpath('//*[@id="home-consultation-title"]/following-sibling::p[1]/text()'), [expected])
        self.assertNotIn('37 wskaźników', (ROOT / 'content/portal-home.html.tpl').read_text())

    def test_home_font_sizes_use_declared_scale(self):
        sheet = (ROOT / 'assets/home.css').read_text()
        tokens = {'sm', 'base', 'lg', 'xl', 'h2', 'h1', 'value'}
        self.assertEqual(set(re.findall(r'--text-([\w-]+)\s*:', sheet)), tokens)
        sizes = re.findall(r'\bfont-size\s*:\s*([^;}]+)', sheet)
        self.assertTrue(sizes)
        self.assertLessEqual(set(sizes), {f'var(--text-{token})' for token in tokens})
        self.assertLessEqual(set(re.findall(r'font-weight:\s*(\d+)', sheet)), {'400', '600', '700'})
