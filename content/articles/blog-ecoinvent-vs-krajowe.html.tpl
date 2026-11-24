<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ecoinvent a krajowe bazy danych — kiedy uśrednianie szkodzi dokładności LCA — poLCA Blog</title>
    <meta name="description" content="Jak ocenić reprezentatywność danych krajowych i międzynarodowych. Korekta wcześniejszego zalecenia automatycznego wyboru KOBiZE.">
    <link rel="canonical" href="https://polca.org.pl/blog-ecoinvent-vs-krajowe.html">
    <meta property="og:type" content="article">
    <meta property="og:title" content="Ecoinvent a krajowe bazy danych — kiedy uśrednianie szkodzi dokładności LCA — poLCA Blog">
    <meta property="og:description" content="Jak ocenić reprezentatywność danych krajowych i międzynarodowych. Korekta wcześniejszego zalecenia automatycznego wyboru KOBiZE.">
    <meta property="og:url" content="https://polca.org.pl/blog-ecoinvent-vs-krajowe.html">
    <meta property="og:site_name" content="poLCA — Polska Baza Danych LCA">
    <meta property="og:locale" content="pl_PL">
    <meta property="og:image" content="https://polca.org.pl/images/blog-ecoinvent-vs-krajowe.jpg">
    <meta property="article:published_time" content="2025-12-02T00:00:00+01:00">
    <meta property="article:author" content="poLCA — Polska Baza Danych LCA">
    <meta property="article:section" content="Metodyka LCA">
    <meta property="article:tag" content="ecoinvent">
    <meta property="article:tag" content="bazy danych LCA">
    <meta property="article:tag" content="dane krajowe">
    <meta property="article:tag" content="reprezentatywność">
    <meta property="article:tag" content="LCI">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Ecoinvent a krajowe bazy danych — kiedy uśrednianie szkodzi LCA">
    <meta name="twitter:description" content="Jak ocenić reprezentatywność danych krajowych i międzynarodowych. Korekta wcześniejszego zalecenia automatycznego wyboru KOBiZE.">
    <meta name="twitter:image" content="https://polca.org.pl/images/blog-ecoinvent-vs-krajowe.jpg">
    <script type="application/ld+json">{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "https://polca.org.pl/blog-ecoinvent-vs-krajowe.html",
      "headline": "Ecoinvent a krajowe bazy danych — kiedy uśrednianie szkodzi dokładności LCA",
      "description": "Jak ocenić reprezentatywność danych krajowych i międzynarodowych. Korekta wcześniejszego zalecenia automatycznego wyboru KOBiZE.",
      "url": "https://polca.org.pl/blog-ecoinvent-vs-krajowe.html",
      "datePublished": "2025-12-02",
      "dateModified": "2025-12-02",
      "inLanguage": "pl-PL",
      "author": {
        "@type": "Organization",
        "name": "poLCA — Polska Baza Danych LCA",
        "url": "https://polca.org.pl"
      },
      "publisher": {
        "@type": "Organization",
        "name": "Multicert Sp. z o.o.",
        "url": "https://polca.org.pl",
        "logo": {
          "@type": "ImageObject",
          "url": "https://polca.org.pl/favicon.svg"
        }
      },
      "isPartOf": {
        "@type": "Blog",
        "@id": "https://polca.org.pl/blog.html",
        "name": "Blog poLCA"
      },
      "keywords": [
        "ecoinvent",
        "bazy danych LCA",
        "dane krajowe LCI",
        "KOBiZE",
        "EPD Polska",
        "reprezentatywność geograficzna",
        "ISO 14044",
        "dane wtórne LCA"
      ]
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "poLCA",
          "item": "https://polca.org.pl/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Blog",
          "item": "https://polca.org.pl/blog.html"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Ecoinvent a krajowe bazy danych"
        }
      ]
    }
  ]
}</script>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <meta name="metadata_revision" content="2026-10-18">
</head>
<body data-minutes="9">
<h1>
                Ecoinvent a krajowe bazy danych — kiedy uśrednianie szkodzi dokładności LCA
            </h1>
<p class="article-lead">
                Ecoinvent to standard branży. Ale „standard” nie znaczy „zawsze poprawny”.
                W polskich EPD i LCA budynków kilka kluczowych zbiorów danych z ecoinvent
                może prowadzić do systematycznego błędu — i możliwość weryfikacji tego
                błędu jest teraz lepsza niż kiedykolwiek.
            </p>
<aside class="legacy-note" aria-label="Informacja o wersji"><p><strong>Informacja o wydaniu.</strong> Dokument historyczny: model energii za 2024 r. Wartość 0,599 kg CO₂e/kWh oznacza składnik kopalny (GWP-fossil), nie GWP-total. Dawna hierarchia trzech poziomów nie jest uniwersalną instrukcją doboru energii do deklaracji środowiskowej. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p></aside>
<figure class="article-figure"><img src="images/blog-ecoinvent-vs-krajowe.jpg" alt="Serwerownia — szafy rack w centrum danych" loading="lazy"></figure>
<ol class="article-findings">
<li>Ecoinvent (v3.10) ma zestawy danych oznaczone <code>PL</code> dla Polski — ale część z nich pochodzi sprzed zmian w polskim miksie energetycznym lub branży materiałów budowlanych.</li>
<li>Procesy wymagające szczególnej oceny reprezentatywności to energia elektryczna, ciepło, cement i stal. Dane krajowe mogą lepiej odpowiadać badanemu procesowi, lecz sam kod „PL” tego nie dowodzi.</li>
<li>Dla procesów tła bez polskich danych (np. wydobycie surowców za granicą) ecoinvent pozostaje najlepszą opcją — tu problem nie istnieje.</li>
<li>ISO 14044 §4.7.3.1 wymaga dokumentacji decyzji o wyborze danych; „użyłem ecoinvent bo tak robią wszyscy” nie jest wystarczającym uzasadnieniem metodycznym.</li>
</ol>
<ul class="article-values">
<li><strong>18 000+ zbiorów danych</strong> <span>Ecoinvent v3.10 (2023)<br>pokrycie procesów globalnych</span></li>
<li><strong>Różne różnica</strong> <span>Porównanie wymaga wspólnych granic i metody</span></li>
<li><strong>5 lat</strong> <span>Maksymalny akceptowalny wiek<br>danych w większości PCR (ISO 14044)</span></li>
</ul>
<div class="article-prose"><h2>Czym jest ecoinvent i co daje</h2>
        <p>
            Ecoinvent to baza danych LCI rozwijana przez Szwajcarskie Centrum Ekotechniki w Zürychu.
            Zawiera ponad 18 000 zestawów danych opisujących procesy przemysłowe, energetyczne,
            transportowe i rolnicze. Jest domyślnym „background system” w oprogramowaniu
            SimaPro, OpenLCA i One Click LCA.
        </p>
        <p>
            Ecoinvent aktualizowany jest regularnie (v3.10 — 2023; v3.9 — 2022 itd.),
            ale pojedyncze zestawy danych mogą pochodzić z oryginalnych badań sprzed wielu lat
            i być aktualizowane rzadziej niż coroczne raporty krajowe.
        </p>

        <div class="callout callout-definition">
            <div class="callout-label">Typy zbiorów danych w ecoinvent</div>
            <p class="callout-body">
                <strong>Cutoff</strong> — domyślny system alokacji; materiały z recyklingu
                wchodzą bezobciążeniowo (metoda cut-off). <strong>System Expansion (APOS)</strong>
                — alokacja przez rozszerzenie systemu. <strong>Consequential</strong>
                — do analiz skutkowych (LCA z pytaniem „co się stanie, jeżeli…”).
                Dla EPD wyrobów budowlanych właściwy jest zazwyczaj system <em>cutoff</em>.
            </p>
        </div>

        <h2>Gdzie ecoinvent może być niewystarczający dla polskich LCA?</h2>
        <p>
            Przeanalizowaliśmy główne procesy w polskich EPD materiałów budowlanych
            i wyodrębniliśmy cztery obszary ryzyka:
        </p>

        <div class="process-steps">
            <div class="process-step">
                <div class="process-step-num">1</div>
                <div class="process-step-content">
                    <div class="process-step-title">Energia elektryczna — najważniejszy przypadek</div>
                    <div class="process-step-text">Wskaźnik KOBiZE dla odbiorcy końcowego za 2024 r. wynosi 0,553 kg CO₂/kWh. Opisuje CO₂, a nie kompletny wynik oceny cyklu życia. Historyczny model poLCA-EN-PL-2024 v9.1 podaje 0,599 kg CO₂e/kWh dla składnika kopalnego (GWP-fossil). Wartości mają różny zakres. Nie należy automatycznie zastępować pełnego zbioru energii samym wskaźnikiem CO₂ KOBiZE. Dobór danych energii zależy od zastosowania, kontroli nad procesem i dokumentów dotyczących dostawy. Sam kraj produkcji nie rozstrzyga wyboru między miksem konsumpcyjnym, rezydualnym i danymi dostawcy. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</div>
                </div>
            </div>
            <div class="process-step">
                <div class="process-step-num">2</div>
                <div class="process-step-content">
                    <div class="process-step-title">Ciepło sieciowe i ciepło technologiczne</div>
                    <div class="process-step-text">
                        Polska ciepłownictwo jest zdominowane przez węgiel kamienny i brąztowy
                        (ok. 60–70% udziału wg GUS 2023). Ecoinvent może modelować
                        polskie ciepło sieciowe na podstawie starszych danych lub europejskiej średniej.
                        Dla instalacji korzystających z sieci ciepłowniczej:
                        sprawdź wskaźnik emisji swojego dystrybutora ciepła (obowiązkowy
                        w Polsce na podstawie Prawa Energetycznego) i porównaj z ecoinvent.
                        <strong>Werdykt: weryfikacja konieczna; często lepszy jest wskaźnik lokalny.</strong>
                    </div>
                </div>
            </div>
            <div class="process-step">
                <div class="process-step-num">3</div>
                <div class="process-step-content">
                    <div class="process-step-title">Cement i beton — ecoinvent vs EPD Polska</div>
                    <div class="process-step-text">
                        Ecoinvent zawiera zestawy danych dla cementu i betonu,
                        ale są one często oparte na średnich europejskich lub globalnych.
                        Dla polskiego betonu: wskaźnik klinkier/cement,
                        miks paliw do pieca i wskaźnik energii elektrycznej różnią się
                        od europejskiej średniej (patrz: artykuł o polskim cemencie).
                        Jeżeli producent dysponuje EPD dla konkretnego wyrobu — należy ją zastosować.
                        Jeżeli nie — należy skonstruować własny model LCI na bazie
                        danych krajowych, a nie używać bezpośrednio ecoinvent dla EU.
                        <strong>Werdykt: użyj EPD dla konkretnego wyrobu dostawcy; jeżeli brak — model krajowy, nie ecoinvent EU.</strong>
                    </div>
                </div>
            </div>
            <div class="process-step">
                <div class="process-step-num">4</div>
                <div class="process-step-content">
                    <div class="process-step-title">Stal konstrukycjna — EAF vs. BF-BOF</div>
                    <div class="process-step-text">
                        W 2023 r. 51,2% stali surowej w Polsce wytopiono w piecach elektrycznych łukowych (EAF),
                        a pozostałą część w wielkich piecach i konwertorach tlenowych (BF-BOF; worldsteel).
                        Ecoinvent może zawierać zmieszane dane dla europejskiej stali.
                        Wskaźniki A1–A3 z czterech deklaracji środowiskowych stali zbrojeniowej z hut EAF w Polsce wynoszą 358–961 kg CO₂e/t
                        (mediana 790) i są znacznie niższe niż dla BF-BOF
                        (~1700–2000 kg CO₂/t) — różnica ma ogromne znaczenie dla LCA budynku
                        z dużym udziałem stali.
                        <strong>Werdykt: weryfikuj źródło stali; użyj EPD producenta lub zbiór danych EAF PL.</strong>
                    </div>
                </div>
            </div>
        </div>

        <h2>Kiedy ecoinvent jest wystarczający?</h2>
        <p>
            Nie każdy zbiór danych ecoinvent wymaga wymiany na dane krajowe.
            Ecoinvent pozostaje najlepszą dostępną opcją dla:
        </p>
        <ul>
            <li><strong>Surowców wydobywanych poza Polską</strong> — ruda żelaza ze Szwecji,
            boksyt z Australii, kruszywo z Belgii. Procesy wydobycia mają globalny charakter
            i polskie dane krajowe nie istnieją.</li>
            <li><strong>Transport międzynarodowy</strong> — transport morski, kolejowy
            i drogowy w krajach innych niż Polska. Tu ecoinvent jest referencją bez alternatywy.</li>
            <li><strong>Procesy chemiczne i pomocnicze</strong> — produkcja środków chemicznych,
            smarów, olejów używanych w procesie produkcji. Brak polskich danych branżowych.</li>
            <li><strong>Procesy o niskim udziale w GWP</strong> — jeżeli dany proces contributes
            poniżej 1–2% do GWP całkowitego, dokładność zbioru danych ma marginalne znaczenie.</li>
        </ul>

        <div class="callout callout-tip">
            <div class="callout-label">Zasada 80/20 w wyborze danych</div>
            <p class="callout-body">
                Zasada: 20% procesów (zwykle energia, główne surowce) odpowiada za 80% GWP.
                Skupiaj się na tych procesach przy wyborze między ecoinvent a danymi krajowymi.
                Dla pozostałych 80% procesów (które dają 20% GWP) ecoinvent jest zazwyczaj
                wystarczający — chociaż zawsze wymagaj udokumentowania wyboru.
            </p>
        </div>

        <h2>Jak to udokumentować metodycznie?</h2>
        <p>
            ISO 14044 §4.7.3.1 wymaga dokumentacji decyzji o jakości danych.
            W raporcie LCA lub EPD należy zdokumentować:
        </p>
        <ul>
            <li><strong>Lista danych wtórnych</strong> — dla każdego istotnego procesu: baza danych,
            nazwa zbioru danych, wersja, rok referencyjny, kraj/region.</li>
            <li><strong>Uzasadnienie wyboru</strong> — dlaczego ten zbiór danych jest najbardziej
            reprezentatywny dla badanego systemu (geograficznie, czasowo, technologicznie).</li>
            <li><strong>Wyniki analizy wrażliwości</strong> — dla zbiorów danych, gdzie istnieje
            alternatywa (ecoinvent vs. krajowy): porównanie wyników przy obydwu opcjach.</li>
            <li><strong>Potwierdzenie weryfikatora</strong> — przy EPD weryfikator sprawdzi
            zgodność wyboru zbiorów danych z PCR i ISO 14044.</li>
        </ul>

        <!-- Comparison table -->
        <div class="card card-lg">
            <div class="card-title">Ecoinvent vs. dane krajowe — podsumowanie dla polskiego EPD</div>
            <div class="portal-table-wrap" tabindex="0" role="region" aria-label="Tabela 1, przewijana poziomo"><table>
                <thead>
                    <tr>
                        <th>Proces</th>
                        <th>Zalecane źródło</th>
                        <th>Uwaga</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Energia elektryczna z sieci</td>
                        <td>Dane energii dobrane do zastosowania; KOBiZE jako źródło części emisji</td>
                        <td>EN 15804+A2 §6.4.3</td>
                    </tr>
                    <tr>
                        <td>Ciepło sieciowe</td>
                        <td>Wskaźnik lokalny / GUS</td>
                        <td>Weryfikacja z ecoinvent PL</td>
                    </tr>
                    <tr>
                        <td>Cement</td>
                        <td>EPD Polska (specific)</td>
                        <td>Jeżeli brak: model krajowy</td>
                    </tr>
                    <tr>
                        <td>Stal (EAF)</td>
                        <td>EPD producenta lub ecoinvent EAF</td>
                        <td>Nie używaj średniej EU BF+EAF</td>
                    </tr>
                    <tr>
                        <td>Transport drogowy w PL</td>
                        <td>Ecoinvent PL (akceptowalne)</td>
                        <td>Niewielka różnica vs EU</td>
                    </tr>
                    <tr>
                        <td>Surowce importowane</td>
                        <td>Dane dostawcy lub reprezentatywny zbiór tła, np. ecoinvent</td>
                        <td>Kraj wydobycia, nie PL</td>
                    </tr>
                </tbody>
            </table></div>
        </div>

        <h2>poLCA: jak uzupełniamy lukę między ecoinvent a Polską</h2>
        <p>
            Polska Baza Danych LCA (poLCA) jest budowana właśnie po to, by uzupełnić
            braki ecoinvent dla polskiego kontekstu. Aktualne priorytety:
        </p>
        <ul>
            <li>Wskaźniki i dokumentacja modeli energii elektrycznej, z zakresem oraz statusem wskazanym dla konkretnej wersji.</li>
            <li>Dane LCI dla kruszywa naturalnego i recycled aggregate z polskich źródeł.</li>
            <li>Dane dla polskich mieszanek betonowych i cementu oparte na danych EPD Polska.</li>
            <li>Transport drogowy w Polsce z aktualną flotą TIR i emisyjnością diesel.</li>
        </ul>
        <p>
            Przejrzyj dostępne zbiory danych w sekcji
            <a href="datasety.html">Baza Zbiorów danych</a> — i porównaj z danymi ecoinvent
            dla swoich kluczowych procesów.
        </p>

        <!-- FAQ -->
        <div class="faq-section">
            <h2 class="faq-section-title">Najczęściej zadawane pytania</h2>

            <details class="faq-item">
                <summary class="faq-q">Czym jest ecoinvent i kiedy go używać?</summary>
                <div class="faq-a">
                    Ecoinvent to szwajcarska baza danych LCI z ponad 18 000 zestawami danych.
                    Jest standardem dla procesów tła (background) w LCA.
                    Dla polskich EPD: odpowiedni dla procesów, gdzie brak krajowych danych
                    i różnica między średnią a Polską jest nieistotna dla wyniku.
                </div>
            </details>

            <details class="faq-item">
                <summary class="faq-q">Dla których procesów ecoinvent może prowadzić do błędów w polskim LCA?</summary>
                <div class="faq-a">Dobór danych energii zależy od zastosowania, kontroli nad procesem i dokumentów dotyczących dostawy. Sam kraj produkcji nie rozstrzyga wyboru między miksem konsumpcyjnym, rezydualnym i danymi dostawcy. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</div>
            </details>

            <details class="faq-item">
                <summary class="faq-q">Jak sprawdzić, która wersja ecoinvent jest użyta w moim oprogramowaniu?</summary>
                <div class="faq-a">Wersję bazy i model systemowy odczytaj z ustawień projektu oraz metadanych zbioru. Dawne numery wersji podane w tym artykule nie są informacją o najnowszym wydaniu.</div>
            </details>

            <details class="faq-item">
                <summary class="faq-q">Czy można mieszać dane z ecoinvent i KOBiZE w jednym LCA?</summary>
                <div class="faq-a">Można łączyć źródła po uzgodnieniu granic, alokacji i metody oceny wpływu. Sam wskaźnik CO₂ nie zastępuje pełnego zbioru energii. Źródła i uzupełnienia trzeba opisać w raporcie.</div>
            </details>
        </div>

        <hr class="blog-post-divider">

        <section class="article-sources"><h2>Źródła</h2><ul><li>Wernet G. i in. (2016), „The ecoinvent database version 3”,
            Int. J. Life Cycle Assess. 21(9):1218–1230;</li><li>ecoinvent v3.10 (2023), dokumentacja systemu alokacji cutoff;</li><li>KOBiZE (2024), Wskaźniki emisyjności CO₂ dla energii elektrycznej, dane za 2023;</li><li>EN 15804+A2:2019/A1:2021, §6.3.6 (dane wtórne), §6.4.3 (energia elektryczna);</li><li>ISO 14044:2006, §4.7.3.1 (jakość danych);</li><li>GUS (2024), Energia 2023 — struktura produkcji ciepła sieciowego;</li><li>EPD Polska / Multicert (2023–2025), rejestr EPD dla cementu i stali.</li></ul></section>
    </div>
</body>
</html>
