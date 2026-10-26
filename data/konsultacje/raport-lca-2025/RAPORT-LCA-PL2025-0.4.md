# Ocena cyklu życia energii elektrycznej dostarczonej w Polsce w 2025 r.

**Raport z badania LCA (oceny cyklu życia) — projekt do przeglądu krytycznego**

| | |
|---|---|
| Oceniany model | `PL2025_METHOD_CLOSURE_CANDIDATE` |
| Wersja ocenianego modelu | zamrożenie R3 z 20.10.2026, 151 plików, SHA-256 `6de11084dfd4f59a883cf9256a01588074ee93bc7f410eac3ecfadd889d0b58f` |
| Wersja raportu | projekt 0.4 z 26.10.2026 (decyzje zlecającego A1, A2 i A13; wykaz zmian danych BAFU; warunki przekazania danych zmodyfikowanych) |
| Zlecający badanie | program EPD Polska; operator programu: Multicert Sp. z o.o. |
| Wykonawca badania | Multicert Sp. z o.o. (zespół poLCA); obliczenia i dokumentację wykonano z użyciem narzędzi sztucznej inteligencji (Codex, Claude) pod nadzorem Grzegorza Suwary |
| Status | wydanie publiczne projektu; nie przeszedł przeglądu krytycznego; dane nie zostały przyjęte do programu EPD Polska |

Raport łączy dokumentację etapów prac z 17–20.10.2026. Nie zmienia centralnego wyniku wersji zamrożonej R3; uzupełnia go o obliczenia diagnostyczne i przeliczone warianty wrażliwości z 25.10.2026. Tabele 1–3, 5 i 6 wygenerowano automatycznie z plików wyników. Pełna dokumentacja robocza zawiera dane objęte licencją BAFU; recenzent pobiera bazę BAFU samodzielnie i otrzymuje od wykonawcy kod, wyniki, wykaz zmian danych BAFU i dokumentację roboczą, bez oryginalnych zbiorów BAFU; dane zmodyfikowane przekazuje się na warunkach równoważnych warunkom BAFU (decyzja A13). Wartości liczbowe z publicznie dostępnych raportów dokumentacji BAFU przytoczono z podaniem źródła; zbiorów danych BAFU nie rozpowszechnia się.

Układ raportu odpowiada wymaganiom PN-EN ISO 14044:2009, pkt 5.2, dotyczącym raportu dla strony trzeciej.

---

## 1. Aspekty ogólne

**1.1. Zlecający i wykonawca.** Zlecającym badanie jest program EPD Polska, którego operatorem jest Multicert Sp. z o.o.; wykonawcą jest Multicert Sp. z o.o. (zespół poLCA). Ponieważ zlecający i wykonawca należą do tej samej organizacji, niezależność oceny zapewnia wyłącznie przegląd krytyczny przez eksperta zewnętrznego (rozdział 8).

**1.2. Data raportu.** 26.10.2026 (projekt 0.4).

**1.3. Zgodność z normami.** Badanie przeprowadzono z zamiarem spełnienia wymagań PN-EN ISO 14040:2009 i PN-EN ISO 14044:2009 oraz z użyciem wskaźników i reguł EN 15804:2012+A2:2019/AC:2021 i EN 15941:2024. **Zgodności nie stwierdzono:** o zgodności rozstrzygnie przegląd krytyczny (rozdział 8). Niniejsze zdanie nie jest stwierdzeniem zgodności w rozumieniu PN-EN ISO 14044, pkt 5.2 a) 3).

**1.4. Udział narzędzi sztucznej inteligencji.** Skrypty obliczeniowe napisał i obliczenia wykonał Codex, dokumentację zestawił Claude, a prowadzący sprawdził i skorygował wyniki przed zamrożeniem. Ocenę jakości danych (73 decyzje) Codex wykonał jako ocenę techniczną; nie jest to ocena eksperta.

## 2. Cel badania

**2.1. Powody.** Nie ma oficjalnego krajowego zbioru danych o wpływie energii elektrycznej na środowisko za 2025 r. w układzie 37 wskaźników EN 15804+A2. Wskaźnik Krajowego Ośrodka Bilansowania i Zarządzania Emisjami (KOBiZE) obejmuje emisje CO₂ przypisane produkcji energii za 2024 r. i nie jest profilem wskaźników wpływu w cyklu życia. W etapie z 20.10.2026 zamknięto trzy kwestie metodyczne wskazane w projekcie zasad EPD Polska: wspólną alokację energii elektrycznej i ciepła, jawny rachunek węgla biogenicznego oraz rozstrzygnięcie istotnych danych zastępczych.

**2.2. Zamierzone zastosowanie.** Wynik ma służyć jako dane tła dla 1 kWh energii elektrycznej w ocenach cyklu życia i deklaracjach środowiskowych wyrobów (EPD) w procesach, w których stosuje się krajowy miks zużycia, w szczególności w etapach A4–C4 i D pozostających poza bezpośrednią kontrolą właściciela deklaracji (EN 15941:2024, E.2.6). Wynik nie jest:
- miksem rezydualnym ani produktem konkretnego sprzedawcy energii;
- profilem określonego poziomu napięcia;
- indywidualnym dowodem niskiej emisji jakiegokolwiek producenta;
- zamiennikiem danych dostawcy energii w procesach pod kontrolą producenta (EN 15941:2024, E.2.1–E.2.2).

Specyfikację zastosowania i projekt decyzji operatora dla tej wersji modelu przygotowano jako niepodpisany projekt (dokument wewnętrzny operatora).

**2.3. Odbiorcy.** Operator programu EPD Polska (decyzja o przyjęciu danych), niezależny recenzent krytyczny, autorzy LCA i EPD korzystający z danych tła oraz uczestnicy konsultacji publicznych na polca.org.pl.

**2.4. Stwierdzenia porównawcze.** Zlecający potwierdził 26.10.2026, że badanie nie jest przeznaczone do wykorzystania w stwierdzeniach porównawczych przewidzianych do udostępnienia publicznego. W razie zmiany przeznaczenia wymagany byłby przegląd krytyczny przeprowadzany przez zespół stron zainteresowanych (PN-EN ISO 14044, 6.3) oraz dodatkowe elementy raportu (5.3).

## 3. Zakres badania

### 3.1. Funkcja i jednostka odniesienia

**Funkcja:** dostarczenie energii elektrycznej do zużycia końcowego w Polsce w 2025 r. w postaci rocznego fizycznego miksu zużycia.

**Jednostka odniesienia:** 1 kWh energii elektrycznej dostępnej do zużycia końcowego w Polsce (AFC, ang. *available for final consumption*, według bilansu Eurostatu `nrg_cb_e`), rok 2025, wartość dla całego kraju bez rozróżnienia poziomów napięcia. Jednostka odniesienia pełni rolę jednostki funkcjonalnej w rozumieniu PN-EN ISO 14044 i jest spójna z celem badania: wynik ma służyć jako dane tła na 1 kWh energii elektrycznej.

Mianownik (152 807,888 GWh) wyznaczono z bilansu:

produkcja netto ze wszystkich źródeł + import − eksport − pobór elektrowni pompowych − pobór akumulatorów − inne przetwarzanie − straty sieciowe = AFC.

Straty sieciowe (9077 GWh) uwzględniono w mianowniku; nie dolicza się ich ponownie w usługach infrastruktury sieciowej. Zużycie końcowe jest mniejsze od AFC o różnicę statystyczną wynoszącą 0,038 GWh.

Wynik pomiaru efektywności (PN-EN ISO 14044, 5.2 c) 2) iii)) nie ma zastosowania: energia elektryczna jest jednorodnym nośnikiem, a parametry jakości dostawy (napięcie, ciągłość) pozostają poza zakresem badania. Dotychczasowe dokumenty używają też określenia „energia dostarczona odbiorcy końcowemu”; w niniejszym raporcie przyjęto definicję AFC.

### 3.2. Granice systemu

**Włączono:**
- wytwarzanie krajowe w 20 rozłącznych kategoriach (Eurostat `nrg_ind_pehcf`, `nrg_ind_pehnf`, 2025): produkcja brutto 174 472,611 GWh, netto 162 454,280 GWh; potrzeby własne 12 018,331 GWh; produkcję elektrowni pompowych odjęto od produkcji energii wodnej;
- import 15 924,133 GWh według kierunku fizycznego przepływu (Polskie Sieci Elektroenergetyczne, PSE, raport 2025, tab. 7.1): Niemcy, Szwecja, Czechy, Litwa, Słowacja (97,9875% importu, miksy ważone danymi Eurostatu za 2025 r.) i Ukraina (2,0125%, profil historyczny);
- eksport 14 972,264 GWh, odjęty proporcjonalnie od krajowego wytwarzania netto bez magazynowania (współczynnik retencji krajowej 0,9072284935);
- magazynowanie w elektrowniach szczytowo-pompowych i akumulatorach;
- usługi infrastruktury sieciowej ważone udziałami poziomów napięcia w 2025 r. (wysokie 17,769560%, średnie 41,414680%, niskie 40,815760%; oszacowanie na podstawie danych czterech operatorów obejmujących 86,41% bazy);
- pełne łańcuchy dostaw paliw (wydobycie, przeróbka, transport, infrastruktura, odpady), woda, materiały, utrzymanie i koniec życia infrastruktury w tym samym grafie procesów;
- paliwa pomocnicze elektrowni na węglu brunatnym (olej ciężki i gaz płynny LPG jako dostawy, bez ponownego spalania).

**Pominięto lub wyłączono z zakresu:**
- miks rezydualny, gwarancje pochodzenia, produkty sprzedawców i profile napięciowe (odrębne produkty danych);
- korekty grafu tła wymuszające bilans zerowy węgla biogenicznego i nowe pochłanianie atmosferyczne;
- współczynniki charakteryzowania dla tlenku węgla i olejów biogenicznych (brak w zamrożonym zestawie; wartość `null`, zob. 5.3);
- godzinowe śledzenie przepływów importu i eksportu (alokację wykonano w ujęciu rocznym).

**Wytwarzanie krajowe — kwantyfikacja.** Tabela 5 podaje 20 kategorii wytwarzania, ich produkcję brutto i netto oraz procesy tła, którymi są odwzorowane (odwzorowanie przejęte z modelu 2024). Dla 2025 r. nie ma danych obserwowanych o produkcji netto według technologii: oszacowano ją na podstawie względnych wskaźników potrzeb własnych z 2024 r. i wspólnego dla źródeł cieplnych mnożnika 1,1822212828, który uzgadnia sumę z danymi obserwowanymi za 2025 r.; dla źródeł niepalnych zachowano stosunki netto/brutto z 2024 r. Kategoria X9900 (ciepło z procesów chemicznych, 75,047 GWh) nie ma przypisanego procesu: zgodnie z przejętą regułą odzyskane ciepło reakcji chemicznych ma zerowe obciążenie z etapów poprzedzających i uwzględnia się wyłącznie zawartą w nim energię. Energia z odpadów (W6100, W6210, W6220; proces BAFU 419687) ma zerowe obciążenie z etapów poprzedzających: 100% obciążeń spalarni przypisano usłudze zagospodarowania odpadów, a 0% produkcji energii. Reguła pochodzi ze źródłowego zbioru danych (Doka 2009) i odpowiada zasadzie „zanieczyszczający płaci” z PN-EN 15804+A2, pkt 6.3.5.1 i 6.3.5.5, przy założeniu, że odpady trafiają do spalarni przed osiągnięciem stanu końca odpadu; analizy stanu końca odpadu dla tych kategorii nie wykonano, więc jest to interpretacja wykonawcy. Dla X9900 pakiet nie zawiera odrębnego uzasadnienia poza przyjęciem analogicznej zasady. Zerowy wynik nie oznacza braku emisji ze spalarni: przypisanie energii elektrycznej całego kopalnego CO₂ ze spalania odpadów zwiększyłoby GWP-total orientacyjnie o 1,5% (przy alokacji energetycznej między energię elektryczną a ciepło o 0,5%; obliczenie diagnostyczne, załącznik D). Odzyskaną energię ujęto jednokrotnie, jako właściwość energetyczną (PENRE i PENRT dla W6100, W6220 i X9900; PERE i PERT dla W6210). Miksy importu zachowują podprocesy dalszego importu i technologie z lat 2021–2023. Dane o akumulatorach za 2025 r. są niespójne (oddanie 3,178 GWh wobec ładowania 1,861 GWh) i tak je oznaczono; w wersji v2 obliczono wariant ze sprawnością 85%.

**Tabela 5. Kategorie wytwarzania krajowego 2025** (produkcja w GWh z dokładnością do 0,001 GWh; udział netto na 1 kWh dostarczoną po odjęciu eksportu, tj. netto kategorii × 0,9072284935 / 152 807,888 GWh)

| Kategoria | Opis (Eurostat) | Brutto, GWh | Netto, GWh | Udział netto na 1 kWh dostarczoną | Procesy tła (numer) |
|---|---|---:|---:|---:|---|
| C0121 | Coking coal | 45,000 | 42,934 | 2,549·10⁻⁴ | 535534 |
| C0129 | Other bituminous coal | 55 377,565 | 49 943,718 | 0,2965 | 535534 |
| C0220 | Lignite | 33 267,563 | 29 767,588 | 0,1767 | 398923 |
| C0350 | Coke oven gas | 1 264,040 | 1 179,236 | 0,007001 | 608517 |
| C0371 | Blast furnace gas | 350,000 | 313,178 | 0,001859 | 379264 |
| C0379 | Other recovered gases | 12,700 | 11,552 | 6,859·10⁻⁵ | 301831 |
| G3000 | Natural gas | 25 019,950 | 23 253,443 | 0,1381 | 302241 |
| O4610 | Refinery gas | 60,000 | 57,245 | 3,399·10⁻⁴ | 301831 |
| O4630 | Liquefied petroleum gases | 0,500 | 0,477 | 2,832·10⁻⁶ | 302241 |
| O4671XR5220B | Gas oil and diesel oil | 147,582 | 133,720 | 7,939·10⁻⁴ | 597488 |
| O4680 | Fuel oil | 2 098,708 | 1 971,986 | 0,01171 | 496531 |
| RA100 | Hydro | 1 599,090 | 1 584,764 | 0,009409 | 270757, 136439 |
| RA300 | Wind | 24 386,294 | 24 005,073 | 0,1425 | 598753 |
| RA420 | Solar photovoltaic | 20 509,596 | 20 509,596 | 0,1218 | 614372 |
| R5110-5150_W6000RI | Solid biofuels | 6 551,130 | 6 105,925 | 0,03625 | 477818 |
| R5300 | Biogases | 1 615,111 | 1 484,918 | 0,008816 | 442004 |
| W6100 | Industrial waste (non-renewable) | 78,292 | 73,635 | 4,372·10⁻⁴ | 419687 |
| W6210 | Renewable municipal waste | 219,660 | 204,092 | 0,001212 | 419687 |
| W6220 | Non-renewable municipal waste | 720,400 | 670,478 | 0,003981 | 419687 |
| X9900 | Other fuels n.e.c. - heat from chemical sources | 75,047 | 75,047 | 4,456·10⁻⁴ | brak (obciążenie zerowe) |

Suma udziałów netto wytwarzania krajowego na 1 kWh dostarczoną: 0,958173 (po odjęciu eksportu, retencja krajowa 0,9072284935; bez importu i magazynów).

**Założenia o produkcji energii elektrycznej** (PN-EN ISO 14044, 5.2 c) 3) iii)): fizyczny miks krajowy i import według przepływu fizycznego, bez gwarancji pochodzenia; struktura krajowa, import i straty pozostały niezmienione od wersji v3. Energię elektryczną zużywaną w procesach tła odwzorowują procesy bazy BAFU:2026. Pobór energii elektrycznej przez procesy inne niż wytwarzanie i sieć wynosi 0,048 kWh na 1 kWh dostarczoną (2,05% GWP-total); 80% tego poboru odwzorowuje zagregowany miks Europejskiej Sieci Operatorów Systemów Przesyłowych Energii Elektrycznej (ENTSO-E) z 2023 r. Dotyczy to także polskich kopalń: zaktualizowano ilość zużywanej przez nie energii elektrycznej, ale nie zmieniono dostawcy. Krajowy miks 2025 zastępuje wyłącznie jednostkę dostarczoną; procesy tła zasilane polską siecią korzystają z miksu PL z bazy BAFU (2023 r.; pobór około 0,000110 kWh na 1 kWh dostarczoną). Zastąpienie energii elektrycznej kopalń miksem krajowym zwiększyłoby GWP-total orientacyjnie o 0,8% (obliczenie diagnostyczne); decyzji w tej sprawie nie podjęto, a przy zamykaniu takiej pętli należy uniknąć podwójnego naliczenia (załącznik D).

### 3.3. Kryteria wyłączenia (odcięcia)

W pierwszym planie nie stosowano masowych, energetycznych ani środowiskowych kryteriów wyłączenia. Obliczenia obejmują pełny graf 4222 aktywnych procesów, bez obcinania. Brakujących danych nie zastępuje się zerami, lecz oznacza się je i opisuje. Dla danych tła nie zadeklarowano jednolitych kryteriów wyłączenia przepływów: metadane procesów BAFU:2026 (format ecoSpold v1) nie zawierają pól dotyczących kryteriów wyłączenia, kompletności ani sposobu przetwarzania danych, a progi podają tylko niektóre raporty dokumentacji bazy (np. Kröhnert 2025, s. 21: 0,1% masy i 1% energii dla części turbin wiatrowych; Oberschelp 2025, s. 13: pomijanie małych udziałów przez zaokrąglenie). Słowo „cut-off” w 269 z 11 947 procesów oznacza odcięcie recyklingu lub alokację produktów ubocznych. Wydawca deklaruje zgodność z wytycznymi jakości danych BAFU DQRv2:2023; tekst wytycznych nie był dostępny. Wyszukiwanie słownikowe w opisach procesów (wyrażenia m.in. „not included”, „unknown”, „not available”, „negligible”) wskazało 832 z 4222 procesów aktywnych w grafie; nie jest to liczba indywidualnie potwierdzonych pominięć. Rozpoznane pominięcia obejmują m.in. brak rekultywacji kopalń, brak energii z odzyskanego metanu (według źródła do 2% energii węgla) i brak ciepła w kopalniach węgla brunatnego. Ilościowej oceny wpływu tych pominięć nie wykonano; zgodności z kryteriami PN-EN 15804+A2, pkt 6.3.6 (1% energii pierwotnej i 1% masy na proces, 5% na moduł) nie wykazano (załącznik D).

Próg 80% bezwzględnych wkładów (EN 15941:2024, 7.1.2) zastosowano wyłącznie do wyboru jednostek objętych oceną jakości danych (rozdział 6), nie do usuwania przepływów.

### 3.4. Baza danych tła

Dane tła pochodzą z zamrożonego modelu 2024 v4, zbudowanego na bazie „Life Cycle Inventory database of the Swiss Federal Administration, BAFU:2026”, wydanie BAFU-2026 v1 (wydawca: szwajcarski Federalny Urząd Środowiska, BAFU/FOEN). Archiwa pobrano 27.09.2026 z serwisu openLCA Nexus po akceptacji warunków użytkowania; graf technosfery pochodzi z archiwum ecoSpold v1 (SHA-256 `ebaab56717a6227b5eb271fcb4c86fb9db206115eb937fb0ec0b10d7accf26c7`; 11 947 procesów, 420 063 wymiany), a plik openLCA w poprawce v1.1 posłużył do uzgodnienia ilości i jednostek. Warunki użytkowania BAFU z 23.06.2026 dopuszczają obliczenia własne na danych, zakazują rozpowszechniania danych jako takich i wymagają cytowania „BAFU:2026”; zmodyfikowane dane można udostępniać osobom trzecim tylko z osobną dokumentacją zmian i na zasadach równoważnych (pkt 2.1–2.3, 3.1–3.5). Pełnego grafu nie udostępnia się publicznie; publikowane są wyniki zbiorcze oraz pojedyncze parametry przytoczone z podaniem źródła. **Decyzja z 26.10.2026 (A13):** poprawki modelu wprowadzone do zbiorów BAFU traktuje się ostrożnie jako dane zmodyfikowane w rozumieniu pkt 3 warunków; ich wykaz (zbiory, charakter i cel zmian) sporządzono w osobnym dokumencie (załącznik K): 55 zmian samych zbiorów (współczynniki macierzy technosfery, wymiany elementarne, wpisy rachunku węgla biogenicznego) oraz 46 korekt emisji pierwszych procesów spalania, ujętych ostrożnie również jako dane zmodyfikowane; obejmuje to m.in. przejętą z modelu 2024 korektę CO₂ biogenicznego w procesie spalania zrębków 617593. Recenzent pobiera bazę BAFU-2026 v1 samodzielnie z serwisu openLCA Nexus i przyjmuje jej warunki; wykonawca przekazuje mu kod, wyniki, wykaz zmian i dokumentację roboczą bez oryginalnych zbiorów BAFU i ich dosłownych wyciągów. Dane zmodyfikowane przekazuje się na warunkach zasadniczo równoważnych warunkom BAFU, bez dodatkowych ograniczeń praw (pkt 3.4 i 5.1); umowa o poufności obejmuje wyłącznie własną dokumentację roboczą wykonawcy. Szczegóły i sumy kontrolne: załącznik C. Część procesów w bazach BAFU i ecoinvent ma wspólne pochodzenie, co ogranicza niezależność porównań z ecoinvent.

### 3.5. Metoda obliczeń i oprogramowanie

Obliczenia wykonano własnymi skryptami w języku Python 3.13.16 (NumPy 2.5.3, SciPy 1.18.1). Model ma postać macierzową: x = M⁻¹y, wyniki = C·x + d, gdzie M — macierz technosfery aktywnych procesów, y — wektor zapotrzebowania, C — macierz współczynników charakteryzowania, d — wektor bezpośrednich korekt. Rozwiązanie główne: rozkład rzadki `splu` (`MMD_AT_PLUS_A`, 3 iteracje poprawki reszty); rozwiązanie kontrolne: `splu` (`COLAMD`, 5 iteracji). Reszta końcowa ‖Mx − y‖∞ wynosi 2,2·10⁻¹⁶–4,4·10⁻¹⁶.

Wyniki każdego przebiegu zapisuje się w nowym katalogu wraz z manifestem sum SHA-256 wejść i wyjść; skrypt nie nadpisuje istniejących wyników. Wynik końcowy uzyskano w przebiegach wykonanych w kolejności: `allocation-002` (wspólna alokacja) → `energy-001` (zmiana grafu dostaw biogazu) → `integrated-energy-001` (rachunek węgla biogenicznego) → `integrated-energy-002` (regionalizacja wody kopalnianej; wynik końcowy).

### 3.6. Rok i status danych

Rok 2025 dotyczy modelowanego miksu, krajowych aktywności i dostawy. Nie oznacza to, że wszystkie 37 wskaźników oparto na pomiarach z 2025 r.: część danych tła pochodzi z lat 2000–2024 i zachowuje swoje daty oraz oceny jakości. Wszystkie wykorzystane dane roczne Eurostatu za 2025 r. mają oznaczenie `p` (dane wstępne) i mogą zostać zrewidowane. Źródła krajowe i lata ich danych zawiera tabela 4.

## 4. Analiza zbioru wejść i wyjść (LCI)

### 4.1. Procedury zbierania danych i źródła

Dane krajowe pobrano z publicznych źródeł pierwotnych i zarchiwizowano lokalnie wraz z sumami SHA-256.

**Tabela 4. Główne źródła danych krajowych**

| Źródło | Rok danych | Zastosowanie |
|---|---|---|
| Eurostat `nrg_cb_e`, `nrg_ind_pehcf`, `nrg_ind_pehnf` | 2025 (wstępne), 2024 | bilans energii, wytwarzanie, import, eksport, straty |
| PSE, raport roczny z funkcjonowania krajowego systemu elektroenergetycznego (KSE) za 2025 r., tab. 7.1 | 2025 | kraje fizycznego importu |
| Ministerstwo Energii, sprawozdanie za 2025 r. | 2025 | podaż gazu (254 170 GWh) |
| Eurostat (bilans węgla), Comext DS-045409 | 2025 | pula i pochodzenie węgla |
| Agencja Rynku Energii (ARE), EMITOR 2025, wersja ogólna (publ. 2.10.2026) | 2025 | paliwo, energia, CO₂ i emisje do powietrza grupy elektrowni na węglu brunatnym |
| ARE, Sytuacja energetyczna w Polsce, IV kw. 2025 | 2025 | wartość opałowa węgla kamiennego (21,525948 MJ/kg) |
| Komisja Europejska, zweryfikowane emisje w systemie handlu uprawnieniami do emisji (EU ETS) 2025; raporty PGE, TAURON, ENEA za 2025 r. | 2024–2025 | trend intensywności CO₂ węgla kamiennego |
| KOBiZE, wskaźniki emisyjności (publ. 2025) | 2024 | kalibracja SO₂, NOₓ, CO i pyłu z węgla kamiennego |
| NID 2026, krajowy raport inwentaryzacyjny | do 2024 | zależność zawartości węgla od wartości opałowej, utlenienie 0,98 |
| CRT 2024 (wspólne tabele sprawozdawcze); Wyższy Urząd Górniczy (WUG), sprawozdania za 2024 i 2025 r.; Państwowy Instytut Geologiczny – Państwowy Instytut Badawczy (PIG-PIB) | 2024–2025 | metan kopalń, nadkład |
| Operatorzy systemów dystrybucyjnych (Tauron, Enea, Energa, PGE Dystrybucja) | 2024–2025 | udziały napięć |

### 4.2. Opis procesów jednostkowych pierwszego planu

**Węgiel kamienny.** Bazę 2024 wyznaczono z krajowego bilansu węgla energetycznego (kategoria C0129; elektrownie i elektrociepłownie zawodowe oraz autoproducenci, bez samodzielnych ciepłowni): 581 524,423 TJ paliwa, 27 195,058 tys. t węgla, 57 136,056 GWh brutto. Intensywność emisji CO₂ w 2024 r. przy q = 0,35 wynosi 0,891308 kg CO₂/kWh netto. Wskaźnik zmiany 2025/2024, wyznaczony z panelu PGE, TAURON i Elektrowni Kozienice (grupa ENEA) (65,9536% krajowej produkcji netto), wynosi 0,97797. Parametry 2025 na 1 kWh netto: 0,871673 kg CO₂, 9,175738 MJ paliwa, 0,426264 kg węgla. Emisje SO₂, NOₓ i CO oparto na kalibracji KOBiZE 2024 skorygowanej trendem TAURON 2024–2025 (pokrycie 17,72% produkcji z węgla kamiennego). Dla pyłu całkowitego zachowano kalibrację KOBiZE 2024 bez korekty trendem (mnożnik 1). Nowe emisje do powietrza z ARE EMITOR 2025 dotyczą wyłącznie węgla brunatnego.

**Węgiel brunatny.** Przyjęto łączne roczne sumy dla grupy elektrowni na węglu brunatnym z ARE EMITOR 2025 (z Pątnowem II): 29 926 467 MWh energii elektrycznej netto i 2770,235 TJ ciepła netto; paliwo 37 605 500 t; CO₂ 34 561 935 t; emisje do powietrza SO₂, NOₓ, CO, CH₄, pyłu, Cd, Pb i Hg. Po alokacji (q = 0,35) intensywność wynosi około 1,1446 kg CO₂/kWh netto (wartość wyliczona z rejestru alokacji). Grupa ARE jest przybliżeniem kategorii Eurostatu C0220; produkcja netto ARE jest wyższa od oszacowania Eurostatu o 0,534% (miks przyjęto z Eurostatu, paliwo i emisje — z ARE). Różnica wynika z produkcji brutto (dane ARE wyższe o 0,573%), a nie ze wskaźnika potrzeb własnych; dane spółek (PGE i ZE PAK, łącznie 29,92 TWh netto) są zbliżone do ARE. Przyczyny różnicy nie ustalono: najlepiej zgodna liczbowo hipoteza (energia z paliw pomocniczych w grupie ARE) nie wyjaśnia danych za 2024 r. Uproszczony rachunek liniowy, bez pełnych łańcuchów dostaw, daje +0,03% (z wyrównaniem bilansu kosztem węgla kamiennego) albo +0,17% GWP-total (bez wyrównania bilansu); nie jest to przedział niepewności; wpływ jest jednak znacznie mniejszy niż wpływ wyboru q. Proponowaną procedurę uzgodnienia zawiera załącznik D.

**Pozostałe dane krajowe:**
- metan kopalń węgla kamiennego: 0,008240 kg CH₄/kg (CRT 2024 przeskalowane danymi WUG 2025);
- nadkład węgla brunatnego: 5,722 kg/kg (WUG i PIG-PIB, dane 2024 jako zamiennik 2025), z erratą emisji fosforanów (Doka);
- import węgla: udział węgla krajowego w puli 83,28%; pochodzenie importu według Comext (Kazachstan 68,99%, Kolumbia 27,21%);
- gaz: przyjęto strukturę dostaw dla całej gospodarki, a nie strukturę zakupów elektrowni;
- wzbogacanie uranu: procesy dyfuzyjne zastąpiono wirówkowymi o tym samym stopniu wzbogacenia (dyfuzja zakończona w 2012–2013); nie jest to potwierdzona struktura zakupów 2025;
- chlor: struktura technologii membranowej i przeponowej bez technologii rtęciowej (Euro Chlor 2025).

**Bezpośrednia emisja CO₂ na 1 kWh dostarczoną:** węgiel kamienny 0,258689 kg (C0129 0,258467, C0121 0,000222), węgiel brunatny 0,202286 kg.

### 4.3. Procedury obliczeniowe

Wszystkie zmiany zapotrzebowania i bezpośrednich korekt wprowadza się przed jednym, wspólnym rozwiązaniem grafu; różnic między wcześniejszymi profilami nie sumuje się. Zmiana grafu dostaw biogazu (wariant `source_energy`) dotyczy dwóch krawędzi: silnika biogazowego wytwarzającego energię elektryczną i procesu wytwarzania ciepła z biogazu. Objętość biogazu przeliczono tak, aby zachować energię paliwa przy spójnej wartości opałowej mieszaniny (wartości wymian zbiorów BAFU podano w dokumentacji dla recenzenta) i wymaga ponownego rozwiązania całego grafu. Rejestr węgla biogenicznego obejmuje 1068 zdarzeń źródłowych w 680 procesach; po dodaniu pozycji rachunkowych (transfery gazu, rozliczenie drewna) rejestr procesów liczy 683 pozycje.

### 4.4. Walidacja danych i postępowanie z brakującymi danymi

Ocenę jakości opisuje rozdział 6. Zasady postępowania z brakami:
- brak pełnych danych nie blokuje obliczeń; dane zastępcze są jawne, z podaniem źródła, zakresu i wpływu;
- brakujących wartości nie zastępuje się zerami (np. współczynniki dla CO i olejów biogenicznych pozostają `null`);
- zerowe wyniki PERM, PENRM, NRSF, CRU i MER wynikają z przejętych konwencji dotyczących granic systemu, a nie z wykazania braku przepływów.

Kontrole numeryczne wykazały zgodność niezależnie obliczonych sum 37 wskaźników i jednostek fizycznych z dokładnością do 8,9·10⁻¹⁶ oraz niezmienność 194 plików poprzedniej wersji v4; status weryfikacji końcowej: PASS. Kontrola obejmuje arytmetykę, kompletność zapisu oceny i niezmienność źródeł; nie obejmuje zgodności z normami.

### 4.5. Analiza wrażliwości w celu skorygowania granic systemu

Obliczono następujące warianty i analizy diagnostyczne:
- zmiana podstawy objętości biogazu (`source_volume` zamiast `source_energy`): GWP-total 0,647347 zamiast 0,647275 kg CO₂ równ./kWh;
- ilość tarcicy w kopalniach ×1/3 i ×3 (tylko pozycja końcowa CO₂): od 0,000557 do 0,005018 kg CO₂/kWh zamiast 0,001672;
- zwrot wody kopalnianej od 0% do 100%: WDP od 0,02131 do 0,01686 m³ równ. światowego/kWh;
- usunięcie wkładu robót strzałowych (diagnostyka udziału).

Wszystkie 14 wariantów obliczonych wcześniej dla wersji v4 oraz trzy warianty infrastruktury sieci przeliczono metodą ocenianego modelu (q = 0,35 dla obu rodzajów węgla, `source_energy`, jawny rachunek węgla biogenicznego, regionalizacja wody kopalnianej), każdy przez pełne rozwiązanie grafu. Wyniki zawiera tabela 6. Wariantu przydziału eksportu do wspólnej puli krajowej i importowej nie obliczono: wymagałby nowego adaptera wag, którego nie ma w kodzie modelu.

**Tabela 6. Warianty wrażliwości przeliczone dla ocenianego modelu** (GWP-total w kg CO₂ równ./kWh; zmiany względem wyniku centralnego)

| Wariant | GWP-total | Zmiana GWP-total | Trzy wskaźniki o największej zmianie względnej |
|---|---:|---:|---|
| `uranium_historical` | 0,6473 | +0,01004% | ODP +11,79%; IRP +2,295%; RWD +1,515% |
| `oil_light` | 0,6473 | +0,003576% | ODP +0,03096%; POCP +0,01699%; PM +0,01285% |
| `gas_natural` | 0,6473 | −0,0000001632% | ODP +0,000002608%; POCP −0,000002167%; RSF −0,000001146% |
| `hardcoal_v3` | 0,6575 | +1,574% | GWP-fossil +1,579%; GWP-total +1,574%; ADP-fossil +1,372% |
| `metals_historical` | 0,6473 | +0% | HTP-nc +15,67%; HTP-c +3,112%; ETP-fw +0,03961% |
| `methane_historical` | 0,6478 | +0,07431% | GWP-fossil +0,07448%; GWP-total +0,07431%; POCP +0,02138% |
| `dust_historical` | 0,6473 | +0% | PM −0,06913%; GWP-total +0%; GWP-fossil +0% |
| `air_main_only` | 0,6478 | +0,07431% | HTP-nc +15,68%; HTP-c +3,112%; GWP-fossil +0,07448% |
| `heat_qGG` | 0,6473 | −0,0002812% | GWP-fossil −0,0002821%; GWP-total −0,0002812%; ADP-fossil −0,0002801% |
| `heat_qZZ` | 0,6473 | +0,004949% | GWP-fossil +0,004965%; GWP-total +0,004949%; ADP-fossil +0,004929% |
| `heat_qZG` | 0,6470 | −0,03575% | GWP-fossil −0,03587%; GWP-total −0,03575%; ADP-fossil −0,03561% |
| `heat_qGZ` | 0,6475 | +0,04054% | GWP-fossil +0,04067%; GWP-total +0,04054%; ADP-fossil +0,04038% |
| `heat_2021_residual` | 0,6473 | −0,000003460% | GWP-fossil −0,000003471%; GWP-total −0,000003460%; ADP-fossil −0,000003446% |
| `heat_ratio_2022` | 0,6473 | +0,001844% | GWP-fossil +0,001850%; GWP-total +0,001844%; ADP-fossil +0,001837% |
| `export_allocated_to_domestic_and_import_pool` | nie obliczono | — | brak w kodzie modelu adaptera wag wspólnej puli krajowej i importowej (zob. 4.5) |
| `grid_infrastructure_WN` | 0,6433 | −0,6082% | ADP-mm −47,05%; EEE −20,92%; EET −20,61% |
| `grid_infrastructure_SN` | 0,6468 | −0,07863% | ADP-mm −38,97%; EET −14,60%; HWD −14,45% |
| `grid_infrastructure_NN` | 0,6495 | +0,3446% | ADP-mm +60,02%; EET +23,79%; HWD +23,16% |

Warianty infrastruktury sieci zmieniają wyłącznie usługi infrastruktury przy niezmienionych stratach i miksie; nie są profilami dostawy na danym poziomie napięcia.

### 4.6. Alokacja

**Kogeneracja.** Hierarchię postępowania według PN-EN ISO 14044, 4.3.4.2, zastosowano w następujący sposób:
- unikanie alokacji przez podział procesu: zastosowano tam, gdzie pozwalają na to dane, np. dla jednostek wytwarzających wyłącznie energię elektryczną w bazie węgla kamiennego 2024 (Q = 0, cały strumień przypisany energii elektrycznej);
- rozszerzenie systemu o wspólną funkcję wytwarzania energii elektrycznej i ciepła: odrzucono, ponieważ zmieniłoby jednostkę odniesienia;
- rozszerzenie systemu z uwzględnieniem unikniętej produkcji ciepła: odrzucono, ponieważ nie ma dowodu, które źródło ciepła zostałoby zastąpione;
- relacja fizyczna: wybrano klucz jakości energii aE = E/(E + q·Q), z q = 0,35 dla nowych strumieni węgla kamiennego i brunatnego; podziału dokonano przed agregacją;
- klucz ekonomiczny (kolejny poziom hierarchii): nie zastosowano, ponieważ brak jednolitego zbioru przychodów z obu produktów dla tej samej granicy i tego samego roku.

Wartość q = 0,35 przyjęto z pracy Itten i in. 2023 (rozdz. 3.4, s. 39–40) jako przybliżenie jakości ciepła pośrednie między ciepłem grzewczym a parą przemysłową. Nie jest to wartość zmierzona dla Polski w 2025 r. ani wartość nakazana normą; EN 15804+A2, 6.4.3.2, nie nakazuje metody egzergetycznej. Zebrane dane nie pozwalają potwierdzić jednej wartości q dla całej Polski. Procedurę zastąpienia q danymi zakładowymi (temperatury nośnika, parametry pary) opisano w karcie metody alokacji, stanowiącej część dokumentacji roboczej.

**Jednolitość stosowania.** Ten sam klucz zastosowano do obu nowo obliczanych grup paliw. Wcześniejsza wersja v4 stosowała alokację hybrydową (węgiel brunatny według energii, q = 1), którą zastąpiono. Historycznych procesów tła nie podzielono ponownie, ponieważ brak ich inwentarzy sprzed alokacji. Aktywność pierwszego spalania, czyli ilość paliwa na 1 kWh w historycznym procesie spalania, od której zależą pozostałe wymiany tego procesu, pozostaje na poziomie 9,69 MJ/kWh (węgiel kamienny) i 10,19 MJ/kWh (węgiel brunatny); nieaktualizowane emisje, woda, popioły, materiały i infrastruktura zachowują dotychczasowe ilości na kWh. Rzeczywiste zużycie węgla kamiennego jako paliwa wynosi 9,175738 MJ/kWh; wartość 9,69 MJ/kWh służy wyłącznie do skalowania pozostałych wymian historycznego procesu. Ujednolicenie alokacji obejmuje zatem nowe strumienie, a nie całe tło.

**Pozostałe alokacje.** Eksport i import alokowano proporcjonalnie, w ujęciu rocznym. W rachunku biogazu transfer węgla przypisano funkcji dostawy gazu po alokacji źródłowej; pofermentu nie doliczono ponownie. W procesach tła zachowano alokacje przyjęte w bazie źródłowej.

## 5. Ocena wpływu cyklu życia (LCIA)

### 5.1. Metoda, kategorie i wyniki

Wyniki podano dla 37 wskaźników EN 15804:2012+A2:2019/AC:2021. Dla wskaźników wpływu (19 pierwszych w tabeli 1) zastosowano współczynniki charakteryzowania z pakietu Wspólnego Centrum Badawczego Komisji Europejskiej (JRC) „EN_15804” opartego na EF 3.1. Pakiet zawiera m.in.:
- metody dla kategorii zmiana klimatu (`lciamethods/a7ea142a-9749-11ed-a8fc-0242ac120002.xml` i `a7ea186c-9749-11ed-a8fc-0242ac120002.xml`, wersja danych 01.00.000), opisane jako „Baseline model of the IPCC 2021” (GWP100), ze współczynnikiem 29,8 dla CH₄ biogenicznego; w metadanych pozostało starsze odwołanie bibliograficzne „IPCC 2013” — jest to niespójność w samym pakiecie źródłowym;
- metodę niedoboru wody AWARE 100 (wersja danych 03.00.014).

Identyfikatory, wersje danych i sumy kontrolne metod dla wszystkich 19 wskaźników wpływu zestawiono w załączniku E; reguły współczynników w programie obliczeniowym są powiązane z tymi plikami sumą SHA-256 (19 z 19 zgodnych). Pakiet JRC nie ma numeru wydania poza etykietą katalogu „EF-v3.1 (4)”. Jednostka EP-fw (kg P eq) odpowiada poprawce AC:2021.

**Odstępstwa pakietu JRC od PN-EN 15804+A2, tab. C.1–C.2** (do oceny przez recenzenta):
- zmiana klimatu: tab. C.1 wskazuje model IPCC 2013, a metody pakietu opisano jako „Baseline model of the IPCC 2021” ze współczynnikiem 29,8 dla CH₄ (wartość z szóstego raportu IPCC), przy pozostawionym w metadanych odwołaniu do IPCC 2013;
- zubożenie warstwy ozonowej: tab. C.1 wskazuje WMO 2014, a metoda pakietu opiera się na ocenie WMO z 1999 r.;
- toksyczność: tab. C.2 wskazuje USEtox w wersji 2; metody ETP-fw i HTP-c nie podają wersji, HTP-nc podaje wersję 2.1;
- eutrofizacja wód słodkich i morskich: metody cytują Struijs i in. (2008), norma — Struijs i in. (2009b).

Norma (pkt C.4) wskazuje współczynniki EC-JRC pod nazwą „EN_15804”; pakiet o tej nazwie jest źródłem metod. W obliczeniach zastosowano ponadto reguły odwzorowania przepływów i współczynniki zastępcze programu obliczeniowego (m.in. dla promieniowania jonizującego, oparte na własnych profilach aktywności) oraz jawnie opisane odstępstwa dla GWP-biogenic i WDP (5.2). Zgodność 19 sum kontrolnych potwierdza pochodzenie plików metod, a nie wyłączne użycie niezmienionych współczynników (zał. E). Norma (tab. C.2) dopuszcza zastąpienie USEtox 2 zmodyfikowanym modelem JRC, więc różnica metadanych przy toksyczności nie jest sama w sobie dowodem niezgodności.

Wskaźniki zużycia zasobów, odpadów i przepływów wyjściowych (18 pozostałych) nie są wynikiem charakteryzowania; oblicza się je na podstawie odrębnych rejestrów programu obliczeniowego: energia pierwotna z rejestru wartości opałowych zasobów, materiały wtórne i paliwa wtórne z rejestru materiałowego i decyzji zastępczych, odpady i przepływy wyjściowe z reguł klasyfikacji strumieni. Reguły dla każdego z 18 wskaźników opisuje załącznik E. Dla NRSF, CRU i MER program nie zawiera żadnej reguły, a zerowy wynik jest konwencją granicy bez dowodu kompletności; do SM i RSF dodaje się także pozycje rejestru o statusie „do przeglądu” (1 dla SM, 2 dla RSF).

Wyboru kategorii nie uzasadnia się odrębnie, ponieważ wyznacza go EN 15804+A2 dla zastosowania w EPD. Wyniki nie są normalizowane, grupowane ani ważone; nie podaje się wskaźnika zagregowanego.

Nazwy wskaźników w tabeli 1 przyjęto według legend deklaracji wydanych w programie EPD Polska (EPD-P-08.12.2025-PL, s. 18–21). Jedynym urzędowym polskim tekstem jest tłumaczenie poprawki PN-EN 15804+A2:2020-03/AC:2021-11, które obejmuje tylko 13 wskaźników podstawowych i zawiera usterki redakcyjne; polską wersją całej normy nie dysponowano. Zestawienie nazw: załącznik F. Wartości z pełną precyzją zawierają pliki `profil-37.json` i `wskazniki-37.csv` publicznego pakietu konsultacyjnego `2026-10-20.1`.

**Tabela 1. Wyniki dla 1 kWh energii elektrycznej dostarczonej w Polsce, 2025 r.** (wartości zaokrąglone do czterech cyfr znaczących; „wariant v4” — poprzednia opublikowana wersja)

**Wskaźniki podstawowe wpływu na środowisko**

| Skrót | Wskaźnik | Jednostka | Wynik | Wariant v4 | Zmiana wobec v4 |
|---|---|---|---:|---:|---:|
| GWP-total | Zmiana klimatu, całkowity potencjał globalnego ocieplenia | kg CO2 eq | 0,6473 | 0,6445 | +0,4244% |
| GWP-fossil | Zmiana klimatu, paliwa kopalne | kg CO2 eq | 0,6458 | 0,6424 | +0,5292% |
| GWP-biogenic | Zmiana klimatu, węgiel biogeniczny | kg CO2 eq | 0,001346 | 0,002010 | −33,04% |
| GWP-luluc | Zmiana klimatu, użytkowanie gruntów i zmiana użytkowania gruntów | kg CO2 eq | 1,144·10⁻⁴ | 1,144·10⁻⁴ | +0,009784% |
| ODP | Zubożenie warstwy ozonowej | kg CFC11 eq | 4,011·10⁻⁹ | 4,011·10⁻⁹ | +0,005579% |
| AP | Zakwaszenie środowiska lądowego i wód słodkich | mol H+ eq | 0,001085 | 0,001079 | +0,4950% |
| EP-fw | Eutrofizacja wód słodkich | kg P eq | 6,267·10⁻⁵ | 6,206·10⁻⁵ | +0,9692% |
| EP-mar | Eutrofizacja wód morskich | kg N eq | 2,198·10⁻⁴ | 2,189·10⁻⁴ | +0,4045% |
| EP-ter | Eutrofizacja środowiska lądowego | mol N eq | 0,002456 | 0,002447 | +0,3491% |
| POCP | Powstawanie ozonu fotochemicznego (smogu) | kg NMVOC eq | 7,626·10⁻⁴ | 7,599·10⁻⁴ | +0,3500% |
| ADP-mm | Wyczerpywanie zasobów abiotycznych, minerały i metale | kg Sb eq | 7,901·10⁻⁷ | 7,901·10⁻⁷ | +0,005068% |
| ADP-fossil | Wyczerpywanie zasobów abiotycznych, paliwa kopalne | MJ (net calorific) | 7,203 | 7,171 | +0,4447% |
| WDP | Niedobór wody (potencjał pozbawienia wody wskutek jej zużycia) | m3 world eq | 0,01731 | 0,02112 | −18,07% |

**Dodatkowe wskaźniki wpływu na środowisko**

| Skrót | Wskaźnik | Jednostka | Wynik | Wariant v4 | Zmiana wobec v4 |
|---|---|---|---:|---:|---:|
| PM | Emisje pyłu zawieszonego (potencjalna zapadalność na choroby) | disease incidence | 4,736·10⁻⁹ | 4,733·10⁻⁹ | +0,04675% |
| IRP | Promieniowanie jonizujące, potencjalne narażenie zdrowia ludzi | kBq U235 eq | 0,006817 | 0,006811 | +0,08598% |
| ETP-fw | Ekotoksyczność wód słodkich | CTUe | 1,977 | 1,964 | +0,6269% |
| HTP-c | Toksyczność dla ludzi, skutki rakotwórcze | CTUh | 3,235·10⁻¹⁰ | 3,233·10⁻¹⁰ | +0,04618% |
| HTP-nc | Toksyczność dla ludzi, skutki inne niż rakotwórcze | CTUh | 7,826·10⁻⁹ | 7,812·10⁻⁹ | +0,1760% |
| SQP | Wpływ użytkowania gruntów na jakość gleby | dimensionless (pt) | 3,278 | 3,278 | +0,005939% |

**Wskaźniki zużycia zasobów**

| Skrót | Wskaźnik | Jednostka | Wynik | Wariant v4 | Zmiana wobec v4 |
|---|---|---|---:|---:|---:|
| PERE | Zużycie odnawialnej energii pierwotnej jako nośnika energii | MJ | 1,927 | 1,927 | +0,008661% |
| PERM | Zużycie odnawialnych zasobów energii pierwotnej jako surowców | MJ | 0 | 0 | — |
| PERT | Całkowite zużycie odnawialnych zasobów energii pierwotnej | MJ | 1,927 | 1,927 | +0,008661% |
| PENRE | Zużycie nieodnawialnej energii pierwotnej jako nośnika energii | MJ | 7,221 | 7,189 | +0,4436% |
| PENRM | Zużycie nieodnawialnych zasobów energii pierwotnej jako surowców | MJ | 0 | 0 | — |
| PENRT | Całkowite zużycie nieodnawialnych zasobów energii pierwotnej | MJ | 7,221 | 7,189 | +0,4436% |
| SM | Zużycie materiałów wtórnych | kg | 0,001965 | 0,001964 | +0,02799% |
| RSF | Zużycie odnawialnych paliw wtórnych | MJ | 0,002611 | 0,002609 | +0,05114% |
| NRSF | Zużycie nieodnawialnych paliw wtórnych | MJ | 0 | 0 | — |
| FW | Zużycie netto wody słodkiej | m3 | 0,002047 | 0,002046 | +0,06439% |

**Wskaźniki odpadów i przepływów wyjściowych**

| Skrót | Wskaźnik | Jednostka | Wynik | Wariant v4 | Zmiana wobec v4 |
|---|---|---|---:|---:|---:|
| HWD | Odpady niebezpieczne unieszkodliwione | kg | 0,1152 | 0,1152 | +0,004032% |
| NHWD | Odpady inne niż niebezpieczne unieszkodliwione | kg | 1,856 | 1,835 | +1,129% |
| RWD | Odpady promieniotwórcze unieszkodliwione | kg | 2,929·10⁻⁴ | 2,927·10⁻⁴ | +0,07364% |
| CRU | Komponenty do ponownego użycia | kg | 0 | 0 | — |
| MFR | Materiały do recyklingu | kg | 9,651·10⁻⁶ | 9,650·10⁻⁶ | +0,005511% |
| MER | Materiały do odzysku energii | kg | 0 | 0 | — |
| EEE | Eksportowana energia elektryczna | MJ | 0,001021 | 0,001021 | −0,004399% |
| EET | Eksportowana energia cieplna | MJ | 0,004669 | 0,004668 | +0,01069% |

### 5.2. Wybory wartości

**Węgiel biogeniczny.** Zastosowano jawne charakteryzowanie biogenicznego CO₂ i CH₄: współczynnik +1 dla CO₂ (pobranie ma znak ujemny) i 29,8 kg CO₂ równ./kg dla biogenicznego CH₄, z zamrożonego zestawu współczynników charakteryzowania (IPCC 2021, zob. 5.1). Uwzględniono transfery netto węgla dla gazu z osadów ściekowych i bioodpadów oraz końcowe rozliczenie drewna w kopalniach. Nie dopisano nowego pochłaniania ani korekty wymuszającej bilans zerowy. Poprzednia konwencja (neutralne CO₂, 27,1 dla CH₄) służy wyłącznie do porównania z v4.

GWP-biogenic (0,001346 kg CO₂ równ./kWh) jest różnicą dużych wartości o przeciwnych znakach: suma bezwzględnych wkładów wynosi 0,1317, czyli około 98 razy więcej niż wynik. Bez transferów materiałowych wynik wynosiłby 0,00928 kg CO₂ równ./kWh. Wynik jest więc wrażliwy na przyjęte granice rachunku.

**Woda kopalniana.** Dla rozpoznanych krajowych ilości węgla (brunatny 0,219141 kg/kWh, kamienny C0129 0,105262 kg/kWh) zastosowano polskie współczynniki AWARE +1,96 (pobór) i −1,96 (zwrot) zamiast przejętych współczynników globalnych 42,95 i −42,955. Pobór i zwrot 90% są oszacowaniami ze źródła (Dones 2007), a nie pomiarami z 2025 r. Zmiana dostosowuje współczynniki charakteryzowania do lokalizacji; nie świadczy o oszczędności wody.

**Emisje długoterminowe.** Emisje długoterminowe procesów tła (kategorie „groundwater, long-term”, „river, long-term” i „low. pop., long-term”) pozostają w inwentarzu fizycznym, ale są wyłączone z charakteryzowania. Dla poprawionych procesów nadkładu dotyczy to emisji z horyzontu od 100 do 60 000 lat. Regułę przejęto z wcześniejszego modelu; jej zasadność dla zamierzonego zastosowania wymaga oceny recenzenta.

### 5.3. Ograniczenia wyników oceny wpływu

Wyniki oceny wpływu są wyrażeniami względnymi i nie pozwalają przewidywać wpływów na punkty końcowe kategorii, przekroczenia wartości progowych, marginesów bezpieczeństwa ani ryzyka (PN-EN ISO 14044, 5.2 e) 8)).

Dodatkowe ograniczenia:
- wskaźnik zmiany klimatu nie zastępuje pełnego zestawu wskaźników; profil 37 wskaźników należy czytać razem z oceną jakości danych (rozdział 6);
- rachunek węgla biogenicznego nie jest pełnym fizycznym bilansem węgla bazy (właściwości biogazu z 2007 r., źródła modelu silnika z lat 2000–2004);
- dla tlenku węgla i olejów biogenicznych brak współczynników charakteryzowania; diagnostyczny równoważnik utlenienia CO wynosi około 0,00013 kg CO₂/kWh, a skrajne przeliczenie olejów — około 0,0000036 kg CO₂/kWh; wartości tych nie dodano do wyniku;
- dla wskaźników PM, HTP-c, HTP-nc, SQP, PERE, PERT oraz SM, RSF, HWD, MFR, EEE i EET pokrycie oceną jakości jest niskie lub zerowe (ranking diagnostyczny).

### 5.4. Relacje między wynikami oceny wpływu a wynikami analizy zbioru wejść i wyjść

Największe wkłady do GWP-total (udział w sumie bezwzględnych wartości wkładów):
- bezpośrednia emisja CO₂ ze spalania węgla kamiennego: 33,3%;
- bezpośrednia emisja CO₂ ze spalania węgla brunatnego: 26,0%;
- spalanie zrębków w kogeneracji: 6,8%;
- spalanie gazu ziemnego: 6,8%;
- metan kopalń węgla kamiennego: 3,3%.

Bezpośrednia emisja CO₂ ze spalania węgla (kamiennego C0129 i C0121 oraz brunatnego; 0,4610 kg/kWh) stanowi 71,2% wyniku netto.

Największe wkłady w pozostałych wskaźnikach:
- ADP-fossil: wydobycie węgla kamiennego (37,8%) i brunatnego (28,6%);
- EP-fw: nadkład węgla brunatnego (58,1%) i składowanie skały płonnej (22,9%);
- WDP: woda odkarbonizowana (30,2%) i spalanie oleju ciężkiego (14,6%);
- IRP: przerób wypalonego paliwa jądrowego (89,5%, proces historyczny).

## 6. Jakość danych

### 6.1. Metoda oceny

Do oceny wybrano minimalny zestaw jednostek pokrywający co najmniej 80% bezwzględnych wkładów każdego z 13 podstawowych wskaźników (EN 15941:2024, 7.1.2) oraz dodatkowo wskaźników IRP i RWD. Każdą jednostkę oceniono według trzech kryteriów (czas, geografia, technologia) w skali 1–5 zgodnie z EN 15804+A2, tab. E.1. Rejestr zawiera 73 decyzje:
- 60 jednostek istotnych w poprzedniej wersji, w tym 49 przypadków danych zastępczych;
- 7 procesów ujawnionych po wprowadzeniu rachunku węgla biogenicznego;
- 2 procesy infrastruktury kopalń;
- 2 procesy zagraniczne;
- 2 polskie bilanse wody kopalnianej.

Dla każdej decyzji określono zakres dopuszczalnego zastosowania, ograniczenia, warunek aktualizacji i termin przeglądu (przed kolejnym wydaniem rocznym lub po istotnej zmianie źródła). Nie przypisano rozkładów statystycznych i nie przeprowadzono propagacji niepewności w obliczeniach (nie wykonano analizy Monte Carlo). Procesy źródłowe zawierają parametry niepewności (np. SD95 ≈ 3 dla robót strzałowych i ilości drewna w infrastrukturze kopalń, SD95 ≈ 5 dla miedzi), ale wykorzystano je tylko w diagnostyce ilości drewna (4.5).

### 6.2. Wyniki oceny

**Tabela 3. Pokrycie oceną i udział wkładów o słabej lub bardzo słabej aktualności** (ocena czasu 4–5)

| Wskaźnik | Zakres | Ocenione wkłady (udział sumy bezwzględnej) | Zestaw minimalny ≥ 80% | Ocena czasu 4–5 |
|---|---|---:|---:|---:|
| GWP-total | podstawowy | 89,10% | 8 jedn.; 80,03% | 18,51% |
| GWP-fossil | podstawowy | 89,53% | 4 jedn.; 83,44% | 4,637% |
| GWP-biogenic | podstawowy | 86,43% | 9 jedn.; 82,76% | 86,43% |
| GWP-luluc | podstawowy | 81,58% | 3 jedn.; 81,58% | 81,58% |
| ODP | podstawowy | 80,95% | 7 jedn.; 80,95% | 13,73% |
| AP | podstawowy | 85,60% | 12 jedn.; 80,79% | 12,24% |
| EP-fw | podstawowy | 80,93% | 2 jedn.; 80,92% | 80,93% |
| EP-mar | podstawowy | 85,20% | 11 jedn.; 80,65% | 15,70% |
| EP-ter | podstawowy | 84,92% | 10 jedn.; 80,93% | 16,80% |
| POCP | podstawowy | 84,31% | 16 jedn.; 80,89% | 27,06% |
| ADP-mm | podstawowy | 81,64% | 11 jedn.; 81,64% | 81,64% |
| ADP-fossil | podstawowy | 85,35% | 5 jedn.; 82,95% | 72,38% |
| WDP | podstawowy | 84,80% | 9 jedn.; 81,46% | 80,82% |
| IRP | dodatkowo oceniony | 89,62% | 1 jedn.; 89,48% | 89,62% |
| RWD | dodatkowo oceniony | 98,14% | 1 jedn.; 98,12% | 98,14% |

Pokrycie oceną oznacza udział ocenionych wkładów, a nie udział danych dobrej jakości. Wysokie udziały oceny czasu 4–5 (GWP-biogenic, GWP-luluc, EP-fw, ADP-mm, WDP, IRP, RWD, ADP-fossil) nie oznaczają automatycznie niezgodności z EN 15941:2024, 7.3.2, ale ograniczają podstawę ilościową tych wskaźników i wymagają uwzględnienia w interpretacji.

Przykładowe decyzje:
- **transport skroplonego gazu ziemnego (LNG) z USA (602200):** na podstawie pełnych metadanych ocenę czasu skorygowano z 1 na 4, a rok referencyjny z 2023 na 2015;
- **pozostałości po przerobie rud uranu (168014):** gęstość 1800 kg/m³ potwierdzono w źródle (Doka 2008, §3.9.1);
- **przerób wypalonego paliwa (183572):** zachowano go jako historyczny zamiennik europejski; odpowiada za 89,5% IRP;
- **roboty strzałowe (222941):** autor bazy ostrzega przed użyciem tego procesu, gdy jego względna istotność w wyniku jest duża; proces odpowiada za 7,62% bezwzględnych wkładów EP-ter, 5,18% EP-mar i 4,39% POCP; zachowano go jako jawne dane zastępcze tła i obliczono diagnostykę jego udziału.

## 7. Interpretacja

### 7.1. Wyniki

GWP-total wynosi **0,6473 kg CO₂ równ./kWh** (0,6472750830697663) na 1 kWh energii elektrycznej dostarczonej w Polsce w 2025 r.

Zmiana wobec poprzedniej wersji v4 (0,6445 kg CO₂ równ./kWh) wynosi +0,42% i wynika ze zmiany metody, a nie ze zmierzonej zmiany emisji elektrowni:
- wspólna alokacja: +0,0034280 kg/kWh (+0,53%);
- zmiana grafu dostaw biogazu: −0,0000723 kg/kWh;
- rachunek węgla biogenicznego: −0,0006203 kg/kWh.

Wartość WDP zmniejszyła się o 18,07% w wyniku regionalizacji wody kopalnianej.

### 7.2. Wrażliwość na alokację

**Tabela 2. Wrażliwość GWP-total (kg CO₂ równ./kWh) na współczynnik jakości ciepła q** (wartości do czterech cyfr znaczących)

| q węgiel kamienny | q węgiel brunatny | GWP-total | Różnica wobec wyniku centralnego | Test graniczny |
|---:|---:|---:|---:|:-:|
| 0,35 | 1 | 0,6438 | −0,5296% | tak |
| 0,35 | 0,35 | 0,6473 | +0% | nie |
| 0 | 0,35 | 0,7024 | +8,511% | tak |
| 0,1 | 0,35 | 0,6845 | +5,756% | nie |
| 0,2 | 0,35 | 0,6685 | +3,279% | nie |
| 0,5 | 0,35 | 0,6288 | −2,849% | nie |
| 1 | 0,35 | 0,5817 | −10,14% | tak |
| 0,35 | 0 | 0,6492 | +0,2925% | tak |
| 0,35 | 0,1 | 0,6486 | +0,2084% | nie |
| 0,35 | 0,2 | 0,6481 | +0,1247% | nie |
| 0,35 | 0,5 | 0,6465 | −0,1238% | nie |
| 0 | 0 | 0,7043 | +8,803% | tak |
| 0,1 | 0,1 | 0,6859 | +5,964% | nie |
| 0,2 | 0,2 | 0,6693 | +3,404% | nie |
| 0,5 | 0,5 | 0,6280 | −2,973% | nie |
| 1 | 1 | 0,5782 | −10,67% | tak |
| 0,3546 | 0,3546 | 0,6466 | −0,09712% | nie |

Wartości q = 0 i q = 1 to testy graniczne; wariant q = 0,3546 dla obu grup jest diagnostyką konwencji z dyrektywy (UE) 2018/2001, która nie jest wymaganiem dla tego zastosowania. Analiza wrażliwości jest deterministyczna, a uzyskany zakres nie jest przedziałem ufności. Wynik zależy głównie od q dla węgla kamiennego (zakres 0,1207 kg CO₂ równ./kWh); zakres dla q węgla brunatnego wynosi 0,0053.

### 7.3. Porównanie z innymi źródłami

Wskaźnik KOBiZE dla odbiorców końcowych (553 kg CO₂/MWh, czyli 0,553 kg CO₂/kWh, dane za 2024 r.; dla energii elektrycznej wyprodukowanej w instalacjach do spalania paliw 717 kg CO₂/MWh) opisuje emisje CO₂ przypisane produkcji energii z alokacją energetyczną w każdej instalacji. Nie jest wskaźnikiem wpływu w cyklu życia i nie dotyczy 2025 r., dlatego różnicy nie traktuje się ani jako walidacji, ani jako błędu. Kontrolę porównywalności z KOBiZE wykonano dla wersji v4; dla ocenianego modelu jej nie powtórzono. Odrębny test reguły podziału dla bazy węgla kamiennego wykazał, że zmiana q z 0,35 na 1 zmienia intensywność emisji CO₂ tej bazy o −21,85%. Różnica wobec KOBiZE zależy więc w istotnym stopniu od reguły podziału obciążeń między energię elektryczną a ciepło.

### 7.4. Założenia, ograniczenia i oceny eksperckie

1. Wynik jest krajowym fizycznym miksem zużycia; jego zastosowanie w EPD wymaga zgodności z regułą doboru energii programu i EN 15941:2024, załącznik E.
2. Alokacja q = 0,35 jest jawnym przybliżeniem; dane zakładowe o cieple pozwoliłyby ją zastąpić.
3. Ujednolicenie alokacji obejmuje nowe strumienie, nie historyczne procesy tła.
4. Znaczna część danych tła ma słabą aktualność (tabela 3); dotyczy to zwłaszcza wskaźników jądrowych, wody, fosforu, zasobów metali i węgla biogenicznego.
5. Intensywność CO₂ bazy 2024 dla węgla kamiennego jest o 4,292% niższa od intensywności panelu przedsiębiorstw w tym samym roku (0,891308 wobec 0,931280 kg CO₂/kWh netto); różnicy nie wyjaśniono w pełni.
6. Dane Eurostatu za 2025 r. są wstępne.
7. Współczynniki z pakietu JRC opierają się dla zmiany klimatu na ocenie nowszej (IPCC 2021), a dla zubożenia warstwy ozonowej na ocenie starszej (WMO 1999) niż modele wskazane w PN-EN 15804+A2, tab. C.1 (5.1).
8. Wynik nie obejmuje kopalnego CO₂ ze spalania odpadów (alokacja do usługi zagospodarowania odpadów; orientacyjnie +1,5% GWP-total przy przypisaniu całego kopalnego CO₂ energii elektrycznej); energię elektryczną zużywaną w kopalniach odwzorowuje w nim miks ENTSO-E z 2023 r. (zastąpienie miksem krajowym orientacyjnie +0,8%).
9. Spośród wariantów wrażliwości innych niż alokacja największy wpływ na GWP-total ma powrót do poprzedniej bazy paliwa i CO₂ węgla kamiennego (+1,574%); wpływ wariantów uranu i metali dotyczy głównie ODP (+11,79%) oraz HTP-nc (+15,67%).
10. Wszystkie wybory wartości i oceny jakości wykonano z użyciem narzędzi sztucznej inteligencji. Kontrole wykonane przez Claude i Codex nie zastępują oceny eksperta.

### 7.5. Wnioski i zalecenia

Model daje kompletny i odtwarzalny profil 37 wskaźników dla 1 kWh energii elektrycznej dostarczonej w Polsce w 2025 r., z jawnie opisanymi wyborami metodycznymi i ograniczeniami. Przed przyjęciem do programu EPD Polska zaleca się:
- przeprowadzenie przeglądu krytycznego;
- przekazanie recenzentowi dokumentacji według decyzji A13;
- decyzję o zastąpieniu energii elektrycznej kopalń miksem krajowym i o uzgodnieniu różnicy ARE–Eurostat;
- podjęcie decyzji operatora o wpisie do wykazu przyjętych danych.

## 8. Przegląd krytyczny

Przegląd krytyczny nie został jeszcze przeprowadzony. Proponowany zakres przeglądu zawiera dokument pomocniczy wykonawcy (samoocena gotowości do przeglądu krytycznego), stanowiący część dokumentacji roboczej.

| Element (PN-EN ISO 14044, 5.2 g)) | Treść |
|---|---|
| Recenzent (nazwisko, afiliacja) | do uzupełnienia po przeglądzie |
| Raport z przeglądu krytycznego | do dołączenia |
| Odpowiedzi na zalecenia | do dołączenia |

---

## Załącznik A. Stan pozycji do uzupełnienia

„Zamknięte” oznacza zakończenie wskazanej dokumentacji, a nie rozstrzygnięcie przydatności modelu; oceniają ją recenzent i operator.

| Nr | Pozycja | Stan na 26.10.2026 | Gdzie |
|---|---|---|---|
| A1 | Zlecający i wykonawca badania | zamknięte 26.10.2026: program EPD Polska (operator Multicert Sp. z o.o.) i Multicert Sp. z o.o. | 1.1 |
| A2 | Potwierdzenie, że badanie nie służy stwierdzeniom porównawczym przewidzianym do udostępnienia publicznego | zamknięte 26.10.2026: potwierdzone przez zlecającego | 2.4 |
| A3 | Nazwa, wersja i licencja bazy tła | zamknięte: BAFU-2026 v1, warunki użytkowania z 23.06.2026; status danych zmodyfikowanych rozstrzygnięty w A13 | 3.4, zał. C |
| A4 | Kryteria wyłączenia w procesach bazy tła | opisano jakościowo; ilościowej oceny pominięć nie wykonano | 3.3, zał. D |
| A5 | Energia elektryczna w procesach tła | zamknięte opisowo; decyzja o zastąpieniu energii kopalń miksem krajowym otwarta (ok. +0,8% GWP-total) | 3.2, zał. D |
| A6 | Metody charakteryzowania 19 wskaźników | zamknięte; odstępstwa od tab. C.1–C.2 opisano do oceny recenzenta | 5.1, zał. E |
| A7 | Uzasadnienie wyłączenia emisji długoterminowych | reguła opisana; ocena zasadności — recenzent | 5.2 |
| A8 | Polskie nazwy wskaźników | zamknięte: nazwy programu EPD Polska; polska wersja całej normy niedostępna | 5.1, zał. F |
| A9 | Warianty wrażliwości v4 dla ocenianego modelu | częściowo zamknięte: 14 z 14 oraz 3 warianty sieci; wariant eksportu nieobliczony (brak adaptera) | 4.5, tab. 6, zał. H |
| A10 | Różnica 0,534% produkcji netto węgla brunatnego | wyjaśniona częściowo; wpływ +0,03% do +0,17%; procedura uzgodnienia zaproponowana | 4.2, zał. D |
| A11 | Powiązanie pakietu `2026-10-20.1` z zamrożeniem R3 | zamknięte: 37 wartości identycznych, pliki na polca.org.pl zgodne z manifestem | zał. I |
| A12 | Specyfikacja zastosowania i projekt decyzji operatora | zamknięte jako projekt wewnętrzny (niepodpisany) | 2.2 |
| A13 | Dostęp recenzenta do danych licencjonowanych i części poufne | zamknięte 26.10.2026: poprawki traktowane jako dane zmodyfikowane BAFU z wykazem zmian; recenzent pobiera bazę BAFU samodzielnie; dane zmodyfikowane na warunkach równoważnych BAFU; poufność tylko dokumentacji roboczej | 3.4 |
| A14 | Reguły 18 wskaźników zasobów, odpadów i przepływów wyjściowych | zamknięte; brak reguł dla NRSF, CRU i MER (zero konwencyjne) | 5.1, zał. E |
| A15 | Pełne opisy bibliograficzne | zamknięte w zakresie dostępnych plików; braki wymienione w zał. G | zał. G |
| A16 | Opis ilościowy pozostałych technologii pierwszego planu | zamknięte: technologie poza węglem odpowiadają za 19,9% GWP-total | zał. D |
| A17 | Uzasadnienie zerowego obciążenia X9900 i energii z odpadów | częściowo: dla odpadów opisano podstawę (6.3.5.1 i 6.3.5.5) jako interpretację wykonawcy; brak analizy stanu końca odpadu i odrębnego uzasadnienia X9900 | 3.2, zał. D |

## Dokumentacja uzupełniająca

Załączniki C–I i K raportu (baza tła i warunki licencji, analizy diagnostyczne, wykaz zmian danych BAFU, metody i reguły wskaźników, zestawienie nazw, bibliografia, przeliczenie wariantów, powiązanie pakietu publicznego) są częścią dokumentacji roboczej. Zawierają dane objęte licencją BAFU i są przekazywane recenzentowi według decyzji A13, z zachowaniem warunków użytkowania BAFU (pkt 2–3).

## Załącznik B. Pochodzenie tabel i dowody

Tabele 1–3, 5 i 6 wygenerowano skryptem z plików o następujących sumach kontrolnych SHA-256:

- wynik końcowy 37 wskaźników: `979557fae0d52a9c949b2c9d536bdd1eb1ce4baac40017e192edadcd91224a14`
- porównanie z wersją v4: `3a6c2655685a739776476d6b94f80944b8981f64515b9f513e0aa9dd44487988`
- wrażliwość na q (17 par): `14a770343f910a8c8cc445ff046ccd7e306eb10637385a39cecf8d338c50d42d`
- ocena jakości danych: `6bdd554228d94651d76be37693788bce2024ce9a156868cc7476e5247d189a08`
- dane wejściowe wytwarzania krajowego: `2dc32c47f1c1a6854725c597a544f69252e53075c9244c147918a5c9d5016522`
- odwzorowanie kategorii wytwarzania (kod): `2cb2ecc429bfa240ed2c324036eabd8590205440c501144a4417fe98bf9128bb`
- warianty wrażliwości (przebieg run-003): `813c31d231f651bc78f669148d651bad8c6970d08f3b4acfd726b44e1f5b8916`

Zapisy wcześniejszych kontroli technicznych (rundy R1–R3 Claude i Codex) są częścią dokumentacji roboczej.
