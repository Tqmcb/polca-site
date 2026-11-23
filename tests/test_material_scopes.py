import json
import unittest
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]


class MaterialScopeTests(unittest.TestCase):
    def test_current_material_records_and_cards_describe_both_perspectives(self):
        catalog = json.loads((ROOT / 'data/portal-catalog.json').read_text())
        aggregates = [r for r in catalog['datasets'] if r['category_id'] == 'kruszywa']
        self.assertEqual(len(aggregates), 4)
        filler = next(r for r in catalog['datasets'] if r['id'] == 'POLCA-FILLER-LIMESTONE-DEFAULT-2026')
        for item in [*aggregates, filler]:
            with self.subTest(record=item['id']):
                download = ROOT / item['downloads'][0]['href'].lstrip('/')
                record = json.loads(download.read_text())['record']
                card = html.parse(str(ROOT / item['href'].lstrip('/')))
                rows = {row.findtext('dt'): row.findtext('dd') for row in card.xpath('//dl/div[dt and dd]')}
                self.assertEqual(record, item)
                self.assertEqual(rows['Zakres u producenta'], record['production_scope'])
                contexts = record['application_contexts']
                self.assertEqual(contexts['constituent']['module'], 'A1')
                self.assertEqual(contexts['constituent']['transport_module'], 'A2')
                if item is filler:
                    self.assertEqual(list(contexts), ['constituent'])
                    self.assertIn('wypełniacza', record['boundary'])
                else:
                    self.assertEqual(record['boundary'], 'A1-A3')
                    self.assertIn('oszacowania', record['production_scope'])
                    self.assertEqual(contexts['unbound_base']['module'], 'A1-A3')
                    self.assertEqual(contexts['unbound_base']['transport_module'], 'A4')
                for context in contexts.values():
                    self.assertEqual(rows[context['label']], context['description'])
