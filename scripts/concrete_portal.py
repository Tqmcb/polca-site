"""Reference values for ready-mix concrete and build-time calculator inputs."""
import json
from collections import defaultdict
from datetime import date
from html import escape
from statistics import mean, median


def concrete_references(root, catalog):
    evidence = json.loads((root / 'data/concrete-epds.json').read_text())
    means_by_class = defaultdict(list)
    rows_by_class = defaultdict(list)
    for declaration in evidence['declarations']:
        values = defaultdict(list)
        for row in declaration['rows']:
            values[row['strength_class']].append(row['value'])
        for strength, results in values.items():
            means_by_class[strength].append(mean(results))
            rows_by_class[strength].extend(results)

    records = {r['id']: r for r in catalog['datasets']}
    references = {}
    for strength in sorted(means_by_class, key=lambda s: int(s[1:].split('/')[0])):
        means = means_by_class[strength]
        rows = rows_by_class[strength]
        ref = dict(n=len(means), min=min(means), max=max(means), median=None,
                   row_min=min(rows), row_max=max(rows))
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
        'title': 'Wyniki A1–A3 dla klas wytrzymałości betonu w kg CO₂e/m³',
        'table': {'headers': ['Klasa', 'Liczba deklaracji', 'Minimum', 'Mediana', 'Maksimum',
                              'Zakres pojedynczych wyników'], 'rows': rows}
    })
    sources = []
    for doc in evidence['declarations']:
        pages = sorted({r['page'] for r in doc['rows']})
        links = ', '.join(f'<a href="{escape(doc["url"])}#page={p}">s. {p}</a>' for p in pages)
        valid = date.fromisoformat(doc['source_valid_until']).strftime('%d.%m.%Y')
        sources.append(f'<li><strong>{escape(doc["name"])}</strong>, {escape(doc["manufacturer"])} '
                       f'({escape(doc["product"])}), ważna do {valid} ({links}). {escape(doc["note"])}</li>')
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
<p>Każda deklaracja ma jednakową wagę w obrębie klasy. Jeżeli obejmuje kilka receptur lub wytwórni,
przyjęto średnią arytmetyczną ich wyników. Minimum i maksimum odnoszą się do tak obliczonych wartości.
Medianę podano dla klas z co najmniej trzema deklaracjami. W ostatniej kolumnie podano zakres pojedynczych wyników przed uśrednieniem.
Wszystkie wartości podano w kg CO₂e/m³.</p>
{table}
<p>{escape(evidence['transport_note'])}</p>
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
    config = dict(catalog_version=catalog['catalog_version'], factors=factors, processes=processes,
                  cements=list(cements.values()), aggregates=list(aggregates.values()), references=references)

    def options(choices, default):
        return ''.join(f'<option value="{escape(code)}"{" selected" if code == default else ""}>'
                       f'{escape(label)}</option>' for label, code in choices.items())

    body = (root / 'content/concrete-calculator.tmpl').read_text().format(
        cements=options(cements, cements['CEM II']),
        aggregates=options(aggregates, aggregates['Naturalne (piasek i żwir)']),
        classes=options({c: c for c in references}, 'C30/37'),
        config=json.dumps(config, ensure_ascii=False, allow_nan=False).replace('<', r'\u003c'))
    page('kalkulator-betonu.html', 'Ile wynosi ślad węglowy 1 m³ betonu towarowego?',
         'Kalkulator A1–A3 uwzględnia produkcję cementu i kruszywa, ich dostawę do wytwórni '
         'oraz zużycie energii i paliw w wytwórni.',
         body, parent=('Kalkulatory', '/kalkulatory.html'),
         head_extra='<link rel="stylesheet" href="/assets/concrete-calculator.css?v=1">'
                    '<script src="/js/kalkulator-betonu.js?v=1" defer></script>')
