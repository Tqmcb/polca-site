"""One tonne of reinforced precast concrete, based on ITB-EPD 561/2023."""
from decimal import Decimal
from html import escape

from aggregate_guide import number

FORMEE = 'https://www.itb.pl/wp-content/uploads/2024/02/ITB-EPD_561_Formee-Sp.-z-o.o.-Prefabricated-concrete-products.pdf'
DBB = 'https://www.itb.pl/wp-content/uploads/2024/08/ITB-EPD_646_DBB-Biale-Blota-Sp.-z-o.o.-Sp.-k.-Prefabricated-prestressed-HC-type-ceiling-slabs.pdf#page=7'
POZ_BRUK = 'https://www.itb.pl/wp-content/uploads/2023/08/ITB-EPD_491_POZ-BRUK-Sp.-z-o.o.-Sp.j.-Prestressed-hollow-core-panels-Sobota-Plant.pdf#page=9'
CEMENT = 'POLCA-CEMENT-CEM-I-SPC-PL-2025'
# Mass percentages as reported on page 3. Do not normalize them.
MATERIALS = (
    ('Cement CEM I (netto)', '15', CEMENT),
    ('Kruszywa (przyjęto kruszywo naturalne)', '73', 'POLCA-AGG-PL-NATURAL-DEFAULT-2026'),
    ('Wypełniacze (przyjęto mączkę wapienną)', '4', 'POLCA-FILLER-LIMESTONE-DEFAULT-2026'),
    ('Stal zbrojeniowa', '3', 'POLCA-STEEL-REBAR-PL-MEDIAN-2026'),
    ('Woda', '8', None),
    ('Domieszki chemiczne', '0.1', None),
)


def fixed(value, places):
    return f'{value:.{places}f}'.replace('.', ',')


def precast_guide(catalog, section_table):
    records = {r['id']: r for r in catalog['datasets']}
    contributions = {}
    rows = []
    for label, percent, code in MATERIALS:
        mass = Decimal(percent) / 100
        if code:
            record = records[code]
            factor = Decimal(str(record['value']))
            contributions[code] = mass * factor
            factor_cell = f'<a href="{escape(record["href"])}">{number(factor)}</a>'
            result = fixed(contributions[code], 1)
        else:
            factor_cell = '—'
            result = 'pominięto' if label == 'Woda' else 'brak wskaźnika'
        rows.append(f'<tr><th scope="row">{label}</th><td>{percent.replace(".", ",")}%</td>'
                    f'<td>{fixed(mass, 3)}</td><td>{factor_cell}</td><td>{result}</td></tr>')
    total = sum(contributions.values())
    cement = contributions[CEMENT]
    headers = ('Składnik', 'Udział w deklaracji', 'Masa, t', 'Wskaźnik poLCA, kg CO₂e/t', 'Wkład, kg CO₂e')
    epd_title = 'Wynik według deklaracji'
    # Published, independently rounded values from page 7, including the A1–A3 total.
    declared = section_table({'title': epd_title, 'table': {
        'headers': ['Moduł', 'Wpływ na klimat, kg CO₂e/t'],
        'rows': [('A1', '171'), ('A2', '25,0'), ('A3', '42,5'), ('A1–A3', '239')],
    }}, responsive=True)
    return f'''<section class="portal-section" aria-labelledby="przyklad-prefabrykat">
    <h2 id="przyklad-prefabrykat">Jak powstaje wynik A1–A3 dla prefabrykatu żelbetowego?</h2>
    <p>Przykład dotyczy 1 t prefabrykowanych elementów żelbetowych: ścian, płyt stropowych typu filigran, schodów, słupów i belek. Skład i wyniki pochodzą z deklaracji środowiskowej ITB nr 561/2023. Wkład składników w module A1 oszacowano ze wskaźników poLCA.</p>
    <h3 id="sklad-prefabrykatu">Skład 1 t elementu i wkład składników w module A1</h3>
    <div class="portal-table-wrap" role="region" aria-labelledby="sklad-prefabrykatu" tabindex="0">
    <table aria-labelledby="sklad-prefabrykatu"><thead><tr>{''.join(f'<th scope="col">{h}</th>' for h in headers)}</tr></thead>
    <tbody>{''.join(rows)}</tbody><tfoot><tr><th scope="row" colspan="4">Szacunek A1 z cementem netto</th><td>{fixed(total, 1)}</td></tr></tfoot></table></div>
    <p>Udziały podane w deklaracji sumują się do 103,1%. Masy w tabeli odpowiadają udziałom z deklaracji. Deklaracja nie podaje rodzaju kruszywa ani wypełniacza, dlatego przyjęto wskaźniki oznaczone w tabeli.</p>
    <h3>{epd_title}</h3>{declared}
    <p>Szacunek A1 z cementem w wariancie netto wynosi {fixed(total, 1)} kg CO₂e/t. Wyniki podane przez producenta przedstawiono w osobnej tabeli. Deklaracja nie podaje wskaźników przyjętych dla poszczególnych składników.</p>
    <p>Na cement przypada {fixed(cement, 1)} kg CO₂e/t, czyli {fixed(100 * cement / total, 1)}% szacunku netto.</p>
    <p>Dla porównania płyty kanałowe w deklaracjach ITB nr <a href="{DBB}">646/2024</a> i <a href="{POZ_BRUK}">491/2023</a> mają wynik A1–A3 odpowiednio 166 i 201 kg CO₂e/t. Deklaracje nie określają wariantu cementu.</p>
    <p>W deklaracji własnego wyrobu należy przyjąć recepturę zakładu oraz wskaźniki z deklaracji dostawców cementu i stali. Wkład energii elektrycznej zużytej w zakładzie można obliczyć z danych o zużyciu i odpowiednio dobranego profilu. Zakres krajowego miksu fizycznego podano na <a href="/energia-polska-2025-v5.html#zastosowanie">karcie energii Polska 2025 v5</a>.</p>
    <p><a href="{FORMEE}#page=7">Deklaracja ITB nr 561/2023, skład s. 3, wyniki s. 7</a>. Formee Sp. z o.o., EN 15804+A2, ważna do 01.12.2028. W deklaracji podano cement CEM I 42,5R i średnią gęstość wyrobów 2330 kg/m³.</p></section>'''
