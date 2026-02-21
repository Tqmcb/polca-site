# CLAUDE.md — poLCA Site

Zasady projektu dla Claude Code. Czytaj przed każdą zmianą.

## Projekt

Statyczna strona HTML polskiej bazy danych LCA: **polca.org.pl**
Brak systemu budowania (no npm, no bundler). Czyste pliki HTML/CSS/JS.

## Git i branche

- Branche `claude/*` są automatycznie mergowane do `main` przez GitHub Actions
- Commituj zmiany z opisowymi wiadomościami po polsku lub angielsku
- Push zawsze do `claude/` brancha, nigdy bezpośrednio do `main`

## Obrazy — OBOWIĄZKOWY PROTOKÓŁ

**Zanim dodasz jakikolwiek obraz, musisz go zweryfikować wizualnie.**

Kolejność kroków:
1. Pobierz plik do `/tmp/`
2. Użyj narzędzia `Read` na pobranym pliku — zobaczysz obraz
3. Sprawdź czy obraz faktycznie pasuje do tematu artykułu
4. Dopiero po wizualnej akceptacji skopiuj do `images/` i commituj

Nigdy nie commituj obrazu bez jego wcześniejszego obejrzenia.

### Nazewnictwo obrazów

- Blog: `images/blog-{slug}.jpg` — slug musi odpowiadać nazwie pliku HTML
- Hero/strip: `images/hero-*.jpg`, `images/strip-*.jpg`
- Format: zawsze JPG, lowercase kebab-case

### Źródło obrazów (Pexels)

Pobieranie: `https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?w=1200&h=600&auto=compress&cs=tinysrgb`

Wybieraj obrazy tematycznie odpowiednie — np. artykuł o asfalcie = asfalt, nie las.

## Pliki HTML — konwencje

- Język: `<html lang="pl">`
- Kodowanie: UTF-8
- Nowe artykuły: plik `blog-{slug}.html` + obraz `images/blog-{slug}.jpg`
- Każdy artykuł musi mieć pełne meta tagi: canonical, OpenGraph, Twitter Card, JSON-LD (BlogPosting)
- Data publikacji: format ISO 8601 z timezone PL, np. `"2026-01-20T00:00:00+01:00"`

## CSS

- Plik: `style.css` (v5.0.0)
- Używaj istniejących zmiennych CSS (`--accent-*`, `--ink-*`, `--paper-*`, etc.)
- Nazwy klas: BEM-like, lowercase kebab-case
- Fonty: Inter Tight (nagłówki), Inter (treść), IBM Plex Mono (dane/kod)

## JavaScript

- Katalog: `js/`
- Vanilla JS, bez frameworków
- Pattern: IIFE z `'use strict'`
- Animacje: IntersectionObserver z klasami `.fade-in` / `.visible`

## Treść

- Język witryny: **polski**
- Styl: instytucjonalny, naukowy, rzeczowy
- Nie dodawaj emoji ani potocznych zwrotów
