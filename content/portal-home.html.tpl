<section class="home-intro" aria-labelledby="home-title">
  <div class="home-atlas-band">
  <div class="portal-shell home-intro-grid">
    <div class="home-start">
      <h1 id="home-title">Polskie dane środowiskowe</h1>
      <p class="home-description">Wskaźniki dla energii, materiałów i transportu służą do oceny cyklu życia wyrobu lub budynku, w tym do obliczania śladu węglowego.</p>
      <form class="home-search" action="/szukaj.html" method="get" role="search">
        <label for="home-query">Szukaj w danych i dokumentacji</label>
        <div class="portal-search-control"><input id="home-query" type="search" name="q" placeholder="Np. energia 2025, cement"><button type="submit">Szukaj</button></div>
      </form>
      <div class="home-actions"><a href="/datasety.html">Przeglądaj dane</a><a href="/kalkulatory.html">Wszystkie kalkulatory</a></div>
    </div>
    <figure class="home-illustration">
      <a class="home-map-link" href="/mapa-danych.html">
        <span class="home-atlas-art"><picture><source media="(max-width: 760px)" srcset="/images/polca-atlas-mini.webp"><img src="/images/polca-atlas-rzezba.webp" width="1496" height="992" alt="Energia wiatru w Szymankowie, budynki w Warszawie i kruszywa na Dolnym Śląsku."></picture>$atlas_labels</span>
        <span class="home-map-caption"><strong>Mapa danych środowiskowych <span aria-hidden="true">→</span></strong><small>Energia, surowce, transport i budynki w Polsce</small></span>
      </a>
    </figure>
  </div>
  </div>
  <div class="portal-shell">
    <nav class="home-routes" aria-labelledby="home-routes-title">
      <h2 id="home-routes-title">Co chcesz obliczyć?</h2>
      <ul>
        <li><a href="/oblicz-energie-2025.html"><strong>Energia elektryczna</strong><span>Przelicz kWh na ślad węglowy i inne wskaźniki środowiskowe.</span></a></li>
        <li><a href="/wyroby.html"><strong>Wyrób budowlany</strong><span>Znajdź dane, metody i narzędzia dla swojej branży.</span></a></li>
        <li><a href="/zastosowanie-danych.html#budynek"><strong>Budynek</strong><span>Sprawdź, jak dobrać dane do materiałów i eksploatacji.</span></a></li>
      </ul>
    </nav>
  </div>
</section>
<div class="portal-shell">
  <section class="home-energy" aria-labelledby="home-energy-title">
    <header class="home-energy-head">
      <h2 id="home-energy-title">Jaki jest ślad węglowy zużytej energii?</h2>
      <p>Energia elektryczna, Polska $energy_year.<br> Średnia krajowa u odbiorców końcowych, ze stratami sieciowymi, bez rozliczania gwarancji pochodzenia.</p>
    </header>
    <figure class="home-calculation" data-home-calculator data-factor="$energy_factor_raw">
      <figcaption>Ślad węglowy zużytej energii elektrycznej</figcaption>
      <div class="home-equation">
        <div class="home-equation-term home-equation-input"><span class="home-energy-static"><span class="home-equation-label">Zużycie energii</span><strong>100</strong></span><div class="home-energy-editor" hidden><label class="home-equation-label" for="home-energy-use">Zmień zużycie energii</label><input id="home-energy-use" type="text" inputmode="decimal" value="100" autocomplete="off" maxlength="16" aria-describedby="home-energy-unit home-energy-error"></div><span class="home-equation-unit" id="home-energy-unit">kWh</span></div>
        <span class="home-equation-operator" aria-label="razy">×</span>
        <div class="home-equation-term"><span class="home-equation-label">Wskaźnik na 1 kWh</span><strong>$energy_factor</strong><span class="home-equation-unit">kg CO₂e/kWh</span></div>
        <span class="home-equation-operator" aria-label="równa się">=</span>
        <div class="home-equation-term home-equation-result"><span class="home-equation-label">Wkład energii w ślad węglowy</span><output id="home-energy-result" for="home-energy-use" aria-live="off">$example_value</output><span class="home-equation-unit">kg CO₂e</span></div>
      </div>
      <div class="home-energy-presets" hidden><span>Przykłady</span><button type="button" data-energy-preset="100">100 kWh</button><button type="button" data-energy-preset="1000">1000 kWh</button><button type="button" data-energy-preset="10000">10 000 kWh</button></div>
      <p id="home-energy-error" hidden></p><span class="home-sr-only" id="home-energy-announcement" role="status"></span>
      <p class="home-example-source">Źródło: <a href="$energy_href">$energy_source</a>. Wskaźnik podano w zaokrągleniu; wynik obliczono z pełnej wartości. CO₂e oznacza ekwiwalent dwutlenku węgla.</p>
    </figure>
    <div class="home-energy-foot">
      <div class="home-energy-copy"><p>Pełny kalkulator oblicza <strong>$indicator_count wskaźników</strong>, m.in. dla zmiany klimatu, zużycia zasobów i wody oraz ilości odpadów. Każdy wynik podano z jednostką. Opis modelu zawiera metodę, źródła i warunki wykorzystania.</p><a class="home-primary" href="/oblicz-energie-2025.html">Oblicz $indicator_count wskaźników</a><a class="home-water-link" href="$energy_href#woda">Co oznaczają dwa wskaźniki dotyczące wody?</a></div>
      <div class="home-example-status"><p><strong>$energy_status.</strong> Model nie został formalnie przyjęty do stosowania w deklaracjach środowiskowych wyrobów (EPD).</p><a href="$energy_href#status">Zakres i status wersji</a><a href="$energy_href">Model i pliki</a></div>
    </div>
  </section>
</div>
<section class="home-consultation" aria-labelledby="home-consultation-title">
  <div class="portal-shell home-consultation-inner">
    <figure class="home-review-illustration"><img src="/images/polca-model-energii.webp" width="800" height="800" alt="Szkic modelu energii: elektrownia, wiatr, fotowoltaika, transformator pod lupą i licznik energii." loading="lazy"></figure>
    <div><h2 id="home-consultation-title">$consultation_title</h2><p>$consultation_description</p><div class="home-consultation-access"><p>Na stronie projektu są dokumentacja, 37 wskaźników i warianty obliczeń. W zgłoszeniu podaje się temat i wersję pakietu.</p><a href="/konsultacje/energia-polska-2025.html">Zobacz projekt i zgłoś uwagę <span aria-hidden="true">→</span></a></div></div>
  </div>
</section>
<div class="portal-shell">
  <section class="home-products" aria-labelledby="home-products-title">
    <header class="home-products-intro"><h2 id="home-products-title">Dane i metody<br> według rodzaju wyrobu</h2><p>Wybierz rodzaj wyrobu. W jednym miejscu znajdziesz dostępne dane, dokumenty metodyczne i narzędzia dla tej branży.</p><a href="/wyroby.html">Wszystkie rodziny wyrobów</a></header>
    <div class="home-products-index"><div class="home-products-columns" aria-hidden="true"><span>Rodzaj wyrobu</span><span>Co jest dostępne</span></div><ul class="home-products-list">$product_links</ul><div class="home-common"><span>Dane wspólne dla wszystkich branż</span><div><a href="/datasety.html?category=energia">Energia</a><a href="/datasety.html?category=paliwa">Paliwa</a><a href="/datasety.html?category=transport">Transport</a></div></div></div>
  </section>
  <section class="home-guides" aria-labelledby="home-guides-title">
    <div class="home-guides-intro"><h2 id="home-guides-title">Jak dobrać dane do obliczenia?</h2></div>
    <nav aria-label="Przewodniki po danych i obliczeniach">
      <ul class="home-guide-index">
        <li><a href="/jak-korzystac.html"><strong>Pierwsze obliczenie</strong><span>Od wyboru procesu do wyniku z jednostką.</span></a></li>
        <li><a href="/zastosowanie-danych.html"><strong>Wyrób, budynek czy proces?</strong><span>Dobór danych do przedmiotu oceny i etapu cyklu życia.</span></a></li>
        <li><a href="/metodyka.html"><strong>Metody i źródła</strong><span>Pochodzenie wskaźnika, zakres modelu i dokumentacja.</span></a></li>
      </ul>
      <ul class="home-guide-related">
        <li><a href="/slad-weglowy-czy-srodowiskowy.html">Ślad węglowy a ślad środowiskowy</a></li>
        <li><a href="/zastosowanie-epd-cpr.html">Dobór danych do deklaracji środowiskowej wyrobu</a></li>
        <li><a href="/porownanie-baz.html">Porównanie poLCA, KOBiZE i ecoinvent</a></li>
      </ul>
    </nav>
  </section>
  <div class="home-about"><p>poLCA rozwija Multicert, operator programu EPD Polska. Portal udostępnia dane i dokumentację do oceny cyklu życia wyrobów i procesów.</p><a href="/o-polca/">O projekcie poLCA</a></div>
</div>
