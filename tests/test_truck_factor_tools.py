import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TruckFactorInToolsTest(unittest.TestCase):
    def test_calculators_use_catalog_truck_factor(self):
        catalog = json.loads((ROOT / 'data/portal-catalog.json').read_text(encoding='utf-8'))
        value = str(next(r['value'] for r in catalog['datasets'] if r['id'] == 'POLCA-TRUCK-40T-DEFAULT-2026'))
        for path in ('js/kalkulator-kruszywa.js', 'js/kalkulator-mma.js'):
            factor = re.search(r'var EF_TRANSPORT = ([\d.]+);', (ROOT / path).read_text(encoding='utf-8')).group(1)
            self.assertEqual(factor, value, path)
        for path, select in (('kalkulator-kruszywa.html', 'aggSimpleEf'), ('transport-a4.html', 'transMode')):
            page = (ROOT / path).read_text(encoding='utf-8')
            options = re.search(rf'<select id="{select}".*?</select>', page, re.S).group(0)
            self.assertIn(f'value="{value}"', options, path)

    def test_transport_choices_match_page_options(self):
        page = (ROOT / 'transport-a4.html').read_text(encoding='utf-8')
        options = re.findall(r'<option value="([\d.]+)"', re.search(r'<select id="transMode".*?</select>', page, re.S).group(0))
        script = (ROOT / 'js/narzedzia.js').read_text(encoding='utf-8')
        allowed = re.findall(r"'([\d.]+)'", re.search(r"choice\('transMode', \[(.*?)\]", script).group(1))
        self.assertEqual(options, allowed)


if __name__ == '__main__':
    unittest.main()
