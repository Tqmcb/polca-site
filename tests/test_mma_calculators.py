import csv
import json
import re
import subprocess
import unittest
from datetime import date
from pathlib import Path
from statistics import median

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
ENERGY = 'PL2025_PHYSICAL_DELIVERED_v4'
MIXES = ('ac11s', 'ac16w', 'sma11s')


def read(path):
    return json.loads((ROOT / path).read_text())


def by_id(rows, field='id'):
    return {row[field]: row for row in rows}


def read_csv(path, field, delimiter=','):
    with (ROOT / path).open(newline='') as stream:
        return by_id(csv.DictReader(stream, delimiter=delimiter), field)


def pl(value, decimals):
    return f'{value:.{decimals}f}'.replace('.', ',')


class CalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = """
            const {presets, distances, calculate} = require('./js/kalkulator-mma.js');
            const results = {};
            for (const [key, recipe] of Object.entries(presets)) {
                results[key] = calculate(recipe, distances);
            }
            console.log(JSON.stringify(results));
        """
        cls.results = json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT))
        cls.catalog = by_id(read('data/portal-catalog.json')['datasets'])
        cls.mma = html.parse(ROOT / 'kalkulator-mma.html')
        cls.aggregate = html.parse(ROOT / 'kalkulator-kruszywa.html')

    def test_primary_factors_and_sources_across_exports(self):
        factors = [
            ('AGG-PL-CRUSHED', 'AGG-HARD-CRUSHED', 3.99, ['706_Trzuskawica']),
            ('AGG-PL-LIMESTONE', 'AGG-LIMESTONE', 3.27, ['707_Trzuskawica']),
            ('AGG-PL-DOLOMITE', 'AGG-DOLOMITE', 3.91, ['EPD_03-05-2025']),
            ('AGG-PL-NATURAL', 'AGG-NATURAL', 3.86, ['674_CEMEX', 'pdf31.pdf']),
            ('FILLER-LIMESTONE', 'FILLER-LIMESTONE', 72, ['environdec.com/']),
            ('FUEL-DIESEL', 'DIESEL', 3.72, ['135.WO_i_WE_', '32022R0996', 'D2015000168001',
                                               'Mobile_Combustion', 'ar6/wg1', '32023R1185']),
            ('FUEL-NATURAL-GAS', 'NATURAL-GAS', 2.46, ['135.WO_i_WE_', 'Stationary_Combustion',
                                                        'ar6/wg1', '32023R1185']),
        ]
        legacy = by_id(read('data/datasets.json')['datasets'], 'code')
        short = by_id(read('data/polca-gwp-v2026-1.json')['records'])
        csv_records = read_csv('data/datasets.csv', 'code')
        csv_short = read_csv('data/polca-gwp-v2026-1.csv', 'id', ';')
        defaults = read('data/default-methodology.json')['defaults']
        hotspots = {v['dataset_code']: v for group in read('data/mma-hotspots.json')['kluczowe źródło wpływus']
                    for v in group['values'] if 'dataset_code' in v}
        for name, short_name, expected, source_identifiers in factors:
            with self.subTest(name=name):
                code = f'POLCA-{name}-DEFAULT-2026'
                short_id = f'POLCA-GWP-{short_name}-2026'
                record = self.catalog[code]
                card = html.parse(ROOT / record['href'][1:])
                single = read(f'data/datasets/{code}.json')['dataset']
                self.assertEqual(legacy[code], single)
                self.assertEqual(read(f'data/portal-records/{code}.json')['record'], record)
                trace = record['source_trace']
                self.assertEqual(trace, single['source_trace'])
                urls = [s['url'] for s in trace]
                self.assertEqual(len(urls), len(source_identifiers))
                for part in source_identifiers:
                    self.assertTrue(any(part in url for url in urls), part)
                self.assertTrue(set(urls) <= set(card.xpath('//main//a/@href')))
                for row in [record, single, short[short_id], csv_records[code], hotspots[code]]:
                    self.assertEqual(row['source_url'], urls[0])
                self.assertEqual(record['value'], expected)
                self.assertEqual(single['gwp_total_kg_co2e'], expected)
                self.assertEqual(float(csv_records[code]['gwp_total_kg_co2e']), expected)
                self.assertEqual(short[short_id]['value'], expected)
                self.assertEqual(float(csv_short[short_id]['wartosc'].replace(',', '.')), expected)
                self.assertEqual(float(hotspots[code]['value'].split()[0].replace(',', '.')), expected)
                if name.startswith('FUEL'):
                    for url in urls:
                        self.assertIn(url, record['methodology_note'])
                    continue
                self.assertEqual(defaults[code], single['default_methodology'])
                declared = defaults[code]['declared_value'].split()[0]
                self.assertEqual(float(declared.replace(',', '.')), expected)
                self.assertEqual(len(card.xpath('//main//table/tbody/tr')), len(trace))
                for entry in trace:
                    self.assertRegex(entry['url'], r'#page=\d+$')
                    row, = card.xpath('//main//table/tbody/tr[th/a[@href=$url]]', url=entry['url'])
                    self.assertEqual(row.xpath('string(th)'), entry['name'])
                    self.assertEqual(row.xpath('td/text()')[:3], [
                        entry['manufacturer'], entry['product'],
                        date.fromisoformat(entry['source_valid_until']).strftime('%d.%m.%Y')])
                    self.assertEqual(float(row.xpath('string(td[4])').replace(',', '.')),
                                     entry['gwp_total_kg_co2e'])
                self.assertEqual(round(median(s['gwp_total_kg_co2e'] for s in trace), 2), expected)

    def test_fuels_from_heating_values_and_emission_factors(self):
        def non_co2(methane, nitrous_oxide):
            # kg/TJ to g/MJ, with 100-year AR6 characterization factors.
            return (methane * 29.8 + nitrous_oxide * 273) / 1000

        diesel_mj_per_litre = 43.0 * 832 / 1000
        offroad = non_co2(4.15, 28.6)
        self.assertEqual(round(offroad, 2), 7.93)
        diesel = (74.1 + offroad + 21.9) * diesel_mj_per_litre / 1000
        self.assertEqual(round(diesel, 2), self.catalog['POLCA-FUEL-DIESEL-DEFAULT-2026']['value'])
        road = (74.1 + non_co2(3.9, 3.9) + 21.9) * diesel_mj_per_litre / 1000
        self.assertEqual(round(road, 2), 3.48)
        self.assertEqual(round(56.18 * 37.17 / 1000, 2), 2.09)
        gas = (56.18 + non_co2(5, 0.1) + 9.7) * 37.17 / 1000
        self.assertEqual(round(gas, 2), self.catalog['POLCA-FUEL-NATURAL-GAS-DEFAULT-2026']['value'])

    def test_binder_and_mass_of_each_recipe(self):
        # WT-2 2014 cz. I, Bmin in % of mix mass at 2.650 Mg/m³.
        bmin = dict(ac11s=5.8, ac16w=4.6, ac22p=4.0, sma11s=6.6,
                    bbtm11=6.0, pa11=6.0, ma11=6.8, ac16wma=4.6)
        self.assertEqual(set(self.results), set(bmin) | {'ac16ra30'})
        self.assertEqual(set(self.mma.xpath('//*[@id="mmaPreset"]/option/@value')),
                         set(self.results) | {'custom'})
        for key, result in self.results.items():
            with self.subTest(key=key):
                mass = result['m']
                self.assertEqual(sum(mass.values()), 1000)
                self.assertEqual(result['sumMass'], 1000)
                if key == 'ac16ra30':
                    self.assertEqual((mass['bitumen'], mass['ra']), (30, 300))
                else:
                    self.assertEqual(mass['bitumen'], bmin[key] * 10)
                    self.assertEqual(mass['ra'], 0)

    def test_catalog_modules_and_exports_equal_model(self):
        legacy = by_id(read('data/datasets.json')['datasets'], 'code')
        collection = by_id(read('data/datasets/POLCA-MMA-MIXES-2026.json')['datasets'], 'code')
        short = by_id(read('data/polca-gwp-v2026-1.json')['records'])
        csv_short = read_csv('data/polca-gwp-v2026-1.csv', 'id', ';')
        csv_records = read_csv('data/datasets.csv', 'code')
        products = by_id(read('data/mma-hotspots.json')['kluczowe źródło wpływus'])['products']
        hotspots = {row['dataset_code']: row for row in products['values'] if 'dataset_code' in row}
        for key in MIXES:
            with self.subTest(key=key):
                code = f'POLCA-MMA-{key.upper()}-2026'
                result = self.results[key]
                # The calculator JSON export retains six decimal places.
                modules = {k: round(result[v], 6) for k, v in
                           [('A1', 'a1'), ('A2', 'a2'), ('A3', 'a3'), ('A1_A3', 'total')]}
                total = modules['A1_A3']
                single = read(f'data/datasets/{code}.json')
                portal = read(f'data/portal-records/{code}.json')['record']
                for record in (legacy[code], single, collection[code], portal, self.catalog[code]):
                    self.assertEqual(record['gwp_modules_kg_co2e_per_t'], modules)
                    self.assertEqual(record['binder_content_pct_m_m'], result['m']['bitumen'] / 10)
                    self.assertEqual(record.get('value', record.get('gwp_total_kg_co2e')), total)
                    self.assertTrue(any('zarz%2047.pdf' in s['url'] for s in record['source_trace']))
                self.assertEqual(float(csv_records[code]['gwp_total_kg_co2e']), total)
                self.assertEqual(short[code]['value'], total)
                self.assertEqual(float(csv_short[code]['wartosc'].replace(',', '.')), total)
                self.assertEqual(float(hotspots[code]['value'].split()[0].replace(',', '.')), total)

    def test_component_factors_and_select_validation(self):
        def factor(code):
            return self.catalog['POLCA-' + code + '-DEFAULT-2026']['value']

        energy = round(self.catalog[ENERGY]['value'], 4)
        result = self.results['ac16w']
        components = by_id(result['a1items'], 'key')
        self.assertEqual(components['aggF']['gwp'], factor('AGG-PL-NATURAL'))
        self.assertEqual(components['filler']['gwp'], factor('FILLER-LIMESTONE'))
        self.assertEqual(components['bitumen']['gwp'], factor('BITUMEN-ROAD'))
        self.assertEqual(self.results['sma11s']['gwpAggC'], factor('AGG-PL-CRUSHED'))
        self.assertEqual(self.results['ma11']['gwpAggC'], factor('AGG-PL-LIMESTONE'))
        parameters = read('data/datasets/POLCA-MMA-LCI-DEFAULTS-2026.json')['dataset']
        materials = by_id(parameters['calculation_components']['raw_materials_A1'], 'code')
        for component in ['AGG-BASALT', 'AGG-LIMESTONE', 'AGG-NATURAL', 'FILLER-LIMESTONE']:
            material = materials[component]
            self.assertEqual(material['value_kg_co2e_per_t'], self.catalog[material['source']]['value'])
        self.assertEqual(result['el'], 2.5 * energy)
        for page, script, select, variable in (
            (self.mma, 'mma', 'mmaTypeAgg', 'aggTypeSel'),
            (self.aggregate, 'kruszywa', 'aggSimpleType', 'sType'),
        ):
            source = (ROOT / f'js/kalkulator-{script}.js').read_text()
            self.assertEqual(float(re.search(r'var EF_EL = ([\d.]+);', source)[1]), energy)
            allowed = re.search(rf'checkChoice\({variable}, \[(.*?)\]', source)[1]
            self.assertEqual(set(re.findall(r"'([\d.]+)'", allowed)),
                             set(page.xpath(f'//select[@id="{select}"]/option/@value')))
            self.assertNotIn('0,599', page.getroot().text_content())
            self.assertIn('/energia-polska-2025-v4.html', page.xpath('//a/@href'))
        source = (ROOT / 'js/kalkulator-kruszywa.js').read_text()
        self.assertEqual(float(re.search(r'var EF_DIESEL = ([\d.]+);', source)[1]),
                         factor('FUEL-DIESEL'))
        self.assertIn('electricity_kg_CO2e_per_kWh: EF_EL', source)
        self.assertNotIn('electricity_fossil_', source)
        options = self.aggregate.xpath('//select[@id="aggSimpleType"]/option')
        self.assertEqual(len(options), len({o.get('value') for o in options}))
        self.assertEqual({float(o.get('value')) for o in options if 'historyczna' in o.text},
                         {4.50, 3.80, 2.50})
        for label, code in [('wapienne łamane', 'AGG-PL-LIMESTONE'), ('naturalne', 'AGG-PL-NATURAL'),
                            ('dolomitowe', 'AGG-PL-DOLOMITE'), ('łamane twarde', 'AGG-PL-CRUSHED'),
                            ('Wypełniacz wapienny', 'FILLER-LIMESTONE')]:
            with self.subTest(label=label):
                value, = self.aggregate.xpath(
                    '//select[@id="aggSimpleType"]/option[contains(., $label)]/@value', label=label)
                self.assertEqual(float(value), factor(code))

    def test_static_results_and_inputs_match_selected_defaults(self):
        preset, = self.mma.xpath('//*[@id="mmaPreset"]/option[@selected]/@value')
        result = self.results[preset]
        self.assertEqual(self.mma.xpath('string(//*[@id="mmaTotal"])'), pl(result['total'], 2))
        for key in ('a1', 'a2', 'a3'):
            id_ = 'mma' + key.upper()
            self.assertEqual(self.mma.xpath(f'string(//*[@id="{id_}"])'), pl(result[key], 2))
            self.assertEqual(self.mma.xpath(f'string(//*[@id="{id_}pct"])'),
                             pl(result[key] / result['total'] * 100, 1))
        for key, value in result['m'].items():
            id_ = 'm' + ('RA' if key == 'ra' else key[0].upper() + key[1:])
            self.assertEqual(float(self.mma.xpath(f'string(//*[@id="{id_}"]/@value)')), value)
        value, = self.aggregate.xpath('//*[@id="aggSimpleType"]/option[@selected]/@value')
        self.assertEqual(self.aggregate.xpath('string(//*[@id="aggTotal"])'), pl(float(value), 2))
