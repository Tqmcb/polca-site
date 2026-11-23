/* poLCA — tabela wskaźników emisji */
(function () {
    'use strict';

    function $(id) { return document.getElementById(id); }
    if (!$('emissionTableBody')) return;

    var emissionFactors = [
        // Energia
        { name: 'Energia elektryczna PL 2025 — GWP-total u odbiorcy', value: '644,5',     unit: 'g CO\u2082e/kWh',   source: 'poLCA Energia Polska 2025 v4', cat: 'energia' },
        { name: 'Miks elektryczny PL — CO₂ u odbiorcy, dane 2024', value: '553',       unit: 'kg CO\u2082/MWh',   source: 'KOBiZE, publikacja XII 2025, dane 2024', cat: 'energia' },
        { name: 'Miks elektryczny PL — GWP-fossil, profil 2024', value: '599',       unit: 'g CO\u2082e/kWh',   source: 'poLCA-EN-PL-2024 v9.1, profil historyczny', cat: 'energia' },
        { name: 'Ciep\u0142o systemowe PL (\u015brednia)',      value: '~380',      unit: 'kg CO\u2082/MWh',   source: 'URE 2024',        cat: 'energia' },
        { name: 'Fotowoltaika (PL, krzemowa)',        value: '50\u201370',     unit: 'g CO\u2082e/kWh',   source: 'poLCA 2024',      cat: 'energia' },
        { name: 'Energia wiatrowa (onshore PL)',      value: '10\u201315',     unit: 'g CO\u2082e/kWh',   source: 'IPCC 2014',       cat: 'energia' },
        { name: '\u015arednia EU (miks elektr.)',           value: '~210',      unit: 'kg CO\u2082/MWh',   source: 'Ember 2025 (dane 2024)',        cat: 'energia' },

        // Paliwa
        { name: 'Gaz ziemny',                        value: '56,1',      unit: 'kg CO\u2082/GJ',    source: 'KOBiZE 2024',     cat: 'paliwa' },
        { name: 'Olej opa\u0142owy',                       value: '77,4',      unit: 'kg CO\u2082/GJ',    source: 'KOBiZE 2024',     cat: 'paliwa' },
        { name: 'W\u0119giel kamienny',                    value: '95,5',      unit: 'kg CO\u2082/GJ',    source: 'KOBiZE 2024',     cat: 'paliwa' },
        { name: 'W\u0119giel brunatny',                    value: '101,2',     unit: 'kg CO\u2082/GJ',    source: 'KOBiZE 2024',     cat: 'paliwa' },
        { name: 'Olej nap\u0119dowy (diesel)',              value: '74,1',      unit: 'kg CO\u2082/GJ',    source: 'IPCC 2006',       cat: 'paliwa' },
        { name: 'Benzyna',                           value: '69,3',      unit: 'kg CO\u2082/GJ',    source: 'IPCC 2006',       cat: 'paliwa' },
        { name: 'LPG',                               value: '63,1',      unit: 'kg CO\u2082/GJ',    source: 'IPCC 2006',       cat: 'paliwa' },
        { name: 'Koks',                              value: '107,0',     unit: 'kg CO\u2082/GJ',    source: 'KOBiZE 2024',     cat: 'paliwa' },
        { name: 'Biomasa (pelet drzewny)',            value: '0 *',       unit: 'kg CO\u2082/GJ',    source: 'EU ETS konwencja', cat: 'paliwa' },

        // Transport
        { name: 'Zestaw ci\u0119\u017carowy 40 t', value: '0,0843', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },
        { name: 'Samoch\u00f3d 20\u201326 t', value: '0,111', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },
        { name: 'Samoch\u00f3d 12\u201314 t', value: '0,156', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },
        { name: 'Samoch\u00f3d 7,5\u201312 t', value: '0,261', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },
        { name: 'Kolej elektryczna', value: '0,0170', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },
        { name: 'Barka \u015br\u00f3dl\u0105dowa', value: '0,0201', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },
        { name: 'Masowiec morski', value: '0,00540', unit: 'kg CO\u2082e/tkm', source: 'ÖKOBAUDAT 2026 (20.26.070), dane DE', cat: 'transport' },

        // Materiały budowlane
        { name: 'Cement CEM I — \u015brednia krajowa', value: '766', unit: 'kg CO\u2082e/t', source: 'EPD sektorowa SPC 2025, brutto', cat: 'materialy' },
        { name: 'Cement CEM II — \u015brednia krajowa', value: '613', unit: 'kg CO\u2082e/t', source: 'EPD sektorowa SPC 2025, brutto', cat: 'materialy' },
        { name: 'Cement CEM III — \u015brednia krajowa', value: '483', unit: 'kg CO\u2082e/t', source: 'EPD sektorowa SPC 2025, brutto', cat: 'materialy' },
        { name: 'Cement CEM IV — \u015brednia krajowa', value: '510', unit: 'kg CO\u2082e/t', source: 'EPD sektorowa SPC 2025, brutto', cat: 'materialy' },
        { name: 'Cement CEM V — \u015brednia krajowa', value: '546', unit: 'kg CO\u2082e/t', source: 'EPD sektorowa SPC 2025, brutto', cat: 'materialy' },
        { name: 'Beton C20/25',                      value: '~200',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Beton C25/30',                      value: '~250',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Beton C30/37',                      value: '~300',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Stal BOF (EU avg)',                  value: '~1 780',    unit: 'kg CO\u2082e/t',    source: 'ecoinvent 3.10',  cat: 'materialy' },
        { name: 'Stal zbrojeniowa (PL) — mediana 4 EPD', value: '790 (358\u2013961)', unit: 'kg CO\u2082e/t', source: 'EPD hut w Polsce, mediana poLCA', cat: 'materialy' },
        { name: 'Aluminium (pierwotne)',              value: '~8 000',    unit: 'kg CO\u2082e/t',    source: 'EAA',             cat: 'materialy' },
        { name: 'Aluminium (recykling)',              value: '~600',      unit: 'kg CO\u2082e/t',    source: 'EAA',             cat: 'materialy' },
        { name: 'Szk\u0142o p\u0142askie',                      value: '~1 200',    unit: 'kg CO\u2082e/t',    source: 'Glass for Europe', cat: 'materialy' },
        { name: 'Ceg\u0142a ceramiczna',                   value: '~200',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Beton kom\u00f3rkowy (ABK)',               value: '~300',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'We\u0142na mineralna',                   value: '~1 300',    unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
        { name: 'EPS (styropian)',                   value: '~3 200',    unit: 'kg CO\u2082e/t',    source: 'EUMEPS',          cat: 'materialy' },
        { name: 'XPS',                               value: '~4 500',    unit: 'kg CO\u2082e/t',    source: 'XPS Europe',      cat: 'materialy' },
        { name: 'PIR/PUR',                           value: '~3 800',    unit: 'kg CO\u2082e/t',    source: 'PU Europe',       cat: 'materialy' },
        { name: 'Drewno iglaste (C24)',              value: '~ \u2212750',    unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Sklejka',                           value: '~400',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'P\u0142yta gipsowo-kartonowa',            value: '~250',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Mied\u017a (pierwotna)',                  value: '~3 500',    unit: 'kg CO\u2082e/t',    source: 'ICA',             cat: 'materialy' },
        { name: 'Rura PVC',                          value: '~2 000',    unit: 'kg CO\u2082e/t',    source: 'PVC4Pipes',       cat: 'materialy' },
        { name: 'Rura PE-HD',                        value: '~1 800',    unit: 'kg CO\u2082e/t',    source: 'PlasticsEurope',  cat: 'materialy' },
        { name: 'Papa bitumiczna',                   value: '~350',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },

        // Procesy przemysłowe
        { name: 'Produkcja klinkieru (PL) — emisja ca\u0142kowita', value: '775', unit: 'kg CO\u2082/t', source: 'EPD sektorowa SPC 2025, dane 2022', cat: 'procesy' },
        { name: 'Produkcja klinkieru (PL) — emisja procesowa', value: '470', unit: 'kg CO\u2082/t', source: 'EPD sektorowa SPC 2025, dane 2022', cat: 'procesy' },
        { name: 'Kalcynacja CaCO\u2083 (wapna)',          value: '785',       unit: 'kg CO\u2082/t CaO', source: 'IPCC 2006',    cat: 'procesy' },
        { name: 'Produkcja wapna palonego',          value: '~750',      unit: 'kg CO\u2082/t',     source: 'EuLA',            cat: 'procesy' },
        { name: 'Huta szk\u0142a (miks PL)',              value: '~500',      unit: 'kg CO\u2082/t',     source: 'Glass for Europe', cat: 'procesy' },
        { name: 'Elektroliza aluminium',             value: '~6 500',    unit: 'kg CO\u2082e/t',    source: 'IAI',             cat: 'procesy' },
        { name: 'Spalanie gazu w kotle (>1 MW)',     value: '56,1',      unit: 'kg CO\u2082/GJ',    source: 'KOBiZE 2024',     cat: 'procesy' },
        { name: 'Paliwa alternatywne w cemencie PL', value: '70\u201380%',    unit: 'udzia\u0142 substytucji', source: 'SPC 2024',   cat: 'procesy' }
    ];

    var currentFilter = 'all';

    function renderEmissionTable() {
        var tbody = $('emissionTableBody');
        var search = ($('emissionSearch').value || '').toLowerCase();
        var html = '';
        var count = 0;

        for (var i = 0; i < emissionFactors.length; i++) {
            var f = emissionFactors[i];

            // Filter by category
            if (currentFilter !== 'all' && f.cat !== currentFilter) continue;

            // Filter by search
            if (search && f.name.toLowerCase().indexOf(search) === -1 &&
                f.source.toLowerCase().indexOf(search) === -1 &&
                f.unit.toLowerCase().indexOf(search) === -1) continue;

            var sourceLabel = (f.name.indexOf('Miks elektryczny PL') === 0 || f.source === 'Założenie historyczne kalkulatora') ? f.source : 'Zestaw historyczny; przypisanie: ' + f.source;
            var isHighlight = f.cat === 'energia' && f.name.indexOf('Miks elektryczny PL') === 0 && f.name.indexOf('LCA') === -1;

            html += '<tr role="row">' +
                '<td role="cell" style="font-weight: 500;">' + f.name + '</td>' +
                '<td role="cell" class="mono' + (isHighlight ? ' highlight' : '') + '">' + f.value + ' ' + f.unit + '</td>' +
                '<td role="cell" style="font-size: 0.78rem; color: var(--text-tertiary);">' + sourceLabel + '</td>' +
                '</tr>';
            count++;
        }

        if (count === 0) {
            html = '<tr role="row"><td role="cell" colspan="3" style="text-align: center; color: var(--text-tertiary); padding: 2rem;">Brak wyników dla podanych kryteriów</td></tr>';
        }

        tbody.innerHTML = html;
        $('tableCount').textContent = count + ' ' + (count === 1 ? 'wskaźnik' : [2,3,4].includes(count % 10) && ![12,13,14].includes(count % 100) ? 'wskaźniki' : 'wskaźników');
    }

    // Filter pills
    $('emissionFilters').addEventListener('click', function (e) {
        var btn = e.target.closest('.tool-filter-pill');
        if (!btn) return;

        var pills = this.querySelectorAll('.tool-filter-pill');
        for (var i = 0; i < pills.length; i++) pills[i].classList.remove('active');
        btn.classList.add('active');

        currentFilter = btn.getAttribute('data-filter');
        renderEmissionTable();
    });

    $('emissionSearch').addEventListener('input', renderEmissionTable);
    renderEmissionTable();
})();
