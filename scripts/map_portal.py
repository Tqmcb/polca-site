"""Geographic homepage illustration from explicit coordinates and small map symbols."""
import base64
import json
import math
from html import escape


def build(api):
    root, page = api['ROOT'], api['page']
    data = json.loads((root / 'content/home-map.json').read_text())
    ring = data['country']['coordinates'][0]
    cosine = math.cos(math.radians(52))
    xs, ys = [lon * cosine for lon, lat in ring], [-lat for lon, lat in ring]
    scale = min(650 / (max(xs) - min(xs)), 580 / (max(ys) - min(ys)))
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

    def project(lon, lat):
        return 400 + (lon * cosine - cx) * scale, 325 + (-lat - cy) * scale

    def path(coords):
        return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in (project(*p[:2]) for p in coords))

    outline = path(ring) + ' Z'
    icon_defs = []
    for name in ['elektrownia', 'kruszywa']:
        encoded = base64.b64encode((root / f'images/mapa-symbol-{name}.webp').read_bytes()).decode()
        icon_defs.append(f'<image id="{name}" width="100" height="100" href="data:image/webp;base64,{encoded}"/>')
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800" height="650" viewBox="0 0 800 650" role="img" aria-labelledby="map-title map-desc">
<title id="map-title">{escape(data['title'])}</title>
<desc id="map-desc">Główne miasta Polski oraz wybrane elektrownie Bełchatów, Kozienice, Opole i Turów. Regiony kruszyw kamiennych: Dolny Śląsk i Świętokrzyskie. Punkty odpowiadają przybliżonym lokalizacjom; drobne szkice są symbolami obiektów.</desc>
<metadata>{escape(json.dumps(data['sources'], ensure_ascii=False))}</metadata>
<defs><path id="poland" d="{outline}"/><clipPath id="country-clip"><use href="#poland"/></clipPath>{''.join(icon_defs)}</defs>
<style>text{{font-family:'Source Sans 3',Arial,sans-serif;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}}.city-label{{font-size:20px;font-weight:600;fill:#263e56}}.plant-label{{font-size:18px;font-weight:600;fill:#1355c4}}.region-label{{font-size:18px;font-weight:600;fill:#526173}}.region-kind{{font-size:14px;font-weight:400}}.callout{{fill:none;stroke:#879bb0;stroke-width:1.2}}.city-dot{{fill:#263e56;stroke:#fff;stroke-width:2}}</style>
<use href="#poland" fill="#f3f7fb" stroke="#748ca3" stroke-width="2" stroke-linejoin="round"/>
<g clip-path="url(#country-clip)" fill="none" stroke="#bfd8ef" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">''']
    for river in data['rivers']:
        geom = river['geometry']
        lines = geom['coordinates'] if geom['type'] == 'MultiLineString' else [geom['coordinates']]
        svg.extend(f'<path d="{path(line)}"/>' for line in lines)
    svg.append('</g>')
    for group, symbol in [('plants', 'elektrownia'), ('regions', 'kruszywa')]:
        for item in data[group]:
            x, y = project(item['lon'], item['lat'])
            ix, iy, size = item['icon']
            target_x, target_y = ix + size / 2, iy + size * .72
            svg.append(f'<g><title>{escape(item["name"])}</title><path class="callout" d="M{x:.2f},{y:.2f} L{target_x:.2f},{target_y:.2f}"/><use href="#{symbol}" transform="translate({ix} {iy}) scale({size / 100})"/>')
            if group == 'plants':
                svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="#1355c4" stroke="#fff" stroke-width="1.5"/><text class="plant-label" x="{item["label"][0]}" y="{item["label"][1]}" text-anchor="middle">{escape(item["name"])}</text>')
            else:
                tx, ty, anchor = item['label']
                svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#526173" stroke="#fff" stroke-width="1.5"/><text class="region-label" x="{tx}" y="{ty}" text-anchor="{anchor}">{escape(item["name"])}<tspan class="region-kind" x="{tx}" dy="18">kruszywa kamienne</tspan></text>')
            svg.append('</g>')
    for city in data['cities']:
        x, y = project(city['lon'], city['lat'])
        dx, dy, anchor = city['label']
        radius = 4.5 if city['name'] == 'Warszawa' else 3.5
        svg.append(f'<g><circle class="city-dot" cx="{x:.2f}" cy="{y:.2f}" r="{radius}"/><text class="city-label" x="{x + dx:.2f}" y="{y + dy:.2f}" text-anchor="{anchor}">{escape(city["name"])}</text></g>')
    svg.append('</svg>')
    (root / 'images/polca-mapa-geograficzna.svg').write_text('\n'.join(svg) + '\n')
    rows = ''.join(f'<tr><th scope="row">{escape(p["name"])}</th><td>{escape(p["place"])}</td><td><a href="{escape(p["source"])}">Potwierdzenie lokalizacji</a></td></tr>' for p in data['plants'])
    body = f'''<p class="portal-map-hint" id="map-scroll-hint">Na telefonie przesuń mapę w bok, aby zobaczyć całość.</p><figure class="portal-map-large" tabindex="0" role="region" aria-label="Mapa Polski, przewijana na małym ekranie"><a href="/images/polca-mapa-geograficzna.svg" aria-label="Otwórz mapę Polski w pełnym rozmiarze"><img src="/images/polca-mapa-geograficzna.svg" width="800" height="650" alt="Mapa Polski z nazwami 13 miast, czterema wybranymi elektrowniami i dwoma regionami wydobycia kruszyw kamiennych."></a></figure>
<div class="portal-prose"><p>Kropki z ciemnymi podpisami oznaczają miasta. Niebieskie podpisy i szkice elektrowni wskazują wybrane zakłady. Symbole kruszyw odnoszą się do regionów wydobycia kamienia. Rysunki są znakami mapy; nie odwzorowują architektury konkretnych instalacji.</p>
<h2>Wybrane elektrownie</h2><p>Położenie zakładu może różnić się od położenia miasta, od którego pochodzi jego nazwa.</p><div class="portal-table-wrap"><table><thead><tr><th>Elektrownia</th><th>Miejscowość</th><th>Źródło</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>Przybliżone współrzędne pochodzą z <a href="{data['sources']['plant_coordinates']}">bazy elektrowni World Resources Institute</a>, z rekordów wskazujących University of Dąbrowa Górnicza jako źródło lokalizacji. Wykorzystano wyłącznie położenie obiektów, bez danych o mocy i aktualnym stanie pracy.</p>
<h2>Regiony kruszyw</h2><p>Dolny Śląsk i Świętokrzyskie wyróżniają się koncentracją górnictwa kamienia łamanego i blocznego, opisaną przez <a href="{data['sources']['regions']}">Państwowy Instytut Geologiczny – Państwowy Instytut Badawczy</a>. Symbole umieszczono orientacyjnie przy Rogoźnicy w okolicach Strzegomia oraz przy Morawicy na południe od Kielc. Położenia odniesiono do <a href="{data['regions'][0]['coordinate_source']}">mapy kopalni Rogoźnica</a> i <a href="https://www.openstreetmap.org/way/344605001">obrysu wyrobiska w Morawicy w OpenStreetMap</a>. Dane wyrobiska: © <a href="https://www.openstreetmap.org/copyright">autorzy OpenStreetMap</a>.</p>
<h2>Podkład geograficzny</h2><p>Kontur kraju, miasta oraz główne rzeki pochodzą z <a href="https://www.naturalearthdata.com/">Natural Earth</a> — zbioru danych w <a href="https://www.naturalearthdata.com/about/terms-of-use/">domenie publicznej</a>. Mapa jest uproszczona i nie przedstawia kompletnego wykazu instalacji ani pokrycia zasobów bazy poLCA.</p></div>'''
    page('mapa-polski.html', 'Mapa Polski', 'Miasta, wybrane elektrownie i regiony surowcowe pokazane na stronie głównej poLCA.', body, head_extra='<link rel="stylesheet" href="/assets/map.css?v=20261020geography">')
