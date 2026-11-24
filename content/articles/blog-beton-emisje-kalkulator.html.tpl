<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jak liczyć emisje CO₂ dla betonu w Polsce? Wytwórnia krok po kroku — poLCA</title>
    <meta name="description" content="Jak obliczyć wynik A1–A3 dla 1 m³ betonu towarowego: wzór, przykład dla receptury z 330 kg cementu CEM II i dane, które należy zastąpić danymi wytwórni.">
    <link rel="canonical" href="https://polca.org.pl/blog-beton-emisje-kalkulator.html">
    <meta property="og:type" content="article">
    <meta property="og:title" content="Jak liczyć emisje CO₂ dla betonu w Polsce? Wytwórnia krok po kroku">
    <meta property="og:description" content="Jak obliczyć wynik A1–A3 dla 1 m³ betonu towarowego: wzór, przykład dla receptury z 330 kg cementu CEM II i dane, które należy zastąpić danymi wytwórni.">
    <meta property="og:url" content="https://polca.org.pl/blog-beton-emisje-kalkulator.html">
    <meta property="og:image" content="https://polca.org.pl/images/blog-beton-emisje-kalkulator.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="600">
    <meta property="og:site_name" content="poLCA — Polska Baza Danych LCA">
    <meta property="og:locale" content="pl_PL">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Jak liczyć emisje CO₂ dla betonu w Polsce?">
    <meta name="twitter:description" content="Jak obliczyć wynik A1–A3 dla 1 m³ betonu towarowego: wzór, przykład dla receptury z 330 kg cementu CEM II i dane, które należy zastąpić danymi wytwórni.">
    <meta name="twitter:image" content="https://polca.org.pl/images/blog-beton-emisje-kalkulator.jpg">
    <script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Jak liczyć emisje CO₂ dla betonu w Polsce? Wytwórnia krok po kroku",
  "description": "Jak obliczyć wynik A1–A3 dla 1 m³ betonu towarowego: wzór, przykład dla receptury z 330 kg cementu CEM II i dane, które należy zastąpić danymi wytwórni.",
  "image": "https://polca.org.pl/images/blog-beton-emisje-kalkulator.jpg",
  "datePublished": "2026-02-24T00:00:00+01:00",
  "dateModified": "2026-11-24T00:00:00+01:00",
  "author": {
    "@type": "Organization",
    "name": "Multicert Sp. z o.o.",
    "url": "https://polca.org.pl"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Multicert Sp. z o.o.",
    "logo": {
      "@type": "ImageObject",
      "url": "https://polca.org.pl/favicon.svg"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://polca.org.pl/blog-beton-emisje-kalkulator.html",
    "description": "Jak obliczyć wynik A1–A3 dla 1 m³ betonu towarowego: wzór, przykład dla receptury z 330 kg cementu CEM II i dane, które należy zastąpić danymi wytwórni."
  },
  "keywords": [
    "beton",
    "LCA",
    "emisje CO2",
    "GWP",
    "wytwórnia betonu",
    "KOBiZE",
    "poLCA",
    "EPD"
  ],
  "articleSection": "Dane"
}</script>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <meta name="metadata_revision" content="2026-10-18">
</head>
<body data-minutes="4">
<h1>Jak liczyć emisje CO₂ dla betonu w Polsce? Wytwórnia krok po kroku</h1>
<p class="article-lead">
                Wynik A1–A3 dla 1 m³ betonu towarowego oblicza się jako sumę iloczynów: masa każdego składnika razy jego wskaźnik,
                masa składnika razy odległość przewozu razy wskaźnik transportu oraz zużycie energii w wytwórni razy wskaźnik energii.
            </p>
<aside class="legacy-note" aria-label="Sprostowanie"><p><strong>Sprostowanie z 23.11.2026.</strong> Wpis przeredagowano. Wcześniejsza wersja podawała udziały źródeł emisji (np. 13% dla energii elektrycznej) i różnicę +18% nazwaną błędem danych generycznych. Tych wartości nie dało się odtworzyć z podanych założeń. Wcześniejsza wersja zawierała też wzór mnożący masę cementu przez wskaźnik dla klinkieru.</p></aside>
<figure class="article-figure"><img src="images/blog-beton-emisje-kalkulator.jpg" alt="Robotnicy wyrównujący świeżo wylany beton"></figure>
<ol class="article-findings">
<li>Wynik A1–A3 dla 1 m³ betonu towarowego oblicza się jako sumę iloczynów: masa każdego składnika razy jego wskaźnik, masa składnika razy odległość przewozu razy wskaźnik transportu oraz zużycie energii w wytwórni razy wskaźnik energii.</li>
<li>Masy składników należy przyjąć z receptury, odległości z dokumentów dostaw, a zużycie energii z liczników wytwórni.</li>
<li>Dla przykładowej receptury z 330 kg cementu CEM II <strong>wynik wynosi 173,4 kg CO₂e/m³ netto</strong> (219,6 brutto), a <strong>cement odpowiada za ok. 90% wyniku</strong>.</li>
</ol>
<aside class="article-tools"><a href="/kalkulator-betonu.html">Kalkulator betonu towarowego</a>
<ul><li><a href="kalkulator.html">Kalkulator emisji CO₂</a></li><li><a href="narzedzia.html">Kalkulator modułu A4</a></li><li><a href="datasety.html?q=beton">Katalog danych</a></li></ul></aside>
<div class="article-prose">

        <div class="prose">
            <h2 id="wzor">Jak zbudowany jest wynik A1–A3 betonu?</h2>
            <p>Według EN 16757 produkcja składników betonu należy do modułu A1, ich przewóz do wytwórni do modułu A2, a produkcja w wytwórni do modułu A3. Dla 1 m³ betonu:</p>
            <ul>
                <li><strong>A1</strong> = Σ (masa składnika [t/m³] × wskaźnik składnika [kg CO₂e/t]),</li>
                <li><strong>A2</strong> = Σ (masa składnika [t/m³] × odległość [km] × wskaźnik transportu [kg CO₂e/(t·km)]),</li>
                <li><strong>A3</strong> = zużycie energii elektrycznej [kWh/m³] × wskaźnik energii [kg CO₂e/kWh] + zużycie paliw × wskaźnik paliwa.</li>
            </ul>
            <p>Masy składników należy przyjąć z receptury, odległości z dokumentów dostaw, a zużycie energii z liczników wytwórni.</p>

            <h2 id="przyklad">Jaki wynik daje przykładowa receptura?</h2>
            <p>Przykład dotyczy 1 m³ betonu z 330 kg cementu CEM II i 1850 kg kruszywa naturalnego. Recepturę, odległości (cement 100 km, kruszywo 30 km) i zużycie energii (4 kWh/m³) przyjęto dla ilustracji; nie opisują one konkretnej wytwórni. W obliczeniach pominięto wodę i domieszki. Katalog nie zawiera wskaźnika dla domieszek. Wynik obejmuje więc pięć pozycji z tabeli, a nie wszystkie procesy, które EN 16757 przypisuje modułom A1–A3.</p>
        </div>

<!-- concrete-example -->
        <div class="prose">
            <h2 id="dane">Które dane należy zastąpić danymi wytwórni?</h2>
            <ul>
                <li><strong>Cement:</strong> wskaźnik z deklaracji środowiskowej dostawcy cementu; średnia krajowa SPC 2025 tylko wtedy, gdy dostawca nie ma takiej deklaracji. Wartość netto przyjmujemy, gdy deklaracja środowiskowa cementu podaje wynik netto albo potwierdza, że współspalane paliwa mają status odpadu. W pozostałych przypadkach przyjmujemy wartość brutto. Porównujemy wyłącznie wyniki obliczone w tym samym wariancie.</li>
                <li><strong>Receptura:</strong> rzeczywiste masy składników na 1 m³.</li>
                <li><strong>Przewóz:</strong> odległości i rodzaj pojazdów z dokumentów dostaw.</li>
                <li><strong>Energia i paliwa:</strong> roczne zużycie z liczników i faktur podzielone przez roczną produkcję betonu w m³.</li>
            </ul>
            <p>Obliczenia dla cementu w betonie i dla kruszyw pokazują <a href="/wyroby/15.html#modul-a1-cement">karta cementu</a> i <a href="/wyroby/24.html">karta kruszyw</a>.</p>
        </div>

        <div class="prose">
            <section class="article-sources"><h2>Źródła wskaźników</h2><ul><li><a href="https://www.polskicement.pl/content/uploads/2026/01/EPD-Deklaracja-srodowiskowa-2025-POL.pdf#page=5">deklaracja sektorowa SPC 2025, tabela 2</a>;</li><li><a href="/dane/polca-agg-pl-natural-default-2026.html">rekord poLCA dla kruszywa naturalnego</a>;</li><li><a href="/dane/polca-truck-40t-default-2026.html">ÖKOBAUDAT 2026, zestaw ciężarowy 40 t</a>;</li><li><a href="/energia-polska-2025-v5.html">Energia Polska 2025 v5</a>.</li></ul></section>
        </div>
    </div>
</body>
</html>
