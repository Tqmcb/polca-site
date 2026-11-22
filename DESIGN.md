---
name: poLCA
description: Polski atlas danych środowiskowych, obliczeń i dokumentacji.
colors:
  ink: "#142c45"
  link: "#1355c4"
  muted: "#526173"
  line: "#d4dce4"
  soft: "#f3f6fa"
  paper: "#ffffff"
  dark-surface-text: "#c9d7e9"
  consultation-wash: "#eff5fc"
  result-caption: "#d7e2f0"
  input-border: "#8292a5"
  preset-border: "#aab8c9"
  input-error: "#963c36"
typography:
  display-home:
    fontFamily: '"Source Sans 3", Arial, sans-serif'
    fontSize: "clamp(2.6rem, 4.1vw, 3.55rem)"
    fontWeight: 620
    lineHeight: 1.04
    letterSpacing: "-0.038em"
  headline:
    fontFamily: '"Source Sans 3", Arial, sans-serif'
    fontSize: "2rem"
    fontWeight: 600
    lineHeight: 1.14
    letterSpacing: "-0.025em"
  body:
    fontFamily: '"Source Sans 3", Arial, sans-serif'
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  square: "0"
  field: "3px"
  control: "4px"
spacing:
  small: "8px"
  medium: "16px"
  large: "24px"
  section-gap: "64px"
components:
  button-primary:
    backgroundColor: "{colors.link}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "10px 20px"
  button-primary-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  consultation-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "11px 12px"
---

# Interfejs poLCA

## Overview

poLCA ma charakter atlasu danych i dokumentacji obliczeń. Hierarchię tworzą tytuły, proporcje kolumn, odstępy i cienkie linie. Liczby występują w obliczeniach, tabelach i opisach zbiorów; nie są dekoracją strony.

Biała powierzchnia służy czytaniu i pracy z danymi. Granat porządkuje tekst i wydziela diagram modelu oraz wynik obliczenia. Autorskie szkice techniczne łączą energię, materiały, transport i budynek oraz towarzyszą zaproszeniu do konsultacji. Kobalt wskazuje odnośniki, czynności i wybrany element. Każdy rodzaj treści ma właściwy mu układ: indeks zasobów, równanie, diagram, wykaz dokumentów, lista pytań lub formularz korespondencji.

Treści są po polsku. Rok danych, wersja modelu, jednostka, źródło i status pozostają rozpoznawalnymi, odrębnymi informacjami. Sposób prezentacji wyniku nie stanowi potwierdzenia jego kwalifikacji do zastosowania.

## Colors

Paleta opiera się na bieli, granacie i jednym akcencie kobaltowym. Wartości kolorów określa część YAML; ich odpowiednikami w arkuszu wspólnym są zmienne `--portal-ink`, `--portal-link`, `--portal-muted`, `--portal-line` oraz `--portal-soft`.

- **Granat (`ink`)**: podstawowy tekst, istotne linie podziału i ciemne powierzchnie diagramu oraz konsultacji.
- **Kobalt (`link`)**: odnośniki, przyciski główne, aktywny krok i wynik wyróżniony w równaniu.
- **Biel (`paper`)**: główne tło i tekst na ciemnej powierzchni.
- **Przygaszony granat (`muted`)**: objaśnienia, jednostki pomocnicze i metadane na jasnym tle.
- **Jasna linia (`line`)**: podział wierszy, obramowania i granice grup treści.
- **Chłodne jasne tło (`soft`)**: nagłówki tabel, podgląd wiadomości i objaśnienia statusu.
- **Jasny tekst diagramu (`dark-surface-text`)**: opisy uzupełniające na granatowym tle modelu.

Status jest opisany słowami. Nie używać żółtych płaszczyzn ani kolorowych etykiet jako domyślnego sposobu wyróżniania zastrzeżeń lub etapów oceny.

## Typography

Cały portal korzysta z lokalnie przechowywanego kroju **Source Sans 3**, z odmianą prostą i kursywą. Pliki w `assets/fonts/` są ładowane przez `@font-face` z `font-display: swap`. Krój zastępczy to Arial, następnie bezszeryfowy krój systemowy.

Duży tytuł otwarcia ma mały odstęp między wierszami i wyraźnie przewyższa wielkością tekst. Nagłówki sekcji są lżejsze od tradycyjnych pogrubionych nagłówków interfejsu. Tekst objaśnień zachowuje odstęp między wierszami umożliwiający czytanie pełnych akapitów. Podstawowy rozmiar tekstu wynosi 18 px.

Nie dodawać ozdobnych nadtytułów, etykiet pisanych wersalikami ani numeracji sekcji, która nie wyjaśnia kolejności czynności. Nazwa sekcji ma wystarczać do rozpoznania jej zawartości. Metadane publikacji pozostają zwykłym tekstem powiązanym z dokumentem.

W równaniach i tabelach stosowane są cyfry tabelaryczne (`font-variant-numeric: tabular-nums`). Jednostka to część wyniku. Zmiana skali pisma nie może oddzielać wartości od jednostki ani usuwać objaśnienia skrótu.

## Layout

Wspólna szerokość treści to maksymalnie 1180 px. Na większych ekranach kontener zachowuje łącznie 64 px bocznego marginesu, poniżej 850 px — 40 px, a poniżej 540 px — 32 px. Tekst metody ma węższą kolumnę o maksymalnej szerokości 76 znaków typograficznych (`76ch`).

Układy dwukolumnowe są asymetryczne: szeroka kolumna zawiera obliczenie, opis lub formularz, węższa — nawigację, tytuł albo instrukcję. Nie stosować jednakowego podziału do wszystkich sekcji. Równanie korzysta z szerokości strony, zaproszenie do konsultacji tworzy odrębny pas, a dane branżowe są indeksem z opisem dostępnych materiałów.

Przewodniki na stronie głównej mają pełnoszeroki tytuł i objaśnienie nad dwukolumnowym indeksem pytań. Nie powtarzają układu katalogu z opisem w bocznej kolumnie.

W przewodniku „poLCA, KOBiZE czy ecoinvent?” obie tabele zajmują całą szerokość głównego kontenera. Szerokość wiersza tekstu ograniczamy na akapitach. Na telefonie każdy wiersz otrzymuje własny nagłówek, a pod nim pojawiają się podpisane pola z pozostałych kolumn. Przy odbiorze sprawdzamy, czy na wąskim ekranie można odczytać wartość razem z jej źródłem, miksem i rokiem.

Strona konsultacji zachowuje odrębną strukturę pytań, dokumentów i korespondencji. Pytania są rozwijanymi pozycjami, dokumentacja zajmuje pełną szerokość i zawiera wykaz plików z formatami, a zgłoszenie jest formularzem z instrukcją w bocznej kolumnie.

Przy szerokości poniżej 760 px główne kompozycje strony głównej i konsultacji przechodzą do jednej kolumny. Równanie i diagram zmieniają układ, zachowując kolejność informacji. Tabele przewija się wewnątrz podpisanego obszaru, a nie przez rozszerzenie całej strony.

## Elevation & Depth

Warstwa danych jest oszczędna, a autorskie ilustracje wprowadzają przestrzeń i lekkość. Podział treści wynika z odstępów, pojedynczych linii i zmian tła. Nie stosować cieni do obwodzenia kolejnych sekcji ani do tworzenia pozornej głębi kart. Obrys aktywnego kroku i podkreślenie aktywnej pozycji nawigacji oznaczają stan elementu.

## Shapes

Diagram, równanie i główne powierzchnie mają prostokątną formę. Zaokrąglenie pól konsultacji wynosi 3 px, a wspólnych przycisków i pól portalu — 4 px. Wyszukiwanie na stronie głównej ma narożniki 4 px. Obszar interaktywnego równania ma narożniki 8 px, a wynik 6 px. Małe koła w nawigacji procesu są punktami kolejnych etapów.

Linie mają przeważnie grubość 1 px. Grubszy obrys służy wskazaniu fokusu klawiatury, nie dekoracyjnemu obramowaniu treści. Nie dodawać szerokich kolorowych pasków przy uwagach i zastrzeżeniach.

## Components

### Nawigacja i wyszukiwanie

Wspólna nawigacja prowadzi do wyrobów, danych, kalkulatorów, przewodników oraz metod i źródeł. Wyszukiwanie jest dostępne w nagłówku, a na stronie głównej również przy opisie portalu. Wynik wyszukiwania i indeks zasobów przedstawiają rzeczywistą zawartość; nie zastępują jej marketingowymi kartami.

Odnośniki mają rozpoznawalne podkreślenie lub strukturę wiersza nawigacyjnego. Najechanie zmienia kolor lub podkreślenie. Fokus klawiatury ma kobaltowy obrys o grubości 3 px i odstępie 3 px; na ciemnych powierzchniach obrys jest biały. Odnośnik pomijający nawigację prowadzi do głównej treści.

### Przyciski i pola

Przycisk główny jest kobaltowy z białym tekstem; po najechaniu staje się granatowy. Przycisk pomocniczy ma jasne tło i kobaltowy tekst. Etykieta wskazuje konkretną czynność. Stan wyłączony ogranicza dostępność działania i zmniejsza intensywność elementu.

Pola mają białe tło, cienkie obramowanie i widoczną etykietę. Tekst podpowiedzi nie zastępuje etykiety. Na telefonie formularz układa się w jedną kolumnę, a obszary tekstowe można powiększać w pionie. Podgląd przygotowanej wiadomości jest odróżniony jasnym tłem.

### Obliczenie i diagram modelu

Przykład na stronie głównej pozwala zmienić zużycie i pokazuje zależność: zużycie energii × wskaźnik modelu = wynik. Obliczenie używa pełnej precyzji publicznego modelu v4. Bez skryptów pozostaje statyczny przykład dla 100 kWh. Każdy człon ma nazwę i jednostkę. Pod obliczeniem znajduje się źródło, a obok opisu zastosowania — status wersji i odnośnik do jej zakresu.

Diagram konsultacji rozdziela dane wejściowe, obliczenie dla jednostki odniesienia i wyniki. Linie pokazują połączenia tych elementów; nie są ozdobnym wzorem tła. Diagram pozostaje czytelny bez odtwarzania opisu.

Przechodzenie przez kroki zmienia aktywny etap, opis i wyróżnienie odpowiedniej części diagramu. Ruch następuje po działaniu użytkownika. Odtwarzanie można zatrzymać; zatrzymuje je także klawisz Escape, przejście fokusu do treści kroku lub ukrycie karty przeglądarki. Preferencja ograniczenia ruchu wyłącza odtwarzanie i przejścia. Wszystkie opisy są dostępne bez skryptów.

### Pytania, dokumentacja i korespondencja

Pytania korzystają z natywnych elementów rozwijanych. Wybranie tematu uzupełnia zgłoszenie bez automatycznego przewijania i przenoszenia fokusu. Dokumentacja rozróżnia opis metody, pliki do pobrania i tabelę wyników. Format pliku jest widoczny przy odnośniku.

Formularz przygotowuje wiadomość do samodzielnego wysłania. Tekst, przyciski i komunikaty mają odróżniać przygotowanie wiadomości od jej wysyłki i późniejszej publikacji uwagi. Rejestr ma osobny stan pusty; nie zastępować go przykładowymi komentarzami. Informacje o prywatności pozostają przy formularzu.

## Do's and Don'ts

- Zachowuj jednostki, źródła, wersję i status razem z wynikiem.
- Dobieraj układ do treści: indeks do zasobów, równanie do zależności liczbowej, diagram do przepływu danych, tabelę do porównań.
- Stosuj semantyczne nagłówki, etykiety pól, natywne kontrolki i widoczne stany klawiatury.
- Przy zmianie układu sprawdzaj rzeczywisty tekst na komputerze i telefonie, w tym przewijanie tabel oraz łamanie jednostek.
- Nie buduj strony z powtarzanych równych kafelków, ozdobnych numerów i etykiet nad nagłówkami.
- Nie dodawaj żółtych wstawek, gradientów, ozdobnych wykresów ani automatycznie uruchamianych animacji.
- Nie przedstawiaj publikacji lub kontroli technicznej jako formalnego zatwierdzenia zastosowania danych.
- Nie zmieniaj danych modelu ani domyślnego profilu kalkulatora w ramach zmiany wyglądu.

Źródłem implementacji są `assets/portal.css`, `assets/home.css`, `assets/consultation.css`, `content/portal-home.html.tpl`, `scripts/consultation_portal.py`, `js/home.js` i `js/consultation.js`.

## Ilustracje

Na stronie głównej formularz wyszukiwania prowadzi do danych. Obok niego znajduje się mapa rzeźby terenu Polski z trzema przykładami zastosowania danych. Cieniowanie pochodzi z danych wysokościowych Mapzen, a granica i rzeki z Natural Earth. Pełna mapa przedstawia 13 miast oraz przykłady wykorzystania energii wiatru, fotowoltaiki, energetyki konwencjonalnej, kruszyw, cementu, transportu i budynków. Jej rolą jest wprowadzenie do tematów danych środowiskowych. Nie zawiera rankingu, wartości emisji ani oznaczeń oceniających zakłady. Wielkość szkiców służy czytelności, bez znaczenia liczbowego. Powiększony widok i źródła położenia są na `/mapa-danych.html`.

Zachowujemy grafitowo-kobaltowe szkice na jasnym tle. Turbina ma trzy łopaty, panele fotowoltaiczne czytelne podpory, a rysunki budynków i transportu są symbolami tematów przy miastach, bez wskazywania konkretnej inwestycji. Linie łączą przesunięte szkice z punktami odniesienia. Współrzędnych nigdy nie przesuwa się dla kompozycji; położenie obiektów jest orientacyjne w skali kraju. Kruszywa reprezentują Dolny Śląsk i Świętokrzyskie.

Kontur, rzeki i miasta zapisano w `content/home-map.json`; przykłady, źródła i rozmieszczenie szkiców — w `content/topic-map.json`. Mapę tematyczną generuje `scripts/topic_map_portal.py`. Mapę rzeźby generuje opcjonalny skrypt `scripts/render_home_relief.py`. Na telefonie podgląd pojawia się jako niewielka ilustracja przy odsyłaczu za wyszukiwarką. Pełna mapa zachowuje minimum 660 px szerokości, a jej podpisy można odczytać po przewinięciu osobnego obszaru dostępnego z klawiatury.

Osobny materiał `/mapa-polski.html` pokazuje 20 największych zgłoszonych emisji CO₂ ogółem do powietrza w polskim zbiorze E-PRTR za 2024 r., łącznie z biomasą. Zestawienie opisuje zgłoszoną roczną skalę emisji, a nie efektywność produkcji ani pełną emisję Polski. Powierzchnia niebieskiego koła jest proporcjonalna do rocznej emisji; szare szkice kruszyw są kontekstem bez udziału w rankingu. Dane i pochodzenie są w `data/mapa-emisje-pl-2024.json`, rozmieszczenie w `content/map-emissions-layout.json`, generator w `scripts/map_portal.py`. Ranking i tematyczny wstęp mają odmienne cele.

Szkic elektrowni, wiatru, fotowoltaiki, transformatora pod lupą i licznika towarzyszy konsultacji modelu energii. Ilustracje nie oznaczają formalnego zatwierdzenia wyników. Mapa nie przedstawia kompletnego wykazu instalacji ani pokrycia zasobów bazy poLCA. Na telefonie ilustracje ustępują miejsca wyszukiwarce, polom kalkulatora i objaśnieniom. Zachowują swoje proporcje; podgląd na stronie głównej prowadzi bezpośrednio do pełnej mapy.

W panelu energii ilustracja metody pokazuje stację transformatorową i licznik na przezroczystym tle. Na telefonie zajmuje szerokość tekstu. W sekcji zastosowania przykład i zasady doboru danych tworzą dwie kolumny na komputerze, a na telefonie następują po sobie. Przy odbiorze porównujemy widok obu sąsiednich sekcji na całej szerokości strony.

Katalog wyrobów i karty kruszyw, prefabrykatów betonowych oraz cementu wykorzystują wygenerowane ilustracje fotograficzne typowych procesów. Wyszukiwarka rodzin znajduje się przed ilustracjami. Opisy danych i wartości wskaźników pochodzą z katalogu poLCA.

Wspólnym motywem nagłówków są poziomice Łysogór w jasnej zieleni. W tle treści barwa stopniowo przechodzi w biel, a tabele i wyniki zachowują jednolite podłoże. Nawigacja ma sześć znaków liniowych. Każda z 36 rodzin wyrobów ma własny piktogram obok nazwy. Znaki znajdują się w pliku `assets/ikony-polca.svg`, a ich samodzielne wersje do pobrania w archiwum `assets/ikony-polca.zip` tworzonym podczas budowania portalu.
