"""Cement as a constituent of concrete, using the current SPC sector records."""
from html import escape

from aggregate_guide import CONCRETE_STANDARD, ELECTRICITY, TRUCK, concrete_operation, render_case

BASIS_RULE = ('Wartość netto przyjmujemy, gdy deklaracja środowiskowa cementu podaje wynik netto albo potwierdza, '
              'że współspalane paliwa mają status odpadu. W pozostałych przypadkach przyjmujemy wartość brutto. '
              'Porównujemy wyłącznie wyniki obliczone w tym samym wariancie.')


def cement_guide(catalog, section_table):
    records = {r['id']: r for r in catalog['datasets']}
    cements = {kind: records[f'POLCA-CEMENT-CEM-{kind}-SPC-PL-2025'] for kind in ('I', 'II', 'III', 'IV', 'V')}
    cem_i = cements['I']
    details = f'''<details class="aggregate-epd" id="srednia-krajowa-cementu">
      <summary>Co obejmuje średnia krajowa dla cementu?</summary>
      <p>Deklaracja sektorowa Stowarzyszenia Producentów Cementu obejmuje dane cementowni członkowskich za 2022 r. Dla CEM I deklarowana wartość netto wynosi <strong>{cem_i['value']} kg CO₂e/t</strong>. Wartość brutto wynosi {cem_i['gwp_gross_kg_co2e']} kg CO₂e/t i stanowi informację dodatkową.</p>
      <p>W wariancie netto emisje ze spalania kopalnej części paliw o statusie odpadu przypisuje się systemowi, w którym powstał odpad (EN 15804+A2, pkt 6.3.5.1 i załącznik D.3.2). {BASIS_RULE}</p>
      <p><a href="{escape(cem_i['source_url'])}">Deklaracja sektorowa SPC 2025, tabela 2, s. 5</a></p></details>'''
    case = {
        'name': 'cement', 'id': 'cement-w-betonie', 'ingredient': True, 'title': 'Cement jako składnik betonu',
        'image': '/images/cement-beton-fotografia.jpg',
        'alt': 'Cementownia z piecem obrotowym, cementowóz na drodze i betoniarnia z silosami.',
        'point_basis': {'material': 'netto na 1 t cementu', 'distance': 'na 1 t cementu', 'power': 'na 1 m³ betonu'},
        'default_material': cements['II']['id'], 'material_scope': 'Cement', 'material_genitive': 'cementu',
        'material_target': 'cementownia', 'extras': details,
        'material_description': ('Wskaźniki netto są średnimi krajowymi dla poszczególnych rodzajów cementu, obliczonymi na podstawie danych cementowni za 2022 r. '
                                 'W deklaracji betonu należy stosować wskaźnik z deklaracji środowiskowej dostawcy cementu, jeżeli jest dostępna.'),
        'material_note': 'Wskaźnik powinien odpowiadać rodzajowi cementu w recepturze betonu.',
        'transport_target': 'przewoz-cementu', 'transport_destination': 'do betoniarni', 'distance': 100,
        'transport_description': 'Dostawę cementu z cementowni do betoniarni uwzględnia się w module A2 betonu.',
        'operation': concrete_operation(records[ELECTRICITY]),
        'reading_note': ('<strong>Jak odnieść wynik do 1 m³ betonu?</strong> W A1 i A2 pokazano wkład 1 t cementu. '
                         'Każdą z tych wartości należy pomnożyć przez masę cementu w recepturze (t/m³). '
                         'W A3 podano tylko wkład energii elektrycznej na 1 m³ betonu. '
                         f'Podział na moduły według <a href="{CONCRETE_STANDARD}">EN 16757, pkt 6.2.2</a>.'),
    }
    example = render_case(case, [dict(r, title=f'CEM {kind} — netto (SPC 2025)') for kind, r in cements.items()], records[TRUCK])
    table_title = 'Ile wnosi cement do 1 m³ betonu?'
    table = section_table({'title': table_title, 'table': {
        'headers': ['Rodzaj cementu', 'Wskaźnik netto, kg CO₂e/t', 'Wkład netto, kg CO₂e/m³',
                    'Wskaźnik brutto, kg CO₂e/t', 'Wkład brutto, kg CO₂e/m³'],
        'rows': [[f'CEM {kind}', r['value'], f"{r['value'] * 0.3:.1f}".replace('.', ','),
                  r['gwp_gross_kg_co2e'], f"{r['gwp_gross_kg_co2e'] * 0.3:.1f}".replace('.', ',')]
                 for kind, r in cements.items()],
    }}, responsive=True)
    return f'''<section id="modul-a1-cement" class="portal-section aggregate-guide" aria-labelledby="cement-guide-title">
    <h2 id="cement-guide-title">Jaki wpływ na klimat ma cement w betonie?</h2>
    <p class="aggregate-intro">Cement kupowany przez betoniarnię jest składnikiem betonu. Produkcję cementu w cementowni uwzględnia się w module A1 betonu, a przewóz cementu do betoniarni – w module A2. Wskaźniki poLCA dla cementu to średnie krajowe z sektorowej deklaracji środowiskowej Stowarzyszenia Producentów Cementu z 2025 r.</p>
    <p class="aggregate-help">Wybierz punkt, aby zobaczyć współczynnik i obliczenie.</p>
    {example}
    <section aria-labelledby="wklad-cementu"><h3 id="wklad-cementu">{table_title}</h3>
    <p>Przykład dla 300 kg cementu w 1 m³ betonu. Ilość cementu należy przyjąć z receptury.</p>
    {table}
    <p>Mniejszy wynik dla CEM III wynika głównie z mniejszego udziału klinkieru. Według PN-EN 197-1 cement CEM I zawiera 95–100% klinkieru, a CEM III/A 35–64%. <a href="https://www.atlas.com.pl/wp-content/uploads/2017/02/ATLAS-Domieszki-Rodzaje_cementow.pdf">Zestawienie rodzajów cementu według PN-EN 197-1</a></p>
    </section></section>'''
