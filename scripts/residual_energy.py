"""Render the two published, aggregated residual electricity profiles."""
import csv
from decimal import Decimal
from html import escape
from string import Template

PAGE = 'energia-rezydualna-polska-2025-v6.html'
DATA = 'data/energia-rezydualna-polska-2025-v6.csv'


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


def build(root, page):
    with (root / DATA).open(encoding='utf-8-sig', newline='') as stream:
        records = list(csv.DictReader(stream, delimiter=';'))
    totals = next(row for row in records if row['kod'] == 'GWP-total')
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
        rows='\n'.join(rows), csv_url='/' + DATA,
    )
    page(PAGE, 'Polski miks rezydualny energii elektrycznej w 2025 r.',
         'Model badawczy poLCA v6, sprawdzony technicznie. Wyniki dla 1 kWh dostarczonej na średnim i niskim napięciu. Rok 2025 odnosi się do atrybutów pochodzenia energii.',
         body, parent=('Katalog danych', '/datasety.html'),
         head_extra='<link rel="stylesheet" href="/assets/residual-energy.css">')
