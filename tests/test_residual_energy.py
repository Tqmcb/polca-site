import csv
from decimal import Decimal
from pathlib import Path
import unittest

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
ROUTE = 'energia-rezydualna-polska-2025-v6.html'


def read_value(label):
    base, marker, power = label.replace(',', '.').partition(' × 10')
    if marker:
        power = power.translate(str.maketrans('⁻⁰¹²³⁴⁵⁶⁷⁸⁹', '-0123456789'))
        return Decimal(base).scaleb(int(power))
    return Decimal(base)


class ResidualElectricity(unittest.TestCase):
    def test_published_voltage_profiles(self):
        doc = html.fromstring((ROOT / ROUTE).read_bytes())
        records = doc.xpath('//section[@aria-labelledby="wskazniki"]//tbody/tr')
        download, = doc.xpath('//section[@aria-labelledby="wskazniki"]//a[@download]/@href')
        with (ROOT / download.lstrip('/')).open(encoding='utf-8-sig') as stream:
            data = list(csv.DictReader(stream, delimiter=';'))
        self.assertEqual(len(records), 37)
        self.assertEqual(len(data), 37)
        self.assertEqual(len({row['kod'] for row in data}), 37)
        for row, item in zip(records, data):
            self.assertEqual(item['na'], '1 kWh')
            self.assertIn(item['wskaznik'], row[0].text_content())
            self.assertIn(item['jednostka'], row[0].text_content())
            for cell, key in zip(row[1:], ('srednie_napiecie', 'niskie_napiecie')):
                value = Decimal(item[key])
                self.assertAlmostEqual(read_value(cell.text), value, delta=abs(value) * Decimal('0.00005'))
        totals = next(row for row in data if row['kod'] == 'GWP-total')
        self.assertEqual(Decimal(totals['srednie_napiecie']), Decimal('0.7966910117799431'))
        self.assertEqual(Decimal(totals['niskie_napiecie']), Decimal('0.8344047068544689'))
        self.assertEqual(doc.xpath('//dl//strong/text()'), ['0,796691', '0,834405'])

    def test_fuel_sensitivity_profiles(self):
        doc = html.parse(str(ROOT / ROUTE))
        section, = doc.xpath('//section[@aria-labelledby="porownanie-wegla"]')
        download, = section.xpath('.//a[@download]/@href')
        with (ROOT / download.lstrip('/')).open(encoding='utf-8-sig') as stream:
            data = list(csv.DictReader(stream, delimiter=';'))
        self.assertEqual(len(data), 74)
        tables = section.xpath('.//details//table')
        self.assertEqual(len(tables), 2)
        columns = ('bazowy_v6', 'wariant_krajowy_bez_podzialu_wegla', 'wariant_krajowy_i_pula_europejska_bez_podzialu_wegla')
        for voltage, table in zip(('średnie', 'niskie'), tables):
            items = [row for row in data if row['napiecie'] == voltage]
            self.assertEqual(len({row['kod'] for row in items}), 37)
            records = table.xpath('./tbody/tr')
            self.assertEqual(len(records), len(items))
            for item, row in zip(items, records):
                self.assertEqual(item['na'], '1 kWh')
                self.assertIn(item['kod'], row[0].text_content())
                self.assertIn(item['jednostka'], row[0].text_content())
                self.assertEqual(len(row), 4)
                for col, cell in zip(columns, row[1:]):
                    raw = Decimal(item[col])
                    self.assertAlmostEqual(read_value(cell.text), raw, delta=abs(raw) * Decimal('0.00005'))
                base, full = Decimal(item[columns[0]]), Decimal(item[columns[2]])
                self.assertEqual(Decimal(item['roznica_pelny_minus_bazowy']), full - base)
                pct = item['zmiana_pelny_wzgledem_bazowego_proc']
                if base:
                    self.assertEqual(Decimal(pct), (100 * (full - base) / base).quantize(Decimal('0.000001')))
                else:
                    self.assertEqual(pct, '')

    def test_guide_links_to_card(self):
        guide = html.fromstring((ROOT / 'zastosowanie-epd-cpr.html').read_bytes())
        self.assertIn('/' + ROUTE, guide.xpath('//main//a/@href'))
