import csv
import json
import unittest
from decimal import Decimal
from pathlib import Path

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
SPC_URL = 'https://www.polskicement.pl/content/uploads/2026/01/EPD-Deklaracja-srodowiskowa-2025-POL.pdf#page=5'
# Table 2, page 5, in kg CO₂e per tonne: gross, fossil, net.
TABLE_2 = {'I': (766, 766, 584), 'II': (613, 613, 473), 'III': (483, 483, 398),
           'IV': (510, 510, 397), 'V': (546, 545, 430)}
OLD_CLASSES = ['I-52-5R', 'I-42-5R', 'I-42-5N', 'I-32-5R', 'II-A-S-42-5R', 'II-B-S-32-5R',
               'II-A-V-32-5R', 'II-B-V-32-5R', 'III-A-42-5N', 'III-B-32-5N']
OLD_IDS = {f'POLCA-CEMENT-CEM-{c}-EPD-PL-2024' for c in OLD_CLASSES} | {'POLCA-CEMENT-CEM-IV-AVG-SPC-EPD-PL-2025'}


def spc_id(kind):
    return f'POLCA-CEMENT-CEM-{kind}-SPC-PL-2025'


def read(path):
    return json.loads((ROOT / path.lstrip('/')).read_text())


class CementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read('data/portal-catalog.json')
        cls.cements = {r['id']: r for r in cls.catalog['datasets'] if r['category_id'] == 'cement'}
        cls.family = html.parse(str(ROOT / 'wyroby/15.html'))

    def test_sector_indicators_match_table_2(self):
        self.assertEqual(set(self.cements), {spc_id(kind) for kind in TABLE_2})
        for kind, (gross, fossil, net) in TABLE_2.items():
            record = self.cements[spc_id(kind)]
            with self.subTest(kind=kind):
                self.assertEqual((record['value'], record['gwp_fossil_kg_co2e'], record['gwp_net_kg_co2e'],
                                  record['gwp_gross_kg_co2e'], record['cement_basis']), (net, fossil, net, gross, 'netto'))
                self.assertEqual(record['source_url'], SPC_URL)
                self.assertEqual(record['gwp_fossil_basis'], 'brutto')
                self.assertEqual(record['source_name'], 'Deklaracja środowiskowa sektorowa SPC 2025, tabela 2')
                self.assertEqual(record['source_valid_until'], '2030-12-18')
                self.assertEqual((record['year'], record['publication_year'], record['year_type']), (2022, 2025, 'reference'))
                self.assertEqual((record['unit'], record['boundary']), ('kg CO₂e/t', 'A1–A3'))
                self.assertEqual(record['status_id'], 'published_sector_dataset')
                self.assertEqual(record['cpr_family_ids'], [15])
                self.assertEqual(read(record['downloads'][0]['href'])['record'], record)
                card = html.parse(str(ROOT / record['href'][1:]))
                self.assertIn(SPC_URL, card.xpath('//main//a/@href'))
                self.assertIn(record['methodology_note'], card.xpath('//main//p/text()'))
                self.assertTrue(record['methodology_note'].startswith(
                    'Wartość podstawowa to globalne ocieplenie netto z tabeli 2 deklaracji SPC. '
                    'Nie obejmuje ona emisji ze spalania kopalnej części paliw o statusie odpadu. '
                    'Według zasady „zanieczyszczający płaci” (EN 15804+A2, pkt 6.3.5.1, załącznik D.3.2) '
                    'emisje te przypisuje się systemowi, w którym powstał odpad.'))
                self.assertIn('Porównanie z danymi EU ETS lub CBAM wymaga uzgodnienia granic obliczeń.', record['methodology_note'])
                self.assertIn(f'GWP-fossil: {fossil} kg CO₂e/t (składnik kopalny według rozliczenia brutto)',
                              card.xpath('//main//p/text()'))
                self.assertIn(f'Wartość brutto (informacja dodatkowa): {gross} kg CO₂e/t', card.xpath('//main//p/text()'))

    def test_basis_rule_on_all_cement_pages(self):
        rule = ('Wartość netto przyjmujemy, gdy deklaracja środowiskowa cementu podaje wynik netto albo potwierdza, '
                'że współspalane paliwa mają status odpadu. W pozostałych przypadkach przyjmujemy wartość brutto. '
                'Porównujemy wyłącznie wyniki obliczone w tym samym wariancie.')
        entries = read('data/rejestr-zmian.json')['wpisy']
        self.assertIn(rule, [entry.get('skutek_dla_deklaracji') for entry in entries])
        paths = ['wyroby/15.html', 'sektor-cement.html', 'kalkulator-betonu.html',
                 'blog-cement-polska.html', 'blog-beton-emisje-kalkulator.html']
        paths.extend(record['href'][1:] for record in self.cements.values())
        for path in paths:
            with self.subTest(path=path):
                self.assertIn(rule, html.parse(str(ROOT / path)).xpath('string(//main)'))

    def test_archived_cards_remain_addressable_with_current_replacement(self):
        archived = {r['id']: r for r in self.catalog['withdrawn_datasets'] if r['category_id'] == 'cement'}
        self.assertEqual(set(archived), OLD_IDS)
        for old_id, record in archived.items():
            with self.subTest(id=old_id):
                replacement = self.cements[spc_id(old_id.split('-')[3])]
                self.assertEqual(record['superseded_by'], replacement['id'])
                self.assertEqual(record['status_id'], 'withdrawn')
                self.assertIs(record['is_default'], False)
                self.assertEqual(record['href'], f'/dane/{old_id.lower()}.html')
                page = html.parse(str(ROOT / record['href'][1:]))
                notice = ('Wskaźnik wycofany 23.11.2026. Wartości nie potwierdzono w deklaracji środowiskowej producenta. '
                          'Wskaźnik zastąpiono średnią krajową dla rodzaju cementu z deklaracji sektorowej SPC 2025.')
                self.assertIn(notice, page.xpath('string(//main)'))
                self.assertIn(replacement['href'], page.xpath('//main//a/@href'))
                self.assertEqual(read(record['downloads'][0]['href'])['record'], record)
        for file in ('szukaj.html', 'datasety.html'):
            doc = html.parse(str(ROOT / file))
            rows = json.loads(doc.xpath('string(//*[@id="portal-search-data"])'))
            self.assertEqual({r['id'] for r in rows if r['kind'] == 'dataset' and r['category_id'] == 'cement'}, set(self.cements))
            for r in rows:
                if r['id'] in self.cements:
                    self.assertIn(f"{r['value']} netto", r['keywords'])
                    self.assertIn(f"{r['gwp_gross_kg_co2e']} brutto", r['keywords'])
            self.assertTrue(OLD_IDS.isdisjoint(doc.xpath('//@data-record-id')))
        shared = read('data/product-dataset-map.json')['shared_datasets']
        self.assertEqual({r['code'] for r in shared if r['code'].startswith('POLCA-CEMENT-')}, set(self.cements))

    def test_legacy_csv_marks_the_same_records_as_json(self):
        source_rows = read('data/datasets.json')['datasets']
        with (ROOT / 'data/datasets.csv').open() as source_csv:
            csv_rows = {r['code']: r for r in csv.DictReader(source_csv)}
        for row in source_rows:
            code = row['code']
            if code in OLD_IDS or code in self.cements:
                self.assertEqual(read(f'data/datasets/{code}.json')['dataset'], row)
                self.assertEqual(csv_rows[code]['status'], row['status'])
                self.assertEqual(Decimal(csv_rows[code]['gwp_total_kg_co2e']), row['gwp_total_kg_co2e'])
                if code in self.cements:
                    self.assertEqual(row['gwp_total_kg_co2e'], self.cements[code]['value'])
                    self.assertEqual(int(csv_rows[code]['gwp_gross_kg_co2e']), self.cements[code]['gwp_gross_kg_co2e'])
                    self.assertEqual(csv_rows[code]['cement_basis'], 'netto')
                    self.assertEqual((row['gwp_fossil_basis'], csv_rows[code]['gwp_fossil_basis']), ('brutto', 'brutto'))
                    self.assertEqual(int(csv_rows[code]['gwp_fossil_kg_co2e']), self.cements[code]['gwp_fossil_kg_co2e'])
        legacy = read('data/polca-gwp-v2026-1.json')['records']
        with (ROOT / 'data/polca-gwp-v2026-1.csv').open() as old_csv:
            legacy_csv = {r['id']: r for r in csv.DictReader(old_csv, delimiter=';')}
        current = {r['id']: r for r in legacy if r['group'] == 'cement' and 'wycofany' not in r['status']}
        self.assertEqual(set(current), set(self.cements))
        for code, r in current.items():
            expected = self.cements[code]
            for export in (r, legacy_csv[code]):
                self.assertEqual(export['gwp_fossil_basis'], 'brutto')
                self.assertEqual(int(export['gwp_fossil_kg_co2e']), expected['gwp_fossil_kg_co2e'])
            self.assertEqual((r['value'], r['value_gross']), (expected['value'], expected['gwp_gross_kg_co2e']))
            self.assertEqual((int(legacy_csv[code]['wartosc']), int(legacy_csv[code]['wartosc_brutto'])),
                             (r['value'], r['value_gross']))
        cement_rows = [r for r in legacy if r['group'] == 'cement' and r['id'] not in current]
        self.assertEqual(len(cement_rows), 11)
        for row in cement_rows:
            self.assertIn('wycofany', row['status'])
            self.assertEqual(row['status'], legacy_csv[row['id']]['status'])
            self.assertEqual(row['replace_with'], spc_id(row['id'].split('-')[4]))
            self.assertEqual(row['replace_with'], legacy_csv[row['id']]['zastap_danymi'])

    def test_family_indicators_and_calculator_follow_current_records(self):
        ids = [spc_id(kind) for kind in TABLE_2]
        self.assertEqual(self.family.xpath('//*[@id="dane"]//@data-record-id'), ids)
        guide, = self.family.xpath('//*[@id="modul-a1-cement"]')
        self.assertEqual(guide.xpath('.//*[@data-case]/@data-case'), ['cement'])
        self.assertFalse(guide.xpath('.//*[contains(@class,"aggregate-choice")]'))
        material, = guide.xpath('.//article[@data-kind="material"]')
        options = material.xpath('.//select/option')
        self.assertEqual([o.get('value') for o in options], ids)
        for option in options:
            record = self.cements[option.get('value')]
            self.assertEqual(Decimal(option.get('data-factor')), record['value'])
            self.assertEqual(option.get('data-source'), record['href'])
        selected, = material.xpath('.//option[@selected]/@value')
        self.assertEqual(selected, spc_id('II'))
        value = self.cements[selected]['value']
        self.assertEqual(Decimal(material.get('data-factor')), value)
        self.assertEqual(material.xpath('.//a[@data-source]/@href'), [self.cements[selected]['href']])
        for text in material.xpath('.//*[@data-output]/text()') + guide.xpath('.//a[@data-step="1"]//*[@data-output]/text()'):
            self.assertEqual(Decimal(text.replace(',', '.')), value)
        self.assertEqual(guide.xpath('.//input[@data-param="distance"]/@value'), ['100'])
        self.assertEqual(guide.xpath('.//input[@data-param="power"]/@value'), ['2'])
        rows = guide.xpath('.//table/tbody/tr')
        self.assertEqual(len(rows), 5)
        for row, kind in zip(rows, TABLE_2):
            gross, _, net = TABLE_2[kind]
            expected = [f'CEM {kind}']
            for value in (net, gross):
                expected.extend([str(value), f"{Decimal(value) * Decimal('0.3'):.1f}".replace('.', ',')])
            self.assertEqual(row.xpath('./*/text()'), expected)

    def test_sector_chart_and_legacy_indicators_use_declared_values(self):
        sector = html.parse(str(ROOT / 'sektor-cement.html'))
        self.assertIn('deklaracja sektorowa SPC 2025, s. 4', sector.xpath('//a[contains(@href,"#page=4")]/text()'))
        table, = sector.xpath('//table[.//th[contains(., "netto (podstawowa)")]]')
        blog = html.parse(str(ROOT / 'blog-cement-polska.html'))
        chart = dict(zip(blog.xpath('//*[@class="vcol-label"]/text()'), blog.xpath('//*[@class="vcol-value"]/text()')))
        text = (ROOT / 'js/wskazniki-emisji.js').read_text().splitlines()
        materials = (ROOT / 'js/gwp-materialow.js').read_text().splitlines()
        fallback = html.parse(str(ROOT / 'gwp-materialow.html'))
        for kind, (gross, _, net) in TABLE_2.items():
            name = f'CEM {kind}'
            row, = table.xpath('.//tr[td/strong=$name]', name=name)
            self.assertEqual(row.xpath('td[@class="mono"]/text()'), [str(net), str(gross)])
            self.assertEqual(int(chart[name]), net)
            self.assertTrue(any(name + ' —' in line and f"value: '{net}'" in line and 'netto' in line for line in text))
            if kind in ('I', 'II', 'III'):
                self.assertTrue(any(name + ' (' in line and f'gwp: {net},' in line and 'netto' in line for line in materials))
                row, = fallback.xpath('//noscript//tr[contains(td[1], $label)]', label=name + ' (')
                self.assertEqual(row.xpath('string(td[2])'), str(net))
                self.assertIn('netto', row.xpath('string(td[1])'))

    def test_aggregate_page_has_no_cement_guide(self):
        page = (ROOT / 'wyroby/24.html').read_text(encoding='utf-8')
        self.assertNotIn('modul-a1-cement', page)
        self.assertNotIn('cement-beton-fotografia', page)
