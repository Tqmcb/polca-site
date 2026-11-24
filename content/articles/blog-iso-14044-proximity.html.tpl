<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zasada proximity w ISO 14044 — co norma mówi o wyborze danych LCI — poLCA Blog</title>
    <meta name="description" content="Historyczne omówienie doboru danych i przykłady dla wskazanych lat. Reprezentatywność i możliwość wykorzystania należy ocenić dla konkretnego wyrobu oraz zastosowania.">
    <link rel="canonical" href="https://polca.org.pl/blog-iso-14044-proximity.html">
    <meta property="og:type" content="article">
    <meta property="og:title" content="Zasada proximity w ISO 14044 — co norma mówi o wyborze danych LCI — poLCA Blog">
    <meta property="og:description" content="Historyczne omówienie doboru danych i przykłady dla wskazanych lat. Reprezentatywność i możliwość wykorzystania należy ocenić dla konkretnego wyrobu oraz zastosowania.">
    <meta property="og:url" content="https://polca.org.pl/blog-iso-14044-proximity.html">
    <meta property="og:site_name" content="poLCA — Polska Baza Danych LCA">
    <meta property="og:locale" content="pl_PL">
    <meta property="og:image" content="https://polca.org.pl/images/blog-iso-14044-proximity.jpg">
    <meta property="article:published_time" content="2025-10-28T00:00:00+01:00">
    <meta property="article:author" content="poLCA — Polska Baza Danych LCA">
    <meta property="article:section" content="Metodyka LCA">
    <meta property="article:tag" content="ISO 14044">
    <meta property="article:tag" content="LCI">
    <meta property="article:tag" content="jakość danych">
    <meta property="article:tag" content="reprezentatywność">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Zasada proximity w ISO 14044 — co norma mówi o wyborze danych LCI">
    <meta name="twitter:description" content="Historyczne omówienie doboru danych i przykłady dla wskazanych lat. Reprezentatywność i możliwość wykorzystania należy ocenić dla konkretnego wyrobu oraz zastosowania.">
    <meta name="twitter:image" content="https://polca.org.pl/images/blog-iso-14044-proximity.jpg">
    <script type="application/ld+json">{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "https://polca.org.pl/blog-iso-14044-proximity.html",
      "headline": "Zasada proximity w ISO 14044 — co norma mówi o wyborze danych LCI",
      "description": "Historyczne omówienie doboru danych i przykłady dla wskazanych lat. Reprezentatywność i możliwość wykorzystania należy ocenić dla konkretnego wyrobu oraz zastosowania.",
      "url": "https://polca.org.pl/blog-iso-14044-proximity.html",
      "datePublished": "2025-10-28",
      "dateModified": "2025-10-28",
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
        "ISO 14044",
        "LCI",
        "jakość danych LCA",
        "reprezentatywność geograficzna",
        "proxy data",
        "dane pierwotne",
        "dane wtórne",
        "ecoinvent"
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
          "name": "Zasada proximity w ISO 14044"
        }
      ]
    }
  ]
}</script>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <meta name="metadata_revision" content="2026-10-18">
</head>
<body data-minutes="8">
<h1>
                Zasada proximity w ISO 14044 — co norma mówi o wyborze danych LCI
            </h1>
<p class="article-lead">
                ISO 14044 nie mówi wprost „użyj danych krajowych”. Mówi coś precyzyjniejszego:
                dane inwentaryzacyjne powinny być reprezentatywne dla badanego systemu.
                Co to oznacza w praktyce i dlaczego europejska średnia dla cementu
                może być błędem metodycznym w polskim EPD.
            </p>
<aside class="legacy-note" aria-label="Informacja o wersji"><p><strong>Informacja o wydaniu.</strong> Dane i przykłady odnoszą się do wydań oraz lat wskazanych w artykule. Nie zastępują danych konkretnego wyrobu lub zakładu. <a href="/jak-korzystac.html">Zasady doboru danych</a> · <a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</p></aside>
<figure class="article-figure"><img src="images/blog-iso-14044-proximity.jpg" alt="Lupa na dokumentach analitycznych" loading="lazy"></figure>
<ol class="article-findings">
<li>ISO 14044 wymaga, by dane LCI były <strong>reprezentatywne</strong> pod trzema względami: geograficznym, czasowym i technologicznym.</li>
<li>„Proximity” to nieformalna nazwa zasady, że im bliżej danych do rzeczywistego systemu, tym wyższa jakość LCA — norma tego wymaga, nawet jeśli nie używa tego słowa.</li>
<li>Dane generyczne (ecoinvent, bazy europejskie) są dopuszczalne dla procesów tła — dla procesów pierwszego planu wymagane są dane pierwotne lub branżowe.</li>
<li>Dostępność danych krajowych nie rozstrzyga automatycznie wyboru. Należy porównać ich reprezentatywność, granice, kompletność i dokumentację z innymi dostępnymi danymi.</li>
</ol>
<ul class="article-values">
<li><strong>3 wymiary</strong> <span>Reprezentatywność danych LCI wg ISO 14044:<br>geograficzna, czasowa, technologiczna</span></li>
<li><strong>5 lat</strong> <span>Maksymalny wiek danych pierwotnych<br>akceptowany w większości PCR</span></li>
<li><strong>Różne zakresy</strong> <span>599 kg CO₂e/MWh i około 210 kg CO₂/MWh<br>opisują różne granice; nie stanowią rankingu</span></li>
</ul>
<aside class="article-tools"><div class="card-title">Narzędzia LCA poLCA</div>
        <p class="card-text">
            Tabela polskich wskaźników emisji i przeliczniki jednostek — pomocne przy
            stosowaniu zasady proximity i doborze danych LCI.
        </p>
        <a href="narzedzia.html">
            Przejdź do narzędzi
            <svg width="14" height="14" viewbox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </a></aside>
<div class="article-prose"><h2>Skąd pochodzi pojęcie „proximity” w LCA?</h2>
        <p>
            Termin <em>proximity principle</em> nie występuje wprost w tekście ISO 14044.
            Pochodzi z praktyki LCA i literatury akademickiej jako skrót myślowy dla wymagania
            sekcji 4.7.3.1 normy dotyczącego jakości danych. Norma stanowi,
            że dane inwentaryzacyjne powinny <strong>odzwierciedlać właściwości technologiczne,
            geograficzne i czasowe</strong> badanego systemu.
        </p>
        <p>
            W praktyce zasada ta rozstrzyga kluczowe pytanie każdego LCA:
            czy wolno mi użyć danych z globalnej bazy generycznej,
            czy muszę pozyskać dane specyficzne dla mojego kraju, branży, instalacji?
        </p>

        <div class="callout callout-definition">
            <div class="callout-label">Definicja normatywna</div>
            <p class="callout-body">
                <strong>ISO 14044:2006, §4.7.3.1:</strong> „Dane powinny być
                reprezentatywne dla definiowanych procesów jednostkowych objętych granicami systemu.
                Należy udokumentować czasą reprezentatywność danych,
                geograficzną reprezentatywność danych oraz technologiczną
                reprezentatywność danych.“
            </p>
        </div>

        <h2>Trzy wymiary reprezentatywności danych</h2>

        <div class="process-steps">
            <div class="process-step">
                <div class="process-step-num">1</div>
                <div class="process-step-content">
                    <div class="process-step-title">Reprezentatywność geograficzna</div>
                    <div class="process-step-text">
                        Dane powinny pochodzić z tego samego kraju lub regionu co badany system.
                        Dla polskiego producenta cementu: dane o emisjach z klinkieryzacji
                        powinny odzwierciedlać polskie surowce (skład margli i wapieni),
                        polski miks paliw do pieca cementowego, polską sieć energetyczną.
                        Użycie řredniej europejskiej oznacza systematyczne przesuniecie wyniku
                        — w przypadku Polski zwykle zaniżone GWP (europejska sieć emituje ok. 2× mniej niż polska).
                    </div>
                </div>
            </div>
            <div class="process-step">
                <div class="process-step-num">2</div>
                <div class="process-step-content">
                    <div class="process-step-title">Reprezentatywność czasowa</div>
                    <div class="process-step-text">
                        Dane powinny pochodzić z okresu odpowiadającego rokowi referencyjnemu EPD.
                        Wskaźnik KOBiZE jest publikowany corocznie — użycie wskaźnika sprzed 5 lat
                        dla aktualnej EPD jest błędem. Podobnie: dane o emisjach z produkcji stali
                        sprzed 2015 r. mogą nie uwzględniać zmian technologicznych w piecach elektrycznych.
                        Większość PCR wymaga, by dane pierwotne pochodziły z ostatnich 5 lat.
                    </div>
                </div>
            </div>
            <div class="process-step">
                <div class="process-step-num">3</div>
                <div class="process-step-content">
                    <div class="process-step-title">Reprezentatywność technologiczna</div>
                    <div class="process-step-text">
                        Dane powinny opisywać tę samą technologię produkcji co badany system.
                        Producent asfaltobetonu z nowoczesną suszarnią kontraprzepływową
                        nie może użyć danych dla starszych technologii współprądowych.
                        Producent stali z pieca elektrycznego — nie może stosować średniej
                        włączającej piece martenowskie. Technologia bezpośrednio determinuje
                        wielkość emisji i zużycie energii.
                    </div>
                </div>
            </div>
        </div>

        <h2>Hierarchia danych w LCA: co jest „pierwszy plan”, co „tło”</h2>
        <p>
            ISO 14044 i praktyka LCA dzielą procesy na dwie kategorie z różnymi wymaganiami:
        </p>

        <div class="card card-lg">
            <div class="card-title">Procesy pierwszego planu vs. tła</div>
            <div class="portal-table-wrap" tabindex="0" role="region" aria-label="Tabela 1, przewijana poziomo"><table>
                <thead>
                    <tr>
                        <th>Kategoria</th>
                        <th>Definicja</th>
                        <th>Wymagane dane</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Foreground<br>(pierwszy plan)</td>
                        <td>Procesy, na które producent ma bezpośredni wpływ: własna produkcja, transport wewnętrzny, instalacje na budowie</td>
                        <td>Dane pierwotne (pomiary, faktury, bilanse)</td>
                    </tr>
                    <tr>
                        <td>Background<br>(tło)</td>
                        <td>Procesy poza kontrolą producenta: wydobycie surowców, produkcja energii w sieci, transport zewnętrzny</td>
                        <td>Dane wtórne (bazy: ecoinvent, poLCA) — z zachowaniem proximity</td>
                    </tr>
                </tbody>
            </table></div>
        </div>

        <p>Dla procesów tła należy ocenić zakres, jednostkę, reprezentatywność i dokumentację dostępnych danych. KOBiZE może dostarczać część danych emisyjnych, lecz samo CO₂ nie zastępuje pełnego zbioru cyklu życia energii. Krajowe pochodzenie źródła nie przesądza automatycznie o jego wyborze.</p>

        <div class="callout callout-warning">
            <div class="callout-label">Korekta wcześniejszego porównania</div>
            <p class="callout-body">Wcześniejsze twierdzenie o zaniżeniu GWP o ok. 50% oraz automatycznym naruszeniu §4.7.3.1 ISO 14044 zostało wycofane. Zestawienie wskaźników o różnych granicach nie uzasadnia takiego wniosku ani odrzucenia EPD. Najpierw trzeba sprawdzić zakres porównywanych danych.</p>
        </div>

        <h2>Dane proxy: kiedy są dopuszczalne?</h2>
        <p>
            Sytuacje, gdy idealne dane (specyficzne, aktualne, o właściwej technologii)
            nie są dostępne, są w LCA normalne. Norma dopuszcza stosowanie danych proxy
            (zastępczych), pod warunkami:
        </p>
        <ul>
            <li><strong>Uzasadnienie wyboru</strong> — należy udokumentować, dlaczego
            konkretne proxy jest najlepszą dostępną alternatywą i jak blisko
            odpowiada rzeczywistemu procesowi.</li>
            <li><strong>Analiza wrażliwości</strong> — należy pokazać, że wybór proxy
            nie zmienia istotnie wyników lub wniosków. Jeżeli zmienia — konieczne
            są lepsze dane.</li>
            <li><strong>Opis niepewności</strong> — ISO 14044 §4.7.3 wymaga oceny
            jakości danych; stosowanie proxy bez dokumentacji niepewności
            jest niezgodne z normą.</li>
        </ul>

        <h2>Proximity w kontekście EN 15804+A2 i EPD</h2>
        <p>
            EN 15804+A2 precyzuje wymagania ISO 14044 dla kontekstu wyrobów budowlanych.
            Kilka kluczowych zapisów:
        </p>
        <ul>
            <li>Dane pierwotne dla procesów pierwszego planu: wymagane z co najmniej jednego roku
            produkcji w okresie ostatnich 5 lat (§6.3.5).</li>
            <li>Wskaźnik energii dobiera się do zastosowania, kontroli nad procesem i dokumentacji dostawy. Historyczne odwołanie do §6.4.3 nie uzasadnia uniwersalnego nakazu fizycznego miksu krajowego.</li>
            <li>Jakość danych wtórnych: należy stosować dane „odpowiednie dla geografii
            badanego systemu”, preferencja dla danych krajowych nad globalnymi (§6.3.6).</li>
        </ul>

        <div class="callout callout-tip">
            <div class="callout-label">Zasada praktyczna</div>
            <p class="callout-body">Źródła do rozważenia w ocenie danych: <strong>(1)</strong> własne pomiary; <strong>(2)</strong> dane branżowe, w tym <a href="https://www.epd.org.pl" target="_blank" rel="noopener noreferrer">EPD Polska</a> i źródła KOBiZE; <strong>(3)</strong> dane tła dla Polski, np. ecoinvent; <strong>(4)</strong> inne reprezentatywne dane europejskie lub globalne. To nie jest stała hierarchia. Wybór wymaga uzasadnienia zakresu, reprezentatywności oraz ograniczeń źródła.</p>
        </div>

        <h2>Dlaczego to ma znaczenie dla polskich producentów?</h2>
        <p>
            Polska ma jeden z wyższych wskaźników emisji energii elektrycznej w Europie.
            Oznacza to, że polskie EPD oparte na krajowych danych będą wykazywać wyższe GWP
            niż porównywalne EPD europejskie — nawet przy tej samej efektywności produkcji.
        </p>
        <p>
            To tworzy pozorną pokusę: użyć europejskiej średniej, żeby poprawić wynik.
            Ale jest to błąd metodyczny, który dewaluuje EPD i może być zakwestionowany
            przez weryfikatora, zamawiającego lub program EPD.
            Rzetelna EPD oparta na danych krajowych jest wiarygodna —
            i lepiej pozycjonuje producenta w długim terminie, gdy unijny miks energetyczny będzie się zielenił.
        </p>

        <!-- FAQ -->
        <div class="faq-section">
            <h2 class="faq-section-title">Najczęściej zadawane pytania</h2>

            <details class="faq-item">
                <summary class="faq-q">Czym jest zasada proximity w ISO 14044?</summary>
                <div class="faq-a">
                    Zasada proximity (bliskiegości danych) oznacza, że dane LCI powinny być
                    jak najbliższe badanemu systemowi pod względem geograficznym, czasowym
                    i technologicznym. Im mniejsza odległość między danymi a rzeczywistym
                    procesem, tym wyższa jakość LCA.
                </div>
            </details>

            <details class="faq-item">
                <summary class="faq-q">Jakie są trzy wymiary reprezentatywności danych LCI?</summary>
                <div class="faq-a">
                    ISO 14044 §4.7.3.1 definiuje trzy wymiary:
                    (1) reprezentatywność geograficzna — czy dane pochodzą z tego samego regionu;
                    (2) reprezentatywność czasowa — czy dane są aktualne;
                    (3) reprezentatywność technologiczna — czy dane opisują tę samą technologię.
                </div>
            </details>

            <details class="faq-item">
                <summary class="faq-q">Kiedy wolno używać danych proxy?</summary>
                <div class="faq-a">
                    Dane proxy są dopuszczalne gdy idealne dane są niedostępne lub niemożliwe
                    do pozyskania. Wymagane jest: dokumentacja wyboru proxy,
                    analiza wrażliwości pokazująca wpływ na wyniki, opis niepewności danych.
                    Proxy powinno być możliwie bliskie technologicznie i geograficznie.
                </div>
            </details>

            <details class="faq-item">
                <summary class="faq-q">Czy ecoinvent ma dane dla Polski?</summary>
                <div class="faq-a">
                    Tak — ecoinvent zawiera zestawy danych z przyrostkiem <code>PL</code>
                    (np. dla energii elektrycznej, transportu, niektórych materiałów).
                    Jednak dane te mogą być starsze niż krajowe publikacje KOBiZE lub
                    nie odzwierciedlać aktualnych zmian w polskim miksie energetycznym.
                    W przypadku energii elektrycznej należy porównać wskaźnik ecoinvent
                    z aktualnym wskaźnikiem KOBiZE i użyć bardziej aktualnego.
                </div>
            </details>
        </div>

        <hr class="blog-post-divider">

        <section class="article-sources"><h2>Źródła</h2><ul><li>ISO 14044:2006, §4.7.3 Wymagania dotyczące jakości danych;</li><li>EN 15804+A2:2019/A1:2021, §6.3.5, §6.3.6, §6.4.3;</li><li>KOBiZE (2024), Wskaźniki emisyjności CO₂ dla energii elektrycznej, dane za 2023;</li><li>ecoinvent v3.10 (2023), dokumentacja zestawu danych <em>electricity production, Poland</em>;</li><li>Hauschild M.Z. i in. (2018), „Life Cycle Assessment: Theory and Practice”, Springer;</li><li>Finnveden G. i in. (2009), „Recent developments in Life Cycle Assessment”, Journal of Environmental Management 91(1).</li></ul></section>
    </div>
</body>
</html>
