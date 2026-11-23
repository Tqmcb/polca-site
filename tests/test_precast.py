import csv
import json
import re
import unittest
from decimal import Decimal
from pathlib import Path
from statistics import median

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
TRUCK = 'POLCA-TRUCK-40T-DEFAULT-2026'
STEEL = 'POLCA-STEEL-REBAR-PL-MEDIAN-2026'
UUID = '330f8948-8463-4b63-a14a-3fedcc175180'


def read(path):
    return json.loads((ROOT / path.lstrip('/')).read_text(), parse_float=Decimal)


def csv_record(path, key, code, delimiter=','):
    with (ROOT / path).open() as file:
        return next(row for row in csv.DictReader(file, delimiter=delimiter) if row[key] == code)


def pl_decimal(text):
    return Decimal(text.replace(',', '.'))


class PrecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r['id']: r for r in read('data/portal-catalog.json')['datasets']}

    def test_transport_sources_and_exported_factors(self):
        truck = self.records[TRUCK]
        (source,) = truck['source_trace']
        self.assertEqual(truck['value'], Decimal('0.0843'))
        self.assertEqual(source['gwp_total_kg_co2e'], Decimal('0.084310395322016'))
        self.assertEqual([source[f'gwp_{key}_kg_co2e'] for key in ('fossil', 'biogenic', 'luluc')],
                         list(map(Decimal, ['0.0823015251223586', '0.000427594315896087', '0.00158127588376131'])))
        self.assertEqual(truck['value'], round(source['gwp_total_kg_co2e'], 4))
        self.assertEqual(source['url'], truck['source_url'])
        self.assertIn(UUID, truck['source_name'])
        self.assertIn(f'uuid={UUID}&version=20.26.070', truck['source_url'])
        self.assertEqual((truck['geography'], truck['year'], truck['source_valid_until']), ('DE', 2023, 2026))
        legacy_id = 'POLCA-GWP-TRUCK-40T-2026'
        short = next(r for r in read('data/polca-gwp-v2026-1.json')['records'] if r['id'] == legacy_id)
        hot = next(r for r in read('data/mma-hotspots.json')['kluczowe źródło wpływus'] if r['id'] == 'transport')
        for code, short_id in ((TRUCK, legacy_id), (STEEL, STEEL)):
            record = self.records[code]
            src = read(record['source_record_href'])['dataset']
            self.assertEqual(src, next(r for r in read('data/datasets.json')['datasets'] if r['code'] == code))
            row = csv_record('data/datasets.csv', 'code', code)
            self.assertEqual((Decimal(row['gwp_total_kg_co2e']), row['source_url']), (record['value'], record['source_url']))
            row = csv_record('data/polca-gwp-v2026-1.csv', 'id', short_id, ';')
            self.assertEqual(pl_decimal(row['wartosc']), record['value'])
        self.assertEqual((short['value'], short['source_url']), (truck['value'], truck['source_url']))
        self.assertEqual(pl_decimal(hot['values'][0]['value'].split()[0]), truck['value'])
        card = html.parse(str(ROOT / truck['href'][1:]))
        self.assertIn(truck['limitations'], card.xpath('//main//p/text()'))

    def test_no_obsolete_truck_factor_in_tools_guides_or_data(self):
        # A token next to the truck ID, transport unit or label is in scope.
        # Other indicators, geographical coordinates and longer decimals are independent.
        old = r'(?<![\d.])0[.,]095(?!\d)'
        stale = re.compile(
            rf'(?:TRUCK-40T|zestaw 40 t|transport(?:_factor)?)[^<>\n]{{0,100}}{old}'
            rf'|{old}\s*(?:kg\s*CO|kg/\(t|kg/tkm|[,;][^;\n]{{0,20}}tkm)', re.I)
        for path in ROOT.rglob('*'):
            if path.suffix.lower() in {'.py', '.js', '.mjs', '.html', '.json', '.csv', '.md', '.php', '.xml'}:
                self.assertIsNone(stale.search(path.read_text()), str(path.relative_to(ROOT)))

    def test_mma_transport_results_follow_the_route_and_recipe(self):
        profile = read('data/mma-client-example.json')
        activity = profile['activity_data']
        mass = activity['recipe_kg_per_mg']
        km = activity['transport_km']
        deliveries = {'virgin_aggregate': 'virgin_aggregate_to_plant', 'rap': 'rap_to_plant',
                      'road_bitumen_35_50': 'bitumen_to_plant', 'limestone_filler': 'filler_to_plant',
                      'additives': 'additives_to_plant'}
        tkm = sum(Decimal(mass[item]) * km[route] for item, route in deliveries.items()) / 1000
        factor = self.records[TRUCK]['value']
        background = next(r for r in profile['background_factors'] if r['dataset_code'] == TRUCK)
        self.assertEqual(background['value'], factor)
        result = profile['module_results_kg_co2e_per_mg']
        for module, distance in [('A2', tkm), ('A4', km['plant_to_site_a4']), ('C2', km['rap_to_processing_c2'])]:
            self.assertEqual(result[module], round(distance * factor, 3))
        self.assertEqual(result['A1-A3'], result['A1'] + result['A2'] + result['A3'])
        self.assertEqual(result['net_with_D'], result['A-C_without_D'] + result['D'])
        indicators = profile['en15804_a2_indicators']
        shares = profile['non_transport_gwp_shares']
        transport = self.records[TRUCK]['source_trace'][0]
        for i, key in enumerate(shares['components']):
            source_factor = transport[f'gwp_{key.split("-")[1]}_kg_co2e']
            for group, stages, work in (
                ('A1-A3', ('A1', 'A3'), tkm),
                ('A4-A5', ('A5',), km['plant_to_site_a4']),
                ('C1-C4', ('C1', 'C3', 'C4'), km['rap_to_processing_c2']),
            ):
                estimate = work * source_factor + sum(result[k] * shares[k][i] for k in stages)
                # Published module totals and components are independently rounded to 0.001.
                self.assertLessEqual(abs(indicators[key][group] - estimate), Decimal('0.001'))
        for group in ('A1-A3', 'A4-A5', 'C1-C4'):
            climate = sum(indicators[k][group] for k in ('GWP-fossil', 'GWP-biogenic', 'GWP-luluc'))
            self.assertLessEqual(abs(indicators['GWP-total'][group] - climate), Decimal('0.002'))

    def test_median_four_declarations_on_card_and_family_roles(self):
        steel = self.records[STEEL]
        sources = steel['source_trace']
        values = [s['gwp_total_kg_co2e'] for s in sources]
        self.assertEqual(values, [358, 775, 805, 961])
        self.assertEqual(steel['value'], 790)
        self.assertEqual(steel['value'], median(values))
        self.assertEqual((steel['unit'], steel['boundary'], steel['publication_year']), ('kg CO₂e/t', 'A1–A3', 2026))
        self.assertEqual(steel['source_url'], sources[1]['url'])
        self.assertEqual(steel['cpr_family_ids'], [16])
        self.assertEqual([(r['family_id'], r['role']) for r in steel['cpr_related']], [(1, 'input_to_product')])
        card = html.parse(str(ROOT / steel['href'][1:]))
        for entry in sources:
            row, = card.xpath('//main//li[a[@href=$url]]', url=entry['url'])
            for text in (entry['manufacturer'], entry['name'], entry['product'], f'{entry["gwp_total_kg_co2e"]} kg CO₂e/t'):
                self.assertIn(text, row.text_content())

    def test_precast_example_uses_declared_masses_and_linked_record_values(self):
        page = html.parse(str(ROOT / 'wyroby/01.html'))
        name = 'przyklad-prefabrykat'
        self.assertEqual(page.xpath('//a[@href=$target]/text()', target='#' + name), ['Przykład obliczeń'])
        section, = page.xpath('//section[h2[@id=$name]]', name=name)
        recipe, declared = section.xpath('.//table')
        rows = recipe.xpath('tbody/tr')
        codes = ['POLCA-CEMENT-CEM-I-SPC-PL-2025', 'POLCA-AGG-PL-NATURAL-DEFAULT-2026',
                 'POLCA-FILLER-LIMESTONE-DEFAULT-2026', STEEL]
        masses = [pl_decimal(row.xpath('string(td[2])')) for row in rows]
        self.assertEqual(masses, list(map(Decimal, ['0.150', '0.730', '0.040', '0.030', '0.080', '0.001'])))
        total = Decimal(0)
        for code, row, mass in zip(codes, rows, masses):
            record = self.records[code]
            self.assertEqual(row.xpath('td[3]/a/@href'), [record['href']])
            self.assertEqual(pl_decimal(row.xpath('string(td[3])')), record['value'])
            contribution = mass * record['value']
            self.assertEqual(pl_decimal(row.xpath('string(td[4])')), round(contribution, 1))
            total += contribution
        self.assertEqual([row.xpath('string(td[4])') for row in rows[4:]], ['pominięto', 'brak wskaźnika'])
        self.assertEqual(pl_decimal(recipe.xpath('string(tfoot/tr/td)')), round(total, 1))
        self.assertIn(f'{total:.1f}'.replace('.', ',') + ' kg CO₂e/t', section.text_content())
        self.assertEqual(declared.xpath('tbody/tr/td/text()'), ['171', '25,0', '42,5', '239'])
