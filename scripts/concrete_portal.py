"""Reference values for ready-mix concrete and build-time calculator inputs."""
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal
from html import escape
from statistics import mean, median

from aggregate_guide import ELECTRICITY, TRUCK
from cement_guide import BASIS_RULE


def worked_example(catalog):
    records = {r['id']: r for r in catalog['datasets']}
    cements = {k: records[f'POLCA-CEMENT-CEM-{k}-SPC-PL-2025'] for k in ('I', 'II', 'III')}
    cement, aggregate = Decimal('0.330'), Decimal('1.850')
    portions = [
        ('A1', 'Cement CEM II (SPC 2025, netto)', cement, '0,330 t', cements['II']),
        ('A1', 'Kruszywo naturalne', aggregate, '1,850 t', records['POLCA-AGG-PL-NATURAL-DEFAULT-2026']),
        ('A2', 'Przewóz cementu, 100 km', cement * 100, '0,330 t × 100 km', records[TRUCK]),
        ('A2', 'Przewóz kruszywa, 30 km', aggregate * 30, '1,850 t × 30 km', records[TRUCK]),
        ('A3', 'Energia elektryczna w wytwórni', 4, '4 kWh', records[ELECTRICITY]),
    ]
    emissions = [quantity * Decimal(str(record['value'])) for _, _, quantity, _, record in portions]
    total = sum(emissions)
    gross = sum(emissions[1:]) + cement * cements['II']['gwp_gross_kg_co2e']

    def pl(value, digits):
        return f'{value:.{digits}f}'.replace('.', ',')

    rows = []
    for (stage, label, _, activity, record), emission in zip(portions, emissions):
        factor = pl(record['value'], 4) if record['id'] == ELECTRICITY else str(record['value']).replace('.', ',')
        unit = 'kg CO₂e/(t·km)' if record['id'] == TRUCK else record['unit']
        rows.append(f'<tr><td>{stage}</td><td><a href="{escape(record["href"])}">{label}</a></td>'
                    f'<td>{activity} × {factor} {escape(unit)}</td><td class="mono">{pl(emission, 2)}</td>'
                    f'<td class="mono">{pl(100 * emission / total, 1)}%</td></tr>')
    increase = cement * (cements['I']['value'] - cements['II']['value'])
    decrease = cement * (cements['II']['value'] - cements['III']['value'])
    return f'''<div class="table-wrap fade-in" style="overflow-x:auto;"><table class="polca-table">
<thead><tr><th>Moduł</th><th>Pozycja</th><th>Obliczenie</th><th>kg CO₂e/m³</th><th>Udział</th></tr></thead>
<tbody>{''.join(rows)}<tr><td colspan="3"><strong>Suma uwzględnionych pozycji A1–A3, wariant netto</strong></td><td class="mono"><strong>{pl(total, 2)}</strong></td><td class="mono">100%</td></tr></tbody></table></div>
<div class="prose fade-in">
<p>W wariancie brutto wskaźnik CEM II wynosi {cements['II']['gwp_gross_kg_co2e']} kg CO₂e/t. Dla tej samej receptury wynik A1–A3 brutto wynosi <strong data-example-gross>{pl(gross, 2)}</strong> kg CO₂e/m³.</p>
<p><a href="/kalkulator-betonu.html">Kalkulator betonu towarowego</a> otwiera się z danymi tego przykładu w wariancie netto. Można w nim zmienić wariant cementu, recepturę, odległości dostaw oraz zużycie energii i paliw.</p>
<p>Cement wnosi {pl(emissions[0], 2)} kg CO₂e/m³, czyli {pl(100 * emissions[0] / total, 1)}% wyniku netto. Przewóz i energia elektryczna w wytwórni odpowiadają razem za {pl(100 * sum(emissions[2:]) / total, 1)}% wyniku.</p>
<p>Przy tej samej masie cementu wynik netto z CEM I ({cements['I']['value']} kg CO₂e/t) byłby wyższy o {pl(increase, 2)} kg CO₂e/m³, a z CEM III ({cements['III']['value']} kg CO₂e/t) niższy o {pl(decrease, 2)} kg CO₂e/m³. Wskaźniki cementu podaje <a href="{escape(cements['II']['source_url'])}">deklaracja sektorowa SPC 2025</a>.</p></div>'''


def concrete_references(root, catalog):
    evidence = json.loads((root / 'data/concrete-epds.json').read_text())
    means_by_class = defaultdict(list)
    rows_by_class = defaultdict(list)
    basis_notes = defaultdict(list)
    for declaration in evidence['declarations']:
        if declaration['cement_basis'] == 'netto':
            continue
        if declaration['cement_basis'] != 'brutto':
            raise ValueError(f"Nieznany wariant cementu w {declaration['name']}")
        values = defaultdict(list)
        for row in declaration['rows']:
            values[row['strength_class']].append(row['value'])
        for strength, results in values.items():
            means_by_class[strength].append(mean(results))
            rows_by_class[strength].extend(results)
            if declaration.get('basis_note'):
                basis_notes[strength].append(declaration['basis_note'])

    records = {r['id']: r for r in catalog['datasets']}
    references = {}
    for strength in sorted(means_by_class, key=lambda s: int(s[1:].split('/')[0])):
        means = means_by_class[strength]
        rows = rows_by_class[strength]
        ref = dict(cement_basis='brutto', n=len(means), min=min(means), max=max(means), median=None,
                   row_min=min(rows), row_max=max(rows))
        if basis_notes[strength]:
            ref['basis_note'] = ' '.join(basis_notes[strength])
        if len(means) >= 3:
            record = records[f"POLCA-CONCRETE-{strength.replace('/', '-')}-EPD-PL-2026"]
            if record['value'] != median(means):
                raise ValueError(f'Mediana w katalogu nie odpowiada deklaracjom dla {strength}')
            ref.update(median=record['value'], record_id=record['id'])
        references[strength] = ref
    return evidence, references


def concrete_guide(evidence, references, section_table, num):
    rows = []
    for strength, ref in references.items():
        rows.append([strength, ref['n'], num(ref['min']),
                     '—' if ref['median'] is None else num(ref['median'], '.1f'), num(ref['max']),
                     f"{num(ref['row_min'])}–{num(ref['row_max'])}"])
    table = section_table({
        'title': 'Wyniki brutto A1–A3 dla klas wytrzymałości betonu w kg CO₂e/m³',
        'table': {'headers': ['Klasa', 'Liczba deklaracji', 'Minimum brutto', 'Mediana brutto', 'Maksimum brutto',
                              'Zakres pojedynczych wyników'], 'rows': rows}
    })
    net_rows = []
    sources = []
    for doc in evidence['declarations']:
        pages = sorted({r['page'] for r in doc['rows']})
        links = ', '.join(f'<a href="{escape(doc["url"])}#page={p}">s. {p}</a>' for p in pages)
        valid = date.fromisoformat(doc['source_valid_until']).strftime('%d.%m.%Y')
        sources.append(f'<li><strong>{escape(doc["name"])}</strong>, {escape(doc["manufacturer"])} '
                       f'({escape(doc["product"])}), wariant {doc["cement_basis"]}, ważna do {valid} ({links}). {escape(doc["note"])}</li>')
        if doc['cement_basis'] == 'netto':
            for row in doc['rows']:
                net_rows.append([row['strength_class'], doc['manufacturer'], doc['name'], 1, num(row['value'])])
    net_title = 'Deklaracje w wariancie netto'
    net_table = section_table({'title': net_title, 'table': {
        'headers': ['Klasa', 'Producent', 'Deklaracja', 'Liczba deklaracji', 'A1–A3 netto, kg CO₂e/m³'],
        'rows': net_rows}})
    excluded = []
    for group in evidence['excluded']:
        links = ', '.join(f'<a href="{escape(doc["url"])}">{escape(doc["label"])}</a>'
                          for doc in group['sources'])
        note = ' ' + escape(group['note']) if group.get('note') else ''
        excluded.append(f'<li>{escape(group["owner"])} ({links}). {escape(group["reason"])}{note}</li>')
    as_of = date.fromisoformat(evidence['as_of']).strftime('%d.%m.%Y')
    return f'''<section id="beton-towarowy" class="family-record-section">
<h2>Ile wynosi ślad węglowy betonu towarowego w polskich deklaracjach?</h2>
<p>Zestawienie obejmuje całkowity potencjał globalnego ocieplenia (GWP-total) dla 1 m³ betonu
od pozyskania surowców do opuszczenia wytwórni (A1–A3). Uwzględniono deklaracje środowiskowe wyrobu
(EPD) według {escape(evidence['standard'])} ważne w dniu {as_of}.</p>
<p>W zestawieniu brutto każda deklaracja ma jednakową wagę w obrębie klasy. Jeżeli deklaracja obejmuje kilka receptur lub wytwórni,
przyjęto średnią arytmetyczną ich wyników. Minimum i maksimum odnoszą się do tak obliczonych wartości.
Medianę podano dla klas z co najmniej trzema deklaracjami. W ostatniej kolumnie podano zakres pojedynczych wyników przed uśrednieniem.
Wszystkie wartości podano w kg CO₂e/m³.</p>
{table}
{''.join('<p>' + escape(doc['basis_note']) + '</p>' for doc in evidence['declarations'] if doc.get('basis_note'))}
<p>{escape(evidence['transport_note'])}</p>
<h3>{net_title}</h3>
<p>W każdej z poniższych klas wynik netto pochodzi z jednej deklaracji. Dla tych klas podajemy zadeklarowaną wartość bez obliczania mediany.</p>
{net_table}
<h3>Z których deklaracji pochodzą wyniki?</h3><ul>{''.join(sources)}</ul>
<h3>Które deklaracje pominięto i dlaczego?</h3><ul>{''.join(excluded)}</ul>
<p>Beton towarowy przypisaliśmy do rodziny 26 w celu wyszukiwania danych w katalogu.</p>
<p><a href="/kalkulator-betonu.html">Kalkulator A1–A3 dla receptury betonu towarowego</a></p></section>'''


def build_calculator(root, catalog, references, page):
    records = {r['id']: r for r in catalog['datasets']}
    cements = {f'CEM {kind}': f'POLCA-CEMENT-CEM-{kind}-SPC-PL-2025'
               for kind in ('I', 'II', 'III', 'IV', 'V')}
    aggregates = {label: f'POLCA-AGG-PL-{key}-DEFAULT-2026' for label, key in [
        ('Naturalne (piasek i żwir)', 'NATURAL'), ('Łamane twarde', 'CRUSHED'),
        ('Wapienne', 'LIMESTONE'), ('Dolomitowe', 'DOLOMITE')]}
    processes = dict(truck='POLCA-TRUCK-40T-DEFAULT-2026', electricity='PL2025_PHYSICAL_DELIVERED_v5',
                     gas='POLCA-FUEL-NATURAL-GAS-DEFAULT-2026', diesel='POLCA-FUEL-DIESEL-DEFAULT-2026')
    factors = {code: {k: records[code][k] for k in ('title', 'value', 'unit', 'href')}
               for code in [*cements.values(), *aggregates.values(), *processes.values()]}
    for code in cements.values():
        factors[code]['gwp_gross_kg_co2e'] = records[code]['gwp_gross_kg_co2e']
    config = dict(catalog_version=catalog['catalog_version'], factors=factors, processes=processes,
                  cements=list(cements.values()), aggregates=list(aggregates.values()), references=references,
                  supplier_epds=json.loads((root / 'data/supplier-cement-epds.json').read_text()))

    def options(choices, default):
        return ''.join(f'<option value="{escape(code)}"{" selected" if code == default else ""}>'
                       f'{escape(label)}</option>' for label, code in choices.items())

    body = (root / 'content/concrete-calculator.tmpl').read_text().format(
        cements=options(cements, cements['CEM II']),
        supplier_groups=options(cements, None),
        aggregates=options(aggregates, aggregates['Naturalne (piasek i żwir)']),
        classes=options({c: c for c in references}, 'C30/37'),
        basis_rule=escape(BASIS_RULE),
        config=json.dumps(config, ensure_ascii=False, allow_nan=False).replace('<', r'\u003c'))
    page('kalkulator-betonu.html', 'Ile wynosi ślad węglowy 1 m³ betonu towarowego?',
         'Kalkulator A1–A3 uwzględnia produkcję cementu i kruszywa, ich dostawę do wytwórni '
         'oraz zużycie energii i paliw w wytwórni.',
         body, parent=('Kalkulatory', '/kalkulatory.html'),
         head_extra='<link rel="stylesheet" href="/assets/concrete-calculator.css?v=3">'
                    '<script src="/js/kalkulator-betonu.js?v=4" defer></script>')
