# Design: Strona metodyki poLCA-EN-PL z systemem komentarzy

**Data:** 2026-04-04
**Projekt:** polca.org.pl — statyczna strona HTML
**Dotyczy:** Nowa strona `metodyka-en-pl.html` z pełną treścią dokumentu v16

---

## Cel

Udostępnienie pełnej dokumentacji metodologicznej wskaźnika poLCA-EN-PL-2024 (v16) na stronie polca.org.pl w formacie umożliwiającym:
1. Czytelne przeglądanie toku obliczeniowego przez praktykujących LCA/EPD
2. Łatwe aktualizowanie treści przy kolejnych wersjach (v17, v18) bez edycji HTML
3. Przyjmowanie uwag i komentarzy od weryfikatorów przez formularz e-mail

---

## Pliki do utworzenia

```
polca-site/
├── data/
│   └── polca-en-pl-2024.json       ← treść dokumentu v16 (jedyne miejsce danych)
├── metodyka-en-pl.html             ← szablon strony (nie zmienia się między wersjami)
└── js/
    └── metodyka-en-pl.js           ← fetch + render + nawigacja + formularz
```

Żaden z tych plików nie istnieje — wszystkie tworzone od zera.

---

## Plik danych: `data/polca-en-pl-2024.json`

### Schemat najwyższego poziomu

```json
{
  "meta": {
    "version": "v16",
    "code": "poLCA-EN-PL-2024",
    "issued": "2026-04-04",
    "status": "Wersja konsultacyjna — do weryfikacji zewnętrznej",
    "operator": "Multicert Sp. z o.o.",
    "program": "EPD Polska (www.epd.org.pl)"
  },
  "result": {
    "value": 0.599,
    "unit": "kg CO₂e/kWh",
    "year": 2024,
    "year_prev": 2023,
    "value_prev": 0.642,
    "change_pct": -6.7
  },
  "sections": [ ... ]
}
```

### Typy sekcji w `sections[]`

Każda sekcja ma obowiązkowe pola `id`, `title`, `type` i `content` (lub `rows`/`steps` zależnie od typu):

| Typ | Zastosowanie | Kluczowe pola |
|-----|-------------|---------------|
| `text` | Akapit lub lista opisowa | `content: string[]` (każdy string = akapit) |
| `table` | Tabela parametrów / wyników | `headers: string[]`, `rows: string[][]` |
| `equation` | Równanie matematyczne | `formula: string`, `numeric: string`, `note: string` |
| `steps` | Numerowane kroki toku obliczeniowego | `steps: [{num, title, text, equation?: {formula, numeric, note}}]` — krok może opcjonalnie zawierać zagnieżdżone równanie |
| `comparison` | Tabela porównawcza (poLCA vs KOBiZE vs inne) | `headers`, `rows`, `note` |
| `uncertainty` | Analiza niepewności / wrażliwości | `headers`, `rows`, `note` |

### Mapowanie sekcji dokumentu v16 → JSON

| ID sekcji | Tytuł | Typ JSON |
|-----------|-------|----------|
| `streszczenie` | Streszczenie | `text` |
| `uzasadnienie` | Uzasadnienie stosowania wskaźnika | `text` |
| `s1-wprowadzenie` | 1. Wprowadzenie | `text` |
| `s1-1-cel` | 1.1 Cel i zakres | `text` |
| `s1-2-zgodnosc` | 1.2 Zgodność normatywna | `steps` (lista norm) |
| `s1-3-uzasadnienie` | 1.3 Uzasadnienie | `text` |
| `s1-4-luka` | 1.4 Luka metodologiczna | `text` |
| `s1-5-terminologia` | 1.5 Terminologia | `table` |
| `s2-metodologia` | 2. Metodologia | `text` |
| `s2-1-granice` | 2.1 Granice systemu | `text` |
| `s2-2-zgodnosc` | 2.2 Zgodność z ISO 14040/14044 | `table` |
| `s2-3-cutoff` | 2.3 Uzasadnienie pominięć (cut-off) | `text` |
| `s2-4-jednostka` | 2.4 Jednostka funkcjonalna | `text` |
| `s2-5-wskaznik` | 2.5 Wskaźnik wpływu | `text` |
| `s3-zrodla` | 3. Źródła danych | `table` |
| `s3-1-parametry` | 3.1 Parametry wejściowe | `table` |
| `s4-tok` | 4. Tok obliczeniowy | `steps` |
| `s4-1-krok0` | 4.1 Krok 0 — EF_PL,prod | `equation` |
| `s4-2-krok1` | 4.2 Krok 1 — Korekta importowa | `equation` |
| `s4-3-krok2` | 4.3 Krok 2 — EF_oper | `equation` |
| `s4-4-krok3` | 4.4 Krok 3 — WTT_CH₄ | `equation` |
| `s4-5-wynik` | 4.5 Wynik końcowy | `equation` |
| `s4-6-kontrola` | 4.6 Kontrola spójności | `table` |
| `s4-7-model` | 4.7 Struktura modelu obliczeniowego | `table` |
| `s4-8-test` | 4.8 Test bilansu energii | `table` |
| `s5-omowienie` | 5. Omówienie wyników | `text` |
| `s5-1-dekompozycja` | 5.1 Porównanie 2023 vs 2024 | `table` |
| `s5-2-kobize` | 5.2 Porównanie z KOBiZE | `comparison` |
| `s6-jakosc` | 6. Ocena jakości danych | `text` |
| `s6-pedigree` | 6b. Matryca jakości danych | `table` |
| `s6-ograniczenia` | 6a. Ograniczenia metody | `text` |
| `s7-niepewnosc` | 7. Analiza niepewności i wrażliwości | `uncertainty` |
| `s8-trendy` | 8. Analiza trendów | `text` |
| `s9-zastosowanie` | 9. Zastosowanie w EPD/LCA | `text` |
| `za-tok` | Załącznik A — Pełny tok obliczeniowy | `steps` + `equation` |
| `zb-niepewnosc` | Załącznik B — Analiza niepewności | `uncertainty` |
| `zc-split` | Załącznik C — Split GWP-fossil/biogenic/luluc | `table` |
| `zd-ilcd` | Załącznik D — Metadane ILCD | `table` |
| `bibliografia` | Bibliografia | `text` |

---

## Plik HTML: `metodyka-en-pl.html`

### Layout

Identyczny z `metodyka.html`:
- Ten sam header/footer
- Boczne menu kotwicowe (`tool-nav`) — generowane z JSON przez JS
- Główna kolumna z treścią (`#doc-content`) — wypełniana przez JS

### Sekcja hero (statyczna w HTML)

Nad renderowaną treścią — statyczna sekcja z kluczowymi danymi:

```
┌────────────────────────────────────────────────────────┐
│  Dokument metodologiczny                               │
│  poLCA-EN-PL-2024                                      │
│  Wersja v16 · Wersja konsultacyjna                     │
│                                                        │
│  [0,599]  [0,642]  [−6,7%]                             │
│  2024     2023     zmiana r/r                          │
│                                                        │
│  Operator: Multicert Sp. z o.o.                        │
│  Program: EPD Polska                                   │
└────────────────────────────────────────────────────────┘
```

Dane hero ładowane z `meta` i `result` w JSON — nie zakodowane na sztywno w HTML.

### Sekcja komentarzy (statyczna w HTML, na końcu)

Po `#doc-content`, przed stopką:

```html
<section id="komentarze" class="section-gap">
  <h2>Uwagi i komentarze</h2>
  <p>Masz uwagi do metodologii lub obliczeń? Wyślij je do zespołu poLCA.</p>
  <form id="comment-form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
    <!-- pola: imię+org (opcjonalne), email (wymagany), sekcja (select), uwaga (textarea) -->
  </form>
  <div id="comment-success" hidden>Dziękujemy za przesłanie uwagi...</div>
</section>
```

Opcje selecta `sekcja` generowane z JSON (tytuły sekcji) przez JS przy inicjalizacji.

---

## Plik JS: `js/metodyka-en-pl.js`

### Struktura (IIFE, `'use strict'`)

```
(function() {
  'use strict';

  // 1. fetchData()         — pobiera JSON, wywołuje init()
  // 2. init(data)          — renderHero, renderSections, buildNav, initForm
  // 3. renderHero(data)    — wypełnia sekcję hero danymi z meta+result
  // 4. renderSections(data)— iteruje sections[], wywołuje render[Typ]()
  // 5. renderText()        — akapity, opcjonalnie lista
  // 6. renderTable()       — tabela z headers + rows
  // 7. renderEquation()    — blok równania: formula + numeric + note
  // 8. renderSteps()       — numerowane kroki
  // 9. renderComparison()  — tabela comparison (jak renderTable + specjalne stylowanie)
  // 10. renderUncertainty()— tabela uncertainty
  // 11. buildNav(sections) — buduje tool-nav, IntersectionObserver dla aktywnego punktu
  // 12. initForm(sections) — obsługa submit Formspree, populuje select sekcji
})();
```

### Obsługa błędów

- Jeśli `fetch` się nie powiedzie: w `#doc-content` wyświetla komunikat z linkiem do pliku DOCX
- Jeśli sekcja ma nieznany typ: renderuje jako `text` z ostrzeżeniem w konsoli
- Formularz: disable przycisku submit podczas wysyłania, re-enable przy błędzie

### Bez zewnętrznych zależności

Tylko natywne: `fetch`, `IntersectionObserver`, `FormData`. Żadnych bibliotek.

---

## Renderowanie równań

Równania renderowane jako HTML z `IBM Plex Mono`:

```html
<div class="equation-block">
  <div class="equation-formula">poLCA = EF_oper + WTT_CH₄ + WTT_fuels + WTT_OZE</div>
  <div class="equation-numeric">0,599 = 0,528 + 0,057 + 0,008 + 0,006</div>
  <div class="equation-note">Suma składowych; wartości w kg CO₂e/kWh</div>
</div>
```

Klasy CSS dodane do `style.css`. Złożone ułamki/indeksy przez `<sup>` / `<sub>`.

---

## Formularz komentarzy (Formspree)

### Pola

| Pole | Typ | Wymagane | Nazwa w Formspree |
|------|-----|----------|-------------------|
| Imię i organizacja | text | Nie | `name` |
| E-mail | email | Tak | `email` |
| Sekcja której dotyczy | select | Nie | `section` |
| Treść uwagi | textarea | Tak | `message` |

### Flow

1. User wypełnia → klika "Wyślij uwagę"
2. JS: `e.preventDefault()`, disable przycisku, `fetch POST` do Formspree
3. Sukces (HTTP 200): formularz `hidden`, `#comment-success` widoczny
4. Błąd: przycisk re-enable, komunikat błędu inline

### Konfiguracja

Endpoint Formspree zakodowany jako stała na początku `metodyka-en-pl.js`:
```js
var FORMSPREE_ENDPOINT = 'https://formspree.io/f/YOUR_FORM_ID';
```
Użytkownik podmienia `YOUR_FORM_ID` po założeniu konta.

---

## Linkowanie w projekcie

Po wdrożeniu dodać linki do nowej strony w:
- `blog-en-pl-2024.html` — link "Pełna dokumentacja metodologiczna →"
- `datasety.html` — sekcja poLCA-EN-PL
- `metodyka.html` — wzmianka w kontekście danych energetycznych
- `sitemap.xml` — nowy wpis

---

## Nie wchodzi w zakres

- Renderowanie LaTeX/MathML (za ciężkie na statyczną stronę — wystarcza HTML)
- System moderacji komentarzy online (Formspree wysyła na e-mail)
- Historia wersji / archiwum poprzednich wersji wskaźnika
- Wersja angielska strony
