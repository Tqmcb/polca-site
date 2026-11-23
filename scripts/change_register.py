"""Static entry targets for the progressively enhanced change register."""
import re
import unicodedata


def entry_anchor(entry):
    # Keep the published fragment format used by rejestr-zmian.html.
    title = unicodedata.normalize('NFD', entry['tytul'].lower().replace('ł', 'l'))
    title = re.sub(r'[\u0300-\u036f]', '', title)
    slug = re.sub(r'[^a-z0-9]+', '-', title).strip('-')
    return f'wpis-{entry["data"]}-{slug}'


def polish_date(iso_date):
    year, month, *day = iso_date.split('-')
    # Historical reviews sometimes specify only the month.
    return f'{int(day[0])}.{month}.{year}' if day else f'{month}.{year}'


def static_entries(entries, escape):
    return '\n'.join(
        f'<article class="rej-entry" id="{escape(entry_anchor(entry))}">'
        f'<time class="rej-date" datetime="{escape(entry["data"])}">{polish_date(entry["data"])}</time>'
        f'<div><h3 class="rej-title">{escape(entry["tytul"])}</h3>'
        f'<p class="rej-desc">{escape(entry["opis"])}</p></div></article>'
        for entry in entries
    )
