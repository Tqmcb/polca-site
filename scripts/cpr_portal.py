"""Product-first navigation; CPR families are discovery metadata, not approvals."""
import json


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
PHOTO_CSS = '<link rel="stylesheet" href="/assets/product-photos.css?v=1">'


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


def family_banner(family, e):
    return f'''<header class="family-photo-banner"><div>
    <h1>{e(family['label'])}</h1>
    <p>Rodzina {family['id']} w załączniku VII do rozporządzenia o wyrobach budowlanych.</p>
    </div>{family_photo(family['id'], standalone=True)}</header>'''


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

    def method_list(items, show_families=False):
        if not items:
            return '<p>W tym katalogu nie wskazano jeszcze branżowego dokumentu c-PCR dla tej rodziny. Dobierz go do konkretnego wyrobu i zasad programu deklaracji.</p>'
        return '<ul class="product-methods">' + ''.join(
            f'<li><h3>{a(m["designation"],m["url"])}</h3><p>{e(m["title_pl"])}</p><p class="product-meta">{e(m["status_label"])}</p><p>{e(m["scope_note"])}</p>' + (links([{'label':f['label']+' (rodzina '+str(f['id'])+')','href':family_url(f['id'])} for f in families if f['id'] in m['family_ids']], 'product-method-families') if show_families else '') + '</li>' for m in items) + '</ul>'

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
        label = f'{n} pozycji danych' if n else 'Bez branżowego zestawu danych'
        if rules(f): label += ' · dokumenty metodyczne'
        elif associated(f, 'article'): label += ' · artykuły'
        product_names = [r['title']+' '+r['id'] for r in associated(f,'dataset')]
        search = ' '.join([str(f['id']), str(f['id']).zfill(2), f['official_name'], f['label']] + f['keywords'] + product_names)
        family_rows += f'<li data-family="{f["id"]}" data-search="{e(search)}" data-available="{str(available(f)).lower()}"><a href="{family_url(f["id"])}"><span class="product-family-code">{f["id"]:02d}</span><span><strong>{e(f["label"])}</strong><small>{e(label)}</small></span><span class="product-open">Otwórz</span></a></li>'
    title = 'Dane dla wyrobów budowlanych'
    lead = 'Dane środowiskowe, metody i narzędzia według rodziny wyrobu.'
    head = (f'<div class="family-directory-intro"><header><h1>{e(title)}</h1><p>{e(lead)}</p></header>'
            + form + '</div>')
    listing = ('<div class="family-list-heading" id="wykaz-rodzin" tabindex="-1"><h2>Wykaz rodzin</h2>'
               '<p id="family-count" role="status" aria-live="polite">Rodziny wyrobów: 36 z 36</p></div>')
    body = head + photo_directory(families, e) + listing + '<noscript><p>Poniżej znajduje się pełna lista. Wyszukiwanie wymaga JavaScript; możesz też użyć wyszukiwania w przeglądarce.</p></noscript><ul class="product-families">' + family_rows + '</ul><div id="family-empty" hidden><h2>Nie znaleziono rodziny</h2><p>Wpisz krótszą nazwę, numer od 1 do 36 albo wyłącz filtr dostępnych materiałów.</p><button type="button" id="family-reset">Pokaż wszystkie rodziny</button></div><p class="product-intro">Dla energii, paliw i transportu wybierz <a href="/dane-wspolne.html">dane wspólne</a>. <a href="/c-pcr/">Jak dobierać zasady PCR i c-PCR</a>.</p>'
    page('wyroby.html', title, lead, body + intro, attrs='data-product-directory', head_extra=PHOTO_CSS, pagehead=False)

    for f in families:
        datasets, tools, articles = (associated(f, k) for k in ['dataset','tool','article'])
        body = '<details class="product-official"><summary>Pełna nazwa rodziny w rozporządzeniu</summary><p>' + e(f['official_name']) + '</p>' + a('Tekst rozporządzenia',source_url) + '</details>'
        destinations = [{'label':'Dane','href':'#dane'},{'label':'Zasady obliczeń','href':'#metoda'},{'label':'Narzędzia i objaśnienia','href':'#narzedzia'}]
        if f['id'] == 24:
            destinations.insert(1, {'label': 'Kruszywo w module A1 betonu', 'href': '#modul-a1'})
        navigation = links(destinations, 'portal-subnav')
        featured = f['id'] in PRODUCT_PHOTOS
        if featured:
            body = family_banner(f, e) + '<nav class="family-banner-links" aria-label="Zawartość karty">' + navigation + '</nav>' + body
        else:
            body += navigation
        body += '<section id="dane" class="portal-section"><h2>Dane dla tej rodziny</h2>' + (''.join(row(r) for r in datasets) if datasets else '<p>W poLCA nie ma obecnie branżowego zestawu danych dla tej rodziny. Poniżej znajdziesz dostępne dokumenty i objaśnienia.</p>') + '</section>'
        inputs = [r for r in catalog['datasets'] if any(x['family_id']==f['id'] and x['role'] in ['input_to_product','process_for_product','parameters_for_product'] for x in r.get('cpr_related',[]))]
        if inputs:
            body += '<section class="portal-section"><h2>Składniki i parametry do obliczeń</h2><p>Dane wejściowe do receptury lub procesu. Nie opisują wyniku dla całego wyrobu.</p>' + links([{'label':r['title'],'href':r['href']} for r in inputs]) + '</section>'
        if f['id']==24:
            body += '<p class="product-intro">Wypełniacz wapienny jest powiązany z rodziną 24 jako kruszywo wypełniające do mieszanki asfaltowej. Inne zastosowanie wymaga odrębnego przypisania.</p>'
            body += '''<section id="modul-a1" class="portal-section portal-prose">
            <h2>Kiedy kruszywo wchodzi do modułu A1 betonu?</h2>
            <p>W ocenie betonu produkcję zakupionego kruszywa do bramy zakładu, który je wytworzył, uwzględnia się w module A1. Transport kruszywa z tego zakładu do betoniarni należy do modułu A2. W deklaracji środowiskowej samego kruszywa procesy przypisuje się do modułów jego własnego cyklu życia. <a href="https://preview.sist.si/sist-preview/70993/968303feeecb4c8dab45d5e529c23d9d/SIST-EN-16757-2023.pdf">EN 16757, pkt 6.2.2</a>.</p>
            <p>Proces rynkowy w bazie ecoinvent może już obejmować dostawę kruszywa. Przed doliczeniem transportu w A2 warto sprawdzić, który odcinek ujęto w danych, aby uwzględnić go tylko raz. <a href="https://support.ecoinvent.org/market-activities">Opis transportu w procesach rynkowych ecoinvent</a>.</p>
            <p><a href="/metodyka-defaults-ue.html#dane-tla-cpr">Jakich danych tła wymaga Komisja Europejska w zamówieniu dotyczącym wyrobów budowlanych?</a></p>
            </section>'''
        body += '<section id="metoda" class="portal-section"><h2>Zasady obliczeń: PCR i c-PCR</h2><p>PCR to zasady kategorii wyrobów, a c-PCR — ich uzupełnienie dla konkretnej grupy produktów. Sprawdź zakres dokumentu i wydanie stosowane w programie deklaracji środowiskowych EPD.</p>' + method_list(rules(f)) + '<p><a href="/c-pcr/#dobor">Jak dobrać metodę i sprawdzić jej status</a></p></section>'
        drafts = [r for r in associated(f, 'method') if r['id'] in ['method-mma','method-kruszywa']]
        if drafts:
            body += '<section class="portal-section"><h2>Dokumenty poLCA dla tej branży</h2>' + links([{'label':r['title'],'href':r['href']} for r in drafts]) + '</section>'
        body += '<section id="narzedzia" class="portal-section"><h2>Narzędzia i objaśnienia</h2>' + (''.join(row(r) for r in tools + articles) if tools or articles else '<p><a href="/zastosowanie-danych.html">Przewodnik doboru danych do wyrobu i budynku</a></p>') + '</section>'
        body += common()
        body += '<p class="product-intro">Przypisanie do rodziny ułatwia znalezienie informacji. Zakres konkretnego wyrobu i zasady oceny wynikają z właściwych dokumentów technicznych.</p>'
        page(family_url(f['id'])[1:],f['label'],'Dane i dokumenty dla rodziny ' + str(f['id']) + ' z załącznika VII CPR.',body,parent=('Rodziny wyrobów','/wyroby.html'),pagehead=not featured,
             attrs='data-product-photo' if featured else '', head_extra=PHOTO_CSS if featured else '')
        if not available(f):
            p=root/family_url(f['id'])[1:]
            p.write_text(p.read_text().replace('</head>','<meta name="robots" content="noindex,follow"></head>'))

    body = '<div class="portal-reading"><section id="wstep" class="portal-prose"><h2>Metoda ogólna i zasady dla wyrobu</h2><p>EN 15804 określa podstawowe zasady deklaracji środowiskowych EPD dla wyrobów budowlanych. Dokument c-PCR uzupełnia je w zakresie określonego rodzaju wyrobu. Jedna rodzina CPR może obejmować kilka różnych dokumentów metodycznych.</p></section><section id="dobor" class="portal-prose"><h2>Jak dobrać metodę</h2><ol><li>Określ wyrób, jego zastosowanie i zakres obliczenia.</li><li>Sprawdź zakres i wydanie dokumentu c-PCR oraz zasady programu EPD.</li><li>Dla oceny wymaganej przez CPR sprawdź właściwą specyfikację techniczną i wymagania mające zastosowanie do wyrobu.</li></ol><p>Wydana norma c-PCR nie jest automatycznie zharmonizowaną specyfikacją techniczną CPR. <a href="/zastosowanie-epd-cpr.html">Więcej o zastosowaniu danych w EPD i CPR</a>.</p></section><section id="cpcr-lista" class="portal-section"><h2>Dokumenty według wyrobu</h2>'
    body += method_list([m for m in methods['documents'] if m['family_ids'] and m['status']=='published' and m['role']=='complementary_pcr'], show_families=True) + '</section><section class="portal-section"><h2>Dokumenty wspólne: zasady i jakość danych</h2>' + method_list([m for m in methods['documents'] if not m['family_ids']]) + '</section><section class="portal-section"><h2>Dokumenty pomocnicze</h2>' + method_list([m for m in methods['documents'] if m['role']=='technical_review'], show_families=True) + '</section><section id="projekty" class="portal-section"><h2>Projekty norm</h2><p>' + e(methods['drafts_intro']) + '</p>' + method_list([m for m in methods['documents'] if m['status']=='draft'], show_families=True) + '</section><section id="powiazania" class="portal-prose"><h2>Dokumenty poLCA</h2><p>Przy dokumentach branżowych podajemy ich wersję i status. Opublikowanie projektu nie potwierdza przyjęcia go jako reguły programu.</p>' + links([{'label':'Mieszanki asfaltowe — metoda i projekt poLCA','href':'/c-pcr/mma.html'},{'label':'Kruszywa — dane i status projektu poLCA','href':'/c-pcr/kruszywa.html'},{'label':'Wybierz rodzinę wyrobu','href':'/wyroby.html'}]) + '</section></div>'
    page('c-pcr/index.html','Zasady obliczeń dla wyrobów','PCR — zasady kategorii wyrobów. c-PCR — zasady uzupełniające dla określonych grup produktów.',body)

    for slug, fid, title, version in [('mma',23,'Mieszanki mineralno-asfaltowe','v1.0-DRAFT'),('kruszywa',24,'Kruszywa','v0.9-DRAFT')]:
        f=next(x for x in families if x['id']==fid)
        body='<div class="portal-reading"><section id="sec-1" class="portal-prose"><h2>Dokumenty metodyczne</h2>' + method_list(rules(f)) + '</section><section id="sec-2" class="portal-prose"><h2>Projekt poLCA — ' + version + '</h2><p>Historyczny projekt reguł programu EPD Polska. Nie jest prezentowany jako zatwierdzone wydanie końcowe. Do nowego opracowania dobierz właściwy dokument branżowy i zasady programu.</p>'
        if slug=='mma':
            body+=links([{'label':'Archiwalny projekt c-PCR MMA — PDF','href':'/c-pcr/c-PCR-MMA-EPD-Polska-2026-v1.0-DRAFT.pdf'},{'label':'Archiwalny raport danych MMA — PDF','href':'/c-pcr/Raport-LCI-MMA-Polska-EN15804A2.pdf'}])
        else: body+='<p>W portalu nie udostępniono pełnego dokumentu projektu c-PCR kruszyw do pobrania.</p>'
        body+='</section>'+''.join(f'<span id="sec-{n}"></span>' for n in range(4,10))+'<section id="sec-3" class="portal-prose"><h2>Dane i obliczenia</h2>' + links([{'label':title+' — dane, narzędzia i dokumenty','href':family_url(fid)}]) + '</section><section class="portal-prose"><h2>Dobór danych</h2><p>Jednostkę, granice systemu, moduły i założenia określ dla konkretnego badania. Samo zestawienie wskaźników materiałowych nie zastępuje metody oceny.</p>' + a('Jak wybrać metodę','/c-pcr/#dobor')+'</section></div>'
        page(f'c-pcr/{slug}.html',title+' — zasady obliczeń i dokumenty','Dokumenty branżowe, status projektu i odnośniki do danych dla wyrobu.',body,parent=('Zasady obliczeń','/c-pcr/'))

    body=common() + '<section class="portal-section"><h2>Wszystkie dane wspólne</h2>' + ''.join(row(r) for r in catalog['datasets'] if r['category_id'] in ['energia','paliwa','transport']) + '</section><section class="portal-section"><h2>Przeliczniki i instrukcje</h2>' + links([{'label':'Kalkulatory energii i transportu','href':'/kalkulatory.html'},{'label':'Dobór danych do zastosowania','href':'/zastosowanie-danych.html'}]) + '</section>'
    page('dane-wspolne.html','Dane wspólne: energia, paliwa i transport','Współczynniki i modele pomocnicze do obliczeń w różnych branżach.',body)
