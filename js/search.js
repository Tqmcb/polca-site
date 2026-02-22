/**
 * poLCA Portal Search
 */
(function() {
    'use strict';

    var pages = [
        { title: 'Dashboard', url: 'index.html', type: 'Portal', tags: 'strona główna portal dashboard' },
        { title: 'Metodyka i Jakość', url: 'metodyka.html', type: 'Baza', tags: 'walidacja ISO EN 15804 jakość siedmiowarstwowa' },
        { title: 'Analiza Sektorowa', url: 'analiza.html', type: 'Baza', tags: 'zniekształcenia sektory cement stal energia' },
        { title: 'Kalkulator Emisji', url: 'kalkulator.html', type: 'Narzędzie', tags: 'CO2 KOBiZE obliczenia kalkulator emisje' },
        { title: 'Narzędzia LCA', url: 'narzedzia.html', type: 'Narzędzie', tags: 'konwerter przelicznik transport porównywarka materiały' },
        { title: 'Baza Datasetów', url: 'datasety.html', type: 'Baza', tags: 'ILCD EcoSpold CSV eksport datasety zbiory' },
        { title: 'Blog', url: 'blog.html', type: 'Blog', tags: 'artykuły wiedza komentarze' },
        { title: 'Polska stal z EAF a europejska średnia', url: 'blog-stal-lca-eaf.html', type: 'Artykuł', tags: 'stal EAF piec elektryczny GWP EPD ecoinvent 0.62' },
        { title: 'poLCA-EN-PL 2024 — emisyjność energii elektrycznej', url: 'blog-en-pl-2024.html', type: 'Artykuł', tags: 'energia elektryczna emisyjność KOBiZE 718 kWh' },
        { title: 'Fotowoltaika a EPD', url: 'blog-fotowoltaika-epd.html', type: 'Artykuł', tags: 'fotowoltaika PV panele słoneczne moduł A EPD' },
        { title: 'Residual mix, AIB i KOBiZE', url: 'blog-residual-mix-aib-kobize.html', type: 'Artykuł', tags: 'residual mix AIB Scope 2 energia wskaźnik' },
        { title: 'Polskie emisje CO₂ a europejska średnia', url: 'blog-emisje-polska-vs-eu.html', type: 'Artykuł', tags: 'emisje CO2 Polska EU miks energetyczny 597' },
        { title: 'CPR 2024/3110 — zmiany dla producentów', url: 'blog-cpr-2024.html', type: 'Artykuł', tags: 'CPR rozporządzenie EPD obowiązek regulacje 2024' },
        { title: 'Granulat asfaltowy (RAP) w LCA', url: 'blog-mma-rap.html', type: 'Artykuł', tags: 'asfalt RAP recykling MMA mieszanka mineralno-asfaltowa' },
        { title: 'EPD — czym są Deklaracje Środowiskowe Produktu', url: 'blog-epd-czym-sa.html', type: 'Artykuł', tags: 'EPD deklaracja środowiskowa LCA certyfikat' },
        { title: 'Ecoinvent a krajowe bazy danych', url: 'blog-ecoinvent-vs-krajowe.html', type: 'Artykuł', tags: 'ecoinvent bazy danych porównanie krajowe polskie' },
        { title: 'Polski cement a europejska średnia', url: 'blog-cement-polska.html', type: 'Artykuł', tags: 'cement klinkier paliwa alternatywne cementownia' },
        { title: 'Zasada proximity w ISO 14044', url: 'blog-iso-14044-proximity.html', type: 'Artykuł', tags: 'ISO 14044 proximity bliskość dane LCI' }
    ];

    var searchInput = document.querySelector('.topbar-search input');
    if (!searchInput) return;

    searchInput.removeAttribute('readonly');

    var dropdown = document.createElement('div');
    dropdown.className = 'search-results';
    searchInput.parentNode.appendChild(dropdown);

    function normalize(str) {
        return str.toLowerCase()
            .replace(/ą/g, 'a').replace(/ć/g, 'c').replace(/ę/g, 'e')
            .replace(/ł/g, 'l').replace(/ń/g, 'n').replace(/ó/g, 'o')
            .replace(/ś/g, 's').replace(/ź/g, 'z').replace(/ż/g, 'z')
            .replace(/₂/g, '2');
    }

    function render(results) {
        if (results.length === 0) {
            dropdown.innerHTML = '<div class="search-no-results">Brak wyników</div>';
            dropdown.classList.add('active');
            return;
        }
        dropdown.innerHTML = results.map(function(r) {
            return '<a href="' + r.url + '" class="search-result-item">' +
                r.title +
                '<span class="search-result-type">' + r.type + '</span>' +
                '</a>';
        }).join('');
        dropdown.classList.add('active');
    }

    searchInput.addEventListener('input', function() {
        var q = normalize(this.value.trim());
        if (q.length < 2) {
            dropdown.classList.remove('active');
            return;
        }
        var results = pages.filter(function(p) {
            var haystack = normalize(p.title + ' ' + p.tags);
            return haystack.indexOf(q) !== -1;
        });
        render(results);
    });

    searchInput.addEventListener('focus', function() {
        if (this.value.trim().length >= 2) {
            dropdown.classList.add('active');
        }
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.topbar-search')) {
            dropdown.classList.remove('active');
        }
    });

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            dropdown.classList.remove('active');
            this.blur();
        }
    });
})();
