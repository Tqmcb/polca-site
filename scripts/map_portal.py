"""Source-backed map of reported industrial CO2 releases; geographic data stay explicit."""
import base64
import json
import math
from decimal import Decimal
from html import escape


def number(value):
    return f'{Decimal(str(value)):,.0f}'.replace(',', '\u202f')


def build(api):
    root, page = api['ROOT'], api['page']
    geography = json.loads((root / 'content/home-map.json').read_text())
    data = json.loads((root / 'data/mapa-emisje-pl-2024.json').read_text())
    layout = json.loads((root / 'content/map-emissions-layout.json').read_text())['facilities']
    rows = data['rows'][:20]
    ring = geography['country']['coordinates'][0]
    cosine = math.cos(math.radians(52))
    xs, ys = [lon * cosine for lon, lat in ring], [-lat for lon, lat in ring]
    scale = min(650 / (max(xs) - min(xs)), 580 / (max(ys) - min(ys)))
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

    def project(lon, lat):
        return 400 + (lon * cosine - cx) * scale, 325 + (-lat - cy) * scale

    def path(coords):
        return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in (project(*p[:2]) for p in coords))

    def radius(tonnes):
        # Area, not radius, is proportional to the reported annual release.
        return 24 * math.sqrt(float(tonnes) / 30_000_000)

    icons = []
    for name in ['elektrownia', 'kruszywa', 'rafineria', 'cementownia', 'huta']:
        encoded = base64.b64encode((root / f'images/mapa-symbol-{name}.webp').read_bytes()).decode()
        icons.append(f'<image id="{name}" width="100" height="100" href="data:image/webp;base64,{encoded}"/>')
    outline = path(ring) + ' Z'

    def draw(detail):
        selected = rows if detail else rows[:10]
        count = len(selected)
        table_reference = 'Numery zakładów odpowiadają tabeli na stronie poLCA.' if detail else 'Nazwy zakładów odpowiadają pierwszym dziesięciu pozycjom tabeli na stronie poLCA.'
        title = f'{count} największych zgłoszonych źródeł CO₂ w Polsce — 2024'
        svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="720" viewBox="0 0 800 720" role="img" aria-labelledby="map-title map-desc">
<title id="map-title">{title}</title><desc id="map-desc">CO₂ ogółem, łącznie z biomasą, do powietrza. Dane E-PRTR za 2024 rok. Powierzchnia niebieskiego koła odpowiada emisji. Kropki miast i szare symbole regionów kruszyw są odniesieniami geograficznymi. {table_reference}</desc>
<metadata>{escape(json.dumps({k: data[k] for k in ['year', 'measure_pl', 'source_url', 'retrieved', 'selection', 'license', 'source_provider']}, ensure_ascii=False))}</metadata>
<defs><path id="poland" d="{outline}"/><clipPath id="country-clip"><use href="#poland"/></clipPath>{''.join(icons)}</defs>
<style>text{{font-family:Arial,sans-serif;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}}.city-label{{font-size:18px;font-weight:600;fill:#263e56}}.plant-label{{font-size:16px;font-weight:600;fill:#1355c4}}.region-label{{font-size:14px;fill:#526173}}.callout{{fill:none;stroke:#879bb0;stroke-width:1.1}}.city-dot{{fill:#263e56;stroke:#fff;stroke-width:2}}.rank{{font-size:13px;font-weight:700;fill:#1355c4;stroke-width:0}}.legend{{font-size:15px;fill:#526173}}</style>
<use href="#poland" fill="#f3f7fb" stroke="#748ca3" stroke-width="1.6"/>
<g clip-path="url(#country-clip)" fill="none" stroke="#bfd8ef" stroke-width="2" stroke-linecap="round">''']
        for river in geography['rivers']:
            geom = river['geometry']
            lines = geom['coordinates'] if geom['type'] == 'MultiLineString' else [geom['coordinates']]
            svg.extend(f'<path d="{path(line)}"/>' for line in lines)
        svg.append('</g>')
        for item in selected:
            x, y = project(item['longitude'], item['latitude'])
            r = radius(item['quantity_tonnes'])
            svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="#1355c4" fill-opacity=".16" stroke="#1355c4" stroke-width=".9"/>')
        # Small grey quarry symbols remain material context, not members of the ranking.
        for region, pos in zip(geography['regions'], [(172,349,46,196,428),(685,440,44,708,499)]):
            x, y = project(region['lon'], region['lat'])
            ix, iy, size, tx, ty = pos
            svg.append(f'<path class="callout" d="M{x:.2f},{y:.2f} L{ix+size/2},{iy+size*.8}"/><use href="#kruszywa" transform="translate({ix} {iy}) scale({size/100})" opacity=".75"/><text class="region-label" x="{tx}" y="{ty}" text-anchor="middle">{escape(region["name"])}<tspan x="{tx}" dy="16">kruszywa</tspan></text>')
        for item in selected:
            cfg = layout[item['local_id']]
            x, y = project(item['longitude'], item['latitude'])
            title = f'{item["rank"]}. {cfg["label"]}: {number(item["quantity_tonnes"])} t CO₂/rok; 2024, łącznie z biomasą'
            svg.append(f'<g><title>{escape(title)}</title>')
            if not detail:
                ix, iy, size, tx, ty = cfg['hero_layout']
                label_lines = cfg.get('hero_label_lines', [cfg['label']])
                label = escape(label_lines[0]) + ''.join(f'<tspan x="{tx}" dy="17">{escape(line)}</tspan>' for line in label_lines[1:])
                svg.append(f'<path class="callout" d="M{x:.2f},{y:.2f} L{ix+size/2},{iy+size*.75}"/><use href="#{cfg["symbol"]}" transform="translate({ix} {iy}) scale({size/100})"/><text class="plant-label" x="{tx}" y="{ty}" text-anchor="middle">{label}</text>')
            else:
                bx, by = cfg['detail_badge']
                svg.append(f'<path class="callout" d="M{x:.2f},{y:.2f} L{bx},{by}"/><circle cx="{bx}" cy="{by}" r="12" fill="#fff" stroke="#1355c4" stroke-width="1.2"/><text class="rank" x="{bx}" y="{by+4}" text-anchor="middle">{item["rank"]}</text>')
            svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.5" fill="#1355c4"/></g>')
        for city in geography['cities']:
            x, y = project(city['lon'], city['lat'])
            dx, dy, anchor = city['label']
            if city['name'] == 'Wrocław': dx, dy, anchor = 0, -28, 'middle'
            if city['name'] == 'Warszawa': dx, dy, anchor = -12, -15, 'end'
            if city['name'] == 'Kielce': dx, dy, anchor = 0, -15, 'middle'
            if city['name'] == 'Katowice': dx, dy, anchor = 20, -17, 'start'
            svg.append(f'<circle class="city-dot" cx="{x:.2f}" cy="{y:.2f}" r="3.2"/><text class="city-label" x="{x+dx:.2f}" y="{y+dy:.2f}" text-anchor="{anchor}">{escape(city["name"])}</text>')
        svg.append('<g class="legend"><text x="82" y="680">Roczna emisja CO₂</text>')
        for tonnes, x in [(5_000_000,303),(15_000_000,421),(30_000_000,554)]:
            r = radius(tonnes)
            svg.append(f'<circle cx="{x}" cy="674" r="{r:.2f}" fill="#1355c4" fill-opacity=".16" stroke="#1355c4" stroke-width=".9"/><text x="{x+r+9:.2f}" y="679">{tonnes//1_000_000} mln t</text>')
        svg.append('</g><text x="400" y="715" text-anchor="middle" font-size="12" fill="#526173">CO₂ ogółem, z biomasą · 2024 · Źródło: EEA / E-PRTR</text></svg>')
        return '\n'.join(svg) + '\n'

    for name, detail in [('polca-mapa-geograficzna.svg',False),('polca-mapa-emisji-20.svg',True)]:
        (root / 'images' / name).write_text(draw(detail))
    table_rows = []
    for p in rows:
        cfg = layout[p['local_id']]
        sector = 'Rafinerie' if p['eprtr_annex_i_main_activity'] == '1(a)' else p['sector_pl']
        # The public download preserves source names and identifiers verbatim.
        table_rows.append(f'''<tr id="zaklad-{p['rank']}"><td>{p['rank']}</td><th scope="row">{escape(cfg['label'])}<small>{escape(p['city'])}</small><details><summary>Nazwa i identyfikator w źródle</summary><p>{escape(p['name'])}<br>{escape(p['namespace'])} / {escape(p['local_id'])}</p></details></th><td>{escape(sector)}</td><td class="map-value">{number(p['quantity_tonnes'])}</td></tr>''')
    total = sum(Decimal(p['quantity_tonnes']) for p in rows)
    body = f'''<p class="map-measure"><strong>2024 · CO₂ ogółem, łącznie z biomasą</strong><br>20 największych zgłoszonych wartości emisji do powietrza w polskich raportach E-PRTR — Europejskiego Rejestru Uwalniania i Transferu Zanieczyszczeń.</p>
<p class="portal-map-hint">Na telefonie przesuń mapę w bok, aby zobaczyć całość.</p>
<figure class="portal-map-large" tabindex="0" role="region" aria-label="Mapa emisji CO₂, przewijana na małym ekranie"><a href="/images/polca-mapa-emisji-20.svg" aria-label="Otwórz mapę emisji w pełnym rozmiarze"><img src="/images/polca-mapa-emisji-20.svg" width="800" height="720" alt="20 największych zgłoszonych źródeł CO₂ ogółem w Polsce w 2024 roku. Numery zakładów odpowiadają tabeli poniżej."></a></figure>
<p class="map-reading">Powierzchnia niebieskiego koła odpowiada rocznej emisji. Numery odsyłają do tabeli. Szare szkice kruszyw pokazują kontekst surowcowy i nie należą do zestawienia emitentów.</p>
<h2>Zakłady i zgłoszone emisje</h2>
<p>Wybrane zakłady zgłosiły łącznie <strong>{number(total)} t CO₂</strong> za 2024 r. To suma dla tych 20 zakładów, nie całej Polski.</p>
<div class="portal-table-wrap map-table-wrap" tabindex="0" role="region" aria-label="Zestawienie zakładów i emisji, przewijane na małym ekranie"><table class="map-table"><thead><tr><th scope="col">Nr</th><th scope="col">Zakład / miejscowość</th><th scope="col">Branża</th><th scope="col">Emisja<br>t CO₂/rok</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>
<p class="map-downloads"><a href="/data/mapa-emisje-pl-2024.csv" download>Pobierz dane 20 zakładów (CSV)</a><a href="/data/mapa-emisje-pl-2024.json" download>Pobierz dane z opisem zakresu (JSON)</a></p>
<div class="portal-prose"><h2>Jak czytać te dane</h2>
<p>To zgłoszone uwolnienia CO₂ z zakładów do powietrza, obejmujące także CO₂ z biomasy. Nie są to emisje wyłącznie z paliw kopalnych ani suma wszystkich gazów cieplarnianych. Wielkość rocznej emisji opisuje skalę emisji zakładu; sama nie rozstrzyga o emisyjności tony produktu ani o efektywności producenta.</p>
<p>Mapa nie obejmuje wszystkich źródeł w Polsce, w tym rozproszonego transportu i ogrzewania budynków. Nie przedstawia też śladu węglowego wyrobów w całym cyklu życia. Na stronie głównej pokazano 10 pierwszych zakładów z tego samego zestawienia.</p>
<p>Zakłady nr 7 i 8 w Dąbrowie Górniczej mają niemal te same współrzędne źródłowe, dlatego ich koła na mapie się nakładają. Są wykazane osobno w tabeli.</p>
<h2>Źródło i sposób wyboru</h2>
<p>Dane pobrano 20 października 2026 r. z <a href="{data['source_url']}">oficjalnego zbioru emisji przemysłowych Europejskiej Agencji Środowiska</a>. Wybrano Polskę, rok sprawozdawczy 2024, substancję CO₂ i emisję do powietrza. Spośród 138 opublikowanych wartości wybrano 20 największych. Zgłoszone ilości w kilogramach podzielono przez 1000, aby uzyskać tony; nie uzupełniano braków oszacowaniami. Wyciąg opracowano na podstawie danych Europejskiej Agencji Środowiska, udostępnianych na licencji <a href="https://creativecommons.org/licenses/by/4.0/deed.pl">CC BY 4.0</a> — z uznaniem autorstwa.</p>
<p>Nazwy źródłowe, identyfikatory i współrzędne zachowano w plikach do pobrania. Krótkie podpisy na mapie służą orientacji; historyczna nazwa w rejestrze nie przesądza o aktualnym operatorze. Współrzędne mają dokładność zgłoszenia, a szkice są symbolami branż. Emisji zakładowych nie dodawano do pokrywających się danych o poszczególnych instalacjach spalania.</p>
<p>Wybór roku 2024 dotyczy tego zbioru emisji przemysłowych. Istnienie danych za 2025 r. w unijnym systemie handlu uprawnieniami do emisji nie oznacza identycznej miary ani kompletności tego samego zestawu zakładów. Definicje i pliki źródłowe udostępnia <a href="https://industry.eea.europa.eu/industrial-emissions/dataset">Europejski Portal Emisji Przemysłowych</a>.</p>
<h2>Geografia i regiony surowcowe</h2><p>Kontur, miasta i rzeki pochodzą z <a href="https://www.naturalearthdata.com/">Natural Earth</a>. Regiony kamienia łamanego i blocznego oznaczono zgodnie z opisem <a href="{geography['sources']['regions']}">Państwowego Instytutu Geologicznego – Państwowego Instytutu Badawczego</a>, orientacyjnie przy Rogoźnicy i Morawicy. Źródła punktów regionalnych: <a href="{geography['regions'][0]['coordinate_source']}">mapa Colas</a> i © <a href="https://www.openstreetmap.org/copyright">autorzy OpenStreetMap</a>.</p></div>'''
    page('mapa-polski.html','Źródła CO₂ w Polsce','Największe zgłoszone emisje przemysłowe w 2024 roku: zakłady, lokalizacje i dane źródłowe.',body,head_extra='<link rel="stylesheet" href="/assets/map.css?v=20261020emissions">')
