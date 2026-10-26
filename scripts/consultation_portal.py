"""Generate the consultation module from public, versioned editorial data."""
from __future__ import annotations

import html
import json
import math
import re
from urllib.parse import urlsplit


PAGE = "konsultacje/energia-polska-2025.html"
METHOD_PAGE = "konsultacje/energia-polska-2025-metoda.html"
REPORT_PAGE = "konsultacje/energia-polska-2025-raport-lca.html"
DATA = "/data/konsultacje/energia-2025-20261020/"
STEP_IDS = ("zrodla", "granice", "obliczenia", "sprawdzenie", "przeglad", "uwagi")
QUESTION_IDS = ("granice", "alokacja", "biogeniczny", "jakosc")
STATES = {
    "completed": "Etap wykonany",
    "planned": "Etap planowany",
    "open": "Konsultacje",
}
COMMENT_STATUSES = {
    "received": "Zgłoszona",
    "in_review": "W analizie",
    "author_response": "Odpowiedź autora",
    "revision_required": "Wymaga poprawy",
    "resolved": "Rozstrzygnięta",
}


def esc(value):
    """All editorial strings are text, never trusted HTML."""
    return html.escape(str(value if value is not None else ""), quote=True)


def safe_href(value):
    value = str(value)
    if any(ord(char) < 32 for char in value) or "\\" in value:
        raise ValueError("Niedozwolony adres w treści konsultacji")
    parsed = urlsplit(value)
    if value.startswith("#") or (value.startswith("/") and not value.startswith("//")):
        if parsed.scheme or parsed.netloc:
            raise ValueError("Niedozwolony adres lokalny")
        return esc(value)
    if parsed.scheme == "https" and parsed.netloc and not parsed.username and not parsed.password:
        return esc(value)
    raise ValueError("Adres musi być lokalny albo korzystać z HTTPS")


def identifier(value):
    value = str(value)
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", value):
        raise ValueError("Niedozwolony identyfikator konsultacji")
    return value


def link(label, href, download=False):
    attr = " download" if download else ""
    return f'<a href="{safe_href(href)}"{attr}>{esc(label)}</a>'


def links(items):
    return '<ul class="consult-links">' + "".join(
        f'<li>{link(item["label"], item["href"])}</li>' for item in items
    ) + "</ul>"

def display_unit(unit):
    """Polish display labels; the source unit remains in data and exports."""
    return {
        "disease incidence": "przypadki zachorowań",
        "dimensionless (pt)": "bezwymiarowy (pkt)",
        "MJ (net calorific)": "MJ (wartość opałowa)",
        "m3 world eq": "m³ równoważnika światowego",
    }.get(unit, unit)


def method_sections(items):
    seen = set()
    result = []
    for section in items:
        section_id = identifier(section["id"])
        if section_id in seen:
            raise ValueError("Powtórzony identyfikator sekcji metody")
        seen.add(section_id)
        result.append(
            f'<section class="consult-method-section" id="{esc(section_id)}">'
            f'<h2>{esc(section["title"])}</h2>'
            + "".join(f"<p>{esc(text)}</p>" for text in section["paragraphs"])
            + links(section.get("links", []))
            + "</section>"
        )
    return "".join(result)


def registry(entries, package_version):
    if not entries:
        return (
            '<div class="consult-empty"><h3>Nie ma jeszcze opublikowanych uwag</h3>'
            "<p>Po opracowaniu zgłoszeń zamieścimy tutaj ich treść, odpowiedzi "
            "i rozstrzygnięcia. Brak opublikowanych uwag nie oznacza akceptacji modelu.</p></div>"
        )
    result = []
    seen = set()
    for entry in entries:
        if entry["package_version"] != package_version:
            raise ValueError("Uwaga dotyczy innej wersji pakietu")
        if re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", json.dumps(entry, ensure_ascii=False)):
            raise ValueError("Usuń adres e-mail przed publikacją uwagi")
        if entry["status"] == "resolved" and not str(entry.get("resolution", "")).strip():
            raise ValueError("Rozstrzygnięta uwaga wymaga treści rozstrzygnięcia")
        entry_id = identifier(entry["id"])
        if entry_id in seen:
            raise ValueError("Powtórzony identyfikator uwagi")
        seen.add(entry_id)
        state = COMMENT_STATUSES[entry["status"]]
        fields = [
            ("Fragment", entry.get("section")),
            ("Uwaga", entry["comment"]),
            ("Źródło", entry.get("source")),
            ("Proponowana poprawka", entry.get("proposal")),
            ("Odpowiedź autora", entry.get("response")),
            ("Rozstrzygnięcie", entry.get("resolution")),
            ("Wersja po zmianie", entry.get("changed_in_version")),
        ]
        metadata = " · ".join(str(entry[key]) for key in ("submitted_at", "author_label") if entry.get(key))
        metadata += " · Pakiet " + package_version
        result.append(
            f'<article class="consult-comment" id="uwaga-{esc(entry_id)}">'
            f'<p class="consult-meta">{esc(entry_id)} · {esc(state)}</p>'
            f'<h3>{esc(entry["topic"])}</h3><p class="consult-muted">{esc(metadata)}</p>'
            '<dl class="consult-comment-fields">'
            + "".join(
                f"<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>"
                for label, value in fields if value
            )
            + "</dl></article>"
        )
    return "".join(result)


def build(api):
    root, page = api["ROOT"], api["page"]
    copy = json.loads((root / "content/consultation-energy.json").read_text(encoding="utf-8"))
    profile = json.loads((root / DATA.lstrip("/") / "profil-37.json").read_text(encoding="utf-8"))
    comments = json.loads((root / DATA.lstrip("/") / "uwagi.json").read_text(encoding="utf-8"))
    if tuple(step["id"] for step in copy["steps"]) != STEP_IDS:
        raise ValueError("Wyjaśnienie musi zawierać sześć uzgodnionych kroków")
    if tuple(question["id"] for question in copy["questions"]) != QUESTION_IDS:
        raise ValueError("Wymagane są cztery uzgodnione pytania")
    if [step["state"] for step in copy["steps"]] != ["completed"] * 4 + ["planned", "open"]:
        raise ValueError("Statusy kroków nie odpowiadają zakresowi konsultacji")
    if len(copy["method_sections"]) != 7:
        raise ValueError("Nota powinna zawierać siedem sekcji")
    if comments["model_id"] != profile["model_id"] or comments["package_version"] != profile["package_version"]:
        raise ValueError("Rejestr i profil dotyczą różnych wersji")
    indicators = profile["indicators"]
    if len(indicators) != 37 or len({row["code"] for row in indicators}) != 37:
        raise ValueError("Profil musi zawierać 37 różnych wskaźników")
    if any(not math.isfinite(float(row["value_per_kWh"])) for row in indicators):
        raise ValueError("Wyniki wskaźników muszą być skończone")

    model_id, version = profile["model_id"], profile["package_version"]
    total = next(row["value_per_kWh"] for row in indicators if row["code"] == "GWP-total")
    unit = profile["functional_unit"]
    unit_description = unit["description_pl"] if isinstance(unit, dict) else str(unit)
    css = '<link rel="stylesheet" href="/assets/consultation.css?v=20261020design">'
    js = '<script src="/js/consultation.js?v=20261020" defer></script>'

    step_navigation = []
    step_content = []
    for index, step in enumerate(copy["steps"], 1):
        step_navigation.append(
            f'<li><button type="button" data-step-select="{index - 1}" '
            f'aria-controls="krok-{esc(step["id"])}">'
            f'<span class="consult-step-dot" aria-hidden="true"></span>'
            f'<span>{esc(step["title"])}</span></button></li>'
        )
        step_content.append(
            f'<li class="consult-step" id="krok-{esc(step["id"])}" data-step="{index - 1}">'
            f'<div class="consult-step-heading"><h3>{esc(step["title"])}</h3>'
            f'<p class="consult-step-state">{esc(STATES[step["state"]])}</p></div>'
            f'<p>{esc(step["text"])}</p>{link(step["evidence_label"], step["evidence_href"])}</li>'
        )
    questions = "".join(
        f'<article class="consult-question" id="pytanie-{esc(question["id"])}">'
        f'<details><summary><h3>{esc(question["title"])}</h3></summary>'
        f'<div class="consult-question-content"><p>{esc(question["text"])}</p><p class="consult-question-hint">{esc(question["hint"])}</p></div></details>'
        f'<button type="button" class="consult-text-button" data-question-select="{esc(question["id"])}" hidden>'
        "Wybierz to pytanie</button></article>"
        for index, question in enumerate(copy["questions"], 1)
    )
    options = "".join(
        f'<option value="{esc(question["id"])}">{esc(question["title"])}</option>'
        for question in copy["questions"]
    )
    rows = "".join(
        f'<tr data-code="{esc(row["code"])}" data-value="{esc(row["value_per_kWh"])}" '
        f'data-unit="{esc(row["impact_unit"])}"><th scope="row">'
        f'<span>{esc(row["name_pl"])}</span><small>{esc(row["code"])}</small></th>'
        f'<td class="consult-result-value">{esc(format(float(row["value_per_kWh"]), ".6g").replace(".", ","))}</td>'
        f'<td>{esc(display_unit(row["impact_unit"]))}/{esc(row.get("denominator_unit", "kWh"))}</td></tr>'
        for row in indicators
    )
    downloads = [
        ("Pełny pakiet konsultacyjny", "Polska-energia-2025-konsultacje.zip", "ZIP"),
        ("Profil z opisem i statusem", "profil-37.json", "JSON"),
        ("37 wskaźników do arkusza", "wskazniki-37.csv", "CSV"),
        ("Metoda i zmiany", "METODA-I-ZMIANY.txt", "TXT"),
        ("Warunki wykorzystania", "WARUNKI-WYKORZYSTANIA.txt", "TXT"),
        ("Ocena jakości danych", "jakosc-danych.json", "JSON"),
        ("Analiza wrażliwości 37 wyników", "wrazliwosc-37.csv", "CSV"),
        ("Wyniki kontroli technicznej", "kontrola-techniczna.json", "JSON"),
        ("Wykaz plików i sumy kontrolne", "manifest.json", "JSON"),
    ]
    download_html = "".join(
        f"<li>{link(label, DATA + filename, download=True)}<span>{esc(format_label)}</span></li>"
        for label, filename, format_label in downloads
    )
    body = f'''<div class="consultation" data-consultation data-model-id="{esc(model_id)}" data-package-version="{esc(version)}">
<header class="consult-intro" aria-labelledby="consult-intro-title">
  <div class="consult-title-row"><h1 id="consult-intro-title">Model energii.<br><span>Polska 2025.</span></h1>
    <div class="consult-intro-copy"><p>{esc(copy["intro"])}</p><div class="consult-actions"><a class="portal-button" href="#pytania">Zobacz pytania</a><a href="/{METHOD_PAGE}">Przeczytaj metodę</a></div></div>
  </div>
  <div class="consult-publication"><p><strong>Projekt do konsultacji</strong><span>Pakiet {esc(version)}</span></p><p>Przegląd ekspercki: planowany.<br><a href="#status">Zakres wykonanej kontroli</a></p><p>W kalkulatorze pozostaje<br><a href="/energia-polska-2025-v4.html">wcześniejsza wersja v4</a>.</p></div>
</header>
<nav class="consult-jump" aria-label="Na tej stronie"><a href="#jak-powstaje-wynik">Jak liczymy</a><a href="#pytania">Pytania</a><a href="#dokumentacja">Dokumentacja</a><a href="#zglos-uwage">Zgłoś uwagę</a><a href="#rejestr">Uwagi i odpowiedzi</a></nav>

<section class="consult-section consult-explainer" id="jak-powstaje-wynik" aria-labelledby="explainer-title">
  <div class="consult-section-heading"><h2 id="explainer-title">Od źródła do wyniku.</h2><p>Prześledź obliczenia, sprawdź ich podstawy i zobacz, które etapy oceny pozostają otwarte.</p></div>
  <figure class="consult-model" aria-labelledby="model-caption">
    <figcaption id="model-caption">Model fizycznego miksu energii dostarczonej odbiorcy · Polska {esc(profile["reference_year"])}</figcaption>
    <div class="consult-model-flow">
      <div class="consult-model-inputs" data-model-node="inputs"><div><strong>Dane krajowe</strong><span>Produkcja prądu i ciepła</span></div><div><strong>Historyczne tło</strong><span>Procesy i dane zastępcze</span></div></div>
      <div class="consult-model-connector" aria-hidden="true"><span></span></div>
      <div class="consult-model-core" data-model-node="model"><span>Obliczenia dla</span><strong>1 kWh</strong><span>Granice systemu i alokacja</span></div>
      <div class="consult-model-connector consult-model-connector-single" aria-hidden="true"><span></span></div>
      <div class="consult-model-output" data-model-node="output"><strong>37 wskaźników</strong><p>Wpływ na klimat w cyklu życia</p><span class="consult-model-value" data-consultation-gwp="{esc(total)}">{esc(format(float(total), ".6f").replace(".", ","))} <small>kg CO₂e/kWh</small></span></div>
    </div>
    <p class="consult-model-note">Wynik projektu. CO₂e oznacza ekwiwalent dwutlenku węgla. <a href="#wyniki">Sprawdź wszystkie wyniki i jednostki</a>.</p>
  </figure>
  <div class="consult-player-controls" data-player-controls hidden>
    <div class="consult-player-buttons"><button type="button" class="consult-button" data-play aria-pressed="false">Odtwórz kroki</button><button type="button" class="consult-button consult-button-secondary" data-show-all aria-expanded="false">Pokaż cały opis</button></div>
    <p id="consult-step-status" role="status" aria-live="polite" aria-atomic="true"></p>
    <p class="consult-motion-note" data-motion-note hidden>Ograniczony ruch: wybierz krok, aby przeczytać jego opis.</p>
  </div>
  <div class="consult-process-reader">
    <ol class="consult-step-navigation" aria-label="Wybierz krok wyjaśnienia" data-step-navigation hidden>{"".join(step_navigation)}</ol>
    <div class="consult-process-detail"><div class="consult-progress" data-step-progress hidden aria-hidden="true"><span></span></div>
    <ol class="consult-steps">{"".join(step_content)}</ol>
    <div class="consult-step-arrows" data-step-arrows hidden><button type="button" class="consult-text-button" data-step-prev>Poprzedni krok</button><button type="button" class="consult-text-button" data-step-next>Następny krok</button></div></div>
  </div>
  <noscript><p class="consult-muted">Powyżej dostępny jest cały opis. Odtwarzanie kroków wymaga JavaScript.</p></noscript>
</section>

<section class="consult-section consult-agenda" id="pytania" aria-labelledby="questions-title">
  <div class="consult-section-heading"><h2 id="questions-title">Co wymaga rozstrzygnięcia?</h2><p>Wybierz temat, w którym możesz wskazać lepsze dane, uzasadnienie lub poprawkę. Możesz też zgłosić inną uwagę.</p></div>
  <div class="consult-questions">{questions}</div>
  <p id="consult-question-status" class="consult-feedback" role="status" aria-live="polite"></p>
  <p><a href="#zglos-uwage">Przejdź do przygotowania uwagi</a></p>
</section>

<section class="consult-section consult-documentation" id="dokumentacja" aria-labelledby="documentation-title">
  <div class="consult-section-heading"><h2 id="documentation-title">Metoda, wyniki i pliki</h2><p>Dokumentacja dotyczy pakietu {esc(version)}. Najpierw przeczytaj zakres modelu oraz opis danych zastępczych.</p></div>
  <p class="consult-method-link"><a href="/{METHOD_PAGE}">Przeczytaj notę metodyczną</a><span>Założenia, zmiany względem v4 i ograniczenia projektu.</span></p>
  <p class="consult-method-link"><a href="/{REPORT_PAGE}">Przeczytaj projekt raportu LCA (oceny cyklu życia)</a><span>Wersja 0.4 z 26.10.2026. Projekt do przeglądu krytycznego.</span></p>
  <ul class="consult-downloads">{download_html}</ul>
  <details class="consult-results" id="wyniki"><summary>Wszystkie 37 wyników dla 1 kWh</summary>
    <div class="consult-results-inner"><p>{esc(unit_description)}</p><p class="consult-muted">Wartości w tabeli są zaokrąglone do sześciu cyfr znaczących. Pełna precyzja znajduje się w plikach JSON i CSV. Wskaźników o różnych jednostkach ani sum i ich składników nie dodaje się ponownie.</p>
    <p class="consult-table-hint">Na małym ekranie przewiń tabelę w bok.</p><div class="consult-table-wrap" tabindex="0" role="region" aria-label="Tabela 37 wyników — przewijana poziomo"><table><caption>Projekt Polska {esc(profile["reference_year"])} · pakiet {esc(version)}</caption><thead><tr><th scope="col">Wskaźnik</th><th scope="col">Wartość</th><th scope="col">Jednostka</th></tr></thead><tbody>{rows}</tbody></table></div></div>
  </details>
</section>

<section class="consult-section consult-status" id="status" aria-labelledby="status-title">
  <div><h2 id="status-title">Co zostało sprawdzone?</h2></div>
  <div><p>{esc(copy["status_summary"])}</p><p>Nota metodyczna jest opracowaniem autora. Raport z niezależnego krytycznego przeglądu eksperckiego nie jest jeszcze dostępny. Ewentualny przegląd, konsultacje publiczne i decyzja operatora programu będą odrębnie udokumentowane.</p><p><a href="/{METHOD_PAGE}">Przeczytaj zakres kontroli i ograniczenia</a></p></div>
</section>

<section class="consult-section consult-correspondence" id="zglos-uwage" aria-labelledby="form-title">
  <div class="consult-section-heading"><h2 id="form-title">Przygotuj uwagę do modelu</h2><p>Formularz porządkuje treść wiadomości. Wysyłasz ją samodzielnie ze swojej poczty na <a href="mailto:info@epd.org.pl">info@epd.org.pl</a>.</p></div>
  <noscript><p class="consult-form-fallback">Aby skorzystać z formularza, włącz JavaScript. Możesz też napisać na <a href="mailto:info@epd.org.pl">info@epd.org.pl</a>: podaj pakiet {esc(version)}, temat, fragment, uwagę, źródło i proponowaną poprawkę.</p></noscript>
  <form id="consultation-form" action="#zglos-uwage" method="get" autocomplete="off" aria-describedby="consult-privacy">
    <fieldset id="consult-form-fields" disabled><legend>Treść zgłoszenia</legend>
      <div class="consult-form-grid">
        <div class="consult-field"><label for="consult-topic">Temat <span>(wymagany)</span></label><select id="consult-topic" required><option value="">Wybierz temat</option>{options}<option value="inne">Inna uwaga</option></select></div>
        <div class="consult-field"><label for="consult-section">Fragment dokumentu <span>(opcjonalnie)</span></label><input id="consult-section" type="text" maxlength="240" placeholder="Np. nota metodyczna, punkt lub kod wskaźnika"></div>
        <div class="consult-field consult-field-wide"><label for="consult-comment">Uwaga <span>(wymagana)</span></label><textarea id="consult-comment" rows="5" maxlength="6000" required placeholder="Opisz, co wymaga sprawdzenia i dlaczego."></textarea></div>
        <div class="consult-field consult-field-wide"><label for="consult-source">Źródło lub dowód <span>(opcjonalnie)</span></label><textarea id="consult-source" rows="2" maxlength="3000" placeholder="Link, tytuł publikacji, rok danych lub opis dowodu."></textarea></div>
        <div class="consult-field consult-field-wide"><label for="consult-proposal">Proponowana poprawka <span>(opcjonalnie)</span></label><textarea id="consult-proposal" rows="3" maxlength="4000" placeholder="Wskaż lepsze dane, zmianę założenia lub sposób sprawdzenia."></textarea></div>
        <div class="consult-field consult-field-wide"><label for="consult-signature">Podpis do publikacji <span>(opcjonalnie)</span></label><input id="consult-signature" type="text" maxlength="160" placeholder="Imię i nazwisko lub nazwa organizacji"><p class="consult-field-help">Podaj wyłącznie podpis, który może być widoczny przy uwadze. Bez podpisu zgłoszenie może zostać opublikowane anonimowo. Adres e-mail pozostaje w korespondencji.</p></div>
      </div>
      <div class="consult-form-actions"><button type="button" class="consult-button" data-mail>Otwórz w programie pocztowym</button><button type="button" class="consult-button consult-button-secondary" data-copy>Kopiuj treść</button><button type="button" class="consult-button consult-button-secondary" data-download>Pobierz treść</button></div>
    </fieldset>
    <p id="consult-form-status" class="consult-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
    <div id="consult-preview" class="consult-preview" hidden><label for="consult-message">Treść do wysłania</label><textarea id="consult-message" rows="12" readonly spellcheck="false"></textarea><p class="consult-muted">Możesz zaznaczyć i skopiować tę treść. Samo przygotowanie, skopiowanie lub pobranie wiadomości nie oznacza jej zgłoszenia.</p></div>
  </form>
<aside class="consult-form-notes"><h3>Przed wysłaniem</h3>
  <p class="consult-privacy-note" id="consult-privacy">Formularz działa w tej karcie przeglądarki. Jego kod nie wysyła treści na serwer ani nie zapisuje jej w plikach cookies lub lokalnym magazynie danych. Kopiowanie, pobranie pliku i otwarcie poczty następują po wybraniu przycisku. Nie dołączaj danych poufnych ani kopii materiałów objętych ograniczeniami licencyjnymi.</p>
  <p class="consult-privacy-note">Administratorem danych przesłanych w korespondencji jest Multicert Sp. z o.o., ul. Mydlarska 47, 04-690 Warszawa. Dane wykorzystujemy do obsługi konsultacji i odpowiedzi na zgłoszenie; dobrowolnie podany podpis służy także oznaczeniu autora opublikowanej uwagi. Kontakt w sprawie danych, w tym zmiany lub usunięcia podpisu: <a href="mailto:biuro@multicert.pl">biuro@multicert.pl</a>. <a href="https://multicert.pl/polityka-prywatnosci/">Ogólne zasady ochrony danych w Multicert</a>.</p>
</aside>
</section>

<section class="consult-section" id="rejestr" aria-labelledby="registry-title">
  <div class="consult-section-heading"><h2 id="registry-title">Uwagi i odpowiedzi</h2><p>Publikujemy opracowane uwagi do tej wersji wraz z odpowiedzią i sposobem rozstrzygnięcia. Przed publikacją usuwamy dane kontaktowe oraz informacje poufne.</p></div>
  <ol class="consult-review-path" aria-label="Przebieg obsługi uwagi"><li>Uwaga w korespondencji</li><li>Opracowanie i publikacja</li><li>Odpowiedź autora</li><li>Rozstrzygnięcie i ewentualna zmiana</li></ol>
  <div data-consultation-registry data-entry-count="{len(comments["entries"])}">{registry(comments["entries"], version)}</div>
  <p class="consult-muted">Stan rejestru: {esc(comments["updated_at"])} · {link("Pobierz rejestr uwag (JSON)", DATA + "uwagi.json", download=True)}</p>
</section></div>'''
    page(PAGE, copy["title"], copy["lead"], body, head_extra=css + js, pagehead=False, attrs='data-page="consultation"')
    method_body = (
        '<article class="consultation consult-method">'
        f'<p class="consult-meta">Nota autora do konsultacji · pakiet {esc(version)}</p>'
        '<p class="consult-method-intro">Ta nota opisuje projekt modelu i jego ograniczenia. '
        'Nie jest raportem niezależnego krytycznego przeglądu.</p>'
        f'<p>{link("Wróć do konsultacji i zgłoś uwagę", "/" + PAGE)}</p>'
        f'<p>{link("Przeczytaj projekt raportu LCA (oceny cyklu życia), wersja 0.4", "/" + REPORT_PAGE)}</p>'
        + '<nav class="consult-method-nav" aria-label="Spis treści noty">'
        + links([{"label":section["title"], "href":"#" + identifier(section["id"])}
                 for section in copy["method_sections"]])
        + "</nav>"
        + method_sections(copy["method_sections"])
        + f'<p class="consult-method-return">{link("Przejdź do pytań i formularza", "/" + PAGE + "#pytania")}</p>'
        + "</article>"
    )
    page(
        METHOD_PAGE,
        "Energia Polska 2025 — nota metodyczna do konsultacji",
        f"Zakres, źródła, zmiany i ograniczenia projektu. Pakiet {version}.",
        method_body,
        parent=("Konsultacje modelu", "/" + PAGE),
        head_extra=css,
    )
