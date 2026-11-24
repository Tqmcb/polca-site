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
        records = doc.xpath('//table/tbody/tr')
        download, = set(doc.xpath('//main//a[@download]/@href'))
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

    def test_guide_links_to_card(self):
        guide = html.fromstring((ROOT / 'zastosowanie-epd-cpr.html').read_bytes())
        self.assertIn('/' + ROUTE, guide.xpath('//main//a/@href'))
