"""Product-first navigation; CPR families are discovery metadata, not approvals."""
import json
from itertools import groupby

from aggregate_guide import TRUCK, aggregate_guide, display_result
from cement_guide import cement_guide
from concrete_portal import build_calculator as build_concrete_calculator, concrete_guide, concrete_references
from precast_guide import precast_guide

from atlas_icons import family_icon


def load(root):
    return json.loads((root / 'data/cpr-families.json').read_text()), json.loads((root / 'data/product-methods.json').read_text())


def family_url(family_id):
    return f'/wyroby/{int(family_id):02d}.html'


# The visible family names and public URLs come from the same taxonomy as the directory.
PRODUCT_PHOTOS = {
    24: ('kruszywa', 'Dane materiałowe i kalkulator kruszyw',
         'Ilustracja kopalni odkrywkowej z poziomami wydobywczymi i pryzmą kruszywa.'),
    1: ('beton', 'Zasady oceny i składniki do obliczeń',
        'Ilustracja prefabrykowanych elementów betonowych na podkładach przed halą.'),
    15: ('cement', 'Dane dla poszczególnych rodzajów cementu',
         'Ilustracja pieca obrotowego i instalacji w cementowni.'),
}
FAMILY_CSS = '<link rel="stylesheet" href="/assets/product-photos.css?v=20261122-linki">'


def family_photo(family_id, *, standalone=False):
    image, _, description = PRODUCT_PHOTOS[family_id]
    alt = description if standalone else ''
    return (f'<img class="family-photo photo-{image}" src="/images/wyroby-{image}.webp" '
            f'alt="{alt}" decoding="async">')


def photo_directory(families, e):
    items = []
    by_id = {family['id']: family for family in families}
    for family_id, (_, description, _) in PRODUCT_PHOTOS.items():
        family = by_id[family_id]
        items.append(f'''<li><a href="{family_url(family_id)}">
        {family_photo(family_id)}<span class="family-photo-caption">
        <strong>{e(family['label'])}</strong><span>{e(description)}</span></span></a></li>''')
    return ('<nav class="family-photo-directory" aria-label="Kruszywa, prefabrykaty betonowe i spoiwa">'
            '<ul>' + ''.join(items) + '</ul></nav>')


def family_heading(family, e, navigation):
    family_id = family['id']
    heading = f'''<div class="family-heading">
    <span class="family-insignia">{family_icon(family_id)}</span>
    <div><h1>{e(family['label'])}</h1>
    <p>Rodzina {family_id} w załączniku VII do rozporządzenia o wyrobach budowlanych.</p>
    </div></div>'''
    nav = f'<nav class="family-banner-links" aria-label="Zawartość karty">{navigation}</nav>'
    if family_id in PRODUCT_PHOTOS:
        return (f'<header class="family-photo-banner">{heading}'
                f'{family_photo(family_id, standalone=True)}</header>{nav}')
    return f'<div class="family-overview"><header>{heading}</header>{nav}</div>'


def dataset_count(count):
    if count == 0:
        return 'Bez branżowego zestawu danych'
    if count == 1:
        return '1 pozycja danych'
    noun = 'pozycje' if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14 else 'pozycji'
    return f'{count} {noun} danych'


def family_data(datasets, family_id, api):
    e, a, num = (api[key] for key in ('e', 'a', 'num'))
    if not datasets:
        return ('<section id="dane" class="family-record-section"><h2>Dostępność danych dla rodziny</h2>'
                '<p>W katalogu poLCA nie ma jeszcze branżowego zestawu danych dla tej rodziny.</p></section>')

    def metadata(record):
        year = record.get('year')
        year_label = {'publication': 'Rok publikacji', 'reference': 'Rok odniesienia'}.get(record.get('year_type'), 'Rok')
        return {
            'indicator': record.get('indicator_label'),
            'status': record.get('status_label'),
            'year': f'{year_label} {year}' if year else '',
            'formats': ', '.join(record.get('formats', [])),
        }

    def labels(values):
        return ''.join(f'<span>{e(value)}</span>' for value in values if value)

    metadata_rows = [metadata(record) for record in datasets]
    first = metadata_rows[0]
    shared = {key: value for key, value in first.items() if all(row[key] == value for row in metadata_rows)}
    heading = 'Wskaźniki dla kruszyw' if family_id == 24 else 'Wskaźniki środowiskowe dla wyrobów'
    parts = [f'<section id="dane" class="family-record-section"><h2>{heading}</h2>']
    if family_id == 15:
        parts.append('<p>Wskaźniki dla poszczególnych klas cementu wycofano '
                     '<a href="/rejestr-zmian.html#rejestr">23.11.2026</a>, ponieważ ich wartości nie potwierdzono w deklaracjach środowiskowych producentów.</p>')
    shared_labels = labels(shared.values())
    if shared_labels:
        parts.append(f'<p class="family-record-meta">{shared_labels}</p>')
    parts.append('<div class="family-indicators">')
    for description, grouped in groupby(datasets, key=lambda record: record.get('description', '')):
        group = list(grouped)
        if description and len(group) > 1:
            parts.append(f'<p class="family-indicators-scope">{e(description)}</p>')
        for record in group:
            details = description if len(group) == 1 else ''
            card_class = 'family-indicator'
            if family_id == 24 and record['id'] == 'POLCA-FILLER-LIMESTONE-DEFAULT-2026':
                card_class += ' family-indicator-filler'
                details = ('Wartość dla 1 t kruszywa wypełniającego do mieszanki asfaltowej. '
                           'Inne zastosowanie wymaga odrębnego przypisania.')
            item_labels = labels(value for key, value in metadata(record).items() if key not in shared)
            value = record.get('value')
            parts.append(f'<article class="{card_class}" data-record-id="{e(record["id"])}">')
            parts.append(f'<h3>{a(record["title"], record["href"])}</h3>')
            if isinstance(value, (int, float)):
                displayed = api['record_value'](record) if record['category_id'] == 'beton' else num(value)
                parts.append(f'<p class="family-indicator-value"><strong>{e(displayed)}</strong> <span>{e(record.get("unit"))}</span></p>')
            if details:
                parts.append(f'<p class="family-indicator-note">{e(details)}</p>')
            if item_labels:
                parts.append(f'<p class="family-indicator-note family-record-meta">{item_labels}</p>')
            parts.append('</article>')
    parts.append('</div></section>')
    return ''.join(parts)


def family_guides(has_methods, has_tools, api):
    icon = api['navigation_icon']
    # Keep old fragment URLs useful even on families with only shared guidance.
    method_anchor = '' if has_methods else ' id="metoda"'
    tool_anchor = '' if has_tools else ' id="narzedzia"'
    method_note = '' if has_methods else '<small>W katalogu nie wskazano dokumentu branżowego dla tej rodziny.</small>'
    return f'''<aside class="family-guides" aria-labelledby="family-shared-title">
    <h2 id="family-shared-title">Dane i zasady wspólne dla wyrobów</h2>
    <ul>
      <li{method_anchor}>{icon('methods')}<div><a href="/c-pcr/#dobor">Jak dobrać zasady kategorii wyrobu i sprawdzić ich status?</a>{method_note}</div></li>
      <li>{icon('data')}<a href="/dane-wspolne.html">Energia elektryczna, paliwa i transport</a></li>
      <li>{icon('methods')}<a href="/metodyka-defaults-ue.html#dane-tla-cpr">Dane tła w zamówieniu Komisji Europejskiej</a></li>
      <li{tool_anchor}>{icon('guide')}<a href="/zastosowanie-danych.html">Dobór danych do obliczeń dla wyrobu i budynku</a></li>
    </ul></aside>'''


def build(api):
    root, page, e, a, links, row = (api[k] for k in ('ROOT', 'page', 'e', 'a', 'links', 'row'))
    taxonomy, methods = load(root)
    families = taxonomy['families']
    catalog = api['CAT']
    records = catalog['datasets'] + catalog['resources']
    source_url = 'https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32024R3110'

    def associated(f, kind):
        return [r for r in records if r['kind'] == kind and (f['id'] in r.get('cpr_family_ids', []) or (kind=='article' and any(x['family_id']==f['id'] for x in r.get('cpr_related',[]))))]

    def rules(f):
        return [m for m in methods['documents'] if f['id'] in m['family_ids']]

    def available(f):
        return any(associated(f, k) for k in ['dataset', 'tool', 'article']) or bool(rules(f))

    def method_list(items, show_families=False, family_id=None):
        if not items:
            return '<p>W tym katalogu nie wskazano jeszcze branżowego dokumentu c-PCR dla tej rodziny. Dobierz go do konkretnego wyrobu i zasad programu deklaracji.</p>'
        cards = []
        for method in items:
            scope = method.get('family_scope', {}).get(str(family_id), method['scope_note'])
            card = (f'<li><h3>{a(method["designation"], method["url"])}</h3>'
                    f'<p>{e(method["title_pl"])}</p><p class="product-meta">{e(method["status_label"])}</p>'
                    f'<p>{e(scope)}</p>')
            if show_families:
                related = [{'label': f['label'] + ' (rodzina ' + str(f['id']) + ')',
                            'href': family_url(f['id'])} for f in families if f['id'] in method['family_ids']]
                card += links(related, 'product-method-families')
            cards.append(card + '</li>')
        return '<ul class="product-methods">' + ''.join(cards) + '</ul>'

    def aggregate_projects(items):
        checked_on = min(m['checked_on'] for m in items)
        display_date = '.'.join(reversed(checked_on.split('-')))
        cards = ''.join(
            '<article><h3>' + e(m['title_pl']) + '</h3><p>' + e(m['scope_note'])
            + '</p><p>' + a(m['designation'], m['url']) + '</p></article>' for m in items)
        return ('<section id="sec-1" class="portal-section"><h2 id="projekty-cen">Jakie zastosowania kruszyw obejmują projekty CEN?</h2>'
                '<div class="portal-reading"><p>Podstawowe zasady deklaracji środowiskowych wyrobów budowlanych określa '
                + a('PN-EN 15804+A2', 'https://sklep.pkn.pl/normy/pn-en-15804-a2-2020-03p.html')
                + '. Europejski Komitet Normalizacyjny (CEN) prowadzi prace nad zasadami dla samych kruszyw. '
                f'Według stanu na <time datetime="{e(checked_on)}">{e(display_date)} r.</time> '
                'oba projekty komitetu CEN/TC 154 mają status „Preliminary” (etap wstępny).</p></div>'
                '<div class="portal-columns">' + cards + '</div></section>')

    def piping_table(items):
        rows = ''.join(
            f'<tr><th scope="row">{e(m["installation"])}</th>'
            f'<td>{a(m["designation"], m["url"])}<br>{e(m["scope_note"])}</td></tr>'
            for m in items)
        family_ids = {fid for m in items for fid in m['family_ids']}
        family_links = [{'label': f['label'] + ' (rodzina ' + str(f['id']) + ')',
                         'href': family_url(f['id'])} for f in families if f['id'] in family_ids]
        return ('<section id="przewody"><h3>Jak dobrać normę dla przewodów z tworzyw sztucznych?</h3>'
                '<p>Obie normy uzupełniają EN 15804. O wyborze decydują miejsce montażu i zastosowanie przewodu.</p>'
                '<div class="portal-table-wrap" role="region" aria-label="Dobór normy dla przewodów" tabindex="0">'
                '<table><thead><tr><th scope="col">Miejsce montażu</th><th scope="col">Norma i zakres</th></tr></thead>'
                '<tbody>' + rows + '</tbody></table></div>' + links(family_links, 'product-method-families') + '</section>')

    def common():
        return '<section class="portal-section product-common"><h2>Energia, paliwa i transport</h2><p>Dane pomocnicze do procesów w różnych branżach. Wybór zależy od granic obliczenia i przyjętej metody.</p>' + links([
            {'label':'Energia elektryczna','href':'/datasety.html?category=energia'},
            {'label':'Paliwa','href':'/datasety.html?category=paliwa'},
            {'label':'Transport','href':'/datasety.html?category=transport'},
        ], 'product-inline-links') + '</section>'

    from home_portal import build as build_home
    build_home(api, families)

    intro = '<p class="product-intro">Podział obejmuje 36 rodzin z <a href="' + source_url + '">załącznika VII do CPR — rozporządzenia o wyrobach budowlanych (UE) 2024/3110</a>. Przy każdej rodzinie widać, jakie materiały zawiera portal.</p>'
    form = '<form id="family-search" class="portal-search" action="/wyroby.html" role="search"><div class="family-search-label"><label for="family-query">Nazwa lub numer rodziny</label><a href="#wykaz-rodzin">Pełny wykaz</a></div><div class="portal-search-control"><input id="family-query" type="search" name="q" placeholder="Np. kruszywo, drzwi, 24"><button type="submit">Szukaj</button></div><div class="family-search-options"><label class="product-checkbox"><input type="checkbox" name="available" value="1"> Tylko rodziny z materiałami w poLCA</label></div></form>'
    family_rows = ''
    for f in families:
        n = len(associated(f, 'dataset'))
        label = dataset_count(n)
        family_rules = rules(f)
        if family_rules and all(m['status'] == 'preliminary' for m in family_rules):
            label += ' · projekty CEN'
        elif family_rules: label += ' · dokumenty metodyczne'
        elif associated(f, 'article'): label += ' · artykuły'
        product_names = [r['title']+' '+r['id'] for r in associated(f,'dataset')]
        search = ' '.join([str(f['id']), str(f['id']).zfill(2), f['official_name'], f['label']] + f['keywords'] + product_names)
        family_rows += f'<li data-family="{f["id"]}" data-search="{e(search)}" data-available="{str(available(f)).lower()}"><a href="{family_url(f["id"])}"><span class="family-list-insignia">{family_icon(f["id"])}</span><span class="product-family-code">{f["id"]:02d}</span><span><strong>{e(f["label"])}</strong><small>{e(label)}</small></span></a></li>'
    title = 'Dane dla wyrobów budowlanych'
    lead = 'Dane środowiskowe, metody i narzędzia według rodziny wyrobu.'
    head = (f'<div class="family-directory-intro"><header><h1>{e(title)}</h1><p>{e(lead)}</p></header>'
            + form + '</div>')
    listing = ('<div class="family-list-heading" id="wykaz-rodzin" tabindex="-1"><h2>Wykaz rodzin</h2>'
               '<p id="family-count" role="status" aria-live="polite">Rodziny wyrobów: 36 z 36</p></div>')
    body = head + photo_directory(families, e) + listing + '<noscript><p>Poniżej znajduje się pełna lista. Wyszukiwanie wymaga JavaScript; możesz też użyć wyszukiwania w przeglądarce.</p></noscript><ul id="family-list" class="product-families">' + family_rows + '</ul><div id="family-empty" hidden><h2>Nie znaleziono rodziny</h2><p>Wpisz krótszą nazwę, numer od 1 do 36 albo wyłącz filtr dostępnych materiałów.</p><button type="button" id="family-reset">Pokaż wszystkie rodziny</button></div><p class="product-intro">Dla energii, paliw i transportu wybierz <a href="/dane-wspolne.html">dane wspólne</a>. <a href="/c-pcr/">Jak dobierać zasady PCR i c-PCR</a>.</p>'
    page('wyroby.html', title, lead, body + intro, attrs='data-product-directory', head_extra=FAMILY_CSS, pagehead=False)

    for f in families:
        datasets, tools, articles = (associated(f, k) for k in ['dataset', 'tool', 'article'])
        family_methods = rules(f)
        drafts = [r for r in associated(f, 'method') if r['id'] in ['method-mma', 'method-kruszywa']]
        has_methods = bool(family_methods or drafts)
        has_tools = bool(tools or articles)
        destinations = [{'label': 'Dane', 'href': '#dane'}]
        if f['id'] == 24:
            destinations.append({'label': 'Zastosowania kruszywa', 'href': '#modul-a1'})
        elif f['id'] == 15:
            destinations.append({'label': 'Cement w betonie', 'href': '#modul-a1-cement'})
        elif f['id'] == 1:
            destinations.append({'label': 'Przykład obliczeń', 'href': '#przyklad-prefabrykat'})
        elif f['id'] == 26:
            destinations.append({'label': 'Beton według klasy wytrzymałości', 'href': '#beton-towarowy'})
        destinations += [
            {'label': 'Dokumenty branżowe' if has_methods else 'Dobór zasad obliczeń', 'href': '#metoda'},
            {'label': 'Narzędzia i opracowania' if has_tools else 'Dobór danych', 'href': '#narzedzia'},
        ]
        body = family_heading(f, e, links(destinations, 'portal-subnav'))
        body += family_data(datasets, f['id'], api)
        inputs = [r for r in catalog['datasets'] if any(x['family_id']==f['id'] and x['role'] in ['input_to_product','process_for_product','parameters_for_product'] for x in r.get('cpr_related',[]))]
        if inputs:
            body += ('<section class="family-record-section"><h2>Składniki i parametry do obliczeń</h2>'
                     '<p>Dane wejściowe do receptury lub procesu. Nie opisują wyniku dla całego wyrobu.</p>'
                     + links([{'label':r['title'],'href':r['href']} for r in inputs], 'family-inputs') + '</section>')
        extra = FAMILY_CSS + '<link rel="stylesheet" href="/assets/family-record.css?v=1">'
        if f['id'] == 24:
            mma_profile = json.loads((root / 'data/mma-client-example.json').read_text())
            body += aggregate_guide(catalog, mma_profile)
        elif f['id'] == 15:
            body += cement_guide(catalog, api['section_table'])
        elif f['id'] == 1:
            body += precast_guide(catalog, api['section_table'])
        elif f['id'] == 26:
            evidence, references = concrete_references(root, catalog)
            body += concrete_guide(evidence, references, api['section_table'], api['num'])
            build_concrete_calculator(root, catalog, references, page)
        if f['id'] in (15, 24):
            extra += ('<link rel="stylesheet" href="/assets/aggregate-guide.css?v=7">'
                      '<script src="/assets/aggregate-guide.js?v=2" defer></script>')

        if has_methods or has_tools:
            body += '<div class="family-resources">'
            if has_methods:
                body += '<section id="metoda"><h2>Dokumenty dla tej rodziny</h2>'
                if f['id'] == 24 and family_methods and all(m['status'] == 'preliminary' for m in family_methods):
                    body += '<p>Projekty branżowych zasad dla kruszyw są na etapie wstępnym.</p>'
                    body += a('Zakres obu części i karty projektów CEN', '/c-pcr/kruszywa.html#projekty-cen')
                elif family_methods:
                    body += method_list(family_methods, family_id=f['id'])
                    if any('installation' in m for m in family_methods):
                        body += a('Porównanie norm dla przewodów według miejsca montażu', '/c-pcr/index.html#przewody')
                else:
                    body += '<p>W katalogu nie wskazano branżowych zasad uzupełniających (c-PCR) dla tej rodziny.</p>'
                for draft in drafts:
                    body += (f'<p class="family-resource-link">{a(draft["title"], draft["href"])}</p>'
                             f'<p class="family-resource-detail">{e(draft["status_label"])} · {e(draft["year"])} · wersja archiwalna</p>')
                body += '</section>'
            if has_tools:
                body += '<section id="narzedzia"><h2>Narzędzia i opracowania dla wyrobu</h2>'
                for resource in tools + articles:
                    details = ' · '.join(str(v) for v in (resource.get('status_label'), resource.get('year')) if v)
                    transport_note = ''
                    if f['id'] == 24 and resource['id'] == 'tool-kruszywa':
                        factor = next(r['value'] for r in catalog['datasets'] if r['id'] == TRUCK)
                        transport_note = (
                            f'<p>Przy przewozie 1 t kruszywa na budowę na odległość 40 km wynik na karcie wynosi '
                            f'{display_result(40 * factor)} kg CO₂e w module A4 (współczynnik {api["num"](factor)} kg CO₂e/(t·km)). '
                            'Kalkulator stosuje ten sam współczynnik.</p>')
                    body += (f'<article class="family-resource" data-record-id="{e(resource["id"])}">'
                             f'<h3>{a(resource["title"], resource["href"])}</h3>'
                             f'<p>{e(resource["description"])}</p>{transport_note}<small>{e(details)}</small></article>')
                body += '</section>'
            body += '</div>'

        body += family_guides(has_methods, has_tools, api)
        body += ('<details class="product-official"><summary>Pełna nazwa rodziny w rozporządzeniu</summary><p>'
                 + e(f['official_name']) + '</p><p>Zakres wyrobu i zasady oceny określają właściwe dokumenty techniczne.</p>'
                 + a('Tekst rozporządzenia',source_url) + '</details>')
        page(family_url(f['id'])[1:], f['label'], 'Dane i dokumenty dla rodziny ' + str(f['id']) + ' z załącznika VII CPR.',
             body, parent=('Rodziny wyrobów','/wyroby.html'), pagehead=False,
             attrs='data-product-family data-product-photo' if f['id'] in PRODUCT_PHOTOS else 'data-product-family', head_extra=extra)
        if not available(f):
            p=root/family_url(f['id'])[1:]
            p.write_text(p.read_text().replace('</head>','<meta name="robots" content="noindex,follow"></head>'))

    body = '<div class="portal-reading"><section id="wstep" class="portal-prose"><h2>Metoda ogólna i zasady dla wyrobu</h2><p>EN 15804 określa podstawowe zasady deklaracji środowiskowych EPD dla wyrobów budowlanych. Dokument c-PCR uzupełnia je w zakresie określonego rodzaju wyrobu. Jedna rodzina CPR może obejmować kilka różnych dokumentów metodycznych.</p></section><section id="dobor" class="portal-prose"><h2>Jak dobrać metodę</h2><ol><li>Określ wyrób, jego zastosowanie i zakres obliczenia.</li><li>Sprawdź zakres i wydanie dokumentu c-PCR oraz zasady programu EPD.</li><li>Dla oceny wymaganej przez CPR sprawdź właściwą specyfikację techniczną i wymagania mające zastosowanie do wyrobu.</li></ol><p>Wydana norma c-PCR nie jest automatycznie zharmonizowaną specyfikacją techniczną CPR. <a href="/zastosowanie-epd-cpr.html">Więcej o zastosowaniu danych w EPD i CPR</a>.</p></section><section id="cpcr-lista" class="portal-section"><h2>Dokumenty według wyrobu</h2>'
    published = [m for m in methods['documents'] if m['family_ids'] and m['status']=='published' and m['role']=='complementary_pcr']
    body += method_list([m for m in published if 'installation' not in m], show_families=True)
    body += piping_table([m for m in published if 'installation' in m])
    body += '</section><section class="portal-section"><h2>Dokumenty wspólne: zasady i jakość danych</h2>' + method_list([m for m in methods['documents'] if not m['family_ids']]) + '</section><section class="portal-section"><h2>Dokumenty pomocnicze</h2>' + method_list([m for m in methods['documents'] if m['role']=='technical_review'], show_families=True) + '</section><section id="projekty" class="portal-section"><h2>Projekty norm</h2><p>' + e(methods['drafts_intro']) + '</p>' + method_list([m for m in methods['documents'] if m['status']=='draft'], show_families=True) + '</section>'
    body += ('<section id="prace-wstepne" class="portal-prose"><h2>Prace CEN na etapie wstępnym</h2>'
             '<p>' + a('Kruszywa jako składnik wyrobu i do zastosowania bezpośredniego', '/c-pcr/kruszywa.html#projekty-cen') + '</p></section>')
    body += '<section id="powiazania" class="portal-prose"><h2>Dokumenty poLCA</h2><p>Przy dokumentach branżowych podajemy ich wersję i status. Opublikowanie projektu nie potwierdza przyjęcia go jako reguły programu.</p>' + links([{'label':'Mieszanki asfaltowe — metoda i projekt poLCA','href':'/c-pcr/mma.html'},{'label':'Kruszywa — dane i status projektu poLCA','href':'/c-pcr/kruszywa.html'},{'label':'Wybierz rodzinę wyrobu','href':'/wyroby.html'}]) + '</section></div>'
    page('c-pcr/index.html','Zasady obliczeń dla wyrobów','PCR — zasady kategorii wyrobów. c-PCR — zasady uzupełniające dla określonych grup produktów.',body)

    for slug, fid, title, version in [('mma',23,'Mieszanki mineralno-asfaltowe','v1.0-DRAFT'),('kruszywa',24,'Kruszywa','v0.9-DRAFT')]:
        f=next(x for x in families if x['id']==fid)
        preliminary = [m for m in rules(f) if m['status'] == 'preliminary']
        if slug == 'kruszywa' and preliminary:
            body = aggregate_projects(preliminary) + '<div class="portal-reading">'
            other_rules = [m for m in rules(f) if m['status'] != 'preliminary']
            if other_rules:
                body += '<section class="portal-prose"><h2>Dokumenty metodyczne</h2>' + method_list(other_rules) + '</section>'
        else:
            body = '<div class="portal-reading"><section id="sec-1" class="portal-prose"><h2>Dokumenty metodyczne</h2>' + method_list(rules(f)) + '</section>'
        body += '<section id="sec-2" class="portal-prose"><h2>Projekt poLCA — ' + version + '</h2><p>Historyczny projekt reguł programu EPD Polska. Nie jest prezentowany jako zatwierdzone wydanie końcowe. Do nowego opracowania dobierz właściwy dokument branżowy i zasady programu.</p>'
        if slug=='mma':
            body+=links([{'label':'Archiwalny projekt c-PCR MMA — PDF','href':'/c-pcr/c-PCR-MMA-EPD-Polska-2026-v1.0-DRAFT.pdf'},{'label':'Archiwalny raport danych MMA — PDF','href':'/c-pcr/Raport-LCI-MMA-Polska-EN15804A2.pdf'}])
            body += ('<p class="portal-callout">Tabela 6.1 raportu przyjmuje zawartość lepiszcza wyższą niż minimalne wartości WT-2 2014 '
                     '(np. 15% dla AC 11 S przy Bmin 5,8%). Wyniki z tej tabeli są zawyżone; aktualne wartości podają '
                     '<a href="/wyroby/23.html#dane">rekordy poLCA</a> i <a href="/kalkulator-mma.html">kalkulator MMA</a>.</p>')
        else: body+='<p>W portalu nie udostępniono pełnego dokumentu projektu c-PCR kruszyw do pobrania.</p>'
        body+='</section>'+''.join(f'<span id="sec-{n}"></span>' for n in range(4,10))+'<section id="sec-3" class="portal-prose"><h2>Dane i obliczenia</h2>' + links([{'label':title+' — dane, narzędzia i dokumenty','href':family_url(fid)}]) + '</section><section class="portal-prose"><h2>Dobór danych</h2><p>Jednostkę, granice systemu, moduły i założenia określ dla konkretnego badania. Samo zestawienie wskaźników materiałowych nie zastępuje metody oceny.</p>' + a('Jak wybrać metodę','/c-pcr/#dobor')+'</section></div>'
        page(f'c-pcr/{slug}.html',title+' — zasady obliczeń i dokumenty','Dokumenty branżowe, status projektu i odnośniki do danych dla wyrobu.',body,parent=('Zasady obliczeń','/c-pcr/'))

    body=common() + '<section class="portal-section"><h2>Wszystkie dane wspólne</h2>' + ''.join(row(r) for r in catalog['datasets'] if r['category_id'] in ['energia','paliwa','transport']) + '</section><section class="portal-section"><h2>Przeliczniki i instrukcje</h2>' + links([{'label':'Kalkulatory energii i transportu','href':'/kalkulatory.html'},{'label':'Dobór danych do zastosowania','href':'/zastosowanie-danych.html'}]) + '</section>'
    page('dane-wspolne.html','Dane wspólne: energia, paliwa i transport','Współczynniki i modele pomocnicze do obliczeń w różnych branżach.',body)
