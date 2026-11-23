"""Build the homepage with figures derived from the published catalogue."""
import csv
import json
from string import Template

from atlas_icons import family_icon
from atlas_projection import WIDTH, HEIGHT, project, projection
from change_register import entry_anchor, polish_date
from consultation_portal import DATA as CONSULTATION_DATA


def counted(count, singular, few, many):
    if count == 1:
        return f'{count} {singular}'
    noun = few if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14 else many
    return f'{count} {noun}'


def family_coverage(labels):
    # Family names contain 'i' themselves, so a semicolon list keeps the count readable.
    count = counted(len(labels), 'rodziny', 'rodzin', 'rodzin')
    if not labels:
        return f'Wskaźniki liczbowe nie są jeszcze dostępne dla żadnej rodziny.'
    names = [label[:1].lower() + label[1:] for label in labels]
    lead = 'Jest to' if len(labels) == 1 else 'Są to'
    return f'Wskaźniki liczbowe podajemy obecnie dla {count}. {lead}: ' + '; '.join(names) + '.'


def update_items(entries, escape):
    newest = sorted(entries, key=lambda entry: entry['data'], reverse=True)[:4]
    return '\n'.join(
        f'<li><time datetime="{escape(entry["data"])}">{polish_date(entry["data"])}</time>'
        f' · <a href="/rejestr-zmian.html#{escape(entry_anchor(entry))}">{escape(entry["tytul"])}</a></li>'
        for entry in newest
    )


def atlas_labels(root, escape):
    geography = json.loads((root / 'content/home-map.json').read_text())
    topics = json.loads((root / 'content/topic-map.json').read_text())
    points = {item['id']: item for item in topics['items']}
    params = projection(geography['country']['coordinates'][0])
    grid, labels = [], []
    for lon in (16, 20, 24):
        x, _ = project(lon, 52, params)
        grid.append(f'<path d="M{x:.1f} 12 V477"/><text x="{x+5:.1f}" y="475">{lon}°E</text>')
    for lat in (50, 52, 54):
        _, y = project(20, lat, params)
        grid.append(f'<path d="M18 {y:.1f} H732"/><text x="18" y="{y-5:.1f}">{lat}°N</text>')
    for key, place, theme in [
        ('wiatr-szymankowo', 'Szymankowo', 'Energia wiatru'),
        ('budynki', 'Warszawa', 'Budynki'),
        ('Dolny Śląsk', 'Dolny Śląsk', 'Kruszywa'),
    ]:
        item = points[key]
        x, y = project(item['lon'], item['lat'], params)
        labels.append(f'<g transform="translate({x:.1f} {y:.1f})"><circle r="6"/>'
                      f'<text x="17" y="-1" text-anchor="start">{escape(place)}</text>'
                      f'<text class="atlas-theme" x="17" y="20" text-anchor="start">{escape(theme)}</text></g>')
    return (f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" class="home-atlas-marks" aria-hidden="true">'
            + '<g class="atlas-graticule">' + ''.join(grid) + '</g><g class="atlas-points">'
            + ''.join(labels) + '</g></svg>')


def build(api, families):
    root, page, e = (api[key] for key in ('ROOT', 'page', 'e'))
    records = api['CAT']['datasets']
    methods = json.loads((root / 'data/product-methods.json').read_text())['documents']
    energy = next(r for r in records if r['id'] == 'PL2025_PHYSICAL_DELIVERED_v4')
    consultation = json.loads((root / 'content/consultation-energy.json').read_text())
    sensitivity_file = root / CONSULTATION_DATA.lstrip('/') / 'wrazliwosc-37.csv'
    with sensitivity_file.open(encoding='utf-8-sig', newline='') as source:
        scenarios = list(csv.DictReader(source, delimiter=';'))
    consultation_description = consultation['home_description'].format(
        indicator_count=len({row['indicator'] for row in scenarios}),
        variant_count=len({row['scenario'] for row in scenarios}),
    )
    current_ids = {family_id for record in records for family_id in record.get('cpr_family_ids', [])}
    labels = [family['label'] for family in families if family['id'] in current_ids]
    picks = [next(f for f in families if f['id'] == n) for n in [15, 24, 23, 1, 16, 20]]
    product_links = ''
    for family in picks:
        has_data = family['id'] in current_ids
        has_method = any(family['id'] in method['family_ids'] for method in methods)
        label = 'Dane i dokumenty' if has_data else ('Metody i objaśnienia' if has_method else 'Artykuły i objaśnienia')
        product_links += (
            f'<li><a href="/wyroby/{family["id"]:02d}.html">'
            f'<span class="home-family-name">{family_icon(family["id"], css_class="home-family-icon")}'
            f'<strong>{e(family["label"])}</strong></span><small>{label}</small></a></li>'
        )
    body = Template((root / 'content/portal-home.html.tpl').read_text()).substitute(
        atlas_labels=atlas_labels(root, e),
        positions=counted(api['CAT']['counts']['data_positions'], 'pozycję', 'pozycje', 'pozycji'),
        family_total=len(families),
        family_coverage=e(family_coverage(labels)),
        update_items=update_items(api['CHANGE_ENTRIES'], e),
        energy_year=e(energy['year']),
        indicator_count=e(energy['indicator_count']),
        energy_href=e(energy['href']),
        energy_status=e(energy['status_label']),
        energy_status_lower=e(energy['status_label'][:1].lower() + energy['status_label'][1:]),
        energy_source=e(energy['source_name']),
        energy_factor=e(f'{energy["value"]:.4f}'.replace('.', ',')),
        energy_factor_raw=e(energy['value']),
        example_value=e(f'{energy["value"] * 100:.2f}'.replace('.', ',')),
        product_links=product_links,
        consultation_title=e(consultation['home_title']),
        consultation_description=e(consultation_description),
    )
    page(
        'index.html',
        'Polskie dane do obliczeń śladu węglowego i środowiskowego',
        'poLCA: dane i kalkulatory dla energii, materiałów i transportu. Obliczenia dla wyrobów budowlanych oraz dokumentacja do deklaracji środowiskowych EPD.',
        body,
        home=True,
        head_extra='<script src="/js/home.js?v=20261020illustrations" defer></script>',
    )
