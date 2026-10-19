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
 def test_energy_profile_values_for_current_and_archived_cards(self):
  for version in ('v3','v4'):
   with self.subTest(version=version):
    profile=json.loads((ROOT/f'data/energia-pl-2025-{version}/profil-37.json').read_text(),parse_float=Decimal)
    d=html.parse(str(ROOT/f'energia-polska-2025-{version}.html'))
    elements=d.xpath('//tr[@data-code]')
    rows={r.get('data-code'):r for r in elements}
    self.assertEqual(len(elements),37)
    self.assertEqual(len(rows),37)
    total=next(i['value_per_kWh'] for i in profile['indicators'] if i['code']=='GWP-total')
    self.assertEqual(d.xpath('//div[@class="en25-metric"]/strong')[0].text, format(total,'.6f').replace('.',','))
    for item in profile['indicators']:
     self.assertEqual(Decimal(rows[item['code']].get('data-value')),item['value_per_kWh'])
     self.assertEqual(rows[item['code']].get('data-unit'),item['impact_unit'])
     if version=='v4':
      visible=rows[item['code']].xpath('./td[contains(@class,"en25-value")]')[0].text
      self.assertEqual(Decimal(visible.replace(',','.')), Decimal(format(float(item['value_per_kWh']),'.6g')))
 def test_calculator_embeds_current_full_profile(self):
  profile=json.loads((ROOT/'data/energia-pl-2025-v4/profil-37.json').read_text(),parse_float=Decimal)
  d=html.parse(str(ROOT/'oblicz-energie-2025.html'))
  embedded=json.loads(d.xpath('//*[@id="energy-profile-data"]')[0].text,parse_float=Decimal)
  self.assertEqual(embedded,profile)
  codes=d.xpath('//*[@data-energy-result]/@data-energy-result')
  self.assertEqual(codes,[i['code'] for i in profile['indicators']])
  self.assertEqual(len(codes),37)
  for link in ('/energia-polska-2025-v4.html', '/data/energia-pl-2025-v4/WARUNKI-WYKORZYSTANIA.txt'):
   self.assertIn(link,d.xpath('//main//a/@href'))
 def test_search_and_catalog_embed_current_model(self):
  profile=json.loads((ROOT/'data/energia-pl-2025-v4/profil-37.json').read_text(),parse_float=Decimal)
  total=next(i['value_per_kWh'] for i in profile['indicators'] if i['code']=='GWP-total')
  for name in ('datasety.html','szukaj.html'):
   with self.subTest(page=name):
    d=html.parse(str(ROOT/name))
    records=json.loads(d.xpath('//*[@id="portal-search-data"]')[0].text,parse_float=Decimal)
    current=[r for r in records if r['id']==profile['model_id']]
    self.assertEqual(len(current),1)
    self.assertEqual(current[0]['value'],total)
    self.assertEqual(current[0]['href'],'/energia-polska-2025-v4.html')
    self.assertFalse(any(r['id']=='PL2025_PHYSICAL_DELIVERED_v3_REVIEW' for r in records))
if __name__=='__main__':unittest.main()
