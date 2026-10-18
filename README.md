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

Opcja `--migrate-shell` skryptu `build-portal.py` odświeża wspólną nawigację i stopkę zachowanych starszych stron. Ich treść merytoryczna pozostaje w HTML. Zmianę układu należy obejrzeć w przeglądarce na telefonie i komputerze.

Testy sprawdzają spójność katalogu, lokalne odnośniki, jednostki, podstawowe elementy nawigacji oraz zachowanie opublikowanego pakietu energii 2025. Zmiana opisu portalu nie zmienia wersji ani statusu źródłowego modelu.

## Publikacja

Serwis jest publikowany przez GitHub Pages. Obecne przepływy GitHub Actions automatycznie tworzą i łączą pull request dla gałęzi `claude/**`. Wysłanie takiej gałęzi należy traktować jako publikację: dopiero po kontroli treści, obliczeń i wyglądu.

Warunki wykorzystania danych podano przy zbiorach. Licencja fontu Source Sans 3 znajduje się w `assets/fonts/LICENSE.md`.
