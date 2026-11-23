<section class="home-intro" aria-labelledby="home-title">
  <div class="home-atlas-band" aria-hidden="true"></div>
  <div class="portal-shell home-intro-grid">
    <div class="home-start">
      <h1 id="home-title">Polskie dane do oceny cyklu życia wyrobów i budynków</h1>
      <p class="home-description">Katalog zawiera $positions danych dla energii, paliw, transportu i materiałów budowlanych. Przy każdej wartości podajemy jednostkę, rok, źródło i status.</p>
      <form class="home-search" action="/szukaj.html" method="get" role="search">
        <label for="home-query">Szukaj w danych i dokumentacji</label>
        <div class="portal-search-control"><input id="home-query" type="search" name="q" placeholder="Np. energia 2025, cement"><button type="submit">Szukaj</button></div>
      </form>
      <div class="home-actions"><a href="/datasety.html">Przeglądaj dane</a><a href="/kalkulatory.html">Wybierz kalkulator</a></div>
    </div>
    <nav class="home-routes" aria-labelledby="home-routes-title">
      <h2 id="home-routes-title">Co można obliczyć na podstawie danych poLCA?</h2>
      <ul>
        <li><a href="/oblicz-energie-2025.html"><strong>Energia elektryczna</strong><span>Przelicz kWh na ślad węglowy i inne wskaźniki środowiskowe.</span></a></li>
        <li><a href="/wyroby.html"><strong>Wyrób budowlany</strong><span>Znajdź dane i metody dla rodziny wyrobów ($family_total rodzin według rozporządzenia CPR 2024/3110).</span></a></li>
        <li><a href="/zastosowanie-danych.html#budynek"><strong>Budynek</strong><span>Sprawdź, jak dobrać dane dla materiałów i etapu użytkowania budynku.</span></a></li>
      </ul>
    </nav>
    <figure class="home-illustration">
      <a class="home-map-link" href="/mapa-danych.html">
        <span class="home-atlas-art"><picture><source media="(max-width: 760px)" srcset="/images/polca-atlas-mini.webp"><img src="/images/polca-atlas-rzezba.webp" fetchpriority="high" width="1496" height="992" alt="Energia wiatru w Szymankowie, budynki w Warszawie i kruszywa na Dolnym Śląsku."></picture>$atlas_labels</span>
        <span class="home-map-caption"><strong>Mapa danych środowiskowych <span aria-hidden="true">→</span></strong><small>Energia, surowce, transport i budynki w Polsce</small></span>
      </a>
    </figure>
  </div>
</section>
<div class="portal-shell">
  <section class="home-energy" aria-labelledby="home-energy-title">
    <header class="home-energy-head">
      <h2 id="home-energy-title">Jaki jest ślad węglowy 1 kWh energii elektrycznej w Polsce w $energy_year r.?</h2>
    </header>
    <div class="home-calculation" data-home-calculator data-factor="$energy_factor_raw">
      <figure class="home-equation">
        <div class="home-equation-term home-equation-input"><span class="home-energy-static"><span class="home-equation-label">Zużycie energii</span><strong>100</strong></span><div class="home-energy-editor" hidden><label class="home-equation-label" for="home-energy-use">Zmień zużycie energii</label><input id="home-energy-use" type="text" inputmode="decimal" value="100" autocomplete="off" maxlength="16" aria-describedby="home-energy-unit home-energy-error"></div><span class="home-equation-unit" id="home-energy-unit">kWh</span></div>
        <span class="home-equation-operator" aria-label="razy">×</span>
        <div class="home-equation-term"><span class="home-equation-label">Wskaźnik na 1 kWh</span><strong>$energy_factor</strong><span class="home-equation-unit">kg CO₂e/kWh</span></div>
        <span class="home-equation-operator" aria-label="równa się">=</span>
        <div class="home-equation-term home-equation-result"><span class="home-equation-label">Wkład energii w ślad węglowy</span><output id="home-energy-result" for="home-energy-use" aria-live="off">$example_value</output><span class="home-equation-unit">kg CO₂e</span></div>
        <figcaption>Średnia krajowa dla odbiorców końcowych w $energy_year r., z uwzględnieniem strat sieciowych, bez rozliczania gwarancji pochodzenia.</figcaption>
      </figure>
      <div class="home-energy-presets" hidden><span>Przykłady</span><button type="button" data-energy-preset="100">100 kWh</button><button type="button" data-energy-preset="1000">1000 kWh</button><button type="button" data-energy-preset="10000">10 000 kWh</button></div>
      <p id="home-energy-error" hidden></p><span class="home-sr-only" id="home-energy-announcement" role="status"></span>
      <p class="home-example-source">Źródło: <a href="$energy_href">$energy_source</a>. Wskaźnik podano w zaokrągleniu; wynik obliczono z pełnej wartości. CO₂e oznacza ekwiwalent dwutlenku węgla.</p>
    </div>
    <div class="home-energy-foot">
      <div class="home-energy-copy"><p>Pełny kalkulator oblicza <strong>$indicator_count wskaźników</strong>, m.in. dotyczących zmiany klimatu, zużycia zasobów i wody oraz ilości odpadów. Opis modelu zawiera metodę, źródła i warunki wykorzystania.</p><a class="home-primary" href="/oblicz-energie-2025.html">Oblicz $indicator_count wskaźników</a><a class="home-water-link" href="$energy_href#woda">Co oznaczają dwa wskaźniki dotyczące wody?</a></div>
      <div class="home-example-status"><p><strong>Status modelu: $energy_status_lower.</strong> Nie podjęliśmy decyzji o stosowaniu modelu w deklaracjach środowiskowych wyrobów (EPD).</p><a href="$energy_href#status">Zakres i status wersji</a><a href="$energy_href">Opis modelu i pliki do pobrania</a></div>
    </div>
  </section>
</div>
<section class="home-consultation" aria-labelledby="home-consultation-title">
  <div class="portal-shell home-consultation-inner">
    <h2 id="home-consultation-title">$consultation_title</h2><p>$consultation_description</p><div class="home-consultation-access"><p>W zgłoszeniu należy podać, której części modelu dotyczy uwaga, oraz wersję pakietu danych podaną w opisie modelu.</p><a href="/konsultacje/energia-polska-2025.html">Zgłoś uwagę do modelu <span aria-hidden="true">→</span></a></div>
  </div>
</section>
<div class="portal-shell">
  <section class="home-products" aria-labelledby="home-products-title">
    <header class="home-products-intro"><h2 id="home-products-title">Jakie dane i metody są dostępne dla rodzin wyrobów budowlanych?</h2><p>Dla $family_total rodzin wyrobów według CPR 2024/3110 podajemy dostępne dane, metody i objaśnienia. $family_coverage</p><a href="/wyroby.html">Przeglądaj $family_total rodzin wyrobów</a></header>
    <div class="home-products-index"><div class="home-products-columns" aria-hidden="true"><span>Rodzina wyrobów</span><span>Co jest dostępne</span></div><ul class="home-products-list">$product_links</ul><div class="home-common"><span>Dane wspólne dla wszystkich branż</span><div><a href="/datasety.html?category=energia">Energia</a><a href="/datasety.html?category=paliwa">Paliwa</a><a href="/datasety.html?category=transport">Transport</a></div></div></div>
  </section>
  <section class="home-updates" aria-labelledby="home-updates-title">
    <h2 id="home-updates-title">Co ostatnio zmieniliśmy w danych?</h2>
    <ol>$update_items</ol>
    <a href="/rejestr-zmian.html">Pełny rejestr zmian</a>
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
  <div class="home-about"><p>Portal poLCA prowadzimy jako Multicert, operator programu EPD Polska. Udostępniamy dane i dokumentację do oceny cyklu życia wyrobów i procesów.</p><a href="/o-polca/">O projekcie poLCA</a></div>
</div>
