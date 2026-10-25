#!/usr/bin/env python3
"""Build static portal pages and shared navigation. Requires lxml for legacy HTML."""
from pathlib import Path
import json, html as h, re, argparse
from urllib.parse import urlsplit, unquote
from collections import Counter
from lxml import html, etree
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'data/portal-catalog.json').read_text())
COPY=json.loads((ROOT/'content/portal-pages.json').read_text())
GENERATED=set()
def e(x): return h.escape(str(x if x is not None else ''),quote=True)
def a(label,href,cls='',extra=''):return f'<a href="{e(href)}"'+(f' class="{e(cls)}"' if cls else '')+f' {extra}>{e(label)}</a>'
def links(items,cls='portal-list'):return f'<ul class="{cls}">'+''.join('<li>'+a(x['label'],x['href'])+'</li>' for x in items)+'</ul>'
NAV=[('Wyroby','/wyroby.html','products'),('Dane','/datasety.html','data'),('Kalkulatory','/kalkulatory.html','tools'),('Jak korzystać','/jak-korzystac.html','guide'),('Metody i źródła','/metodyka.html','methods')]
def group(path):
 if path.startswith(('wyroby/','c-pcr/')) or path=='wyroby.html':return 'products'
 if path.startswith('dane/') or path in ['datasety.html','energia-polska-2025-v3.html','energia-polska-2025-v4.html','pobierz.html','dane-wspolne.html']:return 'data'
 if 'kalkulat' in path or path in ['narzedzia.html','oblicz-energie-2025.html']:return 'tools'
 if path in ['jak-korzystac.html','pytania.html','zastosowanie-danych.html','slad-weglowy-czy-srodowiskowy.html','porownanie-baz.html','zastosowanie-epd-cpr.html']:return 'guide'
 if path.startswith(('metody','konsultacje/')) or path in ['wiarygodnosc.html','podstawy-normatywne.html']:return 'methods'
 return ''
def header(path):
 nav=''.join(a(title,url,'is-active' if g==group(path) else '', 'aria-current="page"' if path==url[1:] else '') for title,url,g in NAV)
 return f'''<a class="portal-skip-link" href="#main">Przejdź do treści</a><header class="portal-header"><div class="portal-shell"><a class="portal-brand" href="/" aria-label="poLCA — strona główna">po<span>LCA</span><small>Dane środowiskowe dla Polski</small></a><button class="portal-menu-toggle" type="button" aria-expanded="false" aria-controls="portal-navigation" hidden>Menu</button><nav class="portal-nav" id="portal-navigation" aria-label="Główna nawigacja">{nav}</nav><a class="portal-search-link" href="/szukaj.html">Szukaj</a></div></header>'''
def footer():return '''<footer class="portal-footer"><div class="portal-shell"><div><a class="portal-brand" href="/">po<span>LCA</span></a><p>Dane i modele do oceny cyklu życia.</p><p>Multicert Sp. z o.o.<br>Operator programu EPD Polska</p></div><div><h2>Dane i obliczenia</h2><a href="/wyroby.html">Rodziny wyrobów</a><a href="/dane-wspolne.html">Energia, paliwa i transport</a><a href="/datasety.html">Katalog danych</a><a href="/kalkulatory.html">Kalkulatory</a><a href="/pobierz.html">Pliki do pobrania</a></div><div><h2>Pomoc w doborze</h2><a href="/jak-korzystac.html">Jak korzystać</a><a href="/pytania.html">Pytania i odpowiedzi</a><a href="/metodyka.html">Metody i źródła</a></div><div><h2>O projekcie</h2><a href="/o-polca/">O poLCA</a><a href="/rejestr-zmian.html">Rejestr zmian</a><a href="/o-polca/cytowanie.html">Jak cytować</a><a href="mailto:info@epd.org.pl">info@epd.org.pl</a></div></div><div class="portal-shell portal-footer-bottom"><span>© 2026 Multicert</span><span>Warunki wykorzystania opisano przy zbiorach.</span><a href="https://epd.org.pl/">Program EPD Polska</a></div></footer>'''
def crumb(title,parent=None):
 return '<nav class="portal-breadcrumbs" aria-label="Ścieżka strony">'+a('Strona główna','/')+'<span aria-hidden="true">/</span>'+((a(parent[0],parent[1])+'<span aria-hidden="true">/</span>') if parent else '')+f'<span aria-current="page">{e(title)}</span></nav>'
def page(path,title,lead,body,parent=None,attrs='',home=False,head_extra='',pagehead=True):
 mainhead='' if home else crumb(title,parent)+('' if not pagehead else f'<header class="portal-pagehead"><h1>{e(title)}</h1><p class="portal-lead">{e(lead)}</p></header>')
 home_css='<link rel="stylesheet" href="/assets/home.css?v=20261021topics">' if home else ''
 main_class='portal-main home-main' if home else 'portal-main portal-shell'
 out=f'''<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — poLCA</title><meta name="description" content="{e(lead)}"><link rel="canonical" href="https://polca.org.pl/{e(path) if path!='index.html' else ''}"><meta property="og:title" content="{e(title)} — poLCA"><meta property="og:description" content="{e(lead)}"><meta property="og:type" content="website"><meta property="og:url" content="https://polca.org.pl/{e(path) if path!='index.html' else ''}"><link rel="stylesheet" href="/assets/portal.css?v=20261020design">{home_css}<script src="/js/portal.js?v=20261019cpr" defer></script>{head_extra}</head><body class="portal">{header(path)}<main id="main" class="{main_class}" {attrs}>{mainhead}{body}</main>{footer()}</body></html>'''
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(out+'\n');GENERATED.add(path)
def num(v):return format(v,'.6g').replace('.',',')
def status(r):return f'<span class="portal-status portal-status-{e(r.get("status_id",""))}">{e(r.get("status_label",""))}</span>'
def row(r):
 val=f'<div class="portal-result-value"><strong>{e(num(r["value"]))}</strong><small>{e(r.get("unit"))}</small><small>{e(r.get("indicator_label"))}</small></div>' if isinstance(r.get('value'),(int,float)) else ''
 kind={'dataset':'Dane','tool':'Kalkulator','method':'Metoda i instrukcja','article':'Artykuł'}.get(r['kind'],'Zasób')
 return f'''<article class="portal-result" data-record-id="{e(r['id'])}"><div><div class="portal-result-meta"><span>{kind}</span><span>{e(r.get('category_label',''))}</span>{('<span>'+e(r['year'])+'</span>') if r.get('year') else ''}</div><h2>{a(r['title'],r['href'],'portal-result-title')}</h2><p class="portal-result-description">{e(r.get('description',''))}</p><div class="portal-result-meta">{status(r)}<span>{e(' · '.join(r.get('formats',[])))}</span></div></div>{val}</article>'''
def searchform():return '''<form class="portal-search" action="/szukaj.html" method="get" role="search"><label for="q">Wyszukaj dane, kalkulator lub odpowiedź</label><div class="portal-search-control"><input id="q" type="search" name="q" placeholder="Np. energia 2025, cement, ślad węglowy" autocomplete="off"><button type="submit">Szukaj</button></div></form>'''
def select(name,label,options):return f'<label for="filter-{name}">{label}</label><select id="filter-{name}" name="{name}"><option value="">Wszystkie</option>'+''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in options)+'</select>'
def build_catalog(all=False):
 records=CAT['datasets']+CAT['resources'] if all else CAT['datasets'];path='szukaj.html' if all else 'datasety.html'
 cats={r['category_id']:r['category_label'] for r in records if r.get('category_id')};years=sorted({r['year'] for r in records if r.get('year')},reverse=True);statuses={r['status_id']:r['status_label'] for r in records if r.get('status_id')}
 families=json.loads((ROOT/'data/cpr-families.json').read_text())['families']
 filters=select('family','Rodzina wyrobu',[(f['id'],str(f['id'])+' — '+f['label']) for f in families])+select('category','Temat',cats.items())+select('year','Rok odniesienia',[(y,y) for y in years])+select('status','Status',statuses.items())
 if all:filters=select('kind','Rodzaj zasobu',[('dataset','Dane'),('tool','Kalkulatory'),('method','Metody i instrukcje'),('article','Artykuły')])+filters
 body=f'''<div class="portal-catalog-layout"><form id="catalog-filters" action="/{path}" method="get"><label for="catalog-query">{'Szukaj w całym portalu' if all else 'Szukaj w danych'}</label><div class="portal-search-control"><input id="catalog-query" type="search" name="q" placeholder="Wpisz nazwę lub pytanie"><button type="submit">Szukaj</button></div><details class="portal-filters" open><summary>Zawęź wyniki</summary><div>{filters}<button type="reset">Wyczyść filtry</button></div></details></form><div class="portal-results-panel"><p id="result-count" role="status" aria-live="polite">Wyniki: {len(records)}</p><noscript><p>Filtrowanie wymaga włączenia JavaScript. Poniżej znajdziesz pełną listę; możesz użyć funkcji szukania w przeglądarce.</p></noscript><div id="catalog-results">{''.join(row(r) for r in records)}</div><div id="catalog-empty" class="portal-callout" hidden><h2>Brak wyników dla tych ustawień</h2><p>Spróbuj krótszej nazwy lub usuń filtry. Pomoc w doborze danych znajdziesz w <a href="/jak-korzystac.html">przewodniku</a>.</p><button type="button" data-reset-filters>Wyczyść wyszukiwanie</button></div></div></div><script id="portal-search-data" type="application/json">{json.dumps(records,ensure_ascii=False).replace('<','\\u003c')}</script>'''
 if not all:body='<p>Możesz też zacząć od <a href="/wyroby.html">rodzaju wyrobu</a> lub wybrać <a href="/dane-wspolne.html">energię, paliwa i transport</a>.</p><span id="referencyjne-szczegoly"></span>'+body
 page(path,'Szukaj w poLCA' if all else 'Katalog danych','Znajdź dane, kalkulator, metodę lub odpowiedź.' if all else 'Wybierz temat i sprawdź rok, zakres oraz status danych przed użyciem.',body,attrs=f'data-catalog-mode="{"all" if all else "datasets"}"')
def sections(secs):
 out=[]
 for i,s in enumerate(secs):
  block=f'<section class="portal-prose" id="{e(s.get("id", "sekcja-"+str(i+1)))}"><h2>{e(s["title"])}</h2>'+''.join(f'<p>{e(p)}</p>' for p in s.get('paragraphs',[]))
  if s.get('table'):
   t=s['table'];block+='<p class="portal-scroll-hint">Przewiń tabelę w bok, aby zobaczyć wszystkie kolumny.</p><div class="portal-table-wrap" tabindex="0" role="region" aria-label="'+e(s['title'])+' — tabela przewijana"><table><thead><tr>'+''.join('<th scope="col">'+e(x)+'</th>' for x in t['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+e(x)+'</th>') if j==0 else '<td>'+e(x)+'</td>' for j,x in enumerate(row))+'</tr>' for row in t['rows'])+'</tbody></table></div>'
  out.append(block+links(s.get('links',[]))+'</section>')
 return ''.join(out)
def build_copy():
 for c in COPY['pages']:
  toc=links([{'label':sec['title'],'href':'#'+sec.get('id','sekcja-'+str(i+1))} for i,sec in enumerate(c['sections'])], 'portal-subnav')
  body='<div class="portal-reading">'+toc+sections(c['sections'])+'</div>'
  page(c['path'],c['title'],c['lead'],body)
def build_cards():
 for r in CAT['datasets']:
  if not r['href'].startswith('/dane/'):continue
  fields=[('Rodzaj wskaźnika',r.get('indicator_label')),('Jednostka',r.get('unit')),('Rok',r.get('year')),('Znaczenie roku',{'reference':'Rok danych','publication':'Rok publikacji','application':'Rok zastosowania'}.get(r.get('year_type'),'')),('Obszar',r.get('geography')),('Zakres',r.get('boundary')),('Status',r.get('status_label')),('Identyfikator',r['id'])]
  meta='<dl class="portal-metadata">'+''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in fields if v is not None and v!='')+'</dl>'
  value=(f'<p class="portal-dataset-value"><strong>{e(num(r["value"]))}</strong> <span>{e(r.get("unit"))}</span></p><p>{e(r.get("indicator_label"))}</p>') if isinstance(r.get('value'),(int,float)) else '<p>Zestaw parametrów modelu. Szczegóły zawiera plik danych.</p>'
  downloads='<ul class="portal-downloads">'+''.join('<li>'+a(x['label'],x['href'],extra='download')+f'<span>{e(x["format"])}</span></li>' for x in r['downloads'])+'</ul>'
  source=a(r['source_name'],r['source_url']) if r.get('source_url') else e(r.get('source_name',''))
  more=links([{'label':x['title'],'href':x['href']} for x in CAT['datasets'] if x['id'] in r.get('related_ids',[])])
  notes=[]
  if r['id']=='POLCA-EN-PL-LCA-2024':notes.append('Wartość 0,599 dotyczy składnika kopalnego wpływu na klimat. Informacyjna suma w pełnym modelu 2024 wynosi 0,600 kg CO₂e/kWh. Rekord do pobrania zachowuje rozróżnienie rodzaju wskaźnika.')
  if r['id']=='KOBIZE-EN-PL-ENDUSER-2024':notes.append('Wartość dotyczy emisji CO₂ u odbiorcy końcowego, w granicach opisanych w publikacji KOBiZE. Do pełnej oceny cyklu życia energii służy odrębny profil środowiskowy.')
  if r.get('status_id') in ['proxy','reference','earlier_model','control']:notes.append('Dobór do konkretnego obliczenia wymaga zgodności jednostki, granic i roku. Status opisuje tę pozycję katalogu; źródło i warunki stosowania są wskazane w pliku oraz dokumentacji.')
  body=f'<div class="portal-detail-layout"><div><section class="portal-prose">{status(r)}{value}{meta}</section><section class="portal-prose"><h2>Źródło i interpretacja</h2><p>{source}</p>'+''.join(f'<p>{e(t)}</p>' for t in notes)+f'<p>{a("Dokumentacja metody",r["methodology_href"])}</p><p>{a("Jak dobrać dane do zastosowania","/zastosowanie-danych.html")}</p></section>'+ (f'<section class="portal-prose"><h2>Powiązane dane</h2>{more}</section>' if more!='<ul class="portal-list"></ul>' else '')+f'</div><aside class="portal-callout"><h2>Pliki do pobrania</h2>{downloads}<p>Jednostki, założenia oraz warunki wykorzystania sprawdź razem z danymi.</p><p>{a("Formaty i integracja","/o-polca/gotowosc-dpp.html")}</p></aside></div>'
  family_links=[{'label':str(f['id'])+' — '+f['label'],'href':f'/wyroby/{f["id"]:02d}.html'} for f in json.loads((ROOT/'data/cpr-families.json').read_text())['families'] if f['id'] in r.get('cpr_family_ids',[])]
  if family_links:body='<nav aria-label="Rodzina wyrobu">'+links(family_links,'product-inline-links')+'</nav>'+body
  page(r['href'][1:],r['title'],r['description'],body,parent=('Katalog danych','/datasety.html'))
def build_indexes():
 tools=[r for r in CAT['resources'] if r['kind']=='tool'];articles=[r for r in CAT['resources'] if r['kind']=='article']
 page('kalkulatory.html','Kalkulatory','Wybierz, co chcesz obliczyć. Każde narzędzie pokazuje przyjęte współczynniki i zakres wyniku.','<div class="portal-reading">'+''.join(row(r) for r in tools)+'</div>')
 page('blog.html','Artykuły i wyjaśnienia','Objaśnienia pojęć i analizy sektorowe. Przy korzystaniu z danych liczbowych sprawdź rocznik i wersję.','<div class="portal-reading">'+''.join(row(r) for r in articles)+'</div>')
 docs=[{'label':'MET-001 — energia Polska 2024 (PDF)','href':'/metodyki/MET-001-poLCA-EN-PL-2024.pdf'},{'label':'MET-001 — opis i korekta','href':'/metodyki/MET-001-poLCA-EN-PL-2024.html'},{'label':'MET-002 — wcześniejsza metodyka energii (PDF)','href':'/metodyki/MET-002-energia.pdf'},{'label':'MET-002 — opis i korekta','href':'/metodyki/MET-002-energia.html'},{'label':'Energia dla producenta — wcześniejszy dokument (PDF)','href':'/dokumenty/onepager-energia-producent.pdf'},{'label':'Energia dla producenta — aktualizacja objaśnień','href':'/dokumenty/onepager-energia-producent.html'}]
 body='<div class="portal-reading"><section class="portal-prose"><h2>Model energii Polska 2025</h2><p>Wyniki, opis metody i przykład obliczenia są dostępne razem z wersją modelu.</p>'+links([{'label':'Energia Polska 2025 v4 — dokumentacja i pliki','href':'/energia-polska-2025-v4.html#pliki'}])+'</section><section class="portal-prose"><h2>Wcześniejsze dokumenty</h2><p>Pliki PDF zachowują treść z daty wydania. Korekty dotyczące wyboru miksu energii i zakresu wskaźników opisano w towarzyszących wersjach internetowych. Do nowego obliczenia korzystaj z aktualnej instrukcji doboru danych.</p>'+links(docs)+'</section><section class="portal-prose"><h2>Zasady dla kategorii wyrobów</h2>'+links([{'label':'Projekty dokumentów dla mieszanek asfaltowych i kruszyw','href':'/c-pcr/'}])+'</section></div>'
 page('metodyki/index.html','Dokumenty metodyczne','Dokumentacja modeli i wcześniejsze wydania wraz z objaśnieniami.',body,parent=('Metody i źródła','/metodyka.html'))
 body='<div class="portal-reading"><section class="portal-prose"><h2>Energia elektryczna — Polska 2025 v4</h2><p>Profil 37 wskaźników wraz z instrukcją, przykładem i warunkami wykorzystania.</p>'+links([{'label':x['label']+' · '+x['format'],'href':x['href']} for x in CAT['datasets'][0]['downloads']])+'</section>'
 for c in CAT['collections']:body+=f'<section class="portal-prose"><h2>{e(c["title"])}</h2><p>{e(c["description"])}</p>'+links([{'label':x['label']+' · '+x['format'],'href':x['href']} for x in c['downloads']])+'</section>'
 body+='<section class="portal-prose"><h2>Pojedyncze rekordy i dokumenty</h2>'+links([{'label':'Wybierz rekord w katalogu danych','href':'/datasety.html'},{'label':'Dokumenty metodyczne i korekty wcześniejszych wydań','href':'/metodyki/'},{'label':'Formaty i instrukcja integracji','href':'/o-polca/gotowosc-dpp.html'}])+'</section></div>'
 page('pobierz.html','Pliki do pobrania','Pobierz konkretną wersję danych wraz z dokumentacją. Warunki wykorzystania są przypisane do zbioru.',body,parent=('Dane','/datasety.html'))
 p=ROOT/'pobierz.html';p.write_text(p.read_text().replace('<h2>Pojedyncze rekordy i dokumenty</h2>','<span id="cpcr"></span><h2>Pojedyncze rekordy i dokumenty</h2>'))
 page('metodyka-en-pl.html','Metodyka energii — model 2024','Historyczny model poLCA-EN-PL-2024 v9.1 opisano w dokumencie MET-001.','<p>'+a('Przejdź do metodyki MET-001','/metodyki/MET-001-poLCA-EN-PL-2024.html')+'</p>')
 p=ROOT/'metodyka-en-pl.html';t=p.read_text().replace('href="https://polca.org.pl/metodyka-en-pl.html"','href="https://polca.org.pl/metodyki/MET-001-poLCA-EN-PL-2024.html"').replace('</head>','<meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0; url=/metodyki/MET-001-poLCA-EN-PL-2024.html"></head>');p.write_text(t)
 page('404.html','Nie znaleziono strony','Adres mógł się zmienić. Skorzystaj z wyszukiwarki lub wybierz dział portalu.',searchform()+links([{'label':n,'href':u} for n,u,g in NAV]))
def migrate_shell():
 for p in ROOT.rglob('*.html'):
  rel=p.relative_to(ROOT).as_posix()
  if rel in GENERATED or rel.startswith(('.git/','assets/','tests/')):continue
  doc=html.parse(str(p));body=doc.find('body');head=doc.find('head')
  if body is None or head is None:continue
  for el in body.xpath('./header|./footer|./a[contains(@class,"skip")]|.//*[contains(concat(" ",normalize-space(@class)," ")," polca-sidebar ")]'):
   if el.getparent() is not None:el.getparent().remove(el)
  for el in doc.xpath('//script[@src]'):
   src=el.get('src','')
   if any('/'+n in '/'+src for n in ['sidebar.js','search.js','effects.js','animations.js','nav-mobile.js','portal.js']):el.getparent().remove(el)
  for el in head.xpath('./link[contains(@href,"fonts.googleapis") or contains(@href,"fonts.gstatic") or contains(@href,"/assets/portal.css")]'):head.remove(el)
  for el in head.xpath('.//html'):
   if el.getparent() is not None:el.getparent().remove(el)
  head.append(etree.Element('link',rel='stylesheet',href='/assets/portal.css?v=20261020design'))
  head.append(etree.Element('script',src='/js/portal.js?v=20261019cpr',defer='defer'))
  body.set('class','portal portal-legacy'+(' portal-tool' if group(rel)=='tools' else '')+(' portal-article' if rel.startswith('blog-') else ''))
  nodes=html.fragments_fromstring(header(rel))
  for i,n in enumerate(nodes):body.insert(i,n)
  main=body.xpath('.//main')
  if main:main[0].set('id','main')
  else:
   candidates=body.xpath('./div[contains(@class,"polca-content") or contains(@class,"main-content") or @class="page"]')
   if candidates:candidates[0].tag='main';candidates[0].set('id','main')
  headings=doc.xpath('//h1');title=' '.join(headings[0].itertext()).strip() if headings else '';title=re.sub(r'\s+',' ',title)
  container=body.xpath('//*[@id="main"]')
  if container:
   for old in container[0].xpath('./nav[contains(@class,"portal-breadcrumbs")]'):container[0].remove(old)
   container[0].insert(0,html.fromstring(crumb(title)))
  body.append(html.fromstring(footer()))
  p.write_bytes(etree.tostring(doc,encoding='utf-8',method='html',doctype='<!DOCTYPE html>',pretty_print=False)+b'\n')
def sync_shell():
 # Replace only the existing shared shell; retain legacy content and serialization.
 for p in ROOT.rglob('*.html'):
  rel=p.relative_to(ROOT).as_posix()
  if rel in GENERATED or rel.startswith(('.git/','assets/','tests/')):continue
  text=p.read_text()
  if not re.search(r'<link[^>]+rel=[\"\'](?:shortcut )?icon[\"\']',text):text=text.replace('</head>','<link rel="icon" href="/favicon.svg" type="image/svg+xml"></head>')
  text=re.sub(r'<header class="portal-header">.*?</header>',lambda m:header(rel).split('</a>',1)[1],text,flags=re.S)
  text=re.sub(r'<footer class="portal-footer">.*?</footer>',lambda m:footer(),text,flags=re.S)
  text=re.sub(r'/assets/portal\.css\?v=[^"\s]+','/assets/portal.css?v=20261020design',text)
  text=re.sub(r'/js/portal\.js\?v=[^"\s]+','/js/portal.js?v=20261019cpr',text)
  p.write_text(text)

def build_energy_calculator():
    profile=json.loads((ROOT/'data/energia-pl-2025-v4/profil-37.json').read_text())
    rows=''.join(f'<tr><th scope="row">{e(i["code"])}</th><td>{e(i["name_pl"])}</td><td>{e(num(i["value_per_kWh"]))}</td><td data-energy-result="{e(i["code"])}">{e(num(i["value_per_kWh"]*10))}</td><td>{e(i["impact_unit"])}</td></tr>' for i in profile['indicators'])
    body='''<div id="energy-calculation"><div class="portal-columns"><section class="portal-callout"><h2>Wpisz zużycie energii</h2><form id="energy-form"><label for="energy-quantity">Ilość energii przypisana do obliczanego procesu</label><input id="energy-quantity" type="number" min="0" max="1000000000000" step="any" value="10" required aria-describedby="energy-error"><label for="energy-unit">Jednostka zużycia</label><select id="energy-unit"><option value="kWh">kWh</option><option value="MWh">MWh</option><option value="MJ">MJ energii elektrycznej</option></select><p id="energy-error" hidden role="alert">Wpisz nieujemną liczbę nie większą niż 10¹².</p><button type="submit">Przelicz</button></form><noscript><p>Poniżej pokazano przykład dla 10 kWh. Zmiana ilości i pobranie wyniku wymagają JavaScript.</p></noscript></section><section class="portal-prose"><h2>Jak stosować wynik</h2><p>Przelicznik korzysta z fizycznego krajowego profilu energii Polska 2025 v4. Wynik opisuje wkład podanej ilości prądu; jednostkę wyrobu i etap cyklu życia określasz w swoim obliczeniu.</p><p>Dla energii kupowanej przez zakład dobierz dane zgodnie z zasadami programu. Zależnie od przyjętego podejścia będą to dane dostawcy, własnego wytwarzania, miks rezydualny albo odpowiedni profil fizyczny. Straty sieciowe ujęte w profilu nie wymagają ponownego doliczenia.</p><p><a href="/zastosowanie-epd-cpr.html">Dobór profilu do zastosowania</a> · <a href="/energia-polska-2025-v4.html">Metoda, źródła i status wersji v4</a></p></section></div><section class="portal-section"><h2>Wyniki dla podanej ilości energii</h2><p id="energy-summary" role="status" aria-live="polite">Przykład dla 10 kWh.</p><div class="portal-actions"><button type="button" data-energy-download="csv" disabled>Pobierz wynik CSV</button><button type="button" data-energy-download="json" disabled>Pobierz wynik JSON</button></div><p class="portal-lead-small">Każdy wynik = zużycie w kWh × wskaźnik na 1 kWh. Wskaźników o różnych jednostkach ani sum i ich składników nie dodaje się ponownie.</p><p class="portal-scroll-hint">Na małym ekranie przewiń tabelę w poziomie, aby zobaczyć wynik i jednostkę.</p><div class="portal-table-wrap" tabindex="0" role="region" aria-label="Wyniki 37 wskaźników, tabela przewijana"><table><caption>Wkład energii — Polska 2025 v4</caption><thead><tr><th scope="col">Kod</th><th scope="col">Wskaźnik</th><th scope="col">Wartość na 1 kWh</th><th scope="col">Wynik</th><th scope="col">Jednostka wyniku</th></tr></thead><tbody>'''+rows+'''</tbody></table></div><p>Wersja v4: odbiór techniczny obliczeń oraz wewnętrzna recenzja kodu i metody zakończone; formalne przyjęcie do określonych zastosowań w deklaracjach pozostaje otwarte. Eksport zachowuje oznaczenie modelu, jednostki i status źródłowego profilu.</p><p><a href="/data/energia-pl-2025-v4/WARUNKI-WYKORZYSTANIA.txt">Warunki wykorzystania</a> · <a href="/data/energia-pl-2025-v4/przyklad-10-kWh.json">Źródłowy przykład 10 kWh</a></p></section></div><script id="energy-profile-data" type="application/json">'''+json.dumps(profile,ensure_ascii=False).replace('<','\\u003c')+'''</script><script src="/js/energy-profile.js" defer></script>'''
    page('oblicz-energie-2025.html','Oblicz wkład energii — Polska 2025','Przelicz zużycie prądu na 37 wskaźników środowiskowych. Pobierz wynik wraz z jednostkami i identyfikacją modelu.',body,parent=('Kalkulatory','/kalkulatory.html'))

def sitemap():
 paths=sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.html') if p.name!='404.html' and 'noindex,follow' not in p.read_text() and not any(x.startswith('.') for x in p.relative_to(ROOT).parts))
 xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://polca.org.pl/'+e(p)+'</loc></url>' for p in paths)+'</urlset>\n';(ROOT/'sitemap.xml').write_text(xml)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--migrate-shell',action='store_true');args=parser.parse_args()
 build_catalog();build_catalog(True);build_copy();build_cards();build_indexes();build_energy_calculator()
 from cpr_portal import build as build_products
 build_products(globals())
 from consultation_portal import build as build_consultation
 build_consultation(globals())
 from report_portal import build as build_report
 build_report(globals())
 from map_portal import build as build_map
 build_map(globals())
 from topic_map_portal import build as build_topic_map
 build_topic_map(globals())
 if args.migrate_shell:migrate_shell()
 sync_shell()
 sitemap();print(f'Generated {len(GENERATED)} pages; shell migration: {args.migrate_shell}')
