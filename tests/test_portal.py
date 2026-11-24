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
    self.assertEqual(d.xpath('//footer//div[h2="Pomoc"]/a[@href="/pytania.html"]/following-sibling::*[1]'
                             '[self::a and @href="/blog.html"]/text()'), ['Artykuły i wyjaśnienia'])
    self.assertEqual(len(d.xpath('//*[@id="portal-navigation"]')),1)
 def test_energy_profile_values_for_current_and_archived_cards(self):
  for version in ('v3','v4','v5'):
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
     if version in ('v4','v5'):
      visible=rows[item['code']].xpath('./td[contains(@class,"en25-value")]')[0].text
      self.assertEqual(Decimal(visible.replace(',','.')), Decimal(format(float(item['value_per_kWh']),'.6g')))
 def test_kobize_table_units_follow_each_rows_scope(self):
  card = html.parse(str(ROOT / 'energia-polska-2025-v5.html'))
  table, = card.xpath('//*[@id="kobize"]//details//table')
  self.assertEqual(table.xpath('./thead/tr/th/text()'), ['Krok', 'Wartość', 'Jednostka'])
  self.assertEqual([row.xpath('./td[position() > 1]/text()') for row in table.xpath('./tbody/tr')], [
      ['670,0', 'kg CO₂ równ./MWh'], ['−120,7', 'kg CO₂ równ./MWh'],
      ['549,3', 'kg CO₂/MWh'], ['−79,1', 'kg CO₂/MWh'], ['470,2', 'kg CO₂/MWh'],
      ['+82,8', 'kg CO₂/MWh'], ['553', 'kg CO₂/MWh'],
  ])
 def test_calculator_embeds_current_full_profile(self):
  profile=json.loads((ROOT/'data/energia-pl-2025-v5/profil-37.json').read_text(),parse_float=Decimal)
  d=html.parse(str(ROOT/'oblicz-energie-2025.html'))
  embedded=json.loads(d.xpath('//*[@id="energy-profile-data"]')[0].text,parse_float=Decimal)
  self.assertEqual(embedded,profile)
  codes=d.xpath('//*[@data-energy-result]/@data-energy-result')
  self.assertEqual(codes,[i['code'] for i in profile['indicators']])
  self.assertEqual(len(codes),37)
  for link in ('/energia-polska-2025-v5.html', '/data/energia-pl-2025-v5/WARUNKI-WYKORZYSTANIA.txt'):
   self.assertIn(link,d.xpath('//main//a/@href'))
 def test_archive_button_identifies_calculator_results(self):
  for version in ('v3', 'v4'):
   with self.subTest(version=version):
    doc = html.parse(str(ROOT / f'energia-polska-2025-{version}.html'))
    button, = doc.xpath('//main//a[@href="/oblicz-energie-2025.html"]')
    self.assertEqual(button.text_content(), 'Otwórz panel aktualnej wersji v5')
    self.assertEqual(button.getnext().text_content(), 'Wyniki w panelu dotyczą wersji v5.')
 def test_historical_article_correction_date(self):
  doc = html.parse(str(ROOT / 'blog-en15804-a3-avs3plus.html'))
  self.assertIn('Opis mechanizmu przejściowego skorygowano 19 października 2026 r.', doc.xpath('string(//main)'))
 def test_full_energy_method_retains_release_headings_and_sources(self):
  doc=html.parse(str(ROOT/'oblicz-energie-2025.html'))
  method=doc.xpath('//details[@id="pelna-metoda"]')[0]
  download,=method.xpath('.//a[@download]/@href')
  self.assertEqual(download, '/data/energia-pl-2025-v5/METODA-I-ZMIANY.txt')
  source=(ROOT/download.lstrip('/')).read_text()
  card = html.parse(str(ROOT / 'energia-polska-2025-v5.html'))
  for text in (source, card.xpath('string(//*[@id="metoda"])'), method.text_content()):
   self.assertIn('mimo że wyznaczono je z krajowej struktury', text)
  self.assertEqual(method.xpath('.//h3/text()'),re.findall(r'^\d+\. .+$',source,re.M))
  self.assertEqual(method.xpath('.//a[starts-with(@href,"http")]/@href'),
                   re.findall(r'https?://[^\s<>");]+',source))
  self.assertNotIn('r..',method.text_content())
 def test_climate_panel_uses_profile_shares_and_grams_for_the_initial_quantity(self):
  profile=json.loads((ROOT/'data/energia-pl-2025-v5/profil-37.json').read_text(),parse_float=Decimal)
  per_kwh={item['code']:item['value_per_kWh'] for item in profile['indicators']}
  doc=html.parse(str(ROOT/'oblicz-energie-2025.html'))
  quantity=Decimal(doc.xpath('//*[@id="energy-quantity"]/@value')[0])
  cells=doc.xpath('//*[@data-energy-climate-part]')
  self.assertEqual({cell.get('data-energy-climate-part') for cell in cells},
                   {'GWP-fossil','GWP-biogenic','GWP-luluc'})
  for cell in cells:
   value=per_kwh[cell.get('data-energy-climate-part')]
   displayed_grams=Decimal(cell.text.replace(',','.'))
   expected_grams=value*quantity*1000
   self.assertLess(abs(displayed_grams-expected_grams),expected_grams*Decimal('0.000005'))
   displayed_share=cell.getprevious().text
   self.assertEqual(displayed_share,f'{100*value/per_kwh["GWP-total"]:.4f}%'.replace('.',','))
 def test_search_and_catalog_embed_current_model(self):
  profile=json.loads((ROOT/'data/energia-pl-2025-v5/profil-37.json').read_text(),parse_float=Decimal)
  total=next(i['value_per_kWh'] for i in profile['indicators'] if i['code']=='GWP-total')
  for name in ('datasety.html','szukaj.html'):
   with self.subTest(page=name):
    d=html.parse(str(ROOT/name))
    records=json.loads(d.xpath('//*[@id="portal-search-data"]')[0].text,parse_float=Decimal)
    current=[r for r in records if r['id']==profile['model_id']]
    self.assertEqual(len(current),1)
    self.assertEqual(current[0]['value'],total)
    self.assertEqual(current[0]['href'],'/energia-polska-2025-v5.html')
    self.assertFalse(any(r['id'] in ('PL2025_PHYSICAL_DELIVERED_v3_REVIEW', 'PL2025_PHYSICAL_DELIVERED_v4') for r in records))
if __name__=='__main__':unittest.main()
