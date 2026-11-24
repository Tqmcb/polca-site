#!/usr/bin/env python3
"""Build static portal pages and shared navigation. Requires lxml for legacy HTML."""
from pathlib import Path
import json, html as h, re, argparse
from urllib.parse import urlsplit, unquote
from collections import Counter
from datetime import date
from lxml import html, etree
from atlas_icons import ICON_URL, export_icons
from change_register import static_entries
from cement_guide import BASIS_RULE
from concrete_portal import worked_example
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'data/portal-catalog.json').read_text())
CHANGE_ENTRIES=json.loads((ROOT/'data/rejestr-zmian.json').read_text())['wpisy']
FONT_PRELOAD='<link rel="preload" href="/assets/fonts/SourceSans3-roman.woff2" as="font" type="font/woff2" crossorigin>'
PORTAL_CSS='/assets/portal.css?v=20261123b'
# The published catalog retains its original addresses. Use current routes in the portal.
TOOL_PAGES = {
 'tool-przelicznik': 'przelicznik-jednostek.html',
 'tool-transport': 'transport-a4.html',
 'tool-materialy': 'gwp-materialow.html',
 'tool-wskazniki': 'wskazniki-emisji.html',
}
for resource in CAT['resources']:
 if resource['id'] in TOOL_PAGES:
  resource['href'] = '/' + TOOL_PAGES[resource['id']]
COPY=json.loads((ROOT/'content/portal-pages.json').read_text())
GENERATED=set()
def e(x): return h.escape(str(x if x is not None else ''),quote=True)
def a(label,href,cls='',extra=''):return f'<a href="{e(href)}"'+(f' class="{e(cls)}"' if cls else '')+f' {extra}>{e(label)}</a>'
def links(items,cls='portal-list'):return f'<ul class="{cls}">'+''.join('<li>'+a(x['label'],x['href'])+'</li>' for x in items)+'</ul>'
NAV=[('Wyroby','/wyroby.html','products'),('Dane','/datasety.html','data'),('Kalkulatory','/kalkulatory.html','tools'),('Jak korzystać','/jak-korzystac.html','guide'),('Metody i źródła','/metodyka.html','methods')]
def group(path):
 if path.startswith(('wyroby/','c-pcr/')) or path=='wyroby.html':return 'products'
 if path.startswith('dane/') or path in ['datasety.html','energia-polska-2025-v3.html','energia-polska-2025-v4.html','energia-polska-2025-v5.html','pobierz.html','dane-wspolne.html']:return 'data'
 if 'kalkulat' in path or path in TOOL_PAGES.values() or path in ['narzedzia.html','oblicz-energie-2025.html']:return 'tools'
 if path in ['jak-korzystac.html','pytania.html','zastosowanie-danych.html','slad-weglowy-czy-srodowiskowy.html','porownanie-baz.html','zastosowanie-epd-cpr.html']:return 'guide'
 if path.startswith(('metody','konsultacje/')) or path in ['wiarygodnosc.html','podstawy-normatywne.html']:return 'methods'
 return ''
def navigation_icon(name):
 return (f'<svg class="portal-nav-icon" width="20" height="20" viewBox="0 0 24 24" '
         f'aria-hidden="true" focusable="false"><use href="{ICON_URL}#nav-{name}"></use></svg>')

def header(path):
 nav_links = []
 for title, url, name in NAV:
  active = ' class="is-active"' if group(path) == name else ''
  current = ' aria-current="page"' if path == url[1:] else ''
  nav_links.append(f'<a href="{url}"{active}{current}>{navigation_icon(name)}{e(title)}</a>')
 nav = ''.join(nav_links)
 return f'''<a class="portal-skip-link" href="#main">Przejdź do treści</a><header class="portal-header"><div class="portal-shell"><a class="portal-brand" href="/" aria-label="poLCA — strona główna">po<span>LCA</span><small>Dane środowiskowe dla Polski</small></a><button class="portal-menu-toggle" type="button" aria-expanded="false" aria-controls="portal-navigation" hidden>Menu</button><nav class="portal-nav" id="portal-navigation" aria-label="Główna nawigacja">{nav}</nav><a class="portal-search-link" href="/szukaj.html">{navigation_icon("search")}Szukaj</a></div></header>'''
def footer():return '''<footer class="portal-footer"><div class="portal-shell"><div><a class="portal-brand" href="/">po<span>LCA</span></a><p>Dane i modele do oceny cyklu życia.</p><p>Multicert Sp. z o.o.<br>Operator programu EPD Polska</p></div><div><h2>Dane i obliczenia</h2><a href="/wyroby.html">Rodziny wyrobów</a><a href="/dane-wspolne.html">Energia, paliwa i transport</a><a href="/datasety.html">Katalog danych</a><a href="/kalkulatory.html">Kalkulatory</a><a href="/pobierz.html">Pliki do pobrania</a></div><div><h2>Pomoc</h2><a href="/jak-korzystac.html">Jak korzystać z portalu</a><a href="/pytania.html">Pytania i odpowiedzi</a><a href="/metodyka.html">Metody i źródła</a></div><div><h2>O projekcie</h2><a href="/o-polca/">O poLCA</a><a href="/rejestr-zmian.html">Rejestr zmian</a><a href="/o-polca/cytowanie.html">Jak cytować</a><a href="mailto:info@epd.org.pl">info@epd.org.pl</a></div></div><div class="portal-shell portal-footer-bottom"><span>© 2026 Multicert</span><span>Warunki wykorzystania danych podano w opisie każdego zbioru.</span><a href="https://epd.org.pl/">Program EPD Polska</a></div></footer>'''
def crumb(title,parent=None):
 return '<nav class="portal-breadcrumbs" aria-label="Ścieżka strony">'+a('Strona główna','/')+'<span aria-hidden="true">/</span>'+((a(parent[0],parent[1])+'<span aria-hidden="true">/</span>') if parent else '')+f'<span aria-current="page">{e(title)}</span></nav>'
def page(path,title,lead,body,parent=None,attrs='',home=False,head_extra='',pagehead=True,main_class=None,show_crumb=True,og_type='website'):
 mainhead='' if home else (crumb(title,parent) if show_crumb else '')+('' if not pagehead else f'<header class="portal-pagehead"><h1>{e(title)}</h1><p class="portal-lead">{e(lead)}</p></header>')
 home_css='<link rel="stylesheet" href="/assets/home.css?v=20261123b">' if home else ''
 body_class='portal portal-home' if home else 'portal'
 main_class=main_class or ('portal-main home-main' if home else 'portal-main portal-shell')
 out=f'''<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — poLCA</title><meta name="description" content="{e(lead)}"><link rel="canonical" href="https://polca.org.pl/{e(path) if path!='index.html' else ''}"><meta property="og:title" content="{e(title)} — poLCA"><meta property="og:description" content="{e(lead)}"><meta property="og:type" content="{e(og_type)}"><meta property="og:url" content="https://polca.org.pl/{e(path) if path!='index.html' else ''}">{FONT_PRELOAD}<link rel="stylesheet" href="{PORTAL_CSS}">{home_css}<script src="/js/portal.js?v=20261123" defer></script>{head_extra}</head><body class="{body_class}">{header(path)}<main id="main" class="{main_class}" {attrs}>{mainhead}{body}</main>{footer()}</body></html>'''
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(out+'\n');GENERATED.add(path)
def num(v, spec='.6g'):return format(v,spec).replace('.',',')
def record_value(r):
 if r.get('category_id') == 'beton':
  return num(r['value'], '.1f')
 if 'gwp_modules_kg_co2e_per_t' in r:
  return num(r['value'], '.2f')
 return num(r['value'])
def description_with_basis(r):
 return ' '.join(filter(None, (r.get('description'), r.get('basis_note'))))
def status(r):return f'<span class="portal-status portal-status-{e(r.get("status_id",""))}">{e(r.get("status_label",""))}</span>'
def row(r, dataset_catalog=False):
 val=f'<div class="portal-result-value"><strong>{e(record_value(r))}</strong><small>{e(r.get("unit"))}</small><small>{e(r.get("indicator_label"))}</small></div>' if isinstance(r.get('value'),(int,float)) else ''
 kind={'dataset':'Dane','tool':'Kalkulator','method':'Metoda i instrukcja','article':'Artykuł'}.get(r['kind'],'Zasób')
 meta=[r.get('category_label'),r.get('year')]
 if not dataset_catalog:meta.insert(0,kind)
 title=('<div class="portal-result-meta">'+''.join(f'<span>{e(item)}</span>' for item in meta if item)+'</div>'
        +f'<h2>{a(r["title"],r["href"],"portal-result-title")}</h2>')
 details=(f'<p class="portal-result-description">{e(description_with_basis(r))}</p>'
          +f'<div class="portal-result-meta">{status(r)}<span>{e(" · ".join(r.get("formats",[])))}</span></div>')
 content=title+val+details if dataset_catalog else '<div>'+title+details+'</div>'+val
 return f'<article class="portal-result" data-record-id="{e(r["id"])}">{content}</article>'
def searchform():return '''<form class="portal-search" action="/szukaj.html" method="get" role="search"><label for="q">Wyszukaj dane, kalkulator lub odpowiedź</label><div class="portal-search-control"><input id="q" type="search" name="q" placeholder="Np. energia 2025, cement, ślad węglowy" autocomplete="off"><button type="submit">Szukaj</button></div></form>'''
def select(name,label,options):return f'<label for="filter-{name}">{label}</label><select id="filter-{name}" name="{name}"><option value="">Wszystkie</option>'+''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in options)+'</select>'
def build_catalog(all=False):
 records=CAT['datasets']+CAT['resources'] if all else CAT['datasets'];path='szukaj.html' if all else 'datasety.html'
 cats={r['category_id']:r['category_label'] for r in records if r.get('category_id')};years=sorted({r['year'] for r in records if r.get('year')},reverse=True);statuses={r['status_id']:r['status_label'] for r in records if r.get('status_id')}
 families=json.loads((ROOT/'data/cpr-families.json').read_text())['families']
 filters=select('family','Rodzina wyrobu',[(f['id'],str(f['id'])+' — '+f['label']) for f in families])+select('category','Temat',cats.items())+select('year','Rok odniesienia',[(y,y) for y in years])+select('status','Status',statuses.items())
 if all:filters=select('kind','Rodzaj zasobu',[('dataset','Dane'),('tool','Kalkulatory'),('method','Metody i instrukcje'),('article','Artykuły')])+filters
 disclosure = '<details class="portal-filters" open><summary>Zawęź wyniki</summary>' if all else (
     '<details class="portal-filters"><summary>Zawęź wyniki (<span id="filter-count">0</span>)</summary>')
 rows = ''.join(row(r, dataset_catalog=not all) for r in records)
 body=f'''<div class="portal-catalog-layout"><form id="catalog-filters" action="/{path}" method="get"><label for="catalog-query">{'Szukaj w całym portalu' if all else 'Szukaj w danych'}</label><div class="portal-search-control"><input id="catalog-query" type="search" name="q" placeholder="Wpisz nazwę lub pytanie"><button type="submit">Szukaj</button></div>{disclosure}<div>{filters}<button type="reset">Wyczyść filtry</button></div></details></form><div class="portal-results-panel"><p id="result-count" role="status" aria-live="polite">Wyniki: {len(records)}</p><noscript><p>Filtrowanie wymaga włączenia JavaScript. Poniżej znajdziesz pełną listę; możesz użyć funkcji szukania w przeglądarce.</p></noscript><div id="catalog-results">{rows}</div><div id="catalog-empty" class="portal-callout" hidden><h2>Brak wyników dla tych ustawień</h2><p>Spróbuj krótszej nazwy lub usuń filtry. Pomoc w doborze danych znajdziesz w <a href="/jak-korzystac.html">przewodniku</a>.</p><button type="button" data-reset-filters>Wyczyść wyszukiwanie</button></div></div></div><script id="portal-search-data" type="application/json">{json.dumps(records,ensure_ascii=False).replace('<','\\u003c')}</script>'''
 if not all:body='<p>Możesz też zacząć od <a href="/wyroby.html">rodzaju wyrobu</a> lub wybrać <a href="/dane-wspolne.html">energię, paliwa i transport</a>.</p><span id="referencyjne-szczegoly"></span>'+body
 page(path,'Szukaj w poLCA' if all else 'Katalog danych','Znajdź dane, kalkulator, metodę lub odpowiedź.' if all else 'Wybierz temat i sprawdź rok, zakres oraz status danych przed użyciem.',body,attrs=f'data-catalog-mode="{"all" if all else "datasets"}"')
def section_table(section, responsive=False):
 table = section['table']
 title = e(section['title'])
 headers = table['headers']
 row_role = ' role="row"' if responsive else ''
 group_role = ' role="rowgroup"' if responsive else ''
 col_role = ' role="columnheader"' if responsive else ''
 heading = ''.join(f'<th scope="col"{col_role}>{e(label)}</th>' for label in headers)
 rows = []
 for record in table['rows']:
  row_header = ' role="rowheader"' if responsive else ''
  cells = [f'<th scope="row"{row_header}>{e(record[0])}</th>']
  for j, value in enumerate(record[1:], start=1):
   attrs = f' role="cell" data-label="{e(headers[j])}"' if responsive else ''
   cells.append(f'<td{attrs}>{e(value)}</td>')
  rows.append(f'<tr{row_role}>' + ''.join(cells) + '</tr>')
 table_attrs = f' role="table" aria-label="{title}"' if responsive else ''
 markup = (f'<table{table_attrs}><thead{group_role}><tr{row_role}>{heading}</tr></thead>'
           f'<tbody{group_role}>' + ''.join(rows) + '</tbody></table>')
 if responsive:
  return '<div class="portal-table-wrap">' + markup + '</div>'
 return ('<p class="portal-scroll-hint">Przewiń tabelę w bok, aby zobaczyć wszystkie kolumny.</p>'
         f'<div class="portal-table-wrap" tabindex="0" role="region" aria-label="{title} — tabela przewijana">'
         + markup + '</div>')

def sections(secs, responsive_tables=False):
 out=[]
 for i,s in enumerate(secs):
  block=f'<section class="portal-prose" id="{e(s.get("id", "sekcja-"+str(i+1)))}"><h2>{e(s["title"])}</h2>'+''.join(f'<p>{e(p)}</p>' for p in s.get('paragraphs',[]))
  if s.get('diagram') == 'charakteryzacja':
   block += '''<figure class="characterisation-figure">
   <figcaption>Jak oblicza się wkład emisji metanu w zmianę klimatu?</figcaption>
   <div class="characterisation-equation">
     <div><strong>Emisja metanu do powietrza</strong><span>kg metanu z inwentaryzacji</span></div>
     <span class="characterisation-operator"><span aria-hidden="true">×</span><span class="characterisation-spoken">razy</span></span>
     <div><strong>Współczynnik charakteryzacji</strong><span>kg ekwiwalentu CO₂ na kg metanu</span></div>
     <span class="characterisation-operator"><span aria-hidden="true">=</span><span class="characterisation-spoken">równa się</span></span>
     <div><strong>Wkład emisji metanu</strong><span>kg ekwiwalentu CO₂</span></div>
   </div>
   <p>Wskaźnik zmiany klimatu dla całego procesu to suma wkładów wszystkich przepływów uwzględnionych w tej kategorii.</p>
   </figure>'''
  if s.get('table'):
   block += section_table(s, responsive_tables)
  out.append(block+links(s.get('links',[]))+'</section>')
 return ''.join(out)
def build_comparison(content):
 items = [{'label': s['nav_label'], 'href': '#' + s['id']} for s in content['sections']]
 index = links(items, 'comparison-index')
 intro = f'''<div class="comparison-intro">
 <header class="portal-pagehead"><h1>{e(content['title'])}</h1><p class="portal-lead">{e(content['lead'])}</p></header>
 <nav class="comparison-nav" aria-label="Spis treści porównania">
 <div class="comparison-desktop-index"><p>Spis treści</p>{index}</div>
 <details class="comparison-mobile-index"><summary>Spis treści</summary>{index}</details>
 </nav></div>'''
 body = intro + '<div class="comparison-sections">' + sections(content['sections'], responsive_tables=True) + '</div>'
 page(content['path'], content['title'], content['lead'], body, pagehead=False,
      head_extra='<link rel="stylesheet" href="/assets/comparison.css?v=20261122-linki">')

def build_copy():
 from reading_portal import build as build_reading_page
 from visual_guides import build as build_visual_guide
 for c in COPY['pages']:
  if c.get('layout', '').startswith('guide-'):
   build_visual_guide(c, ROOT, page)
   continue
  if c.get('layout') == 'comparison':
   build_comparison(c)
   continue
  build_reading_page(c, page, links, sections)
def build_cards():
 current = {r['id']: r for r in CAT['datasets']}
 for r in [*CAT['datasets'], *CAT['withdrawn_datasets']]:
  if not r['href'].startswith('/dane/'):continue
  contexts = r.get('application_contexts', {})
  scope_fields = []
  if 'publication_year' in r and r['year_type'] != 'publication':
   label = 'Rok publikacji deklaracji' if r['status_id'] == 'published_sector_dataset' else 'Rok publikacji zbioru'
   scope_fields.append((label, r['publication_year']))
  if contexts:
   scope_fields.append(('Zakres u producenta', r['production_scope']))
   scope_fields.extend((context['label'], context['description']) for context in contexts.values())
  fields=scope_fields+[('Rodzaj wskaźnika',r.get('indicator_label')),('Jednostka',r.get('unit')),('Rok',r.get('year')),('Znaczenie roku',{'reference':'Rok danych','publication':'Rok publikacji','application':'Rok zastosowania'}.get(r.get('year_type'),'')),('Obszar',r.get('geography')),('Zakres',None if contexts else r.get('boundary')),('Status',r.get('status_label')),('Identyfikator',r['id'])]
  meta='<dl class="portal-metadata">'+''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in fields if v is not None and v!='')+'</dl>'
  value=(f'<p class="portal-dataset-value"><strong>{e(record_value(r))}</strong> <span>{e(r.get("unit"))}</span></p><p>{e(r.get("indicator_label"))}</p>') if isinstance(r.get('value'),(int,float)) else '<p>Zestaw parametrów modelu. Szczegóły zawiera plik danych.</p>'
  if 'gwp_gross_kg_co2e' in r:
   value += f'<p>Wartość brutto (informacja dodatkowa): {num(r["gwp_gross_kg_co2e"])} {e(r["unit"])}</p>'
  if 'gwp_fossil_basis' in r:
   value += f'<p>GWP-fossil: {num(r["gwp_fossil_kg_co2e"])} {e(r["unit"])} (składnik kopalny według rozliczenia {e(r["gwp_fossil_basis"])})</p>'
  if r.get('basis_note'):
   value += f'<p>{e(r["basis_note"])}</p>'
  downloads='<ul class="portal-downloads">'+''.join('<li>'+a(x['label'],x['href'],extra='download')+f'<span>{e(x["format"])}</span></li>' for x in r['downloads'])+'</ul>'
  source='<p>' + (a(r['source_name'],r['source_url']) if r.get('source_url') else e(r.get('source_name',''))) + '</p>'
  declarations = [s for s in r.get('source_trace', []) if s['type'] == 'manufacturer_epd']
  if declarations:
   rows = ''.join(
       f'<tr><th scope="row">{a(s["name"], s["url"])}</th><td>{e(s["manufacturer"])}</td>'
       f'<td>{e(s["product"])}</td><td>{date.fromisoformat(s["source_valid_until"]):%d.%m.%Y}</td>'
       f'<td>{num(s["gwp_total_kg_co2e"])}</td></tr>' for s in declarations)
   source = ('<div class="portal-table-wrap" role="region" aria-label="Deklaracje źródłowe" tabindex="0">'
             '<table><caption>Deklaracje środowiskowe przyjęte w obliczeniu</caption><thead><tr>'
             '<th scope="col">Deklaracja</th><th scope="col">Producent</th><th scope="col">Wyrób</th>'
             f'<th scope="col">Ważna do</th><th scope="col">GWP-total A1–A3 [{e(r["unit"])}]</th>'
             f'</tr></thead><tbody>{rows}</tbody></table></div>')
  more=links([{'label':x['title'],'href':x['href']} for x in CAT['datasets'] if x['id'] in r.get('related_ids',[])])
  modules = r.get('gwp_modules_kg_co2e_per_t')
  if modules:
   meta += '<dl class="portal-metadata">' + ''.join(
       f'<div><dt>{label}</dt><dd>{num(modules[key], ".2f")} kg CO₂e/t</dd></div>'
       for key, label in [('A1', 'A1 — surowce'), ('A2', 'A2 — transport'), ('A3', 'A3 — wytwarzanie')]) + '</dl>'
  notes=[r['methodology_note']] if r.get('methodology_note') else []
  if 'gwp_gross_kg_co2e' in r:
   notes.append(BASIS_RULE)
  if r.get('limitations'):notes.append(r['limitations'])
  if r['id']=='POLCA-EN-PL-LCA-2024':notes.append('Wartość 0,599 dotyczy składnika kopalnego wpływu na klimat. Informacyjna suma w pełnym modelu 2024 wynosi 0,600 kg CO₂e/kWh. Rekord do pobrania zachowuje rozróżnienie rodzaju wskaźnika.')
  if r['id']=='KOBIZE-EN-PL-ENDUSER-2024':notes.append('Wartość dotyczy emisji CO₂ u odbiorcy końcowego, w granicach opisanych w publikacji KOBiZE. Do pełnej oceny cyklu życia energii służy odrębny profil środowiskowy.')
  if r.get('status_id') in ['proxy','reference','earlier_model','control']:notes.append('Dobór do konkretnego obliczenia wymaga zgodności jednostki, granic i roku. Status opisuje tę pozycję katalogu; źródło i warunki stosowania są wskazane w pliku oraz dokumentacji.')
  notes_html = ''.join(f'<p>{e(t)}</p>' for t in notes)
  for item in r.get('source_trace', []):
   url = item['url']
   notes_html = re.sub(r'\[([^\[\]]+)\]\(' + re.escape(e(url)) + r'\)',
                       lambda m: a(h.unescape(m[1]), url), notes_html)
  body=f'<div class="portal-detail-layout"><div><section class="portal-prose">{status(r)}{value}{meta}</section><section class="portal-prose"><h2>Źródło i interpretacja</h2>{source}'+notes_html+f'<p>{a("Dokumentacja metody",r["methodology_href"])}</p><p>{a("Jak dobrać dane do zastosowania","/zastosowanie-danych.html")}</p></section>'+ (f'<section class="portal-prose"><h2>Powiązane dane</h2>{more}</section>' if more!='<ul class="portal-list"></ul>' else '')+f'</div><aside class="portal-callout"><h2>Pliki do pobrania</h2>{downloads}<p>Jednostki, założenia oraz warunki wykorzystania sprawdź razem z danymi.</p><p>{a("Formaty i integracja","/o-polca/gotowosc-dpp.html")}</p></aside></div>'
  if 'unbound_base' in contexts:
   guidance = [
    {'label': 'Co należy do A1 betonu i jak ująć transport kruszywa?', 'href': '/wyroby/24.html#modul-a1'},
    {'label': 'Czy ten wskaźnik wystarcza do deklaracji właściwości środowiskowych wyrobu?', 'href': '/metodyka-defaults-ue.html#kruszywo-cpr'}
   ]
   body += '<nav aria-label="Zastosowanie kruszywa">' + links(guidance, 'product-inline-links') + '</nav>'
  family_links=[{'label':str(f['id'])+' — '+f['label'],'href':f'/wyroby/{f["id"]:02d}.html'} for f in json.loads((ROOT/'data/cpr-families.json').read_text())['families'] if f['id'] in r.get('cpr_family_ids',[])]
  if family_links:body='<nav aria-label="Rodzina wyrobu">'+links(family_links,'product-inline-links')+'</nav>'+body
  head_extra = ''
  if r.get('superseded_by'):
   replacement = current[r['superseded_by']]
   body = '<p class="portal-callout">Aktualny wskaźnik: ' + a(replacement['title'], replacement['href']) + '</p>' + body
   head_extra = '<meta name="robots" content="noindex,follow">'
  page(r['href'][1:],r['title'],r['description'],body,parent=('Katalog danych','/datasety.html'),head_extra=head_extra)
def build_indexes():
 tools=[r for r in CAT['resources'] if r['kind']=='tool'];articles=[r for r in CAT['resources'] if r['kind']=='article']
 page('kalkulatory.html','Kalkulatory','Wybierz, co chcesz obliczyć. Każde narzędzie pokazuje przyjęte współczynniki i zakres wyniku.','<div class="portal-reading">'+''.join(row(r) for r in tools)+'</div>')
 page('blog.html','Artykuły i wyjaśnienia','Objaśnienia pojęć i analizy sektorowe. Przy korzystaniu z danych liczbowych sprawdź rocznik i wersję.','<div class="portal-reading">'+''.join(row(r) for r in articles)+'</div>')
 docs=[{'label':'MET-001 — energia Polska 2024 (PDF)','href':'/metodyki/MET-001-poLCA-EN-PL-2024.pdf'},{'label':'MET-001 — opis i korekta','href':'/metodyki/MET-001-poLCA-EN-PL-2024.html'},{'label':'MET-002 — wcześniejsza metodyka energii (PDF)','href':'/metodyki/MET-002-energia.pdf'},{'label':'MET-002 — opis i korekta','href':'/metodyki/MET-002-energia.html'},{'label':'Energia dla producenta — wcześniejszy dokument (PDF)','href':'/dokumenty/onepager-energia-producent.pdf'},{'label':'Energia dla producenta — aktualizacja objaśnień','href':'/dokumenty/onepager-energia-producent.html'}]
 body='<div class="portal-reading"><section class="portal-prose"><h2>Model energii Polska 2025</h2><p>Wyniki, opis metody i przykład obliczenia są dostępne razem z wersją modelu.</p>'+links([{'label':'Energia Polska 2025 v5 — dokumentacja i pliki','href':'/energia-polska-2025-v5.html#pliki'}])+'</section><section class="portal-prose"><h2>Wcześniejsze dokumenty</h2><p>Pliki PDF zachowują treść z daty wydania. Korekty dotyczące wyboru miksu energii i zakresu wskaźników opisano w towarzyszących wersjach internetowych. Do nowego obliczenia korzystaj z aktualnej instrukcji doboru danych.</p>'+links(docs)+'</section><section class="portal-prose"><h2>Zasady dla kategorii wyrobów</h2>'+links([{'label':'Projekty dokumentów dla mieszanek asfaltowych i kruszyw','href':'/c-pcr/'}])+'</section></div>'
 page('metodyki/index.html','Dokumenty metodyczne','Dokumentacja modeli i wcześniejsze wydania wraz z objaśnieniami.',body,parent=('Metody i źródła','/metodyka.html'))
 body='<div class="portal-reading"><section class="portal-prose"><h2>Energia elektryczna — Polska 2025 v5</h2><p>Profil 37 wskaźników wraz z instrukcją, przykładem i warunkami wykorzystania.</p>'+links([{'label':x['label']+' · '+x['format'],'href':x['href']} for x in CAT['datasets'][0]['downloads']])+'</section>'
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
  for el in head.xpath('./link[contains(@href,"fonts.googleapis") or contains(@href,"fonts.gstatic") or contains(@href,"/assets/portal.css") or @href="/assets/fonts/SourceSans3-roman.woff2"]'):head.remove(el)
  for el in head.xpath('.//html'):
   if el.getparent() is not None:el.getparent().remove(el)
  head.append(etree.Element('link',rel='stylesheet',href=PORTAL_CSS))
  head.append(etree.Element('script',src='/js/portal.js?v=20261123',defer='defer'))
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
   parent = ('Kalkulatory', '/kalkulatory.html') if rel in TOOL_PAGES.values() or rel == 'narzedzia.html' else None
   container[0].insert(0,html.fromstring(crumb(title, parent)))
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
  text=re.sub(r'/assets/portal\.css\?v=[^"\s]+',PORTAL_CSS,text)
  if PORTAL_CSS in text and FONT_PRELOAD not in text:
   text=text.replace('<link rel="stylesheet" href="'+PORTAL_CSS+'"',FONT_PRELOAD+'<link rel="stylesheet" href="'+PORTAL_CSS+'"',1)
  if rel=='rejestr-zmian.html':
   text=re.sub(r'(<div id="rejestr-lista">).*?(</div>\s*</section>)',
               lambda m:m[1]+'\n'+static_entries(CHANGE_ENTRIES,e)+'\n        '+m[2],text,count=1,flags=re.S)
  if rel=='blog-beton-emisje-kalkulator.html':
   before, block = text.split('<!-- BEGIN concrete-example -->')
   _, after = block.split('<!-- END concrete-example -->')
   text = before + '<!-- BEGIN concrete-example -->\n' + worked_example(CAT) + '\n<!-- END concrete-example -->' + after
  text=re.sub(r'/js/portal\.js\?v=[^"\s]+','/js/portal.js?v=20261123',text)
  p.write_text(text)

def build_energy_calculator():
    from consultation_portal import display_unit
    from energy_method import full_method_html

    def panel_number(value):
        if value == 0:
            return '0'
        mantissa, _, exponent = format(value, '#.6g').partition('e')
        label = mantissa.rstrip('.').replace('.', ',')
        if exponent:
            superscript = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
            label += '·10' + str(int(exponent)).translate(superscript)
        return label

    profile = json.loads((ROOT / 'data/energia-pl-2025-v5/profil-37.json').read_text())
    indicators = profile['indicators']
    per_kwh = {item['code']: item['value_per_kWh'] for item in indicators}
    total = per_kwh['GWP-total']
    unit_labels = {
        'kg CO2 eq': 'kg równoważnika CO₂', 'kg CFC11 eq': 'kg równoważnika CFC-11',
        'mol H+ eq': 'mol równoważnika H⁺', 'kg P eq': 'kg równoważnika P',
        'kg N eq': 'kg równoważnika N', 'mol N eq': 'mol równoważnika N',
        'kg NMVOC eq': 'kg równoważnika niemetanowych lotnych związków organicznych',
        'kg Sb eq': 'kg równoważnika Sb', 'kBq U235 eq': 'kBq równoważnika U-235',
        'CTUe': 'CTUe (porównawcza jednostka ekotoksyczności)',
        'CTUh': 'CTUh (porównawcza jednostka toksyczności dla ludzi)', 'm3': 'm³',
    }
    parts = (
        ('GWP-fossil', 'Kopalny', 'fossil'),
        ('GWP-biogenic', 'Biogeniczny', 'biogenic'),
        ('GWP-luluc', 'Użytkowanie gruntów i jego zmiany', 'land'),
    )
    minor_total = sum(per_kwh[code] for code, _, _ in parts[1:])

    def bar_segments(series, denominator):
        return ''.join(
            f'<span class="energy-{name}" style="width:{100 * per_kwh[code] / denominator:.9f}%"></span>'
            for code, _, name in series
        )

    def percentage(value):
        return f'{100 * value / total:.4f}'.replace('.', ',')

    parts_rows = ''.join(
        f'<tr><th scope="row"><i class="energy-swatch energy-{name}" aria-hidden="true"></i>{label}</th>'
        f'<td>{percentage(per_kwh[code])}%</td>'
        f'<td data-energy-climate-part="{code}">{panel_number(10 * 1000 * per_kwh[code])}</td></tr>'
        for code, label, name in parts
    )
    rows = ''.join(
        f'<tr><th scope="row">{e(i["code"])}</th><td>{e(i["name_pl"])}</td>'
        f'<td>{panel_number(i["value_per_kWh"])}</td>'
        f'<td data-energy-result="{e(i["code"])}">{panel_number(i["value_per_kWh"] * 10)}</td>'
        f'<td>{e(unit_labels.get(i["impact_unit"], display_unit(i["impact_unit"])))}</td></tr>'
        for i in indicators
    )
    body = (ROOT / 'content/energy-panel.tmpl').read_text().format(
        full_method=full_method_html(ROOT),
        reference=panel_number(total),
        example_total=panel_number(10 * total),
        example_climate_kg=f'{10 * total:.2f}'.replace('.', ','),
        full_bar=bar_segments(parts, total),
        detail_bar=bar_segments(parts[1:], minor_total),
        minor_share=percentage(minor_total),
        parts_rows=parts_rows,
        rows=rows,
        source=e(profile['source_attribution']),
        profile_json=json.dumps(profile, ensure_ascii=False).replace('<', r'\u003c'),
    )
    page(
        'oblicz-energie-2025.html', 'Energia elektryczna w Polsce w 2025 r.',
        'Sprawdź wskaźnik dla 1 kWh, jego składniki i metodę poLCA v5. Przelicz zużycie energii na 37 wskaźników środowiskowych.',
        body, parent=('Kalkulatory', '/kalkulatory.html'), pagehead=False,
        head_extra='<link rel="stylesheet" href="/assets/energy-panel.css?v=20261122-pomiar">',
    )


def sitemap():
 paths=sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.html') if p.name!='404.html' and 'noindex,follow' not in p.read_text() and not any(x.startswith('.') for x in p.relative_to(ROOT).parts))
 xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://polca.org.pl/'+e(p)+'</loc></url>' for p in paths)+'</urlset>\n';(ROOT/'sitemap.xml').write_text(xml)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--migrate-shell',action='store_true');args=parser.parse_args()
 build_catalog();build_catalog(True);build_copy();build_cards();build_indexes();build_energy_calculator()
 from cpr_portal import build as build_products
 build_products(globals())
 export_icons(ROOT, json.loads((ROOT / "data/cpr-families.json").read_text())["families"])
 from consultation_portal import build as build_consultation
 build_consultation(globals())
 from report_portal import build as build_report
 build_report(globals())
 from map_portal import build as build_map
 build_map(globals())
 from topic_map_portal import build as build_topic_map
 build_topic_map(globals())
 from article_guides import build as build_guides
 build_guides(ROOT, CAT['resources'], page, crumb)
 if args.migrate_shell:migrate_shell()
 sync_shell()
 sitemap();print(f'Generated {len(GENERATED)} pages; shell migration: {args.migrate_shell}')
