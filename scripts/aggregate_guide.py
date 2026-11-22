"""Illustrated guide to the supply of aggregate for concrete."""


def aggregate_guide() -> str:
    return '''<section id="modul-a1" class="portal-section aggregate-guide" aria-labelledby="aggregate-guide-title">
    <h2 id="aggregate-guide-title">Kiedy kruszywo wchodzi do modułu A1 betonu?</h2>
    <div class="aggregate-guide-layout">
      <div class="aggregate-figure">
        <img src="/images/kruszywa-droga-do-betoniarni.jpg" width="1600" height="571" loading="lazy" decoding="async" alt="Droga kruszywa z kopalni przez zakład przeróbczy do betoniarni.">
        <nav class="aggregate-points" aria-label="Punkty na ilustracji dostawy kruszywa">
          <a id="punkt-kopalnia" href="#opis-kopalnia" aria-label="1. Produkcja kruszywa, moduł A1 betonu"><span>1</span></a>
          <a id="punkt-transport" href="#opis-transport" aria-label="2. Transport do betoniarni, moduł A2 betonu"><span>2</span></a>
          <a id="punkt-betoniarnia" href="#opis-betoniarnia" aria-label="3. Odbiór w betoniarni"><span>3</span></a>
        </nav>
      </div>
      <ol class="aggregate-stages">
        <li id="opis-kopalnia" tabindex="-1">
          <h3><a href="#punkt-kopalnia" aria-label="Produkcja kruszywa, punkt 1 na ilustracji"><span class="aggregate-stage-number" aria-hidden="true">1</span>Produkcja kruszywa</a></h3>
          <p>W ocenie betonu <strong>moduł A1</strong> obejmuje produkcję zakupionego kruszywa do bramy jego producenta.</p>
        </li>
        <li id="opis-transport" tabindex="-1">
          <h3><a href="#punkt-transport" aria-label="Transport do betoniarni, punkt 2 na ilustracji"><span class="aggregate-stage-number" aria-hidden="true">2</span>Transport do betoniarni</a></h3>
          <p>Przewóz od bramy producenta kruszywa do betoniarni należy do <strong>modułu A2 betonu</strong>. <a href="https://preview.sist.si/sist-preview/70993/968303feeecb4c8dab45d5e529c23d9d/SIST-EN-16757-2023.pdf">EN 16757, pkt 6.2.2</a>.</p>
        </li>
        <li id="opis-betoniarnia" tabindex="-1">
          <h3><a href="#punkt-betoniarnia" aria-label="Odbiór w betoniarni, punkt 3 na ilustracji"><span class="aggregate-stage-number" aria-hidden="true">3</span>Odbiór w betoniarni</a></h3>
          <p>W betoniarni kończy się dostawa kruszywa ujęta w A2. <a href="https://support.ecoinvent.org/market-activities">Proces rynkowy w bazie ecoinvent</a> może już obejmować transport. Sprawdź zakres danych, aby uwzględnić każdy odcinek tylko raz.</p>
        </li>
      </ol>
      <p class="aggregate-scope"><strong>Jak ocenia się samo kruszywo?</strong> W deklaracji środowiskowej kruszywa procesy przypisuje się do modułów jego własnego cyklu życia.</p>
    </div>
    </section>'''
