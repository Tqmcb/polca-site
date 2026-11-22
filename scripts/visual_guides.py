"""Render the workflow, source index and applications from the portal's editorial copy."""
from decimal import Decimal
from html import escape
import json


def paragraphs(section):
    return ''.join(f'<p>{escape(text)}</p>' for text in section['paragraphs'])


def resources(section, documented=False):
    items = []
    for link in section['links']:
        note = f'<span>{escape(link["note"])}</span>' if documented and link.get('note') else ''
        items.append(f'<li><a href="{escape(link["href"])}">{escape(link["label"])}</a>{note}</li>')
    kind = 'guide-documents' if documented else 'guide-links'
    return f'<ul class="{kind}">{"".join(items)}</ul>'


def page_header(content):
    return (f'<header class="guide-intro"><h1>{escape(content["title"])}</h1>'
            f'<p>{escape(content["lead"])}</p></header>')


def section_link(section):
    return f'<a href="#{escape(section["id"])}">{escape(section["nav_label"])}</a>'


def text_section(section):
    return f'''<section class="guide-section" id="{escape(section['id'])}">
    <h2>{escape(section['title'])}</h2><div>{paragraphs(section)}{resources(section)}</div></section>'''


def printed_number(number, digits):
    return f'{number:.{digits}f}'.replace('.', ',')


def example_flow(root, steps):
    directory = root / 'data/energia-pl-2025-v4'
    profile = json.loads((directory / 'profil-37.json').read_text(), parse_float=Decimal)
    example = json.loads((directory / 'przyklad-10-kWh.json').read_text(), parse_float=Decimal)
    indicator = next(row for row in profile['indicators'] if row['code'] == 'GWP-total')
    result = next(row for row in example['results'] if row['code'] == indicator['code'])
    quantity = example['electricity_quantity_kWh']
    if (example['model_id'] != profile['model_id']
            or indicator['impact_unit'] != 'kg CO2 eq' or result['impact_unit'] != 'kg CO2 eq'
            or indicator['denominator_unit'] != 'kWh'
            or quantity * indicator['value_per_kWh'] != result['value_for_10_kWh']):
        raise ValueError('Niezgodne jednostki, model albo wynik w przykładzie przewodnika.')
    samples = [
        (f'{quantity} <small>kWh</small>', 'Przetwarzanie odpadu w module C3'),
        (f'Polska {profile["reference_year"]}', 'Fizyczny miks dostarczonej energii, wersja v4'),
        (f'≈ {printed_number(indicator["value_per_kWh"], 5)}', 'kg ekwiwalentu CO₂ na 1 kWh'),
        (f'≈ {printed_number(result["value_for_10_kWh"], 2)}', f'kg ekwiwalentu CO₂ dla {quantity} kWh'),
    ]
    nodes = []
    for step, (value, note) in zip(steps, samples, strict=True):
        nodes.append(f'''<li><a href="#{escape(step['id'])}">
        <span class="flow-label">{escape(step['nav_label'])}</span>
        <strong>{value}</strong><span class="flow-note">{escape(note)}</span></a></li>''')
    return f'''<figure class="guide-flow" aria-labelledby="flow-title">
    <figcaption><h2 id="flow-title">Od zużycia energii do wpływu na klimat</h2>
    <p>Cztery kroki przykładu pokazują, jak mnożymy zużycie energii przez wskaźnik profilu. Proces odbywa się poza kontrolą właściciela deklaracji.</p></figcaption>
    <nav aria-label="Etapy doboru danych"><ol>{''.join(nodes)}</ol></nav>
    <div class="flow-source"><span>Wynik obejmuje tylko wkład energii w łączny potencjał globalnego ocieplenia (GWP-total).</span>
    <a href="/data/energia-pl-2025-v4/przyklad-10-kWh.json">Dane przykładowego obliczenia</a></div></figure>'''


def workflow(content, root):
    family, *steps = content['sections']
    return (page_header(content) + example_flow(root, steps)
            + f'<div class="guide-family-link">{section_link(family)}</div>'
            + '<div class="guide-reading">' + ''.join(text_section(s) for s in [*steps, family]) + '</div>')


def methods(content):
    sections = content['sections']
    index = ''.join(f'<li>{section_link(section)}</li>' for section in sections)
    documents = []
    for section in sections:
        documents.append(f'''<section class="method-entry" id="{escape(section['id'])}">
        <div class="method-description"><h2>{escape(section['title'])}</h2>{paragraphs(section)}</div>
        {resources(section, documented=True)}</section>''')
    return (page_header(content) + '<nav class="method-index" aria-label="Tematy dokumentacji">'
            + f'<ul>{index}</ul></nav><div class="method-register">{"".join(documents)}</div>')


# The cutaway block, apartment facade and conveyor distinguish the three scopes of assessment.
# The accompanying HTML states the meaning of each illustration at any viewport width.
APPLICATION_DRAWINGS = {
    'wyrob': '''<path class="drawing-side" d="m14 38 43-20 30 15-44 21Z"/>
        <path d="m14 38 43-20 30 15-44 21-29-16v22l29 16 44-22V33M43 54v22"/>
        <path d="m26 38 11-6 14 7-11 5Zm22-10 10-5 14 7-11 5Z"/>
        <path class="drawing-detail" d="m50 56 29-14m-29 20 29-14m-29 20 29-14M20 62v-9m6 12v-9"/>''',
    'budynek': '''<path class="drawing-side" d="m14 34 42-17 30 16-42 18Z"/>
        <path d="m14 34 42-17 30 16-42 18Zm0 0v31l30 16 42-19V33M44 51v30"/>
        <path d="m21 33 35-14 23 12-35 15Z"/>
        <path class="drawing-detail" d="m18 43 22 12m-22-4 22 12m-22-4 22 12m-17-27v17m9-12v18m16-12 34-15m-34 22 34-15m-34 22 34-15m-29-7v17m11-22v17m11-22v17"/>
        <path d="m43 81 45-20m-75 5 29 16"/>''',
    'proces': '''<path class="drawing-side" d="m18 26 12-6 22 10-11 6Z"/>
        <path d="m18 26 12-6 22 10-11 6-23-10 7 17 10 5 6-12m-6 12 10-5 7-13M28 47v6l7 3v-6"/>
        <path d="m18 55 16 7 42-18 8 4-42 20-24-11Z"/>
        <path d="m18 57 24 11 42-20v6L42 74 18 63Zm24 11v6m-18-8v8m6-5v6m44-17v10m5-12v8"/>
        <path class="drawing-detail" d="m34 59 7 3m0-7 7 4m1-7 8 4m1-8 8 4m0-8 8 4"/>''',
}


def application_drawing(key):
    return ('<svg viewBox="8 12 85 74" class="scope-drawing" aria-hidden="true" focusable="false" '
            'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round">{APPLICATION_DRAWINGS[key]}</svg>')


def applications(content):
    *scopes, declaration = content['sections']
    notes = {
        'wyrob': 'Na tonę, m³ lub sztukę wyrobu',
        'budynek': 'W okresie użytkowania budynku',
        'proces': 'W etapie, w którym zużyto energię',
    }
    branches = []
    for section in scopes:
        key = section['id']
        branches.append(f'''<li><a href="#{escape(key)}">{application_drawing(key)}
        <span><strong>{escape(section['nav_label'])}</strong><small>{escape(notes[key])}</small></span></a></li>''')
    figure = f'''<div class="scope-figure" role="group" aria-labelledby="scope-title">
    <div class="scope-equation"><h2 id="scope-title">Gdzie uwzględnić wkład energii?</h2>
    <p class="scope-factors">Zużycie energii <span>×</span> wskaźnik profilu</p>
    <p class="scope-result"><span aria-label="równa się">=</span> Wkład energii</p></div>
    <nav aria-label="Przedmiot obliczenia"><ul class="scope-branches">{"".join(branches)}</ul></nav></div>'''
    return (page_header(content) + figure
            + f'<div class="guide-family-link">{section_link(declaration)}</div>'
            + '<div class="guide-reading">' + ''.join(text_section(s) for s in content['sections']) + '</div>')


def build(content, root, page):
    layout = content['layout']
    if layout == 'guide-workflow':
        body = workflow(content, root)
    elif layout == 'guide-methods':
        body = methods(content)
    elif layout == 'guide-applications':
        body = applications(content)
    else:
        raise ValueError(f'Nieznany układ przewodnika: {layout}')
    page(content['path'], content['title'], content['lead'], body,
         attrs=f'data-guide="{layout}"', pagehead=False,
         head_extra='<link rel="stylesheet" href="/assets/visual-guides.css?v=20261122-linki">')
