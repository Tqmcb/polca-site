"""Protect product classification boundaries and the public method statuses."""
import json
import unittest
from pathlib import Path
from lxml import html

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text())


class ProductNavigationTests(unittest.TestCase):
    def test_official_family_codes_and_pages(self):
        families = read('data/cpr-families.json')['families']
        self.assertEqual([f['id'] for f in families], list(range(1, 37)))
        self.assertEqual(families[-1]['official_name'], 'DRABINY MOCOWANE NA STAŁE.')
        for f in families:
            doc = html.parse(str(ROOT / f'wyroby/{f["id"]:02d}.html'))
            self.assertIn(f['official_name'], doc.getroot().text_content())
        directory = html.parse(str(ROOT / 'wyroby.html'))
        self.assertEqual(len(directory.xpath('//*[@data-family]')), 36)

    def test_shared_inputs_and_cbam_are_not_product_records(self):
        for r in read('data/portal-catalog.json')['datasets']:
            if r['category_id'] in ['energia', 'paliwa', 'transport', 'cbam']:
                self.assertEqual(r['cpr_family_ids'], [], r['id'])
            if r['category_id'] == 'cement':
                self.assertEqual(r['cpr_family_ids'], [15], r['id'])
            if r['category_id'] == 'kruszywa':
                self.assertEqual(r['cpr_family_ids'], [24], r['id'])

    def test_family_data_rows_match_catalog_without_silent_duplicates(self):
        datasets = read('data/portal-catalog.json')['datasets']
        for family in range(1, 37):
            doc = html.parse(str(ROOT / f'wyroby/{family:02d}.html'))
            rows = doc.xpath('//*[@id="dane"]//*[@data-record-id]/@data-record-id')
            self.assertEqual(rows, [r['id'] for r in datasets if family in r['cpr_family_ids']])
            self.assertEqual(len(rows), len(set(rows)))

    def test_methods_distinguish_draft_and_published_scope(self):
        methods = {r['id']: r for r in read('data/product-methods.json')['documents']}
        self.assertEqual(methods['ts18301']['status'], 'published')
        self.assertEqual(methods['ts18301']['family_ids'], [23])
        self.assertEqual(methods['pren17662']['status'], 'draft')
        self.assertEqual(methods['pren17662']['family_ids'], [20])
        self.assertEqual(methods['tr18114']['role'], 'technical_review')
        self.assertIn('Wyłącza beton komórkowy autoklawizowany', methods['en16757']['scope_note'])
        self.assertTrue(all(m['url'].startswith('https://') for m in methods.values()))
        for name in ['mma', 'kruszywa']:
            text = html.parse(str(ROOT / f'c-pcr/{name}.html')).getroot().text_content()
            self.assertIn('Historyczny projekt', text)
            self.assertNotIn('brak europejskiego c-PCR', text.lower())

    def test_shared_navigation_is_consistent(self):
        expected = html.parse(str(ROOT / 'index.html')).xpath('//*[@id="portal-navigation"]//a/@href')
        self.assertEqual(expected[0], '/wyroby.html')
        for path in ROOT.rglob('*.html'):
            doc = html.parse(str(path))
            self.assertEqual(doc.xpath('//*[@id="portal-navigation"]//a/@href'), expected, str(path))
            self.assertEqual(len(doc.xpath('//a[contains(@class,"portal-skip-link")]')), 1, str(path))


if __name__ == '__main__':
    unittest.main()
