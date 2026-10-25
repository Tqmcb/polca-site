# Portal poLCA

Statyczny katalog danych środowiskowych, instrukcji i kalkulatorów dla Polski.

Treści przewodników: `content/portal-pages.json`. Opisy katalogu: `data/portal-editorial.json`. Skrypt katalogu łączy je ze źródłowymi rekordami; nie przelicza modeli. Kanoniczny eksport katalogu to `data/portal-catalog.json`, a pojedynczych pozycji — `data/portal-records/`.

## Budowanie i sprawdzanie

Python 3.10 lub nowszy, z zależnościami z `requirements-dev.txt`:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/build-catalog.py
python3 scripts/build-portal.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
python3 -m http.server 8768
```

Skrypt `build-portal.py` synchronizuje nawigację i stopkę wszystkich stron. Opcja `--migrate-shell` służy do pierwszego dostosowania starszego dokumentu HTML do interfejsu portalu; zwykła przebudowa jej nie wymaga. Zmianę układu należy obejrzeć w przeglądarce na telefonie i komputerze.

Podział według wyrobu: `data/cpr-families.json` zachowuje urzędowe nazwy 36 rodzin z załącznika VII CPR oraz osobne krótkie etykiety i słowa do wyszukiwania. `data/cpr-mapping.json` rozdziela bezpośrednie przypisanie danych od składników, parametrów i kontekstu. Energia, paliwa, transport oraz kontrolne dane CBAM nie są przypisywane jako dane gotowego wyrobu. `data/product-methods.json` podaje dokumenty metodyczne, źródła, zakresy i statusy. Generowanie stron rodzin i działu c-PCR obsługuje `scripts/cpr_portal.py`.

Testy sprawdzają spójność katalogu, lokalne odnośniki, jednostki, podstawowe elementy nawigacji oraz zachowanie opublikowanego pakietu energii 2025. Zmiana opisu portalu nie zmienia wersji ani statusu źródłowego modelu.

## Publikacja

Serwis jest publikowany przez GitHub Pages. Obecne przepływy GitHub Actions automatycznie tworzą i łączą pull request dla gałęzi `claude/**`. Wysłanie takiej gałęzi należy traktować jako publikację: dopiero po kontroli treści, obliczeń i wyglądu.

Warunki wykorzystania danych podano przy zbiorach. Licencja fontu Source Sans 3 znajduje się w `assets/fonts/LICENSE.md`.

## Konsultacje modelu energii

Strony konsultacji generuje `scripts/consultation_portal.py` z treści w
`content/consultation-energy.json` i pakietu
`data/konsultacje/energia-2025-20261020/`. Projekt konsultacyjny jest oddzielony od
modelu v4 używanego w kalkulatorze. Nie zastępuje go podczas zwykłej przebudowy.

Projekt raportu LCA (oceny cyklu życia) na
`konsultacje/energia-polska-2025-raport-lca.html` generuje
`scripts/report_portal.py`, wywoływany przez `build-portal.py`, z polskiego źródła
`content/raport-lca-energia-2025.md`. Treść raportu zmieniaj wyłącznie w źródle
Markdown. Generator tworzy spis nagłówków drugiego poziomu, przewijane tabele
oraz dokładną kopię źródła i manifest SHA-256 w
`data/konsultacje/raport-lca-2025/`. Wersja raportu 0.2 jest odrębna od wersji
zamrożonego pakietu konsultacyjnego; generator nie zapisuje niczego w tym pakiecie.
Raport znajduje się w zasobach `data/portal-editorial.json`, z których
`build-catalog.py` tworzy indeks wyszukiwania. `build-portal.py` aktualizuje też
mapę witryny. Lista kontroli wyglądu dla prowadzącego: `scripts/render_check_raport.md`.

Formularz pomaga przygotować wiadomość w poczcie użytkownika albo skopiować lub
pobrać jej treść. Strona statyczna nie przyjmuje zgłoszeń i nie nadaje im numerów.
Obsługa otrzymanych wiadomości oraz publikacja odpowiedzi odbywają się redakcyjnie.

Rejestr `uwagi.json` jest aktualizowany osobno od zamrożonego pakietu. Przed
publikacją wpisu usuń dane kontaktowe i informacje poufne z każdego pola, zachowaj
sens uwagi oraz użyj podpisu wskazanego do publikacji; brak podpisu oznacz
„Anonimowo”. Każdy wpis otrzymuje `package_version`, trwałe `id`, `topic`, `comment`, `submitted_at`,
`author_label` i `status`. Pola opcjonalne: `section`, `source`, `proposal`,
`response`, `resolution`, `changed_in_version`. Dozwolone statusy:
`received`, `in_review`, `author_response`, `revision_required`, `resolved`.
Wersja każdego wpisu i rejestru musi odpowiadać pakietowi, którego dotyczą uwagi.
Status `resolved` wymaga treści rozstrzygnięcia. Generator odrzuca wpisy zawierające
adres e-mail, co nie zastępuje redakcyjnej kontroli pozostałych danych. Numer wpisu
nie jest dowodem akceptacji modelu.

Po aktualizacji rejestru przebuduj strony i uruchom testy. Zmiana obliczeń wymaga
nowej, jednoznacznie oznaczonej wersji pakietu oraz nowych sum kontrolnych;
nie nadpisuj opublikowanych wyników pod dotychczasową wersją. `manifest.json`
opisuje pliki pakietu, a archiwum ZIP zawiera ich dokładne kopie. Bieżący rejestr
uwag jest celowo wyłączony z manifestu i archiwum.
