<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Residual mix, AIB i KOBiZE — trzy wskaźniki emisji dla energii elektrycznej — poLCA Blog</title>
    <meta name="description" content="Historyczne zestawienie modelu poLCA 2024, miksu rezydualnego i fotowoltaiki. Dobór danych zależy od zastosowania i dokumentacji dostawy; dawne trzy poziomy nie są uniwersalną hierarchią.">
    <link rel="canonical" href="https://polca.org.pl/blog-residual-mix-aib-kobize.html">
    <meta property="og:type" content="article">
    <meta property="og:title" content="Residual mix, AIB i KOBiZE — trzy wskaźniki emisji dla energii elektrycznej — poLCA Blog">
    <meta property="og:description" content="Historyczne zestawienie modelu poLCA 2024, miksu rezydualnego i fotowoltaiki. Dobór danych zależy od zastosowania i dokumentacji dostawy; dawne trzy poziomy nie są uniwersalną hierarchią.">
    <meta property="og:url" content="https://polca.org.pl/blog-residual-mix-aib-kobize.html">
    <meta property="og:site_name" content="poLCA — Polska Baza Danych LCA">
    <meta property="og:locale" content="pl_PL">
    <meta property="og:image" content="https://polca.org.pl/images/blog-residual-mix-aib-kobize.jpg">
    <meta property="article:published_time" content="2026-02-18T00:00:00+01:00">
    <meta property="article:author" content="poLCA — Polska Baza Danych LCA">
    <meta property="article:section" content="Metodyka LCA">
    <meta property="article:tag" content="residual mix">
    <meta property="article:tag" content="AIB">
    <meta property="article:tag" content="KOBiZE">
    <meta property="article:tag" content="poLCA-EN-PL-2024">
    <meta property="article:tag" content="Scope 2">
    <meta property="article:tag" content="Gwarancje Pochodzenia">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Residual mix, AIB i KOBiZE — trzy wskaźniki emisji dla energii elektrycznej">
    <meta name="twitter:description" content="Historyczne zestawienie modelu poLCA 2024, miksu rezydualnego i fotowoltaiki. Dobór danych zależy od zastosowania i dokumentacji dostawy; dawne trzy poziomy nie są uniwersalną hierarchią.">
    <meta name="twitter:image" content="https://polca.org.pl/images/blog-residual-mix-aib-kobize.jpg">
    <script type="application/ld+json">{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "https://polca.org.pl/blog-residual-mix-aib-kobize.html",
      "headline": "Residual mix, AIB i KOBiZE — trzy wskaźniki emisji dla energii elektrycznej i kiedy stosować każdy z nich",
      "description": "Historyczne zestawienie modelu poLCA 2024, miksu rezydualnego i fotowoltaiki. Dobór danych zależy od zastosowania i dokumentacji dostawy; dawne trzy poziomy nie są uniwersalną hierarchią.",
      "url": "https://polca.org.pl/blog-residual-mix-aib-kobize.html",
      "datePublished": "2026-02-18",
      "dateModified": "2026-02-18",
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
        "residual mix",
        "AIB",
        "KOBiZE",
        "Scope 2",
        "Gwarancje Pochodzenia",
        "emisje CO2",
        "energia elektryczna",
        "EPD",
        "LCA",
        "GHG Protocol"
      ],
      "about": [
        {
          "@type": "Thing",
          "name": "Residual mix energii elektrycznej"
        },
        {
          "@type": "Thing",
          "name": "Association of Issuing Bodies (AIB)"
        },
        {
          "@type": "Thing",
          "name": "KOBiZE"
        },
        {
          "@type": "Thing",
          "name": "Raportowanie emisji Scope 2"
        },
        {
          "@type": "Thing",
          "name": "Gwarancje Pochodzenia (GO)"
        }
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
          "name": "Residual mix, AIB i KOBiZE — trzy wskaźniki emisji dla energii elektrycznej"
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
                Residual mix, AIB i KOBiZE — trzy wskaźniki emisji dla energii elektrycznej i kiedy stosować każdy z nich
            </h1>
<p class="article-lead">Artykuł zestawia historyczne założenia: 0,599 kg CO₂e/kWh dla składnika kopalnego modelu poLCA 2024, 0,808 dla ówczesnego wariantu rezydualnego i 0,041 dla wariantu fotowoltaiki. Te liczby nie tworzą uniwersalnej hierarchii wyboru energii. Dobór danych energii zależy od zastosowania, kontroli nad procesem i dokumentów dotyczących dostawy. Sam kraj produkcji nie rozstrzyga wyboru między miksem konsumpcyjnym, rezydualnym i danymi dostawcy. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p>
<aside class="legacy-note" aria-label="Informacja o wersji"><p><strong>Informacja o wydaniu.</strong> Dokument historyczny: model energii za 2024 r. Wartość 0,599 kg CO₂e/kWh oznacza składnik kopalny (GWP-fossil), nie GWP-total. Dawna hierarchia trzech poziomów nie jest uniwersalną instrukcją doboru energii do deklaracji środowiskowej. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p></aside>
<aside class="legacy-note">
                <strong>Aktualizacja wartości po publikacji wpisu.</strong>
                Tekst opisuje stan na luty 2026 i podaje wartość rezydualną z wydania AIB za rok 2024.
                W dniu 28 maja 2026 AIB opublikowało wydanie za rok 2025, w którym wartość dla Polski
                wynosi <strong>0,727 kg CO₂/kWh</strong> wobec 0,808 z poprzedniego wydania.
                Zasada wyboru poziomu opisana w tekście pozostaje bez zmian.
                Zob. <a href="rejestr-zmian.html">rejestr przeglądów i zmian</a>.
            </aside>
<figure class="article-figure"><img src="images/blog-residual-mix-aib-kobize.jpg" alt="Elektrownia z wieżami chłodniczymi" loading="lazy"></figure>
<ol class="article-findings">
<li>Artykuł zestawia historyczne założenia: 0,599 kg CO₂e/kWh dla składnika kopalnego modelu poLCA 2024, 0,808 dla ówczesnego wariantu rezydualnego i 0,041 dla wariantu fotowoltaiki.</li>
<li>Te liczby nie tworzą uniwersalnej hierarchii wyboru energii.</li>
<li>Dobór danych energii zależy od zastosowania, kontroli nad procesem i dokumentów dotyczących dostawy.</li>
</ol>
<aside class="article-tools"><a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a></aside>
<div class="article-prose"><div class="card card-lg section-gap">
        <div class="card-title">3-poziomowa hierarchia wskaźnika energii elektrycznej w Polsce (c-PCR-BET v1.3 §6.3, dane za 2024)</div>
        <div class="vcol-chart" style="height: 260px;">
            <div class="vcol-group">
                <div class="vcol-value">0,599</div>
                <div class="vcol-bar gray" style="height: 74%;"></div>
            </div>
            <div class="vcol-group">
                <div class="vcol-value" style="font-weight: 700;">0,808</div>
                <div class="vcol-bar ink" style="height: 100%;"></div>
            </div>
            <div class="vcol-group">
                <div class="vcol-value">0,041</div>
                <div class="vcol-bar green" style="height: 5%; min-height: 4px;"></div>
            </div>
        </div>
        <div class="vcol-labels">
            <div class="vcol-label">Model 2024 v9.1<br>historyczny GWP-fossil</div>
            <div class="vcol-label">Historyczny wariant rezydualny</div>
            <div class="vcol-label">Historyczny wariant fotowoltaiki</div>
        </div>
        <p class="comp-note">Historyczne wartości: poLCA-EN-PL-2024 v9.1 0,599 kg CO₂e/kWh (GWP-fossil), wariant rezydualny 0,808 i fotowoltaika 0,041. Źródła podano w artykule. Dawny podział na poziomy nie określa uniwersalnego pierwszeństwa danych.</p>
    </div>

    <h2>Skąd biorą się dwa różne wskaźniki dla tego samego kraju?</h2>

        <div class="margin-note">
            <div class="margin-note-label">Kluczowe rozróżnienie</div>
            KOBiZE = fizyczny miks sieci.<br>
            AIB residual mix = miks po „wyjęciu” OZE rozliczonego certyfikatami GO.<br>
            Oba wskaźniki mierzą tę samą energię — innymi metodami.
        </div>

        <p>
            W Polsce w 2023 roku węgiel odpowiadał za ok. 60% produkcji energii elektrycznej.
            Jednocześnie dynamicznie rośnie udział OZE — farmy wiatrowe i fotowoltaika wytwarzały
            łącznie już ok. 20% energii. Na potrzeby raportowania emisji te same kilowatogodziny
            mogą być liczone na dwa fundamentalnie różne sposoby:
        </p>
        <ul>
            <li>
                <strong>Metoda lokalizacyjna (location-based)</strong> — patrzymy na fizyczny miks sieci
                energetycznej. Każda zużyta kWh niesie ze sobą emisje proporcjonalne do średniego
                koszyka wytwarzania w danym kraju. To jest właśnie wskaźnik KOBiZE.
            </li>
            <li><strong>Metoda rynkowa:</strong> uwzględnia dokumenty dostawy i przypisanie atrybutów energii. Sama gwarancja pochodzenia nie oznacza zerowego wyniku w całym cyklu życia. Miks rezydualny nie musi być w każdym kraju wyższy od średniego miksu.</li>
        </ul>
        <p>
            Oba podejścia są prawidłowe w swoich kontekstach. Problem pojawia się, gdy stosuje się
            je zamiennie albo nieadekwatnie do metody raportowania.
        </p>

        <h2>Co dokładnie mierzy KOBiZE</h2>
        <p>
            Krajowy Ośrodek Bilansowania i Zarządzania Emisjami (KOBiZE), działający w strukturach
            Instytutu Ochrony Środowiska — Państwowego Instytutu Badawczego, publikuje corocznie
            oficjalny wskaźnik emisyjności CO₂ dla energii elektrycznej w Polsce.
        </p>
        <p>
            Wskaźnik ten jest <strong>średnią ważoną emisji ze wszystkich źródeł wytwarzania</strong>
            podłączonych do Krajowego Systemu Elektroenergetycznego: węgla kamiennego, węgla brązowego,
            gazu, OZE, kogeneracji. Liczy się tu fizyczne spalanie paliw i związana z nim emisja CO₂,
            podzielona przez całkowitą produkcję energii elektrycznej netto.
        </p>
        <p>Wskaźnik KOBiZE dla odbiorcy końcowego za 2024 r. wynosi 0,553 kg CO₂/kWh. Opisuje CO₂, a nie kompletny wynik oceny cyklu życia. Historyczny model poLCA-EN-PL-2024 v9.1 podaje 0,599 kg CO₂e/kWh dla składnika kopalnego (GWP-fossil). Wartości mają różny zakres. Dane KOBiZE mogą zasilać część modelu, lecz nie potwierdzają same zgodności całego zbioru. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p>

        <h2>Mechanizm residual mix i rola AIB</h2>
        <p>Przy każdym użyciu raportu AIB lub KOBiZE należy odczytać rok danych i datę publikacji z konkretnego wydania. Dawne stwierdzenie, że w całym 2026 r. dostępne są wyłącznie dane rezydualne za 2023 r., nie jest aktualną informacją o dostępności.</p>
        <p>Gwarancje pochodzenia dokumentują atrybuty energii. Ich wykorzystanie wymaga spełnienia odpowiednich kryteriów i wykluczenia podwójnego przypisania. Sam zakup gwarancji nie nadaje energii zerowego wyniku w całym cyklu życia.</p>

        <div class="pull-quote-lg">
            <p>Miks rezydualny opisuje energię po odjęciu atrybutów przypisanych odbiorcom. Jego emisyjności względem średniego miksu nie należy przyjmować z góry.</p>
            <cite>AIB, European Residual Mixes — definicja operacyjna</cite>
        </div>

        <p>
            Dla Polski jest to efekt szczególnie wyraźny. Polscy wytwórcy OZE aktywnie
            uczestniczą w rynku GO, eksportując certyfikaty m.in. do Europy Zachodniej.
            Oznacza to, że krajowe farmy wiatrowe i fotowoltaika są „przypisane”
            zagranicznym nabywcom GO — a polskim odbiorcom bez certyfikatów
            pozostaje miks mocno zdominowany przez węgiel.
        </p>

        <h2>Liczby: jak bardzo się różnią?</h2>
        <p>Historyczne zestawienie zawierało 0,599 kg CO₂e/kWh dla modelu 2024 i 0,808 dla wariantu rezydualnego. Nie są to dwa poziomy jednej skali jakości. Składnik operacyjny 0,528 stanowi około 88% sumy modelu 2024; surowy wskaźnik KOBiZE 0,553 nie jest tą składową.</p>
        <p>Różnica między przywołanymi liczbami nie wyznacza poprawnego sposobu modelowania. Dla deklaracji produktu trzeba najpierw ustalić zakres procesu oraz dokumentację energii. Dobór danych energii zależy od zastosowania, kontroli nad procesem i dokumentów dotyczących dostawy. Sam kraj produkcji nie rozstrzyga wyboru między miksem konsumpcyjnym, rezydualnym i danymi dostawcy. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p>

        <!-- Tabela: kiedy co stosować -->
        <h2>Kiedy stosować który wskaźnik?</h2>

        <div class="card card-lg">
            <div class="portal-table-wrap" tabindex="0" role="region" aria-label="Tabela 1, przewijana poziomo"><table>
                <thead>
                    <tr>
                        <th>Kontekst raportowania</th>
                        <th>Właściwy wskaźnik</th>
                        <th>Podstawa</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>LCA / EPD wyrobów betonowych (EN 15804+A2)</td>
                        <td>Dobór zbioru do procesu i dokumentów dostawy; model 2024 jest historycznym wariantem</td>
                        <td><a href="/jak-korzystac.html">Zasady doboru danych</a></td>
                    </tr>
                    <tr>
                        <td>GHG Protocol Scope 2 — location-based</td>
                        <td><strong>KOBiZE</strong> end-user (553 kg CO₂/MWh za 2024) — średni miks lokalizacyjny</td>
                        <td>GHG Protocol Scope 2 Guidance (2015)</td>
                    </tr>
                    <tr>
                        <td>GHG Protocol Scope 2 — market-based, bez GO / PPA</td>
                        <td><strong>AIB residual mix</strong></td>
                        <td>GHG Protocol Scope 2 Guidance (2015), AIB ERM</td>
                    </tr>
                    <tr>
                        <td>GHG Protocol Scope 2 — market-based, z GO OZE</td>
                        <td><strong>0 kg CO₂/MWh</strong> (dostawca z GO)</td>
                        <td>Współczynnik emisji dostawcy z GO</td>
                    </tr>
                    <tr>
                        <td>EPD z opcją market-based (niektóre PCR)</td>
                        <td><strong>AIB residual mix</strong> lub wsp. dostawcy z GO</td>
                        <td>PCR specificzne, np. IBU PCR Part A v2.0</td>
                    </tr>
                </tbody>
            </table></div>
        </div>

        <h2>Praktyczna pułapka: „zielona energia” bez GO</h2>
        <p>
            Coraz więcej polskich firm deklaruje, że kupuje energię ze źródeł odnawialnych,
            ponieważ dostawca prądu umieścił taką informację w ofercie. Tymczasem sam fakt
            zakupu energii od dostawcy OZE <strong>nie wystarczy</strong> do zastosowania
            wskaźnika 0 kg CO₂/MWh w raportowaniu Scope 2 market-based.
        </p>
        <p>
            Zgodnie z GHG Protocol, metoda rynkowa wymaga potwierdzenia transferu
            <em>atrybutu środowiskowego</em> — czyli faktycznego przekazania Gwarancji
            Pochodzenia na nabywcę. Jeżeli GO są sprzedawane oddzielnie przez dostawcę
            (co jest standardem rynkowym), firma kupująca „zieloną” taryfę bez GO
            wciąż musi zastosować AIB residual mix — a nie 0 ani średnią KOBiZE.
        </p>

        <div class="quote-block">
            <p>
                Taryfa „eko” bez certyfikatów GO to nie zielona energia w rozumieniu GHG
                Protocol. W raportowaniu market-based Scope 2 stosujemy residual mix AIB,
                który dla Polski jest <em>wyższy</em> niż średnia KOBiZE — bo OZE zostały
                już „zabrane” przez tych, którzy faktycznie kupili GO.
            </p>
        </div>

        <h2>Opóźnienie danych AIB i problem aktualności</h2>
        <p>Przy każdym użyciu raportu AIB lub KOBiZE należy odczytać rok danych i datę publikacji z konkretnego wydania. Dawne stwierdzenie, że w całym 2026 r. dostępne są wyłącznie dane rezydualne za 2023 r., nie jest aktualną informacją o dostępności.</p>
        <p>
            W raportach korporacyjnych (np. GRI, CSRD, CDP) należy konsekwentnie stosować
            dane za rok referencyjny raportu lub — jeżeli nie są dostępne — dane za
            ostatni opublikowany rok z wyraźnym przypisem. Mieszanie lat referencyjnych
            dla KOBiZE i AIB jest błędem metodycznym, nawet jeżeli oba wskaźniki
            są samo w sobie poprawne.
        </p>

        <h2>Implikacje dla poLCA i EPD — 3-poziomowa hierarchia</h2>
        <p>
            Baza poLCA i c-PCR-BET-EPD-PL:2026 v1.3 §6.3 wprowadzają <strong>3-poziomową hierarchię</strong>
            wskaźnika energii elektrycznej dla EPD wyrobów betonowych:
        </p>
        <ul>
            <li>Historyczne założenie modelu 2024: 0,599 kg CO₂e/kWh dla składnika kopalnego. Nie jest automatycznym wyborem dla każdego procesu.</li>
            <li><strong>Poziom 2 — market-based (residual mix AIB):</strong>
                <strong>0,808 kg CO₂e/kWh</strong> — dopuszczalny tylko przy równoczesnym raportowaniu Poziomu 1 jako referencji
                (c-PCR-BET v1.3 §6.3.3; Dyr. (UE) 2018/2001 art. 19).</li>
            <li><strong>Poziom 3 — PV on-site:</strong> <strong>0,041 kg CO₂e/kWh</strong> — wyłącznie dla udokumentowanej
                własnej instalacji fotowoltaicznej (c-PCR-BET v1.3 §6.3.1 Poziom 3; ÖKOBAUDAT 2024 PV).</li>
        </ul>
        <p>Dobór danych energii zależy od zastosowania, kontroli nad procesem i dokumentów dotyczących dostawy. Sam kraj produkcji nie rozstrzyga wyboru między miksem konsumpcyjnym, rezydualnym i danymi dostawcy. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p>
        <p>
            Wskaźnik AIB residual mix nie jest stosowany w modelach LCI poLCA — ale ma
            bezpośrednie znaczenie dla raportowania korporacyjnego Scope 2 przez firmy
            będące naszymi użytkownikami. Jeżeli producent opracowuje EPD i jednocześnie
            raportuje emisje korporacyjne (np. w ramach CSRD), powinien świadomie stosować
            oba wskaźniki — w odpowiednich kontekstach — i dokumentować tę różnicę
            w metodyce. Wytyczne w tym zakresie udostępnia
            <a href="https://www.epd.org.pl" target="_blank" rel="noopener noreferrer">program EPD Polska</a>.
        </p>
        <p>
            Próba „spójności” przez używanie jednego wskaźnika we wszystkich
            raportach równocześnie skutkuje błędem w przynajmniej jednym z nich.
        </p>

        <hr class="blog-post-divider">

        <section class="article-sources"><h2>Źródła</h2><ul><li>Multicert Sp. z o.o. (2026), MET-001:2026 — wskaźnik emisyjności energii elektrycznej PL (poLCA-EN-PL-2024 v9.1) = 0,599 kg CO₂e/kWh;</li><li>Multicert Sp. z o.o. (2026), MET-002:2026 — wyłączenie wskaźników KOBiZE z LCA EPD wyrobów budowlanych;</li><li>c-PCR-BET-EPD-PL:2026 v1.3 §6.3 — 3-poziomowa hierarchia wskaźnika energii;</li><li>KOBiZE (2025), „Wskaźniki emisyjności CO₂” za rok 2024 (end-user: 553 kg CO₂/MWh);</li><li>AIB (2025), „European Residual Mixes 2024” (PL: 0,808 kg CO₂e/kWh);</li><li>GHG Protocol, „Scope 2 Accounting Guidance” (2015);</li><li>EN 15804+A2:2019/A1:2021, §6.4.3;</li><li>ISO 14067:2018, §6.4.9.4;</li><li>Rozporządzenie (UE) 2018/2001 (RED II), art. 19 — Gwarancje Pochodzenia.
         <span class="legacy-citation-note">MET-002 przywołano pod tytułem wydania historycznego; <a href="/metodyki/MET-002-energia.html">zob. korektę HTML</a>. Określenie „3-poziomowa hierarchia” opisuje wcześniejsze ujęcie.</span></li></ul></section>

    </div>
</body>
</html>
