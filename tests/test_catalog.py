"""Data, publication-boundary and navigation checks for the portal registry.

Run after generating catalog and pages:
    python3 -m unittest discover -s tests -p test_catalog.py -v
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('build_catalog', ROOT / 'scripts/build-catalog.py')
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
ENERGY_ID = 'PL2025_PHYSICAL_DELIVERED_v4'
ENERGY_HASHES = {
    'Polska-energia-2025-v3-do-recenzji.zip': 'df4adf267fa0e8266aacaa279f5b7becbe6744ef5941f263a82335c31f4e3558',
    'przyklad-10-kWh.json': '368986391b5909145a7a93042dfe50f1d7d73227d62e6ef85e29536c586b99d9',
    'WARUNKI-WYKORZYSTANIA.txt': 'e118707c243b6e53497025e3d3b5b1be816405ff2ec320ab8d1d7afbc26aca75',
    'wskazniki-37.csv': '901e1ab74047a0cc3534ee8cc56bd4354a7c1583a5c11dbba8f1fcb2f9c2d9ae',
    'METODA-I-ZMIANY.txt': '1a5ea4b1b9a45f7d5e92636f56fe239702927de92e2a251d8249df55461623d3',
    'kontrola-eksportu.json': '945704b3c2e9b126d04d8d6da434fbc32f70d4dc6acefd66a276c2d514d16a44',
    'profil-37.json': '93a5eac8f73001c2c493b6b669cda6298ddaa0f63d3eb4a4f839cad7f19c6867',
    'manifest.json': 'd36f816cc72b990c458df6eb75113d66f3c46c492c770523e5884e39810f3dd2',
    'START.txt': 'e6f22acd7f15a5c89767a6cd7943e531486e10578b2f016b979eb3f2236b0592',
}


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'), parse_float=Decimal)


class IDs(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read('data/portal-catalog.json')
        cls.datasets = {x['id']: x for x in cls.catalog['datasets']}
        cls.resources = cls.catalog['resources']
        cls.legacy = {x['code']: x for x in read('data/datasets.json')['datasets']}

    def test_deterministic_and_current(self):
        expected = BUILDER.serialize(BUILDER.build_catalog())
        self.assertEqual(expected, BUILDER.serialize(BUILDER.build_catalog()))
        self.assertEqual(expected, (ROOT / 'data/portal-catalog.json').read_text(encoding='utf-8'))

    def test_positions_not_files_or_indicators(self):
        self.assertEqual(len(self.datasets), 37)
        self.assertEqual(set(self.datasets), set(self.legacy) | {ENERGY_ID})
        self.assertEqual(self.catalog['counts']['data_positions'], 37)
        self.assertEqual(self.catalog['counts']['parameter_sets'], 1)
        self.assertEqual(self.catalog['counts']['control_references'], 8)
        self.assertNotIn('POLCA-MMA-MIXES-2026', self.datasets)
        parameter_sets = [x for x in self.datasets.values() if x['record_type'] == 'parameters']
        self.assertEqual(len(parameter_sets), 1)
        self.assertNotIn('value', parameter_sets[0])
        self.assertEqual(self.datasets[ENERGY_ID]['indicator_count'], 37)

    def test_all_ids_unique_and_relationships_resolve(self):
        all_items = self.catalog['datasets'] + self.resources + self.catalog['collections']
        all_ids = [x['id'] for x in all_items]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        for item in all_items:
            for related in item.get('related_ids', []) + item.get('member_ids', []):
                with self.subTest(id=item['id'], related=related):
                    self.assertIn(related, all_ids)

    def test_values_equal_source_records_and_downloads(self):
        for id, original in self.legacy.items():
            with self.subTest(id=id):
                item = self.datasets[id]
                if item['record_type'] == 'parameters':
                    self.assertIsNone(original['gwp_total_kg_co2e'])
                    continue
                field = 'gwp_fossil_kg_co2e' if id == 'POLCA-EN-PL-LCA-2024' else 'gwp_total_kg_co2e'
                self.assertEqual(item['value'], original[field])
                file = read(item['source_record_href'].lstrip('/'))
                single = file.get('dataset', file)
                self.assertEqual(item['value'], single[field])
                self.assertEqual(item['reference_unit'], original['unit'])
                self.assertEqual(item['year'], original['year'])

    def test_primary_download_preserves_indicator_and_source(self):
        for item in self.datasets.values():
            if item['id'] == ENERGY_ID:
                continue
            with self.subTest(id=item['id']):
                exported = read(item['downloads'][0]['href'].lstrip('/'))['record']
                self.assertEqual(exported['id'], item['id'])
                self.assertEqual(exported['indicator_label'], item['indicator_label'])
                self.assertEqual(exported['unit'], item['unit'])
                self.assertEqual(exported.get('value'), item.get('value'))
                self.assertEqual(exported['source_record_href'], item['source_record_href'])

    def test_energy_scopes_are_distinct(self):
        co2 = self.datasets['KOBIZE-EN-PL-ENDUSER-2024']
        fossil = self.datasets['POLCA-EN-PL-LCA-2024']
        current = self.datasets[ENERGY_ID]
        self.assertEqual(co2['unit'], 'kg CO₂/kWh')
        self.assertEqual(co2['indicator_label'], 'Emisja CO₂')
        self.assertEqual(fossil['value'], Decimal('0.599'))
        self.assertIn('kopalny', fossil['indicator_label'])
        self.assertEqual(fossil['status_id'], 'earlier_model')
        self.assertEqual(current['value'], Decimal('0.6445397488349277'))
        self.assertEqual(current['indicator_count'], 37)
        self.assertEqual(current['status_id'], 'review')
        self.assertFalse(current['is_default'])
        profile = read('data/energia-pl-2025-v4/profil-37.json')
        total = next(x for x in profile['indicators'] if x['code'] == 'GWP-total')
        self.assertEqual(current['value'], total['value_per_kWh'])
        self.assertEqual(current['reference_unit'], profile['functional_unit']['unit'])
        self.assertEqual(current['year'], profile['reference_year'])

    def test_current_profile_keeps_technical_and_formal_status_separate(self):
        profile = read('data/energia-pl-2025-v4/profil-37.json')
        self.assertEqual(profile['model_id'], ENERGY_ID)
        self.assertEqual(profile['variant'], 'selected')
        self.assertEqual(profile['package_version'], '2026-10-19.1')
        self.assertEqual(self.catalog['catalog_version'], profile['package_version'])
        status = profile['status']
        self.assertEqual(status['state'], 'technical_review_complete')
        self.assertTrue(status['computation_complete'])
        self.assertTrue(status['internal_technical_review_completed'])
        for field in ('production_approved', 'formal_EN15804_qualification',
                      'human_verification_recorded', 'operator_decision_signed',
                      'internal_checks_are_external_expert_review'):
            self.assertFalse(status[field], field)
        self.assertEqual(status['external_expert_review'], 'NOT_PERFORMED')
        current = self.datasets[ENERGY_ID]
        self.assertEqual(current['href'], '/energia-polska-2025-v4.html')
        self.assertEqual(current['source_record_href'], '/data/energia-pl-2025-v4/profil-37.json')
        self.assertTrue(all(x['href'].startswith('/data/energia-pl-2025-v4/')
                            for x in current['downloads']))
        self.assertEqual(len(profile['indicators']), 37)
        self.assertEqual(len({x['code'] for x in profile['indicators']}), 37)
        self.assertEqual(profile['quality_assessment']['assessed_data_units'], 60)
        self.assertEqual(profile['quality_assessment']['source_processes'], 49)

    def test_archived_v3_publication_bytes_unchanged(self):
        folder = ROOT / 'data/energia-pl-2025-v3'
        self.assertEqual(set(x.name for x in folder.iterdir() if x.is_file()), set(ENERGY_HASHES))
        for name, expected in ENERGY_HASHES.items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((folder / name).read_bytes()).hexdigest(), expected)

    def test_required_metadata_and_no_inherited_approval(self):
        fields = {'id', 'title', 'kind', 'category_id', 'category_label', 'year', 'year_type',
                  'status_id', 'status_label', 'description', 'href', 'unit', 'boundary',
                  'indicator_label', 'source_name', 'source_url', 'formats', 'downloads',
                  'methodology_href', 'related_ids', 'keywords'}
        for item in self.catalog['datasets'] + self.resources:
            with self.subTest(id=item['id']):
                self.assertTrue(fields.issubset(item))
                self.assertIn(item['kind'], {'dataset', 'tool', 'method', 'article'})
                self.assertIn(item['year_type'], {None, 'reference', 'publication', 'application'})
                self.assertNotIn('production_approved', item)
                self.assertNotIn('ready_to_use', json.dumps(item, default=str))
                self.assertNotIn('ILCD-compatible', json.dumps(item, default=str))
                self.assertNotIn('JSON-LD', item['formats'])
                self.assertLessEqual(len(item['description']), 260)
        self.assertTrue(all(x['year_type'] for x in self.datasets.values()))

    def test_cbam_is_separate_control_category(self):
        controls = [x for x in self.datasets.values() if x['id'].startswith('CBAM-')]
        self.assertEqual(len(controls), 8)
        for item in controls:
            self.assertEqual(item['category_id'], 'cbam')
            self.assertEqual(item['status_id'], 'control')
            self.assertEqual(item['year_type'], 'application')
            self.assertNotIn('A1', item['boundary'])

    def test_downloads_and_format_claims_match_files(self):
        for item in self.catalog['datasets'] + self.resources + self.catalog['collections']:
            expected_formats = []
            for download in item['downloads']:
                with self.subTest(id=item['id'], href=download['href']):
                    file = ROOT / download['href'].lstrip('/')
                    self.assertTrue(file.is_file())
                    self.assertEqual(download['format'], file.suffix[1:].upper())
                    self.assertGreater(file.stat().st_size, 0)
                    if download['format'] not in expected_formats:
                        expected_formats.append(download['format'])
            self.assertEqual(item['formats'], expected_formats)

    def test_all_local_links_and_fragments(self):
        all_items = self.catalog['datasets'] + self.resources + self.catalog['collections']
        for item in all_items:
            links = [item.get(key) for key in ('href', 'source_url', 'source_record_href', 'methodology_href')]
            links += [x['href'] for x in item['downloads']]
            for href in filter(None, links):
                with self.subTest(id=item['id'], href=href):
                    url = urlsplit(href)
                    self.assertIn(url.scheme, ('', 'https', 'http'))
                    if url.netloc and url.netloc not in ('polca.org.pl', 'www.polca.org.pl'):
                        continue
                    self.assertTrue(url.path.startswith('/'), 'Local URL must work from nested pages')
                    target = ROOT / unquote(url.path).lstrip('/')
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), f'Missing page or file: {target.relative_to(ROOT)}')
                    if target.is_file() and url.fragment and target.suffix == '.html':
                        self.assertIn(unquote(url.fragment), IDs(target.read_text()).ids)


if __name__ == '__main__':
    unittest.main()
