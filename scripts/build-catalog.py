#!/usr/bin/env python3
"""Build public discovery metadata without changing model data or calculators."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data/portal-catalog.json'
EDITORIAL = ROOT / 'data/portal-editorial.json'
ENERGY_ID = 'PL2025_PHYSICAL_DELIVERED_v5'


def read_json(path: str | Path):
    path = Path(path)
    return json.loads((path if path.is_absolute() else ROOT / path).read_text(encoding='utf-8'))


def download(label: str, path: str) -> dict:
    file = ROOT / path.lstrip('/')
    if not file.is_file():
        raise ValueError(f'Download does not exist: {path}')
    return {'label': label, 'format': file.suffix[1:].upper(), 'href': '/' + path.lstrip('/')}


def base_record(*, id: str, title: str, kind: str, category_id: str,
                category_label: str, year: int | None, year_type: str | None,
                status_id: str, status_label: str, description: str, href: str,
                downloads: list[dict] | None = None, **extra) -> dict:
    files = downloads or []
    return {
        'id': id, 'title': title, 'kind': kind,
        'category_id': category_id, 'category_label': category_label,
        'year': year, 'year_type': year_type,
        'status_id': status_id, 'status_label': status_label,
        'description': description, 'href': href,
        'unit': None, 'boundary': None, 'indicator_label': None,
        'source_name': None, 'source_url': None,
        'formats': list(dict.fromkeys(item['format'] for item in files)),
        'downloads': files, 'methodology_href': None,
        'related_ids': [], 'keywords': [], **extra,
    }


def build_legacy_record(raw: dict, editorial: dict) -> dict:
    code = raw['code']
    note = editorial['datasets'][code]
    if (raw['status'] == 'withdrawn') != (note['status_id'] == 'withdrawn'):
        raise ValueError(f'Inconsistent withdrawal status for {code}')
    raw_unit = raw['unit']
    denominator = {'l': 'l', 'm3': 'm³', 'tkm': 't·km'}.get(raw_unit, raw_unit)
    category = editorial['categories'][note['category_id']]
    is_parameters = code == 'POLCA-MMA-LCI-DEFAULTS-2026'
    result = base_record(
        id=code, title=note['title'], kind='dataset',
        category_id=note['category_id'], category_label=category,
        year=raw['year'], year_type=note['year_type'],
        status_id=note['status_id'],
        status_label=editorial['statuses'][note['status_id']],
        description=note['description'], href=f'/dane/{code.lower()}.html',
        downloads=[{'label':'Rekord z metryką — JSON','format':'JSON','href':f'/data/portal-records/{code}.json'}],
        record_type='parameters' if is_parameters else 'indicator_value',
        unit='1 t mieszanki' if is_parameters else f'kg CO₂e/{denominator}',
        boundary=note.get('boundary', raw['module_default']),
        indicator_label=None if is_parameters else note.get('indicator_label', 'Wpływ na klimat (GWP)'),
        source_name=note.get('source_name', raw['source_name']),
        source_url=note.get('source_url', raw['source_url']),
        methodology_href=note['methodology_href'],
        related_ids=note.get('related_ids', []),
        keywords=note.get('keywords', []),
        geography=raw['geography'],
        reference_unit=raw_unit,
        source_record_href=f'/data/datasets/{code}.json',
    )
    if 'scope_profile' in note:
        result.update(editorial['material_scopes'][note['scope_profile']])
    if raw['status'] == 'withdrawn':
        result.update(withdrawn_at=raw['withdrawn_at'], superseded_by=raw['superseded_by'],
                      is_default=False)
    if note.get('include_source_trace'):
        result['source_trace'] = raw['source_trace']
        result['limitations'] = raw['limitations']
    if note['status_id'] == 'published_sector_dataset' or note.get('include_source_trace'):
        for field in ('publication_year', 'source_valid_until', 'methodology_note',
                      'gwp_fossil_kg_co2e', 'gwp_fossil_basis', 'gwp_net_kg_co2e', 'gwp_gross_kg_co2e',
                      'cement_basis', 'basis_note',
                      'binder_content_pct_m_m', 'gwp_modules_kg_co2e_per_t'):
            if field in raw:
                result[field] = raw[field]
    if is_parameters:
        result['downloads'].append(download('Parametry i założenia — JSON', result['source_record_href']))
    if code == 'KOBIZE-EN-PL-ENDUSER-2024':
        result['unit'] = 'kg CO₂/kWh'
    if not is_parameters:
        field = 'gwp_fossil_kg_co2e' if code == 'POLCA-EN-PL-LCA-2024' else 'gwp_total_kg_co2e'
        value = raw[field]
        if not isinstance(value, (int, float)):
            raise ValueError(f'Missing numeric result for {code}')
        result['value'] = value
        if 'gwp_gross_kg_co2e' in result:
            result['keywords'] = result['keywords'] + [f'{value} netto', f'{result["gwp_gross_kg_co2e"]} brutto']
        if note['category_id'] != 'cbam':
            result['keywords'] = result['keywords'] + ['ślad węglowy', 'wpływ na klimat', 'wyrób', 'produkt']
    return result


def build_energy_record(editorial: dict, version: str = 'v5') -> dict:
    directory = f'data/energia-pl-2025-{version}'
    source_file = f'{directory}/profil-37.json'
    model_id = f'PL2025_PHYSICAL_DELIVERED_{version}'
    card = f'/energia-polska-2025-{version}.html'
    current = model_id == ENERGY_ID
    status = 'review' if current else 'archive'
    profile = read_json(source_file)
    if profile['model_id'] != model_id:
        raise ValueError('Unexpected 2025 energy model')
    if profile['status']['state'] != 'technical_review_complete' or profile['is_default']:
        raise ValueError('2025 energy publication status needs a manual catalog review')
    indicators = profile['indicators']
    total = next(item for item in indicators if item['code'] == 'GWP-total')
    note = editorial['energy_2025']
    files = [
        download('Cały pakiet ZIP', f'{directory}/Polska-energia-2025-{version}.zip'),
        download('37 wskaźników — JSON', source_file),
        download('37 wskaźników — CSV', f'{directory}/wskazniki-37.csv'),
        download('Opis pakietu', f'{directory}/START.txt'),
        download('Metoda i zmiany', f'{directory}/METODA-I-ZMIANY.txt'),
        download('Warunki wykorzystania', f'{directory}/WARUNKI-WYKORZYSTANIA.txt'),
        download('Przykład dla 10 kWh', f'{directory}/przyklad-10-kWh.json'),
        download('Kontrola eksportu', f'{directory}/kontrola-eksportu.json'),
        download('Spis plików i sum kontrolnych', f'{directory}/manifest.json'),
    ]
    return base_record(
        id=model_id, title=note['title'] if current else f'Energia elektryczna — Polska 2025, {version}', kind='dataset',
        category_id='energia', category_label=editorial['categories']['energia'],
        year=profile['reference_year'], year_type='reference',
        status_id=status, status_label=editorial['statuses'][status],
        description=note['description'], href=card,
        downloads=files, record_type='indicator_profile',
        unit='kg CO₂e/kWh', reference_unit=profile['functional_unit']['unit'],
        boundary=note['boundary'], indicator_label='GWP-total — wpływ na klimat',
        value=total['value_per_kWh'], indicator_count=len(indicators),
        source_name=f'poLCA — model Polska 2025 {version}',
        source_url=f'/{directory}/METODA-I-ZMIANY.txt',
        source_record_href='/' + source_file,
        methodology_href=card + '#metoda',
        related_ids=['POLCA-EN-PL-LCA-2024', 'KOBIZE-EN-PL-ENDUSER-2024'],
        keywords=['prąd', 'energia elektryczna', '2025', '37 wskaźników', 'miks fizyczny', 'woda', 'odpady', 'ślad węglowy', 'ślad środowiskowy', 'wyrób', 'produkt', 'budynek'],
        geography=profile['country'], is_default=False,
        **({} if current else {'superseded_by': ENERGY_ID}),
    )


def build_resource(raw: dict, editorial: dict) -> dict:
    item = dict(raw)
    item['category_label'] = editorial['categories'][raw['category_id']]
    item['status_label'] = editorial['statuses'][raw['status_id']]
    item['downloads'] = [download(x['label'], x['href']) for x in raw.get('downloads', [])]
    return base_record(**item)


def build_catalog() -> dict:
    editorial = read_json(EDITORIAL)
    legacy = read_json('data/datasets.json')['datasets']
    source_ids = {item['code'] for item in legacy}
    if source_ids != set(editorial['datasets']):
        raise ValueError('Editorial records and source records differ')
    datasets = [build_energy_record(editorial), build_energy_record(editorial, "v4")]
    datasets += [build_legacy_record(item, editorial) for item in legacy]
    resources = [build_resource(item, editorial) for item in editorial['resources']]
    mapping = read_json('data/cpr-mapping.json')
    families = {f['id'] for f in read_json('data/cpr-families.json')['families']}
    record_ids = {r['id'] for r in datasets + resources}
    if set(mapping['records']) - record_ids:
        raise ValueError('Unknown record in CPR mapping')
    for item in datasets + resources:
        ids = mapping['records'].get(item['id'], item.get('cpr_family_ids', []))
        if set(ids) - families:
            raise ValueError('Unknown CPR family')
        item['cpr_family_ids'] = ids
        item['cpr_related'] = mapping.get('related', {}).get(item['id'], [])
        item['cpr_scope_note'] = mapping.get('scope_notes', {}).get(item['id'])
        if any(x['family_id'] not in families for x in item['cpr_related']):
            raise ValueError('Unknown related CPR family')
    collections = []
    for raw in editorial['collections']:
        item = dict(raw)
        item['downloads'] = [download(x['label'], x['href']) for x in raw['downloads']]
        item['formats'] = list(dict.fromkeys(x['format'] for x in item['downloads']))
        collections.append(item)
    all_ids = [x['id'] for x in datasets + resources + collections]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError('Duplicate catalog ID')
    known_ids = set(all_ids)
    for item in datasets + resources:
        for related in item['related_ids']:
            if related not in known_ids:
                raise ValueError(f"Unknown related ID in {item['id']}: {related}")
    withdrawn = [r for r in datasets if r['status_id'] in ('withdrawn', 'archive')]
    datasets = [r for r in datasets if r['status_id'] not in ('withdrawn', 'archive')]
    current_ids = {r['id'] for r in datasets}
    for record in withdrawn:
        if record['superseded_by'] not in current_ids:
            raise ValueError(f"Missing current replacement for {record['id']}")
    return {
        'schema_version': '1.0',
        'catalog_version': editorial['catalog_version'],
        'counts': {
            'data_positions': len(datasets),
            'withdrawn_positions': len(withdrawn),
            'parameter_sets': sum(x['record_type'] == 'parameters' for x in datasets),
            'control_references': sum(x['category_id'] == 'cbam' for x in datasets),
            'resources': len(resources),
            'collections': len(collections),
        },
        'datasets': datasets, 'withdrawn_datasets': withdrawn,
        'resources': resources, 'collections': collections,
    }


def serialize(catalog: dict) -> str:
    return json.dumps(catalog, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check that committed catalog is current')
    args = parser.parse_args()
    catalog = build_catalog()
    output = serialize(catalog)
    records = catalog['datasets'] + catalog['withdrawn_datasets']
    record_files = {ROOT / ('data/portal-records/' + item['id'] + '.json'): serialize({'schema_version':'1.0', 'catalog_version':catalog['catalog_version'], 'record':item, 'usage_note':'Rodzaj wskaźnika, jednostka, granice i status są opisane w rekordzie. Dobierz dane do metody oceny i zastosowania.'}) for item in records}
    if args.check:
        for file, content in record_files.items():
            if not file.exists() or file.read_text(encoding='utf-8') != content:
                print('Record file is stale: ' + str(file.relative_to(ROOT)))
                return 1
    else:
        for file, content in record_files.items():
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding='utf-8')
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != output:
            print('Catalog is stale. Run python3 scripts/build-catalog.py')
            return 1
        print('Catalog is current.')
    else:
        OUTPUT.write_text(output, encoding='utf-8')
        print(f'Written {OUTPUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
