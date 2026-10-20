"""Illustrative geographic introduction to the topics covered by poLCA."""
import base64
import json
import math
from html import escape


def build(api):
    root, page = api['ROOT'], api['page']
    geography = json.loads((root / 'content/home-map.json').read_text())
    topics = json.loads((root / 'content/topic-map.json').read_text())
    ring = geography['country']['coordinates'][0]
    cosine = math.cos(math.radians(52))
    xs, ys = [lon * cosine for lon, lat in ring], [-lat for lon, lat in ring]
    scale = min(650 / (max(xs) - min(xs)), 580 / (max(ys) - min(ys)))
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

    def project(lon, lat):
        return 400 + (lon * cosine - cx) * scale, 325 + (-lat - cy) * scale

    def path(coords):
        return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in (project(*p[:2]) for p in coords))

    icons = []
    for name in sorted({item['icon'] for item in topics['items']}):
        encoded = base64.b64encode((root / f'images/mapa-symbol-{name}.webp').read_bytes()).decode()
        icons.append(f'<image id="{name}" width="100" height="100" href="data:image/webp;base64,{encoded}"/>')
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="650" viewBox="0 0 800 650" role="img" aria-labelledby="map-title map-desc">
<title id="map-title">{escape(topics['title'])}</title>
<desc id="map-desc">Mapa orientacyjna: miasta i przykłady energii wiatru, fotowoltaiki, energetyki konwencjonalnej, kruszyw, cementu, transportu i budynków. Symbole pokazują temat, a nie wartość wskaźnika. Oznaczenia budynków i transportu są ilustracjami tematycznymi przy miastach.</desc>
<metadata>{escape(json.dumps({'scope': topics['scope'], 'checked': topics['checked']}, ensure_ascii=False))}</metadata>
<defs><path id="poland" d="{path(ring)} Z"/><clipPath id="country-clip"><use href="#poland"/></clipPath>{''.join(icons)}</defs>
<style>text{{font-family:Arial,sans-serif;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}}.city-label{{font-size:18px;font-weight:600;fill:#263e56}}.topic-label{{font-size:16px;font-weight:600;fill:#1355c4}}.place-label{{font-size:14px;font-weight:400;fill:#526173}}.callout{{fill:none;stroke:#9badbf;stroke-width:1}}.city-dot{{fill:#263e56;stroke:#fff;stroke-width:2}}</style>
<use href="#poland" fill="#f3f7fb" stroke="#748ca3" stroke-width="1.6"/>
<g clip-path="url(#country-clip)" fill="none" stroke="#bfd8ef" stroke-width="2" stroke-linecap="round">''']
    for river in geography['rivers']:
        geom = river['geometry']
        lines = geom['coordinates'] if geom['type'] == 'MultiLineString' else [geom['coordinates']]
        svg.extend(f'<path d="{path(line)}"/>' for line in lines)
    svg.append('</g>')
    for item in topics['items']:
        x, y = project(item['lon'], item['lat'])
        ix, iy, size, tx, ty = item['layout']
        label = escape(item['lines'][0]) + ''.join(f'<tspan class="place-label" x="{tx}" dy="18">{escape(line)}</tspan>' for line in item['lines'][1:])
        svg.append(f'''<g><title>{escape(item['name'] + '. ' + item['note'])}</title>
<path class="callout" d="M{x:.2f},{y:.2f} L{ix+size/2},{iy+size*.78}"/>
<use href="#{item['icon']}" transform="translate({ix} {iy}) scale({size/100})"/>
<text class="topic-label" x="{tx}" y="{ty}" text-anchor="middle">{label}</text>''')
        if item['kind'] != 'topic':
            svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.5" fill="#748ca3"/>')
        svg.append('</g>')
    offsets = {'Warszawa': (-12, 14, 'end'), 'Łódź': (12, 19, 'start'),
               'Wrocław': (0, -35, 'middle'), 'Katowice': (20, -17, 'start'),
               'Lublin': (-12, -12, 'end')}
    for city in geography['cities']:
        x, y = project(city['lon'], city['lat'])
        dx, dy, anchor = offsets.get(city['name'], city['label'])
        svg.append(f'<circle class="city-dot" cx="{x:.2f}" cy="{y:.2f}" r="3.2"/><text class="city-label" x="{x+dx:.2f}" y="{y+dy:.2f}" text-anchor="{anchor}">{escape(city["name"])}</text>')
    svg.append('</svg>')
    (root / 'images/polca-mapa-danych.svg').write_text('\n'.join(svg) + '\n')

    source_rows = []
    for item in topics['items']:
        if item['kind'] == 'topic':
            continue
        coordinate = (f' Położenie: <a href="{escape(item["coordinate_source"])}">źródło punktu orientacyjnego</a>.'
                      if item.get('coordinate_source') else '')
        source_rows.append(f'<li><strong>{escape(item["name"])}</strong> — <a href="{escape(item["source"])}">opis źródłowy</a>.{coordinate}</li>')
    body = f'''<p class="map-measure">Przykłady energii, surowców, materiałów, transportu i budynków w polskim otoczeniu. Mapa pomaga rozpoznać tematy, których dotyczą dane środowiskowe.</p>
<p class="portal-map-hint">Na telefonie przesuń mapę w bok, aby zobaczyć całość.</p>
<figure class="portal-map-large" tabindex="0" role="region" aria-label="Mapa tematów danych, przewijana na małym ekranie"><a href="/images/polca-mapa-danych.svg" aria-label="Otwórz ilustrację mapy w pełnym rozmiarze"><img src="/images/polca-mapa-danych.svg" width="800" height="650" alt="Mapa Polski: wiatr, fotowoltaika, elektrownia, kruszywa, cement, transport i budynki oraz nazwy 13 miast."></a></figure>
<div class="portal-prose"><h2>Od energii i surowców do budynku</h2>
<p>Rysunki przedstawiają przykłady technologii i zastosowań. Ich wielkość służy czytelności: nie określa produkcji, emisji ani wyniku środowiskowego. Obecność obiektu na mapie nie oznacza dostępności osobnego zbioru danych dla tego zakładu.</p>
<p>Pracę z danymi można zacząć od <a href="/dane-wspolne.html">energii, paliw i transportu</a>, <a href="/wyroby.html">rodzaju wyrobu budowlanego</a> lub <a href="/zastosowanie-danych.html#budynek">zastosowania danych do budynku</a>.</p>
<h2>Oznaczenia i położenie</h2>
<p>Kontur Polski, rzeki i miasta pochodzą z <a href="https://www.naturalearthdata.com/">Natural Earth</a>. Linie prowadzą od szkiców do punktów odniesienia. Budynki przy Warszawie i transport przy Poznaniu są symbolami tematów, bez wskazania konkretnej inwestycji lub przewoźnika.</p>
<ul>{''.join(source_rows)}</ul>
<p>Punkty farm i zakładów są orientacyjne w skali kraju. Nie określają granic ani położenia pojedynczego urządzenia; źródło punktu Szymankowa nie deklaruje dokładnej lokalizacji. Regiony kruszyw oznaczono przy Rogoźnicy i Morawicy. Dla Morawicy wykorzystano dane © <a href="https://www.openstreetmap.org/copyright">autorów OpenStreetMap</a>. Szkice przedstawiają typ obiektu, nie jego rzeczywisty wygląd.</p>
<p>Osobny materiał z wartościami liczbowymi: <a href="/mapa-polski.html">zgłoszone emisje CO₂ z zakładów w Polsce — mapa i dane za 2024 rok</a>.</p></div>'''
    page('mapa-danych.html', 'Polska w danych środowiskowych',
         'Energia, surowce, transport i budynki — przykłady na mapie Polski.', body,
         head_extra='<link rel="stylesheet" href="/assets/map.css?v=20261020emissions">')
