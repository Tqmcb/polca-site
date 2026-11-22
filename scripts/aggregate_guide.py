"""Interactive worked examples for the product family page for aggregates."""
from html import escape

CONCRETE_STANDARD = 'https://preview.sist.si/sist-preview/70993/968303feeecb4c8dab45d5e529c23d9d/SIST-EN-16757-2023.pdf#page=15'
PRODUCT_STANDARD = 'https://sklep.pkn.pl/normy/pn-en-15804-a2-2020-03p.html'
SITKOWKA_EPD = 'https://www.itb.pl/wp-content/uploads/2025/01/ITB-EPD_707_Trzuskawica-S.A.-for-Limestone-aggregates.pdf#page=8'
TRUCK = 'POLCA-TRUCK-40T-DEFAULT-2026'
ELECTRICITY = 'PL2025_PHYSICAL_DELIVERED_v4'
DIESEL = 'POLCA-FUEL-DIESEL-DEFAULT-2026'
DEFAULT_MATERIAL = 'POLCA-AGG-PL-LIMESTONE-DEFAULT-2026'


def number(value, digits=6):
    return f'{value:.{digits}f}'.rstrip('0').rstrip('.').replace('.', ',') or '0'


def display_result(value):
    return f'{value:.2f}'.replace('.', ',')


def product_example(concrete, materials):
    initial = next(r for r in materials if r['id'] == DEFAULT_MATERIAL)
    select = ''.join(
        f'<option value="{escape(r["id"])}" data-factor="{r["value"]}" data-source="{escape(r["href"])}"'
        + (' selected' if r['id'] == DEFAULT_MATERIAL else '')
        + f'>{escape(r["title"])}</option>' for r in materials)
    details = ''
    if concrete:
        explanation = ('W ocenie betonu zakupione kruszywo jest składnikiem. Do A1 betonu wchodzi '
                       'jego produkcja do bramy producenta.')
    else:
        explanation = ('To wartość modelowa do bramy zakładu. Przy kruszywie łamanym własne A3 obejmuje '
                       'm.in. kruszenie i przesiewanie. Rekord poLCA nie podaje osobnej wartości A3. '
                       'Dobór kruszywa zależy od uziarnienia i właściwości przewidzianych w projekcie podbudowy.')
        details = f'''<details class="aggregate-epd" id="a3-kruszywa-sitkowka">
          <summary>Ile wynosi samo A3 kruszywa? Przykład z Sitkówki</summary>
          <p>W deklaracji środowiskowej kruszywa wapiennego z zakładu Trzuskawica w Sitkówce wpływ na klimat wynosi
          0,79 w A1, 0,010 w A2 i <strong>2,48 kg CO₂e/t w A3</strong>. Dla całego etapu A1–A3 producent deklaruje
          3,27 kg CO₂e/t. W deklaracji wartości podano po zaokrągleniu. Dane dotyczą tego zakładu i stanowią odrębny przykład.</p>
          <p><a href="{SITKOWKA_EPD}">Deklaracja ITB nr 707/2024, tabela 3, s. 8</a></p></details>'''
    return {
        'key': 'material', 'code': 'A1' if concrete else 'A1–A3',
        'title': 'Produkcja kruszywa', 'caption': 'Wpływ na klimat na tonę kruszywa u producenta',
        'description': explanation, 'result_unit': 'kg CO₂e/t', 'record': initial,
        'label': 'Rodzaj kruszywa', 'control': f'<select data-param="material" disabled>{select}</select>',
        'argument': 1, 'activity_unit': 't', 'factor_unit': 'kg CO₂e/t', 'extras': details,
        'ids': ('punkt-kopalnia', 'opis-kopalnia') if concrete else ('punkt-kruszywo-podbudowa', 'opis-kruszywo-podbudowa'),
    }


def quantity_control(key, value, unit):
    return (f'<span class="aggregate-input"><input type="text" inputmode="decimal" '
            f'data-param="{key}" value="{number(value)}" autocomplete="off" disabled>'
            f'<span>{unit}</span></span>')


def transport_example(concrete, record):
    place = 'do betoniarni' if concrete else 'na budowę'
    return {
        'key': 'distance', 'code': 'A2' if concrete else 'A4',
        'title': 'Przewóz ' + place, 'caption': 'Wpływ przewozu jednej tony kruszywa',
        'description': ('Samochód dostarcza składnik do produkcji betonu. W bazie ecoinvent '
                        '<a href="https://support.ecoinvent.org/market-activities">dane rynkowe</a> mogą już obejmować '
                        'transport. Dany odcinek należy uwzględnić raz.' if concrete else
                        'Samochód dostarcza gotowe kruszywo od producenta prosto na plac budowy, '
                        'gdzie powstanie podbudowa. Dlatego ten przewóz należy do A4.'),
        'record': record, 'result_unit': 'kg CO₂e/t', 'factor_unit': 'kg CO₂e/(t·km)',
        'argument': 20, 'activity_unit': 'km', 'label': 'Odległość przewozu',
        'control': quantity_control('distance', 20, 'km'),
        'ids': ('punkt-transport', 'opis-transport') if concrete else ('punkt-przewoz-na-budowe', 'opis-przewoz-na-budowe'),
    }


def final_example(concrete, record):
    if concrete:
        return {
            'key': 'power', 'code': 'A3', 'title': 'Produkcja betonu w betoniarni',
            'caption': 'Wkład energii elektrycznej na 1 m³ betonu',
            'description': ('W betoniarni składniki są dozowane i mieszane. Przykład obejmuje '
                            'wyłącznie zużycie energii elektrycznej w zakładzie. Produkcja zakupionych składników należy do A1.'),
            'record': record, 'result_unit': 'kg CO₂e/m³', 'factor_unit': 'kg CO₂e/kWh',
            'argument': 2, 'activity_unit': 'kWh/m³', 'label': 'Zużycie prądu przy produkcji betonu',
            'control': quantity_control('power', 2, 'kWh/m³'),
            'ids': ('punkt-betoniarnia', 'opis-betoniarnia'),
        }
    return {
        'key': 'fuel', 'code': 'A5', 'title': 'Rozścielenie i zagęszczenie',
        'caption': 'Wkład oleju napędowego na 1 t wbudowanego kruszywa',
        'description': ('Rozścielacz lub równiarka rozprowadza kruszywo, a walec zagęszcza warstwę. '
                        'Przykład obejmuje olej napędowy zużyty przez te maszyny przy wbudowaniu.'),
        'record': record, 'result_unit': 'kg CO₂e/t', 'factor_unit': 'kg CO₂e/l',
        'argument': .5, 'activity_unit': 'l/t', 'label': 'Łączne zużycie oleju napędowego przez maszyny',
        'control': quantity_control('fuel', .5, 'l/t'),
        'ids': ('punkt-wbudowanie', 'opis-wbudowanie'),
    }


def scenario(name, image, alt, title, stages):
    points, panels = [], []
    for index, stage in enumerate(stages, start=1):
        record = stage['record']
        factor, quantity = record['value'], stage['argument']
        value = display_result(quantity * factor)
        point_id, panel_id = stage['ids']
        code = stage['code']
        step_title = stage['title']
        key = stage['key']
        unit = stage['result_unit']
        points.append(f'''<a class="aggregate-point" id="{point_id}" href="#{panel_id}" data-step="{index}"
          aria-label="{code}, {step_title}, {value} {unit}" data-marker-name="{code}, {step_title}">
          <span class="aggregate-marker">{code}</span><strong class="aggregate-point-value" data-output>{value}</strong>
          <small class="aggregate-point-unit">{unit}</small></a>''')
        plain_unit = stage['activity_unit']
        factor_unit = stage['factor_unit']
        factor_text = number(factor)
        source = escape(record['href'])
        note = '<small class="aggregate-assumption">Wartość przykładowa. Możesz wpisać własną.</small>' if key != 'material' else ''
        expression = ('1 t' if key == 'material' else f'<span data-quantity>{number(quantity)}</span> {plain_unit}')
        if key == 'material':
            equation_unit = 'kg CO₂e za 1 t'
        else:
            equation_unit = unit
        source_label = {'material': 'Karta kruszywa', 'distance': 'Karta przewozu',
                        'power': 'Energia w Polsce, 2025', 'fuel': 'Karta paliwa'}[key]
        panels.append(f'''<article id="{panel_id}" class="aggregate-panel" data-step="{index}" data-kind="{key}"
          data-factor="{factor}" data-result-unit="{unit}" tabindex="-1">
          <h4 class="aggregate-panel-heading"><span>{code}</span> {step_title}</h4>
          <p class="aggregate-unit-caption">{stage['caption']}</p>
          <p class="aggregate-result" aria-atomic="true"><strong data-output>{value}</strong> <span>{unit}</span></p>
          <label class="aggregate-control">{stage['label']}{stage['control']}</label>{note}
          <p class="aggregate-error" id="{panel_id}-blad" data-error hidden>Wpisz liczbę równą zeru lub większą.</p>
          <p class="aggregate-source">Współczynnik poLCA <strong><span data-factor-value>{factor_text}</span> {factor_unit}</strong> · <a data-source href="{source}">{source_label}</a></p>
          <p class="aggregate-equation">{expression} × <span data-factor-value>{factor_text}</span> {factor_unit}
          ≈ <span data-output>{value}</span> {equation_unit}</p>
          <p>{stage['description']}</p>{stage.get('extras','')}
          <a class="aggregate-backlink" href="#{point_id}">Punkt {code} na ilustracji</a>
          </article>''')
    boundary = (f'<a href="{CONCRETE_STANDARD}">EN 16757, pkt 6.2.2</a>'
                if name == 'beton' else f'<a href="{PRODUCT_STANDARD}">EN 15804+A2, pkt 6.3.5.2–6.3.5.3</a>')
    return f'''<section class="aggregate-case" id="kruszywo-{name}" data-case="{name}" aria-labelledby="tytul-{name}">
      <h3 class="aggregate-case-title" id="tytul-{name}">{title}</h3>
      <div class="aggregate-layout">
        <div class="aggregate-figure"><img src="/images/{image}.jpg" width="1600" height="571" loading="lazy"
            decoding="async" alt="{alt}">
          <nav class="aggregate-points" aria-label="Etapy i wyniki modelu dla zastosowania: {title}">{''.join(points)}</nav>
        </div><div class="aggregate-panels">{''.join(panels)}</div>
        <p class="aggregate-note">Podział na moduły według {boundary}. Wyniki dotyczą jednostek podanych przy poszczególnych punktach.</p>
      </div></section>'''


def aggregate_guide(catalog):
    records = {r['id']: r for r in catalog['datasets']}
    materials = [r for r in records.values() if r['category_id'] == 'kruszywa']
    concrete = scenario('beton', 'kruszywa-droga-do-betoniarni',
                        'Producent kruszywa, wywrotka na drodze i wytwórnia betonu.',
                        'Kruszywo jako składnik betonu',
                        [product_example(True, materials), transport_example(True, records[TRUCK]), final_example(True, records[ELECTRICITY])])
    road = scenario('podbudowa', 'kruszywa-podbudowa-drogi',
                    'Producent kruszywa, przewóz na budowę oraz układanie i zagęszczanie warstwy drogowej.',
                    'Podbudowa z kruszywa niezwiązanego',
                    [product_example(False, materials), transport_example(False, records[TRUCK]), final_example(False, records[DIESEL])])
    return f'''<section id="modul-a1" class="portal-section aggregate-guide" aria-labelledby="aggregate-guide-title">
    <h2 id="aggregate-guide-title">Jak ująć kruszywo w obliczeniach dla betonu i podbudowy?</h2>
    <p class="aggregate-intro">W betonie kruszywo jest składnikiem. Dlatego przewóz do betoniarni należy do A2.
      Przy dostawie gotowego kruszywa na plac budowy ten sam przewóz należy do A4.</p>
    <nav class="aggregate-choices" aria-label="Zastosowanie kruszywa">
      <a class="aggregate-choice" href="#kruszywo-beton">Do betonu</a>
      <a class="aggregate-choice" href="#kruszywo-podbudowa">Na podbudowę</a>
    </nav>
    <p class="aggregate-help">Wybierz punkt na ilustracji, aby zobaczyć współczynnik i obliczenie.</p>
    {concrete}{road}</section>'''
