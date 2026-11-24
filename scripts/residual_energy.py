"""Render the two published, aggregated residual electricity profiles."""
import csv
from decimal import Decimal
from html import escape
from string import Template

PAGE = 'energia-rezydualna-polska-2025-v6.html'
DATA = 'data/energia-rezydualna-polska-2025-v6.csv'
COMPARISON = 'data/energia-rezydualna-polska-2025-v6-porownanie-wegla.csv'
VARIANTS = (
    ('bazowy_v6', 'Model bazowy v6'),
    ('wariant_krajowy_bez_podzialu_wegla', 'Zmiana dla źródeł krajowych'),
    ('wariant_krajowy_i_pula_europejska_bez_podzialu_wegla', 'Zmiana dla źródeł krajowych i puli europejskiej'),
)


def number(raw, digits=5):
    value = Decimal(raw)
    if not value:
        return '0'
    if abs(value) < Decimal('0.0001'):
        mantissa, exponent = f'{value:.{digits - 1}E}'.split('E')
        power = str(int(exponent)).translate(str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))
        return mantissa.rstrip('0').rstrip('.').replace('.', ',') + ' × 10' + power
    places = max(0, digits - value.adjusted() - 1)
    text = f'{value:.{places}f}'
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text.replace('.', ',')


def comparison_tables(records):
    by_voltage = {}
    climate = {}
    change = {}
    for voltage in ('średnie', 'niskie'):
        data = [row for row in records if row['napiecie'] == voltage]
        climate[voltage] = next(row for row in data if row['kod'] == 'GWP-total')
        rows = []
        for row in data:
            if row['kod'] in ('GWP-total', 'HWD', 'NHWD'):
                percent = abs(Decimal(row['zmiana_pelny_wzgledem_bazowego_proc']))
                places = 2 if row['kod'] == 'GWP-total' else 1
                change[voltage, row['kod']] = f'{percent:.{places}f}'.replace('.', ',')
            cells = ''.join(f'<td>{number(row[key])}</td>' for key, _ in VARIANTS)
            rows.append(
                f'<tr><th scope="row">{escape(row["wskaznik"])} '
                f'<small>{escape(row["kod"])} · {escape(row["jednostka"])}</small></th>{cells}</tr>'
            )
        by_voltage[voltage] = '\n'.join(rows)

    headlines = []
    for key, title in VARIANTS:
        cells = ''.join(f'<td>{number(climate[v][key], 6)}</td>' for v in by_voltage)
        headlines.append(f'<tr><th scope="row">{title}</th>{cells}</tr>')
    return {
        'climate_rows': '\n'.join(headlines),
        'medium_rows': by_voltage['średnie'],
        'low_rows': by_voltage['niskie'],
        'change_medium': change['średnie', 'GWP-total'],
        'change_low': change['niskie', 'GWP-total'],
        'hazardous_medium': change['średnie', 'HWD'],
        'nonhazardous_medium': change['średnie', 'NHWD'],
        'hazardous_low': change['niskie', 'HWD'],
        'nonhazardous_low': change['niskie', 'NHWD'],
    }


def build(root, page):
    with (root / DATA).open(encoding='utf-8-sig', newline='') as stream:
        records = list(csv.DictReader(stream, delimiter=';'))
    totals = next(row for row in records if row['kod'] == 'GWP-total')
    with (root / COMPARISON).open(encoding='utf-8-sig', newline='') as stream:
        comparison = list(csv.DictReader(stream, delimiter=';'))
    rows = []
    for row in records:
        rows.append(
            f'<tr><th scope="row">{escape(row["wskaznik"])} '
            f'<small>{escape(row["kod"])} · {escape(row["jednostka"])}</small></th>'
            f'<td>{number(row["srednie_napiecie"])}</td><td>{number(row["niskie_napiecie"])}</td></tr>'
        )
    body = Template((root / 'content/residual-energy.tmpl').read_text()).substitute(
        medium=number(totals['srednie_napiecie'], 6),
        low=number(totals['niskie_napiecie'], 6),
        rows='\n'.join(rows), csv_url='/' + DATA, comparison_url='/' + COMPARISON,
        **comparison_tables(comparison),
    )
    page(PAGE, 'Polski miks rezydualny energii elektrycznej w 2025 r.',
         'Model badawczy poLCA v6 dla 1 kWh dostarczonej na średnim lub niskim napięciu. Wyniki nie mają formalnej kwalifikacji do deklaracji środowiskowych wyrobów (EPD). Rok 2025 dotyczy pochodzenia energii.',
         body, parent=('Katalog danych', '/datasety.html'),
         head_extra='<link rel="stylesheet" href="/assets/residual-energy.css">')
