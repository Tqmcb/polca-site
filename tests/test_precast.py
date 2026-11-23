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
BITUMEN = 'POLCA-BITUMEN-ROAD-DEFAULT-2026'
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

    def test_road_bitumen_agrees_with_eurobitume_and_its_exports(self):
        record = self.records[BITUMEN]
        value, url = record['value'], record['source_url']
        self.assertEqual(value, 530)
        self.assertTrue(url.endswith('/EB-GWP-Report-to-LCA-4.0-2025.pdf#page=8'))
        self.assertEqual(record['source_name'], 'Eurobitume LCA 4.0 (2025), raport GWP, s. 8')
        single = read(record['source_record_href'])['dataset']
        registry = next(r for r in read('data/datasets.json')['datasets'] if r['code'] == BITUMEN)
        for data in (record, registry, single):
            self.assertEqual((data['source_name'], data['source_url']), (record['source_name'], url))
            self.assertEqual(data['source_trace'][0]['url'], url)
            self.assertIn('dla asfaltu utlenionego raport podaje 616 kg CO₂e/t', data['methodology_note'])
        for method in (read('data/default-methodology.json')['defaults'][BITUMEN],
                       registry['default_methodology'], single['default_methodology']):
            self.assertEqual(method['declared_value'], f'{value} kg CO2e/t')
            self.assertEqual(method['source_basis'][0]['url'], url)
        row = csv_record('data/datasets.csv', 'code', BITUMEN)
        self.assertEqual((Decimal(row['gwp_total_kg_co2e']), row['source_url']), (value, url))
        short_id = 'POLCA-GWP-BITUMEN-ROAD-2026'
        short = next(r for r in read('data/polca-gwp-v2026-1.json')['records'] if r['id'] == short_id)
        row = csv_record('data/polca-gwp-v2026-1.csv', 'id', short_id, ';')
        self.assertEqual((short['value'], short['source_url']), (value, url))
        self.assertEqual((pl_decimal(row['wartosc']), row['podstawa']), (value, record['source_name']))
        hotspots = read('data/mma-hotspots.json')['kluczowe źródło wpływus']
        hot = next(r for r in hotspots if r['id'] == 'bitumen')['values'][0]
        self.assertEqual((hot['value'], hot['source_url']), (f'{value} kg CO2e/t', url))

    def test_no_obsolete_road_bitumen_value_in_text(self):
        stale = re.compile(r'(?<![\d.,])450\s*kg\s*CO[2₂]e\s*/\s*t\b', re.I)
        bitumen = re.compile(r'bitum|lepiszcz|asfalt', re.I)
        for path in ROOT.rglob('*'):
            if path.suffix.lower() in {'.html', '.json', '.csv', '.js', '.py', '.md'}:
                text = path.read_text()
                for match in stale.finditer(text):
                    context = text[max(0, match.start() - 200):match.end() + 200]
                    self.assertIsNone(bitumen.search(context), str(path.relative_to(ROOT)))

    def test_mma_results_follow_the_route_and_recipe(self):
        profile = read('data/mma-client-example.json')
        activity = profile['activity_data']
        mass = activity['recipe_kg_per_mg']
        km = activity['transport_km']
        deliveries = {'virgin_aggregate': 'virgin_aggregate_to_plant', 'rap': 'rap_to_plant',
                      'road_bitumen_35_50': 'bitumen_to_plant', 'limestone_filler': 'filler_to_plant',
                      'additives': 'additives_to_plant'}
        tkm = sum(Decimal(mass[item]) * km[route] for item, route in deliveries.items()) / 1000
        factor = self.records[TRUCK]['value']
        for background in profile['background_factors']:
            record = self.records[background['dataset_code']]
            self.assertEqual(background['value'], record['value'])
            if 'source_url' in background:
                self.assertEqual(background['source_url'], record['source_url'])
        result = profile['module_results_kg_co2e_per_mg']
        materials = {'virgin_aggregate': 'POLCA-AGG-PL-CRUSHED-DEFAULT-2026',
                     'rap': 'POLCA-RAP-PROCESSING-DEFAULT-2026', 'road_bitumen_35_50': BITUMEN,
                     'limestone_filler': 'POLCA-FILLER-LIMESTONE-DEFAULT-2026'}
        a1 = sum(mass[item] * self.records[code]['value'] for item, code in materials.items()) / Decimal(1000)
        self.assertEqual(result['A1'], round(a1, 3))
        for module, distance in [('A2', tkm), ('A4', km['plant_to_site_a4']), ('C2', km['rap_to_processing_c2'])]:
            self.assertEqual(result[module], round(distance * factor, 3))
        production = activity['production_a3']
        scenario = activity['scenario_a5_c_d']
        diesel = self.records['POLCA-FUEL-DIESEL-DEFAULT-2026']['value']
        electricity = self.records['POLCA-EN-PL-LCA-2024']['value']
        a3 = (production['natural_gas_m3_per_mg'] * self.records['POLCA-FUEL-NATURAL-GAS-DEFAULT-2026']['value']
              + production['electricity_kwh_per_mg'] * electricity + production['diesel_l_per_mg'] * diesel)
        a1_a3 = a1 + tkm * factor + a3
        a4 = km['plant_to_site_a4'] * factor
        a5 = (scenario['paving_diesel_l_per_mg'] * diesel + a1_a3 * scenario['installation_waste_percent'] / 100
              + scenario['tack_coat_emulsion_kg_per_mg'] * self.records['POLCA-EMULSION-TACK-COAT-DEFAULT-2026']['value'])
        c1 = scenario['milling_diesel_l_per_mg'] * diesel
        c3 = scenario['rap_processing_electricity_kwh_per_mg'] * electricity + scenario['rap_processing_diesel_l_per_mg'] * diesel
        c1_c4 = c1 + km['rap_to_processing_c2'] * factor + c3 + result['C4']
        ac = a1_a3 + a4 + a5 + c1_c4
        d = scenario['module_d_credit_kg_co2e_per_mg']
        for module, expected in {'A3': a3, 'A1-A3': a1_a3, 'A5': a5, 'C1': c1, 'C3': c3, 'C1-C4': c1_c4,
                                 'A-C_without_D': ac, 'D': d, 'net_with_D': ac + d}.items():
            self.assertEqual(result[module], round(expected, 3), module)
        indicators = profile['en15804_a2_indicators']
        for group, total in [('A1-A3', a1_a3), ('A4-A5', a4 + a5), ('C1-C4', c1_c4), ('D', d)]:
            self.assertEqual(indicators['GWP-total'][group], round(total, 3))
        shares = profile['non_transport_gwp_shares']
        transport = self.records[TRUCK]['source_trace'][0]
        non_transport = {'A1': a1, 'A3': a3, 'A5': a5, 'C1': c1, 'C3': c3, 'C4': result['C4']}
        for i, key in enumerate(shares['components']):
            source_factor = transport[f'gwp_{key.split("-")[1]}_kg_co2e']
            for group, stages, work in (
                ('A1-A3', ('A1', 'A3'), tkm),
                ('A4-A5', ('A5',), km['plant_to_site_a4']),
                ('C1-C4', ('C1', 'C3', 'C4'), km['rap_to_processing_c2']),
            ):
                estimate = work * source_factor + sum(non_transport[k] * shares[k][i] for k in stages)
                self.assertEqual(indicators[key][group], round(estimate, 3), (key, group))
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
        table, = card.xpath('//main//table')
        self.assertIn('kg CO₂e/t', table.xpath('string(thead)'))
        for entry in sources:
            row, = table.xpath('tbody/tr[th/a[@href=$url]]', url=entry['url'])
            self.assertEqual(row.xpath('string(th)'), entry['name'])
            self.assertEqual(row.xpath('td/text()')[:2], [entry['manufacturer'], entry['product']])
            self.assertEqual(pl_decimal(row.xpath('string(td[last()])')), entry['gwp_total_kg_co2e'])

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
