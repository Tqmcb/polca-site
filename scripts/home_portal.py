"""Build the homepage with figures derived from the published catalogue."""
from string import Template
import json


def build(api, families):
    root, page, e = (api[key] for key in ('ROOT', 'page', 'e'))
    records = api['CAT']['datasets']
    methods = json.loads((root / 'data/product-methods.json').read_text())['documents']
    energy = next(r for r in records if r['id'] == 'PL2025_PHYSICAL_DELIVERED_v3_REVIEW')
    picks = [next(f for f in families if f['id'] == n) for n in [15, 24, 23, 1, 16, 20]]
    product_links = ''
    for family in picks:
        has_data = any(family['id'] in r.get('cpr_family_ids', []) for r in records)
        has_method = any(family['id'] in method['family_ids'] for method in methods)
        label = 'Dane i dokumenty' if has_data else ('Metody i objaśnienia' if has_method else 'Artykuły i objaśnienia')
        product_links += (
            f'<li><a href="/wyroby/{family["id"]:02d}.html"><span>'
            f'<strong>{e(family["label"])}</strong><small>{label}</small></span>'
            '<span class="home-route-arrow" aria-hidden="true">→</span></a></li>'
        )
    body = Template((root / 'content/portal-home.html.tpl').read_text()).substitute(
        energy_year=e(energy['year']),
        indicator_count=e(energy['indicator_count']),
        energy_href=e(energy['href']),
        energy_status=e(energy['status_label']),
        energy_source=e(energy['source_name']),
        energy_factor=e(f'{energy["value"]:.4f}'.replace('.', ',')),
        example_value=e(f'{energy["value"] * 100:.2f}'.replace('.', ',')),
        product_links=product_links,
    )
    page(
        'index.html',
        'Polskie dane do obliczeń śladu węglowego i środowiskowego',
        'poLCA: dane i kalkulatory dla energii, materiałów i transportu. Obliczenia dla wyrobów budowlanych oraz dokumentacja do deklaracji środowiskowych EPD.',
        body,
        home=True,
    )
