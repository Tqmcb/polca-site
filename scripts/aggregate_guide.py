"""Interactive product scenarios and the worked examples for aggregates."""
from html import escape

CONCRETE_STANDARD = 'https://preview.sist.si/sist-preview/70993/968303feeecb4c8dab45d5e529c23d9d/SIST-EN-16757-2023.pdf#page=15'
PRODUCT_STANDARD = 'https://sklep.pkn.pl/normy/pn-en-15804-a2-2020-03p.html'
SITKOWKA_EPD = 'https://www.itb.pl/wp-content/uploads/2025/01/ITB-EPD_707_Trzuskawica-S.A.-for-Limestone-aggregates.pdf#page=8'
TRUCK = 'POLCA-TRUCK-40T-DEFAULT-2026'
ELECTRICITY = 'PL2025_PHYSICAL_DELIVERED_v4'
DIESEL = 'POLCA-FUEL-DIESEL-DEFAULT-2026'
GAS = 'POLCA-FUEL-NATURAL-GAS-DEFAULT-2026'
ASPHALT_SPEC = 'https://knowledge.bsigroup.com/products/road-materials-environmental-product-declarations-product-category-rules-complementary-to-en-15804-for-bituminous-mixtures'
DEFAULT_MATERIAL = 'POLCA-AGG-PL-LIMESTONE-DEFAULT-2026'


def number(value, digits=6):
    return f'{value:.{digits}f}'.rstrip('0').rstrip('.').replace('.', ',') or '0'


def display_result(value):
    return f'{value:.2f}'.replace('.', ',')


def sitkowka_example():
    return f'''<details class="aggregate-epd" id="a3-kruszywa-sitkowka">
          <summary>Ile wynosi samo A3 kruszywa? Przykład z Sitkówki</summary>
          <p>W deklaracji środowiskowej kruszywa wapiennego z zakładu Trzuskawica w Sitkówce wpływ na klimat wynosi
          0,79 w A1, 0,010 w A2 i <strong>2,48 kg CO₂e/t w A3</strong>. Dla całego etapu A1–A3 producent deklaruje
          3,27 kg CO₂e/t po zaokrągleniu. Są to dane zakładowe za 2023 r. Wartość poLCA dla wapienia jest wskaźnikiem grupowym.</p>
          <p>W Sitkówce do A3 zaliczono roboty strzałowe, rozbijanie większych brył, załadunek, przewóz w zakładzie oraz kruszenie i przesiewanie.</p>
          <p><a href="{SITKOWKA_EPD}">Deklaracja ITB nr 707/2024, tabela 3, s. 8</a></p></details>'''


def product_example(materials, case):
    default_id = case.get('default_material', DEFAULT_MATERIAL)
    material = case.get('material_genitive', 'kruszywa')
    initial = next(r for r in materials if r['id'] == default_id)
    select = ''.join(
        f'<option value="{escape(r["id"])}" data-factor="{r["value"]}" data-source="{escape(r["href"])}"'
        + (' selected' if r['id'] == default_id else '')
        + f'>{escape(r["title"])}</option>' for r in materials)
    return {
        'key': 'material', 'code': 'A1' if case['ingredient'] else 'A1–A3',
        'title': f'Produkcja {material}', 'caption': f'Wpływ na klimat na tonę {material} u producenta',
        'description': case['material_description'], 'result_unit': 'kg CO₂e/t', 'record': initial,
        'label': f'Rodzaj {material}', 'control': f'<select data-param="material" disabled>{select}</select>',
        'argument': 1, 'activity_unit': 't', 'factor_unit': 'kg CO₂e/t', 'extras': case.get('extras', ''),
        'target': case['material_target'],
    }


def quantity_control(key, value, unit):
    return (f'<span class="aggregate-input"><input type="text" inputmode="decimal" '
            f'data-param="{key}" value="{number(value)}" autocomplete="off" disabled>'
            f'<span>{unit}</span></span>')


def transport_example(record, case):
    distance = case.get('distance', 20)
    material = case.get('material_genitive', 'kruszywa')
    return {
        'key': 'distance', 'code': 'A2' if case['ingredient'] else 'A4',
        'title': 'Przewóz ' + case['transport_destination'], 'caption': f'Wpływ przewozu 1 t {material} na podaną odległość',
        'description': ('Źródło współczynnika dla zestawu 40 t nie określa stopnia załadowania ani udziału pustych przebiegów. ' + case['transport_description']),
        'record': record, 'result_unit': 'kg CO₂e/t', 'factor_unit': 'kg CO₂e/(t·km)',
        'argument': distance, 'activity_unit': 'km', 'label': 'Odległość przewozu w jedną stronę',
        'control': quantity_control('distance', distance, 'km'),
        'target': case['transport_target'],
    }


def scenario(case, stages):
    name = case['name']
    title = case['title']
    case_id = case.get('id', f'kruszywo-{name}')
    image = case.get('image', f'/images/kruszywa-{name}-fotografia.jpg')
    points, panels = [], []
    for index, stage in enumerate(stages, start=1):
        record = stage['record']
        factor, quantity = record['value'], stage['argument']
        value = display_result(quantity * factor)
        point_id = 'punkt-' + stage['target']
        panel_id = 'opis-' + stage['target']
        code = stage['code']
        step_title = stage['title']
        key = stage['key']
        unit = stage['result_unit']
        scope = {'material': case.get('material_scope', 'Kruszywo'), 'distance': 'Przewóz', 'power': 'Prąd', 'fuel': 'Paliwo', 'gas': 'Gaz'}[key]
        accessible_name = f'{code}, {scope}, {step_title}'
        basis = case.get('point_basis', {}).get(key)
        basis_label = ''
        if basis:
            accessible_name += ', ' + basis
            basis_label = f'<span class="aggregate-point-basis">{basis}</span>'
        points.append(f'''<a class="aggregate-point" id="{point_id}" href="#{panel_id}" data-step="{index}"
          aria-label="{accessible_name}, {value} {unit}" data-marker-name="{accessible_name}">
          <span class="aggregate-point-scope">{scope}</span>
          <span class="aggregate-marker">{code}</span><strong class="aggregate-point-value" data-output>{value}</strong>
          <small class="aggregate-point-unit">{unit}</small>{basis_label}</a>''')
        plain_unit = stage['activity_unit']
        factor_unit = stage['factor_unit']
        factor_text = number(factor)
        source = escape(record['href'])
        note = '<small class="aggregate-assumption">Wartość przykładowa. Możesz wpisać własną.</small>' if key != 'material' else ''
        if key == 'material':
            material_note = case.get('material_note', 'Wskaźnik powinien odpowiadać frakcji kruszywa, '
                                     'technologii produkcji i zakresowi procesów ujętych w danych.')
            note = f'<small class="aggregate-assumption">{material_note}</small>'
        elif key == 'gas':
            note = ('<small class="aggregate-assumption">Zużycie przyjęte w '
                    '<a href="/data/mma-client-example.json">przykładowym profilu poLCA dla betonu asfaltowego AC 16 W z 20% granulatu asfaltowego</a>. Możesz wpisać zużycie ze swojej wytwórni.</small>')
        expression = ('1 t' if key == 'material' else f'<span data-quantity>{number(quantity)}</span> {plain_unit}')
        equation_unit = 'kg CO₂e' if key == 'material' else unit
        operator = '=' if key == 'material' else '≈'
        source_label = {'material': 'Karta ' + case.get('material_genitive', 'kruszywa'), 'distance': 'Karta przewozu',
                        'power': 'Energia w Polsce, 2025', 'fuel': 'Karta paliwa', 'gas': 'Karta gazu ziemnego'}[key]
        panels.append(f'''<article id="{panel_id}" class="aggregate-panel" data-step="{index}" data-kind="{key}"
          data-factor="{factor}" data-result-unit="{unit}" tabindex="-1">
          <div class="aggregate-calculation">
          <h4 class="aggregate-panel-heading"><span>{code}</span> {step_title}</h4>
          <p class="aggregate-unit-caption">{stage['caption']}</p>
          <p class="aggregate-result" aria-atomic="true"><strong data-output>{value}</strong> <span>{unit}</span></p>
          <label class="aggregate-control">{stage['label']}{stage['control']}</label>{note}
          <p class="aggregate-error" id="{panel_id}-blad" data-error hidden>Wpisz liczbę równą zeru lub większą.</p>
          <p class="aggregate-source">Współczynnik poLCA <strong><span data-factor-value>{factor_text}</span> {factor_unit}</strong> · <a data-source href="{source}">{source_label}</a></p>
          <p class="aggregate-equation">{expression} × <span data-factor-value>{factor_text}</span> {factor_unit}
          {operator} <span data-output>{value}</span> {equation_unit}</p>
          </div>
          <p class="aggregate-explanation">{stage['description']}</p>{stage.get('extras','')}
          <a class="aggregate-backlink" href="#{point_id}">Punkt {code} na ilustracji</a>
          </article>''')
    return f'''<section class="aggregate-case" id="{case_id}" data-case="{name}" aria-labelledby="tytul-{name}">
      <header class="aggregate-case-heading">
        <h3 class="aggregate-case-title" id="tytul-{name}">{title}</h3>
        <small>Kadry wygenerowane przez sztuczną inteligencję</small>
      </header>
      <div class="aggregate-layout">
        <div class="aggregate-figure"><img src="{image}" width="1600" height="571" loading="lazy"
            decoding="async" alt="{case['alt']}">
          <nav class="aggregate-points" aria-label="Etapy i wyniki modelu dla zastosowania: {title}">{''.join(points)}</nav>
        </div><div class="aggregate-panels">{''.join(panels)}</div>
        <p class="aggregate-note">{case['reading_note']}</p>
      </div></section>'''


def concrete_operation(record):
    return {
        'key': 'power', 'code': 'A3', 'title': 'Produkcja betonu w betoniarni',
        'caption': 'Wkład energii elektrycznej na 1 m³ betonu',
        'description': ('W betoniarni składniki są dozowane i mieszane. Przykład obejmuje '
                        'wyłącznie zużycie energii elektrycznej w zakładzie. Produkcja zakupionych składników należy do A1.'),
        'record': record, 'result_unit': 'kg CO₂e/m³', 'factor_unit': 'kg CO₂e/kWh',
        'argument': 2, 'activity_unit': 'kWh/m³', 'label': 'Zużycie energii elektrycznej przy produkcji betonu',
        'target': 'betoniarnia',
    }


def render_case(case, materials, transport):
    operation = case['operation']
    operation = dict(operation, control=quantity_control(operation['key'], operation['argument'], operation['activity_unit']))
    return scenario(case, [product_example(materials, case), transport_example(transport, case), operation])


def aggregate_guide(catalog, mma_profile):
    records = {r['id']: r for r in catalog['datasets']}
    materials = [r for r in records.values() if r['category_id'] == 'kruszywa']
    gas_quantity = mma_profile['activity_data']['production_a3']['natural_gas_m3_per_mg']
    cases = [
        {
            'name': 'beton', 'choice': 'Beton', 'ingredient': True,
            'title': 'Kruszywo jako składnik betonu',
            'point_basis': {'material': 'na 1 t kruszywa', 'distance': 'na 1 t kruszywa', 'power': 'na 1 m³ betonu'},
            'alt': 'Zakład produkcji kruszywa, wywrotka i betoniarnia z silosami.',
            'material_target': 'kopalnia',
            'material_description': ('Zakupione kruszywo jest składnikiem betonu. Gdy brakuje pełnych danych inwentaryzacyjnych kruszywa, '
                                     'EN 16757 pozwala wykorzystać wynik A1–A3 z deklaracji kruszywa zgodnej z EN 15804+A2 '
                                     'jako wkład do A1 betonu. Tutaj produkcję do bramy oszacowano ze wskaźnika poLCA.'),
            'transport_target': 'transport', 'transport_destination': 'do betoniarni',
            'transport_description': ('W bazie ecoinvent <a href="https://support.ecoinvent.org/market-activities">dane rynkowe</a> '
                                      'mogą już obejmować dostawę. Każdy odcinek przewozu uwzględnia się tylko raz.'),
            'reading_note': ('<strong>Jak odnieść wynik do 1 m³ betonu?</strong> W A1 i A2 pokazano wkład 1 t kruszywa. '
                             'Każdą z tych wartości pomnóż przez masę kruszywa w recepturze (t/m³). '
                             'W A3 podano tylko wkład energii elektrycznej na 1 m³ betonu. '
                             f'Podział na moduły według <a href="{CONCRETE_STANDARD}">EN 16757, pkt 6.2.2</a>.'),
            'operation': concrete_operation(records[ELECTRICITY]),
        },
        {
            'name': 'mma', 'choice': 'Mieszanka mineralno-asfaltowa', 'ingredient': True,
            'title': 'Kruszywo w mieszance mineralno-asfaltowej na gorąco',
            'alt': 'Zakład produkcji kruszywa, wywrotka i wytwórnia mieszanki mineralno-asfaltowej z suszarką.',
            'material_target': 'kruszywo-mma',
            'material_description': ('W module A1 mieszanki uwzględnia się produkcję zakupionego kruszywa. '
                                     'Dla każdej frakcji znaczenie mają jej masa w recepturze i źródło dostawy. '
                                     'Lepiszcze asfaltowe i pozostałe składniki rozlicza się oddzielnie.'),
            'transport_target': 'przewoz-do-wytworni', 'transport_destination': 'do wytwórni mieszanki',
            'transport_description': ('Dostawa kruszywa do wytwórni należy do A2 mieszanki. '
                                      'Przewóz gotowej mieszanki z wytwórni na budowę należy do A4.'),
            'reading_note': ('<strong>Jak odnieść wynik do 1 t mieszanki?</strong> Wyniki A1 i A2 dla tony kruszywa pomnóż '
                             'przez masę danej frakcji w tonach na tonę mieszanki. Dodaj wkłady poszczególnych frakcji. '
                             f'Podział na moduły według <a href="{ASPHALT_SPEC}">CEN/TS 18301:2026, pkt 6.3.5.2–6.3.5.3</a>. '
                             '<a href="/wyroby/23.html">Dane i zasady obliczeń dla mieszanek</a>.'),
            'operation': {
                'key': 'gas', 'code': 'A3', 'title': 'Spalanie gazu w wytwórni mieszanki',
                'caption': 'Wpływ spalania gazu ziemnego na 1 t gotowej mieszanki',
                'description': ('W suszarce kruszywo jest suszone i podgrzewane przed zmieszaniem z lepiszczem. '
                                'Wynik obejmuje wyłącznie spalanie gazu ziemnego w wytwórni. '
                                'Pełne A3 obejmuje także m.in. energię elektryczną do napędu urządzeń.'),
                'record': records[GAS], 'result_unit': 'kg CO₂e/t', 'factor_unit': 'kg CO₂e/m³',
                'argument': gas_quantity, 'activity_unit': 'm³/t', 'label': 'Zużycie gazu na tonę mieszanki',
                'target': 'gaz-wytwornia-mma',
            },
        },
        {
            'name': 'podbudowa', 'choice': 'Podbudowa niezwiązana', 'ingredient': False,
            'title': 'Podbudowa z kruszywa niezwiązanego',
            'alt': 'Zakład produkcji kruszywa, jego przewóz na budowę i walec na warstwie kruszywa.',
            'material_target': 'kruszywo-podbudowa',
            'material_description': ('Kruszywo jest tu gotowym wyrobem. Ten sam wskaźnik do bramy producenta służy '
                                     'do oszacowania jego etapu A1–A3, bez rozbicia na moduły. Dobór kruszywa zależy '
                                     'od uziarnienia i właściwości przewidzianych w projekcie podbudowy.'),
            'extras': sitkowka_example(),
            'transport_target': 'przewoz-na-budowe', 'transport_destination': 'na budowę',
            'transport_description': 'Dostawa gotowego kruszywa od producenta bezpośrednio na budowę należy do A4.',
            'reading_note': f'Podział na moduły według <a href="{PRODUCT_STANDARD}">EN 15804+A2, pkt 6.3.5.2–6.3.5.3</a>.',
            'operation': {
                'key': 'fuel', 'code': 'A5', 'title': 'Rozścielenie i zagęszczenie',
                'caption': 'Wkład oleju napędowego na 1 t wbudowanego kruszywa',
                'description': ('Rozścielacz lub równiarka rozprowadza kruszywo, a walec zagęszcza warstwę. '
                                'Wynik obejmuje tylko olej napędowy maszyn. W pełnym A5 uwzględnia się również ewentualne straty kruszywa podczas wbudowania.'),
                'record': records[DIESEL], 'result_unit': 'kg CO₂e/t', 'factor_unit': 'kg CO₂e/l',
                'argument': .5, 'activity_unit': 'l/t', 'label': 'Łączne zużycie oleju napędowego przez maszyny',
                'target': 'wbudowanie',
            },
        },
    ]
    choices = {True: [], False: []}
    examples = []
    for case in cases:
        examples.append(render_case(case, materials, records[TRUCK]))
        choices[case['ingredient']].append(f'<a class="aggregate-choice" href="#kruszywo-{case["name"]}">{case["choice"]}</a>')
    groups = []
    for ingredient, label_id, label in [
        (True, 'kruszywo-skladnik', 'Kruszywo jako składnik'),
        (False, 'kruszywo-wbudowane', 'Kruszywo wbudowane bezpośrednio'),
    ]:
        groups.append(f'''<div class="aggregate-choice-group" role="group" aria-labelledby="{label_id}">
          <span class="aggregate-group-label" id="{label_id}">{label}</span>
          <div class="aggregate-group-links">{''.join(choices[ingredient])}</div>
        </div>''')
    return f'''<section id="modul-a1" class="portal-section aggregate-guide" aria-labelledby="aggregate-guide-title">
    <h2 id="aggregate-guide-title">Do których modułów należą produkcja i przewóz kruszywa?</h2>
    <p class="aggregate-intro">Gdy wytwórnia kupuje kruszywo jako składnik wyrobu, jego produkcję u dostawcy uwzględnia się w A1 tego wyrobu,
      a przewóz do wytwórni w A2. Gdy gotowe kruszywo trafia bezpośrednio
      na budowę, jego dostawa należy do A4, a wbudowanie do A5.</p>
    <nav class="aggregate-choices" aria-label="Zastosowanie kruszywa">{''.join(groups)}</nav>
    <p class="aggregate-help">Wybierz punkt, aby zobaczyć współczynnik i obliczenie.
      <a href="/c-pcr/kruszywa.html#projekty-cen">Planowany podział zastosowań kruszywa</a>.</p>
    {''.join(examples)}</section>'''
