import csv
import io
import json
import subprocess
import unittest
from pathlib import Path
from statistics import mean, median

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
KRUSZBET_NOTE = ('Deklaracja Kruszbet nie określa wariantu dla A1–A3; '
                 'zgodnie z regułą poLCA zaliczono ją do wariantu brutto.')


def read(path):
    return json.loads((ROOT / path).read_text())


def page(path):
    return html.parse(str(ROOT / path))


# Published A1–A3 GWP-total by declaration, including all recipes/plants.
CLASSES = {
    'C8/10': {'662': [148, 143]},
    'C12/15': {'662': [163, 158]},
    'C16/20': {'662': [188, 183]},
    'C20/25': {'566': [184], '662': [200, 195]},
    'C25/30': {'558': [255], '566': [189], '662': [219, 214]},
    'C30/37': {'447': [217, 209, 199, 210], '558': [193], '566': [213], '662': [226, 221]},
    'C35/45': {'565': [228], '662': [286, 281]},
    'C40/50': {'565': [245], '662': [312, 307]},
    'C50/60': {'662': [339, 333]},
}


def short_name(declaration):
    return declaration['name'].split()[1].split('/')[0]


class ConcreteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read('data/portal-catalog.json')
        cls.records = {r['id']: r for r in cls.catalog['datasets']}
        cls.source = read('data/concrete-epds.json')
        cls.calculator = page('kalkulator-betonu.html')
        cls.family = page('wyroby/26.html')
        cls.config = json.loads(cls.calculator.xpath('string(//*[@id="concrete-config"])'))
        cls.defaults = {field.get('name'): float(field.get('value'))
                        for field in cls.calculator.xpath('//form//input[@type="number"]')}
        for select in cls.calculator.xpath('//form//select'):
            cls.defaults[select.get('name')], = select.xpath('option[@selected]/@value')
        cls.defaults['cement_basis'], = cls.calculator.xpath('//input[@name="cement_basis" and @checked]/@value')

    def calculate(self, **overrides):
        script = """
            const {calculate, comparison, exportData, toCsv} = require('./js/kalkulator-betonu.js');
            const {inputs, config} = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
            try {
                const result = calculate(inputs, config);
                const data = exportData(inputs, config, result);
                console.log(JSON.stringify({result, comparison: comparison(result), data, csv: toCsv(data)}));
            } catch (e) {
                if (!(e instanceof RangeError)) throw e;
                console.log(JSON.stringify({error: e.message, field: e.field}));
            }
        """
        payload = dict(inputs=self.defaults | overrides, config=self.config)
        return json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT,
                                                  input=json.dumps(payload), text=True))

    def test_source_rows_and_publication_threshold(self):
        sources = {short_name(d): d for d in self.source['declarations'] if d['cement_basis'] == 'brutto'}
        self.assertEqual(set(sources), {'447', '558', '565', '566', '662'})
        self.assertEqual(set(self.config['references']), set(CLASSES))
        legacy = {r['code']: r for r in read('data/datasets.json')['datasets']}
        with (ROOT / 'data/datasets.csv').open(newline='') as stream:
            csv_records = {r['code']: r for r in csv.DictReader(stream)}
        for strength, expected in CLASSES.items():
            with self.subTest(strength=strength):
                actual = {key: [row for row in d['rows'] if row['strength_class'] == strength]
                          for key, d in sources.items()}
                self.assertEqual({key: [r['value'] for r in rows] for key, rows in actual.items() if rows}, expected)
                means = [mean(v) for v in expected.values()]
                ref = self.config['references'][strength]
                self.assertEqual((ref['n'], ref['min'], ref['max']), (len(means), min(means), max(means)))
                values = [v for rows in expected.values() for v in rows]
                self.assertEqual((ref['row_min'], ref['row_max']), (min(values), max(values)))
                code = f"POLCA-CONCRETE-{strength.replace('/', '-')}-EPD-PL-2026"
                if len(means) < 3:
                    self.assertIsNone(ref['median'])
                    self.assertNotIn(code, self.records)
                    self.assertNotIn(code, legacy)
                    self.assertNotIn(code, csv_records)
                    for path in (f'dane/{code.lower()}.html', f'data/datasets/{code}.json', f'data/portal-records/{code}.json'):
                        self.assertFalse((ROOT / path).exists(), path)
                    continue
                record = self.records[code]
                self.assertEqual(record['cement_basis'], 'brutto')
                for export in (ref, record, legacy[code], csv_records[code]):
                    self.assertEqual(export['basis_note'], KRUSZBET_NOTE)
                self.assertIn(KRUSZBET_NOTE, page(record['href'][1:]).xpath('string(//main)'))
                self.assertIn('brutto', record['title'])
                self.assertIn('brutto', record['methodology_note'])
                self.assertEqual(ref['median'], median(means))
                self.assertEqual((record['value'], record['unit'], record['boundary'], record['cpr_family_ids']),
                                 (median(means), 'kg CO₂e/m³', 'A1–A3', [26]))
                self.assertEqual(record['status_id'], 'reference')
                self.assertEqual(record, read(f'data/portal-records/{code}.json')['record'])
                self.assertEqual(legacy[code], read(f'data/datasets/{code}.json')['dataset'])
                self.assertEqual(float(csv_records[code]['gwp_total_kg_co2e']), median(means))
                self.assertEqual(record['source_trace'], legacy[code]['source_trace'])
                self.assertCountEqual([short_name(d) for d in record['source_trace']], expected)
                for trace in record['source_trace']:
                    key = short_name(trace)
                    doc = sources[key]
                    self.assertEqual(trace['gwp_total_kg_co2e'], mean(expected[key]))
                    self.assertEqual(trace['manufacturer'], doc['manufacturer'])
                    self.assertEqual(trace['cement_basis'], doc['cement_basis'])
                    if key == '662':
                        self.assertEqual(trace['basis_note'], KRUSZBET_NOTE)
                    self.assertEqual(trace['source_valid_until'], doc['source_valid_until'])
                    self.assertEqual(trace['url'], doc['url'] + '#page=' + str(actual[key][0]['page']))
                    self.assertEqual(trace['source_rows'], [dict(page=r['page'], value=r['value']) for r in actual[key]])

    def test_family_table_and_navigation(self):
        flat = self.family.xpath('//*[@id="beton-towarowy"]')[0]
        gross_table, net_table = flat.xpath('.//table')
        self.assertIn('Mediana brutto', gross_table.xpath('.//thead//th/text()'))
        self.assertIn(KRUSZBET_NOTE, flat.xpath('p/text()'))
        rows = gross_table.xpath('tbody/tr')
        self.assertEqual([row.xpath('string(th)') for row in rows], list(CLASSES))
        for row in rows:
            strength = row.xpath('string(th)')
            n, low, mid, high, raw = row.xpath('td/text()')
            ref = self.config['references'][strength]
            self.assertEqual((int(n), float(low.replace(',', '.')), float(high.replace(',', '.'))),
                             (ref['n'], ref['min'], ref['max']))
            self.assertEqual(mid, '—' if ref['median'] is None else f"{ref['median']:.1f}".replace('.', ','))
            self.assertEqual([float(s.replace(',', '.')) for s in raw.split('–')], [ref['row_min'], ref['row_max']])
        targets = set(flat.xpath('.//a/@href'))
        for d in self.source['declarations']:
            for row in d['rows']:
                self.assertIn(f"{d['url']}#page={row['page']}", targets)
        for group in self.source['excluded']:
            self.assertIn(group['reason'], flat.text_content())
            self.assertTrue(all(s['url'] in targets for s in group['sources']))
        excluded_list, = flat.xpath('.//h3[contains(., "pominięto")]/following-sibling::ul[1]')
        self.assertIn('Deklaracje podają wyniki dla grup według zawartości cementu, bez przypisania do klas '
                      'wytrzymałości; wynik podstawowy jest w wariancie netto (np. 87,2 kg CO₂e/m³ w deklaracji 434).',
                      excluded_list.xpath('string(li[starts-with(., "Lafarge ECOPact")])'))
        self.assertNotIn('Zabłoccy', excluded_list.text_content())
        self.assertIn('Deklaracja wydana w programie EPD Polska prowadzonym przez Multicert.', flat.text_content())
        self.assertNotIn('Mediana', net_table.xpath('string(thead)'))
        self.assertEqual([r.xpath('./*/text()') for r in net_table.xpath('tbody/tr')], [
            [c, 'Concrete-Zabłoccy sp.j.', 'EPD-P-01.09.2024', '1', v]
            for c, v in [('C20/25', '168,2'), ('C30/37', '212,9')]])
        cemex = excluded_list.xpath('li[starts-with(., "CEMEX")]/a')
        self.assertEqual({a.text: a.get('href').split('#')[-1] for a in cemex},
                         {'ITB-EPD 271': 'page=18', 'ITB-EPD 273': 'page=31', 'ITB-EPD 332': 'page=31',
                          'ITB-EPD 421': 'page=8', 'ITB-EPD 272': 'page=31'})
        for doc in [self.family, page('kalkulatory.html'), page('blog-beton-emisje-kalkulator.html')]:
            self.assertIn('/kalkulator-betonu.html', doc.xpath('//main//a/@href'))
        self.assertIn('/js/kalkulator-betonu.js', [url.split('?')[0] for url in self.calculator.xpath('//script/@src')])
        self.assertTrue(any(entry['data'] == '2026-11-24' and entry['link'] == '/wyroby/26.html#beton-towarowy'
                            for entry in read('data/rejestr-zmian.json')['wpisy']))

    def test_embedded_factors_and_selector_values(self):
        self.assertEqual(self.calculator.xpath('//label[input[@name="cement_basis"]]/text()'),
                         ['netto — wartość deklarowana w deklaracji SPC', 'brutto — informacja dodatkowa w deklaracji SPC'])
        self.assertEqual(self.calculator.xpath('string(//*[@id="concrete-omissions"])'),
                         'W obliczeniach pominięto wodę i domieszki. Katalog nie zawiera wskaźnika dla domieszek.')
        ids = {f'POLCA-CEMENT-CEM-{c}-SPC-PL-2025' for c in ['I', 'II', 'III', 'IV', 'V']}
        self.assertEqual(set(self.config['cements']), ids)
        aggregates = {f'POLCA-AGG-PL-{kind}-DEFAULT-2026' for kind in ['NATURAL', 'CRUSHED', 'LIMESTONE', 'DOLOMITE']}
        self.assertEqual(set(self.config['aggregates']), aggregates)
        self.assertEqual(self.config['processes'], dict(truck='POLCA-TRUCK-40T-DEFAULT-2026',
                         electricity='PL2025_PHYSICAL_DELIVERED_v5', gas='POLCA-FUEL-NATURAL-GAS-DEFAULT-2026',
                         diesel='POLCA-FUEL-DIESEL-DEFAULT-2026'))
        self.assertEqual(set(self.config['factors']), ids | aggregates | set(self.config['processes'].values()))
        for code, factor in self.config['factors'].items():
            keys = ['title', 'value', 'unit', 'href']
            if code in ids:
                keys.append('gwp_gross_kg_co2e')
            self.assertEqual(factor, {key: self.records[code][key] for key in keys})
        for select, keys in [('cement', ids), ('aggregate', aggregates), ('strength_class', CLASSES)]:
            self.assertEqual(set(self.calculator.xpath('//select[@name=$name]/option/@value', name=select)), set(keys))
        self.assertEqual(self.config['catalog_version'], self.catalog['catalog_version'])

    def test_default_recipe_matches_worked_example(self):
        self.assertEqual(self.defaults, dict(cement='POLCA-CEMENT-CEM-II-SPC-PL-2025', cement_basis='netto',
                         aggregate='POLCA-AGG-PL-NATURAL-DEFAULT-2026', strength_class='C30/37',
                         cement_kg=330, aggregate_kg=1850, admixtures_kg=0, cement_km=100,
                         aggregate_km=30, electricity_kwh=4, gas_m3=0, diesel_l=0))
        result = self.calculate()['result']
        energy = self.records[self.config['processes']['electricity']]['value']
        for key, value in dict(A1=163.231, A2=7.46055, A3=4 * energy).items():
            self.assertAlmostEqual(result['stages'][key], value)
        self.assertAlmostEqual(result['total'], sum(result['stages'].values()))
        self.assertAlmostEqual(result['cementShare'], 156.09 / result['total'] * 100)
        self.assertAlmostEqual(result['reference']['difference_from_median'], result['grossTotal'] - 210.875)
        gross = self.calculate(cement_basis='brutto')['result']
        self.assertAlmostEqual(gross['stages']['A1'], 209.431)
        self.assertAlmostEqual(gross['total'], result['grossTotal'])
        self.assertEqual(gross['reference'], result['reference'])
        blog = page('blog-beton-emisje-kalkulator.html')
        self.assertEqual(blog.xpath('string(//*[@data-example-gross])'), f"{gross['total']:.2f}".replace('.', ','))
        table = blog.xpath('//table[.//strong[contains(., "Suma uwzględnionych")]]')[0]
        blog_values = [float(row.xpath('string(td[@class="mono"][1])').replace(',', '.')) for row in table.xpath('tbody/tr')]
        modeled = [round(item['emission_kg_CO2eq_per_m3'], 2) for item in result['breakdown'][:5]]
        self.assertEqual(blog_values, modeled + [round(result['total'], 2)])

    def test_comparison_messages(self):
        for inputs, expected in [
            ({}, 'Klasa C30/37, liczba deklaracji: 4. Mediana: 210,9 kg CO₂e/m³. '
                 'Wynik receptury jest o 8,70 kg CO₂e/m³ wyższy od mediany.'),
            ({'cement_kg': 300}, 'Klasa C30/37, liczba deklaracji: 4. Mediana: 210,9 kg CO₂e/m³. '
                                 'Wynik receptury jest o 9,95 kg CO₂e/m³ niższy od mediany.'),
            ({'strength_class': 'C35/45'}, 'Klasa C35/45, liczba deklaracji: 2. Średnie z poszczególnych deklaracji '
             'mieszczą się w przedziale 228–283,5 kg CO₂e/m³. Wynik receptury jest o 8,43 kg CO₂e/m³ niższy '
             'od dolnej granicy przedziału. Pojedyncze wyniki mieszczą się w przedziale 228–286 kg CO₂e/m³.'),
            ({'strength_class': 'C8/10'}, 'Klasa C8/10, liczba deklaracji: 1. Średnia z jedynej deklaracji wynosi '
             '145,5 kg CO₂e/m³. Pojedyncze wyniki w tej deklaracji mieszczą się w przedziale 143–148 kg CO₂e/m³. '
             'Wynik receptury jest o 71,57 kg CO₂e/m³ wyższy od górnej granicy przedziału.')
        ]:
            with self.subTest(inputs=inputs):
                gross = '200,93' if inputs.get('cement_kg') == 300 else '219,57'
                prefix = f'Do porównania z deklaracjami przyjęto wariant brutto: wynik receptury wynosi {gross} kg CO₂e/m³. '
                for basis in ('netto', 'brutto'):
                    self.assertEqual(self.calculate(**inputs, cement_basis=basis)['comparison'], prefix + expected + ' ' + KRUSZBET_NOTE)
        within = self.calculate(strength_class='C35/45', cement_kg=350)
        self.assertIn('Wynik receptury mieści się w tym przedziale.', within['comparison'])

    def test_all_cement_factors_and_exported_bases(self):
        for code in self.config['cements']:
            for basis, key in [('netto', 'value'), ('brutto', 'gwp_gross_kg_co2e')]:
                with self.subTest(code=code, basis=basis):
                    run = self.calculate(cement=code, cement_basis=basis, cement_kg=1000, aggregate_kg=0,
                                         cement_km=0, electricity_kwh=0)
                    result, data = run['result'], run['data']
                    factor = self.records[code][key]
                    gross = self.records[code]['gwp_gross_kg_co2e']
                    self.assertEqual((result['total'], result['grossTotal']), (factor, gross))
                    self.assertEqual(result['breakdown'][0]['factor'], factor)
                    self.assertEqual(data['inputs']['cement_basis'], basis)
                    self.assertEqual(data['results_kg_CO2eq_per_m3']['gross_A1_A3'], gross)
                    self.assertEqual(data['epd_reference_kg_CO2eq_per_m3']['cement_basis'], 'brutto')
                    self.assertEqual(data['epd_reference_kg_CO2eq_per_m3']['basis_note'], KRUSZBET_NOTE)
                    rows = list(csv.reader(io.StringIO(run['csv']), delimiter=';'))
                    self.assertIn(['basis_note', KRUSZBET_NOTE], rows)
                    self.assertIn(['Wariant cementu', basis], rows)
                    self.assertIn(['A1–A3 brutto', str(gross)], rows)
                    self.assertIn(['Wariant porównania', 'brutto'], rows)

    def test_other_inputs_exports_and_range_only_class(self):
        run = self.calculate(cement=self.config['cements'][2], aggregate='POLCA-AGG-PL-DOLOMITE-DEFAULT-2026',
                             cement_kg=300, aggregate_kg=1700, admixtures_kg=7.25, cement_km=40, aggregate_km=60,
                             gas_m3=3, diesel_l=5, electricity_kwh=0, strength_class='C35/45')
        data = run['data']
        stages = run['result']['stages']
        for key, value in dict(A1=.3*398 + 1.7*3.91, A2=(.3*40 + 1.7*60)*.0843, A3=3*2.46 + 5*3.72).items():
            self.assertAlmostEqual(stages[key], value)
        self.assertIsNone(data['epd_reference_kg_CO2eq_per_m3']['median'])
        self.assertIsNone(data['epd_reference_kg_CO2eq_per_m3']['difference_from_median'])
        self.assertEqual(data['inputs']['admixtures_kg'], 7.25)
        self.assertAlmostEqual(data['results_kg_CO2eq_per_m3']['climate_estimate_A1_A3'], sum(stages.values()))
        rows = list(csv.reader(io.StringIO(run['csv']), delimiter=';'))
        self.assertIn(['Masa domieszek [kg]', '7,25'], rows)
        self.assertIn(['Odległość dostawy cementu [km]', '40'], rows)
        self.assertIn(['Odległość dostawy kruszywa [km]', '60'], rows)
        self.assertIn(['C35/45', '2', '228', '', '283,5', '', '228', '286', ''], rows)
        self.assertIn(['A1–A3', str(round(run['result']['total'], 6)).replace('.', ',')], rows)
        for row in data['results_kg_CO2eq_per_m3']['breakdown']:
            self.assertEqual(data['factors'][row['record_id']], self.config['factors'][row['record_id']])
            self.assertTrue(any(row['record_id'] in cells for cells in rows))

    def test_material_tables_use_the_published_gross_medians(self):
        source = 'mediana deklaracji ITB, wariant brutto'
        for tool in ('gwp-materialow', 'wskazniki-emisji'):
            doc = page(tool + '.html')
            script = (ROOT / 'js' / (tool + '.js')).read_text()
            self.assertIn(KRUSZBET_NOTE, doc.xpath('string(//main)'))
            self.assertFalse(doc.xpath('//tr[td[1]="Beton C20/25"]'))
            self.assertNotIn('Beton C20/25', script)
            for strength in ('C25/30', 'C30/37'):
                label = 'Beton ' + strength
                value = f"{self.config['references'][strength]['median']:.1f}"
                listed = value.replace('.', ',')
                row, = doc.xpath('//tr[td[1]=$label]', label=label)
                self.assertIn(listed, row.xpath('string(td[2])'))
                self.assertEqual(row.xpath('string(td[last()])'), source)
                line, = [line for line in script.splitlines() if label in line]
                self.assertIn(source, line)
                self.assertIn(f'gwp: {value},' if tool == 'gwp-materialow' else f"value: '{listed}'", line)

    def test_invalid_inputs_and_zero_result(self):
        for field in self.calculator.xpath('//form//input[@type="number"]'):
            name = field.get('name')
            label = field.getparent().text.split(' [')[0]
            with self.subTest(field=name):
                self.assertEqual(self.calculate(**{name: -1}),
                                 dict(field=name, error=f'{label}: należy podać liczbę nie mniejszą niż 0.'))
        for field, invalid in [('cement_kg', None), ('diesel_l', '')]:
            with self.subTest(field=field):
                self.assertEqual(self.calculate(**{field: invalid})['field'], field)
        for field, label in [('cement', 'rodzaj cementu'), ('aggregate', 'rodzaj kruszywa'),
                             ('strength_class', 'klasę wytrzymałości')]:
            with self.subTest(field=field):
                self.assertEqual(self.calculate(**{field: 'missing'}),
                                 dict(field=field, error=f'Należy wybrać {label} z listy.'))
        self.assertIn('error', self.calculate(cement_kg=1e300, cement_km=1e300))
        self.assertEqual(self.calculate(cement_basis='nieznany')['field'], 'cement_basis')
        zero = self.calculate(cement_kg=0, aggregate_kg=0, electricity_kwh=0, admixtures_kg=2)['result']
        self.assertEqual(zero['total'], 0)
        self.assertIsNone(zero['cementShare'])
