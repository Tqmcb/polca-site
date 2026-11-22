"""Shared markup for decorative product family pictograms."""
from html import escape
from hashlib import sha256
from pathlib import Path


ICON_FILE = Path(__file__).resolve().parents[1] / "assets/ikony-polca.svg"
ICON_URL = "/assets/ikony-polca.svg?v=" + sha256(ICON_FILE.read_bytes()).hexdigest()[:10]


def family_icon(family_id, *, css_class='family-icon'):
    return (f'<svg class="{escape(css_class, quote=True)}" width="48" height="48" '
            f'viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
            f'<use href="{ICON_URL}#rodzina-{int(family_id):02d}"></use></svg>')


def export_icons(root, families):
    """Make every symbol usable as a standalone image with a descriptive filename."""
    from io import BytesIO
    from xml.etree import ElementTree as ET
    from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

    namespace = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', namespace)
    symbols = ET.parse(root / 'assets/ikony-polca.svg').getroot()
    labels = {f'rodzina-{f["id"]:02d}': ('wyroby', f'{f["id"]:02d} {f["label"]}') for f in families}
    navigation = {'products': 'Wyroby', 'data': 'Dane', 'tools': 'Kalkulatory',
                  'guide': 'Jak korzystać', 'methods': 'Metody i źródła', 'search': 'Szukaj'}
    labels.update({f'nav-{key}': ('nawigacja', title) for key, title in navigation.items()})
    buffer = BytesIO()
    with ZipFile(buffer, 'w') as archive:
        for symbol in symbols:
            folder, title = labels[symbol.attrib['id']]
            viewbox = symbol.attrib['viewBox']
            width, height = viewbox.split()[2:]
            image = ET.Element(f'{{{namespace}}}svg', {'viewBox': viewbox, 'width': width,
                                                       'height': height, 'color': '#142c45'})
            ET.SubElement(image, f'{{{namespace}}}title').text = title
            image.extend(symbol)
            filename = title.replace('/', '-')
            entry = ZipInfo(f'{folder}/{filename}.svg')
            archive.writestr(entry, ET.tostring(image, encoding='utf-8'), compress_type=ZIP_DEFLATED)
    (root / 'assets/ikony-polca.zip').write_bytes(buffer.getvalue())
