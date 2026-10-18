"""Portal navigation and integrity checks across generated and retained pages."""
import json,unittest,re
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit,unquote
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
PAGES=sorted(ROOT.rglob('*.html'))
class PortalTests(unittest.TestCase):
 def test_document_structure_and_machine_metadata(self):
  for path in PAGES:
   text=path.read_text();doc=html.fromstring(text)
   with self.subTest(page=str(path.relative_to(ROOT))):
    for tag in ['html','head','body']:
     self.assertEqual(len(re.findall(r'<'+tag+r'(?:\s|>)',text,re.I)),1)
    for block in doc.xpath('//script[@type="application/ld+json"]|//script[@type="application/json"]'):
     json.loads(block.text)
 def test_local_links_and_assets(self):
  missing=[]
  for path in PAGES:
   doc=html.parse(str(path))
   for attr in ['href','src']:
    for href in doc.xpath('//@'+attr):
     u=urlsplit(href)
     if u.scheme in ['mailto','tel','javascript','data'] or (u.netloc and u.netloc not in ['polca.org.pl','www.polca.org.pl']):continue
     target=ROOT/unquote(u.path).lstrip('/') if u.path.startswith('/') or u.netloc else (path.parent/unquote(u.path) if u.path else path)
     target=target.resolve()
     if target.is_dir():target/= 'index.html'
     if not target.is_file():missing.append(f'{path.relative_to(ROOT)} -> {href}');continue
     if u.fragment and target.suffix=='.html':
      ids=html.parse(str(target)).xpath('//@id|//@name')
      if unquote(u.fragment) not in ids:missing.append(f'{path.relative_to(ROOT)} -> {href} (anchor)')
  self.assertEqual(missing,[],'\n'.join(missing))
 def test_shared_navigation_and_landmarks(self):
  for path in PAGES:
   d=html.parse(str(path))
   with self.subTest(page=str(path.relative_to(ROOT))):
    self.assertEqual(len(d.xpath('//header[contains(@class,"portal-header")]')),1)
    self.assertEqual(len(d.xpath('//main')),1)
    self.assertEqual(len(d.xpath('//*[@id="main"]')),1)
    self.assertEqual(len(d.xpath('//h1')),1)
    self.assertEqual(len(d.xpath('//footer[contains(@class,"portal-footer")]')),1)
    self.assertEqual(len(d.xpath('//*[@id="portal-navigation"]')),1)
 def test_energy_profile_values(self):
  profile=json.loads((ROOT/'data/energia-pl-2025-v3/profil-37.json').read_text(),parse_float=Decimal)
  d=html.parse(str(ROOT/'energia-polska-2025-v3.html'))
  rows={r.get('data-code'):r for r in d.xpath('//tr[@data-code]')}
  self.assertEqual(len(rows),37)
  for item in profile['indicators']:
   self.assertEqual(Decimal(rows[item['code']].get('data-value')),item['value_per_kWh'])
   self.assertEqual(rows[item['code']].get('data-unit'),item['impact_unit'])
if __name__=='__main__':unittest.main()
