<section class="home-intro" aria-labelledby="home-title">
  <div class="portal-shell">
    <div class="home-intro-grid">
      <div>
        <p class="home-eyebrow">Ocena cyklu życia wyrobów i procesów</p>
        <h1 id="home-title">Oblicz ślad węglowy i środowiskowy na polskich danych</h1>
        <p class="home-description">poLCA to dane i kalkulatory do oceny wpływu energii, materiałów i transportu. Pomagają przygotować obliczenia dla wyrobów budowlanych i deklaracji środowiskowych (EPD).</p>
        <div class="home-actions"><a class="home-primary" href="/datasety.html">Znajdź dane</a><a href="/kalkulatory.html">Przejdź do kalkulatorów</a></div>
      </div>
      <nav class="home-routes" aria-labelledby="home-routes-title">
        <h2 id="home-routes-title">Zacznij od swojego zadania</h2>
        <ul>
          <li><a href="/oblicz-energie-2025.html"><span><strong>Energia elektryczna</strong><small>Przelicz kWh na wpływ na klimat i inne wskaźniki.</small></span><span class="home-route-arrow" aria-hidden="true">→</span></a></li>
          <li><a href="/wyroby.html"><span><strong>Wyrób budowlany</strong><small>Znajdź dane, metody i narzędzia dla swojej branży.</small></span><span class="home-route-arrow" aria-hidden="true">→</span></a></li>
          <li><a href="/zastosowanie-danych.html#budynek"><span><strong>Budynek</strong><small>Sprawdź, jak dobrać dane do materiałów i eksploatacji.</small></span><span class="home-route-arrow" aria-hidden="true">→</span></a></li>
        </ul>
      </nav>
    </div>
    <form class="home-search-band" action="/szukaj.html" method="get" role="search">
      <div><label class="home-search-label" for="home-query">Szukaj w danych i dokumentacji</label><p class="home-search-hint">Wskaźniki, kalkulatory, zasady obliczeń i wyjaśnienia.</p></div>
      <div class="portal-search-control"><input id="home-query" type="search" name="q" placeholder="Np. energia 2025, cement, ślad węglowy"><button type="submit">Szukaj</button></div>
    </form>
  </div>
</section>
<div class="portal-shell">
  <section class="home-section home-energy" aria-labelledby="home-energy-title">
    <div class="home-energy-copy">
      <p class="home-eyebrow">Przykład zastosowania danych</p>
      <h2 id="home-energy-title">Energia elektryczna.<br>Polska $energy_year.</h2>
      <p>Wpisz zużycie energii i otrzymaj $indicator_count wskaźników: wpływ na klimat, zużycie zasobów i wody, ilość odpadów oraz pozostałe wyniki modelu.</p>
      <p>Profil opisuje fizyczny miks energii dostarczonej odbiorcy. Do każdego wyniku dołączono jednostkę, a do modelu — metodę, źródła i warunki wykorzystania.</p>
      <div class="home-energy-links"><a href="/oblicz-energie-2025.html">Przelicz własne zużycie →</a><a href="$energy_href">Model i pliki</a></div>
    </div>
    <figure class="home-example">
      <figcaption>Jak dane przekładają się na wynik</figcaption>
      <div class="home-equation">
        <p><strong>100<span class="home-equation-unit">kWh</span></strong><span class="home-equation-label">Zużycie energii</span></p>
        <span class="home-equation-arrow" aria-hidden="true">→</span>
        <p><strong>$example_value<span class="home-equation-unit">kg CO₂e</span></strong><span class="home-equation-label">Wpływ na klimat<br>w cyklu życia</span></p>
      </div>
      <p class="home-example-source">Przykładowe obliczenie: 100 kWh × $energy_factor kg CO₂e/kWh. Źródło: <a href="$energy_href">$energy_source</a>. CO₂e oznacza ekwiwalent dwutlenku węgla.</p>
      <p class="home-example-status"><strong>$energy_status.</strong> Kwalifikacja modelu do konkretnego zastosowania w EPD pozostaje otwarta. <a href="$energy_href#status">Zakres i status wersji</a>.</p>
    </figure>
  </section>
  <section class="home-section" aria-labelledby="home-products-title">
    <div class="home-products">
      <div class="home-products-intro">
        <h2 id="home-products-title">Dane i metody<br>dla Twojego wyrobu</h2>
        <p>Wybierz rodzaj wyrobu. W jednym miejscu znajdziesz dostępne dane, dokumenty metodyczne i narzędzia dla tej branży.</p>
        <a href="/wyroby.html">Przejrzyj wszystkie rodziny wyrobów →</a>
      </div>
      <ul class="home-products-list">$product_links</ul>
    </div>
    <div class="home-common"><strong>Dane wspólne dla branż:</strong><a href="/datasety.html?category=energia">Energia</a><a href="/datasety.html?category=paliwa">Paliwa</a><a href="/datasety.html?category=transport">Transport</a></div>
  </section>
  <section class="home-section home-guides" aria-labelledby="home-guides-title">
    <div>
      <h2 id="home-guides-title">Dobierz dane<br>do celu obliczenia</h2>
      <p>Ślad węglowy opisuje wpływ na klimat. Ocena środowiskowa obejmuje też inne oddziaływania. Przewodniki wyjaśniają, jaki wskaźnik wybrać i jak wykorzystać go w obliczeniu.</p>
      <p>Przy opracowaniu EPD dobierz dane do wyrobu i zasad programu deklaracji. Status oraz warunki wykorzystania sprawdzisz przy konkretnej wersji zbioru.</p>
    </div>
    <ul class="home-guide-links">
      <li><a href="/slad-weglowy-czy-srodowiskowy.html">Ślad węglowy czy środowiskowy?<span aria-hidden="true">→</span></a></li>
      <li><a href="/zastosowanie-epd-cpr.html">Jak dobierać dane do deklaracji EPD?<span aria-hidden="true">→</span></a></li>
      <li><a href="/porownanie-baz.html">Czym poLCA różni się od innych baz?<span aria-hidden="true">→</span></a></li>
      <li><a href="/metodyka.html">Skąd pochodzą dane i jak je obliczono?<span aria-hidden="true">→</span></a></li>
      <li><a href="/jak-korzystac.html">Pierwsze obliczenie — jak zacząć<span aria-hidden="true">→</span></a></li>
    </ul>
  </section>
  <div class="home-about"><p>poLCA rozwija Multicert, operator programu EPD Polska. Portal udostępnia dane i dokumentację do oceny cyklu życia wyrobów i procesów.</p><a href="/o-polca/">O projekcie poLCA →</a></div>
</div>
