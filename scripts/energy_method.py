"""Format the published method from the v4 release for in-page reading."""
from html import escape
from pathlib import Path
import re
from urllib.parse import urlsplit


METHOD_FILE = 'data/energia-pl-2025-v4/METODA-I-ZMIANY.txt'

# Use the citation titles already printed in this edition as the link text.
CITATIONS = (
    'bilansu energii elektrycznej Eurostatu', 'tablic produkcji z paliw',
    'źródeł niepalnych', 'raportu Polskich Sieci Elektroenergetycznych za 2025 r.',
    'arkusz EMITOR 2025', 'formularz G-10.2 za 2025 r.', 'Wyższego Urzędu Górniczego',
    'Państwowego Instytutu Geologicznego', 'errata autora modelu składowania nadkładu',
    'NID 2026', 'zweryfikowanych emisji w unijnym systemie handlu uprawnieniami do emisji, ETS',
    'Departament Energii USA', 'Orano', 'Euro Chlor', 'noty holenderskiej krajowej bazy środowiskowej NMD',
    'raport NMD o elektryczności', 'PN-EN 15804+A2:2020-03', 'wydanie skonsolidowane',
    'EN 15941:2024', 'ogólne instrukcje programu EPD Polska',
)

# The source uses both “title (url)” and a bibliography with unparenthesized URLs.
URL = r'https?://[^\s<>"\);]+'
CITATION = re.compile(
    r'(?P<title>' + '|'.join(map(re.escape, CITATIONS)) + r')'
    + rf'(?: \((?P<parenthesized>{URL})\)|,? (?P<bare>{URL}))'
    + rf'|(?P<other>{URL})'
)

# Add reading breaks at topic changes within the longer source paragraphs.
PARAGRAPH_BREAK = re.compile(
    r'(?<=\.) (?=Kierunki fizycznego importu|Metan ze spalania|Polski iloraz nadkładu|'
    r'Z tego CO₂|Ciepło elektrowni Kozienice|Z v3 zachowano|Rozszerzenie zasady|'
    r'Dla energii kupowanej|Kryteriami oceny zbioru|Najstarsze istotne dane|'
    r'Analizy wrażliwości)'
)


def linked_text(text: str) -> str:
    parts = []
    start = 0
    for match in CITATION.finditer(text):
        url = match['parenthesized'] or match['bare'] or match['other']
        label = match['title'] or urlsplit(url).netloc
        parts.append(escape(text[start:match.start()]))
        parts.append(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>')
        start = match.end()
        if label.endswith('.') and text.startswith('.', start):
            start += 1
    parts.append(escape(text[start:]))
    return ''.join(parts)


def full_method_html(root: Path) -> str:
    title, *blocks = (root / METHOD_FILE).read_text(encoding='utf-8').strip().split('\n\n')
    title = title.replace('METODA I ZMIANY', 'Metoda i zmiany', 1)
    markup = [
        '<details id="pelna-metoda" class="energy-method-full">',
        '<summary>Przeczytaj pełny opis metody v4</summary>',
        '<div class="energy-method-body">',
        f'<p class="energy-method-title">{escape(title)}</p>',
    ]
    for block in blocks:
        if re.fullmatch(r'\d+\. [^\n]+', block):
            markup.append(f'<h3>{escape(block)}</h3>')
        elif block:
            # The published text repeats the same qualification about allocation.
            # Keep it once in the reading view. The release file remains available below.
            block = block.replace(
                'Ograniczenia tych oszacowań opisuje metoda; przyjęcie alokacji dla określonego programu ocenia się osobno. '
                'Nie ogłasza się pełnej harmonizacji każdej pary współproduktów; przyjęcie tej alokacji dla określonego programu ocenia się osobno.',
                'Nie potwierdzono, że zasady alokacji są w pełni spójne dla wszystkich par współproduktów. '
                'Przydatność przyjętych zasad ocenia się odrębnie dla danego programu.',
            )
            markup.extend(f'<p>{linked_text(paragraph)}</p>' for paragraph in PARAGRAPH_BREAK.split(block))
    markup.append(
        f'<p class="energy-method-download"><a href="/{METHOD_FILE}" download>'
        'Pobierz źródłowy opis metody (plik tekstowy)</a></p></div></details>'
    )
    return '\n'.join(markup)
