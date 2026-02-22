/* poLCA — Narzędzia LCA | polca.org.pl
   Unit converter, transport calculator, material comparison, emission factors */

(function () {
    'use strict';

    // ================================================================
    // HELPERS
    // ================================================================
    function fmt(n, decimals) {
        if (typeof decimals === 'undefined') decimals = 2;
        if (Math.abs(n) < 0.0001 && n !== 0) return n.toExponential(2);
        return n.toLocaleString('pl-PL', {
            minimumFractionDigits: 0,
            maximumFractionDigits: decimals
        });
    }

    function $(id) { return document.getElementById(id); }

    // ================================================================
    // 01 — UNIT CONVERTER
    // ================================================================
    var energyFactors = {
        'kWh':  1,
        'MWh':  1000,
        'GJ':   277.778,
        'MJ':   0.27778,
        'kcal': 0.001163
    };

    var massFactors = {
        'g':  0.001,
        'kg': 1,
        't':  1000
    };

    var fuelData = {
        'gas_nm3':  { kWh: 10.55,  label: 'Nm³ gazu ziemnego' },
        'coal_t':   { kWh: 6667,   label: 't węgla kamiennego' },
        'diesel_l': { kWh: 10.0,   label: 'L oleju napędowego' },
        'petrol_l': { kWh: 8.89,   label: 'L benzyny' },
        'lpg_l':    { kWh: 6.67,   label: 'L LPG' },
        'pellet_t': { kWh: 4800,   label: 't pelletu drzewnego' }
    };

    function convertEnergy() {
        var val = parseFloat($('convEnergyVal').value) || 0;
        var from = $('convEnergyFrom').value;
        var kWh = val * energyFactors[from];

        var html = '';
        var units = Object.keys(energyFactors);
        for (var i = 0; i < units.length; i++) {
            var u = units[i];
            if (u !== from) {
                var converted = kWh / energyFactors[u];
                html += '<div class="tool-conv-item">' +
                    '<span class="tool-conv-val">' + fmt(converted) + '</span>' +
                    '<span class="tool-conv-unit">' + u + '</span>' +
                    '</div>';
            }
        }
        $('convEnergyResults').innerHTML = html;
    }

    function convertMass() {
        var val = parseFloat($('convMassVal').value) || 0;
        var from = $('convMassFrom').value;
        var kg = val * massFactors[from];

        var html = '';
        var units = Object.keys(massFactors);
        for (var i = 0; i < units.length; i++) {
            var u = units[i];
            if (u !== from) {
                var converted = kg / massFactors[u];
                var label = u === 't' ? 't (Mg)' : u;
                html += '<div class="tool-conv-item">' +
                    '<span class="tool-conv-val">' + fmt(converted) + '</span>' +
                    '<span class="tool-conv-unit">' + label + '</span>' +
                    '</div>';
            }
        }
        $('convMassResults').innerHTML = html;
    }

    function convertFuel() {
        var val = parseFloat($('convFuelVal').value) || 0;
        var from = $('convFuelFrom').value;
        var data = fuelData[from];
        var kWh = val * data.kWh;

        var html = '<div class="tool-conv-item">' +
            '<span class="tool-conv-val">' + fmt(kWh) + '</span>' +
            '<span class="tool-conv-unit">kWh</span></div>' +
            '<div class="tool-conv-item">' +
            '<span class="tool-conv-val">' + fmt(kWh / 1000) + '</span>' +
            '<span class="tool-conv-unit">MWh</span></div>' +
            '<div class="tool-conv-item">' +
            '<span class="tool-conv-val">' + fmt(kWh / 277.778) + '</span>' +
            '<span class="tool-conv-unit">GJ</span></div>' +
            '<div class="tool-conv-item">' +
            '<span class="tool-conv-val">' + fmt(kWh * 3.6, 1) + '</span>' +
            '<span class="tool-conv-unit">MJ</span></div>';
        $('convFuelResults').innerHTML = html;
    }

    // Converter event listeners
    ['convEnergyVal', 'convEnergyFrom'].forEach(function (id) {
        $(id).addEventListener('input', convertEnergy);
        $(id).addEventListener('change', convertEnergy);
    });
    ['convMassVal', 'convMassFrom'].forEach(function (id) {
        $(id).addEventListener('input', convertMass);
        $(id).addEventListener('change', convertMass);
    });
    ['convFuelVal', 'convFuelFrom'].forEach(function (id) {
        $(id).addEventListener('input', convertFuel);
        $(id).addEventListener('change', convertFuel);
    });

    // ================================================================
    // 02 — TRANSPORT CALCULATOR
    // ================================================================
    function calcTransport() {
        var distance = parseFloat($('transDistance').value) || 0;
        var mass = parseFloat($('transMass').value) || 0;
        var factor = parseFloat($('transMode').value) || 0;
        var returnFactor = parseFloat($('transReturn').value) || 1;

        var total = distance * mass * factor * returnFactor;
        var perTon = mass > 0 ? total / mass : 0;
        var perTkm = distance > 0 && mass > 0 ? total / (distance * mass) : 0;

        $('transResult').textContent = fmt(total, 1);
        $('transPerTon').textContent = fmt(perTon, 2);
        $('transPerTkm').textContent = fmt(perTkm, 3);
    }

    ['transDistance', 'transMass', 'transMode', 'transReturn'].forEach(function (id) {
        $(id).addEventListener('input', calcTransport);
        $(id).addEventListener('change', calcTransport);
    });

    // ================================================================
    // 03 — MATERIAL COMPARISON
    // ================================================================
    var materials = [
        { id: 'cement_i',     name: 'Cement CEM I 42.5',     gwp: 800,   unit: 'kg CO\u2082e/t',  cat: 'Spoiwa',    checked: true },
        { id: 'cement_ii',    name: 'Cement CEM II/B-S',     gwp: 600,   unit: 'kg CO\u2082e/t',  cat: 'Spoiwa',    checked: false },
        { id: 'cement_iii',   name: 'Cement CEM III/A',      gwp: 400,   unit: 'kg CO\u2082e/t',  cat: 'Spoiwa',    checked: false },
        { id: 'concrete_20',  name: 'Beton C20/25',          gwp: 200,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Beton',     checked: false },
        { id: 'concrete_25',  name: 'Beton C25/30',          gwp: 250,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Beton',     checked: true },
        { id: 'concrete_30',  name: 'Beton C30/37',          gwp: 300,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Beton',     checked: false },
        { id: 'steel_eaf',    name: 'Stal EAF (PL)',          gwp: 620,   unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: true },
        { id: 'steel_bof',    name: 'Stal BOF (EU avg)',      gwp: 1780,  unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: true },
        { id: 'rebar',        name: 'Stal zbrojeniowa (PL)',  gwp: 750,   unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'alu_prim',     name: 'Aluminium (pierwotne)', gwp: 8000,  unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'alu_rec',      name: 'Aluminium (recykling)', gwp: 600,   unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'glass',        name: 'Szk\u0142o p\u0142askie',          gwp: 1200,  unit: 'kg CO\u2082e/t',  cat: 'Inne',      checked: false },
        { id: 'brick',        name: 'Ceg\u0142a ceramiczna',       gwp: 200,   unit: 'kg CO\u2082e/t',  cat: 'Ceramika',  checked: false },
        { id: 'aac',          name: 'Beton kom\u00f3rkowy (ABK)',   gwp: 300,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Ceramika',  checked: false },
        { id: 'mw',           name: 'We\u0142na mineralna',       gwp: 1300,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: false },
        { id: 'eps',          name: 'EPS (styropian)',        gwp: 3200,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: true },
        { id: 'xps',          name: 'XPS',                   gwp: 4500,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: false },
        { id: 'pir',          name: 'PIR/PUR',               gwp: 3800,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: false },
        { id: 'timber',       name: 'Drewno iglaste (C24)',  gwp: -750,  unit: 'kg CO\u2082e/m\u00b3', cat: 'Drewno',    checked: true },
        { id: 'plywood',      name: 'Sklejka',               gwp: 400,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Drewno',    checked: false },
        { id: 'gypsum',       name: 'P\u0142yta g-k',              gwp: 250,   unit: 'kg CO\u2082e/t',  cat: 'Wyko\u0144czenie', checked: false },
        { id: 'copper',       name: 'Mied\u017a (pierwotna)',      gwp: 3500,  unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'pvc_pipe',     name: 'Rura PVC',              gwp: 2000,  unit: 'kg CO\u2082e/t',  cat: 'Tworzywa',  checked: false },
        { id: 'pe_pipe',      name: 'Rura PE',               gwp: 1800,  unit: 'kg CO\u2082e/t',  cat: 'Tworzywa',  checked: false }
    ];

    function buildMaterialSelect() {
        var container = $('materialSelect');
        var html = '';
        for (var i = 0; i < materials.length; i++) {
            var m = materials[i];
            html += '<label class="material-chip' + (m.checked ? ' active' : '') + '">' +
                '<input type="checkbox" value="' + m.id + '"' + (m.checked ? ' checked' : '') + '>' +
                '<span class="material-chip-name">' + m.name + '</span>' +
                '<span class="material-chip-cat">' + m.cat + '</span>' +
                '</label>';
        }
        container.innerHTML = html;

        container.addEventListener('change', function (e) {
            if (e.target.type === 'checkbox') {
                var label = e.target.closest('.material-chip');
                if (e.target.checked) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
                renderMaterialChart();
            }
        });
    }

    function renderMaterialChart() {
        var container = $('materialChart');
        var checkboxes = $('materialSelect').querySelectorAll('input[type="checkbox"]:checked');
        var selected = [];

        for (var i = 0; i < checkboxes.length; i++) {
            var id = checkboxes[i].value;
            for (var j = 0; j < materials.length; j++) {
                if (materials[j].id === id) {
                    selected.push(materials[j]);
                    break;
                }
            }
        }

        if (selected.length === 0) {
            container.innerHTML = '<div class="tool-empty-state">Zaznacz materiały do porównania</div>';
            return;
        }

        // Sort by GWP descending
        selected.sort(function (a, b) { return b.gwp - a.gwp; });

        var maxAbs = 0;
        for (var i = 0; i < selected.length; i++) {
            if (Math.abs(selected[i].gwp) > maxAbs) maxAbs = Math.abs(selected[i].gwp);
        }

        var html = '';
        for (var i = 0; i < selected.length; i++) {
            var m = selected[i];
            var pct = Math.abs(m.gwp) / maxAbs * 100;
            var isNeg = m.gwp < 0;
            var barClass = isNeg ? 'material-bar-neg' : 'material-bar-pos';

            html += '<div class="material-bar-row">' +
                '<div class="material-bar-label">' +
                '<span class="material-bar-name">' + m.name + '</span>' +
                '<span class="material-bar-unit">' + m.unit + '</span>' +
                '</div>' +
                '<div class="material-bar-track">' +
                '<div class="material-bar ' + barClass + '" style="width: ' + pct + '%;">' +
                '<span class="material-bar-val">' + fmt(m.gwp, 0) + '</span>' +
                '</div>' +
                '</div>' +
                '</div>';
        }
        container.innerHTML = html;

        // Trigger animation
        requestAnimationFrame(function () {
            var bars = container.querySelectorAll('.material-bar');
            for (var i = 0; i < bars.length; i++) {
                bars[i].style.opacity = '1';
            }
        });
    }

    // ================================================================
    // 04 — EMISSION FACTORS TABLE
    // ================================================================
    var emissionFactors = [
        // Energia
        { name: 'Miks elektryczny PL',               value: '597',       unit: 'kg CO\u2082/MWh',   source: 'KOBiZE 2024',     cat: 'energia' },
        { name: 'Miks elektryczny PL (pe\u0142ne LCA)',   value: '718',       unit: 'g CO\u2082e/kWh',   source: 'poLCA-EN-PL 2024', cat: 'energia' },
        { name: 'Ciep\u0142o systemowe PL (\u015brednia)',      value: '~380',      unit: 'kg CO\u2082/MWh',   source: 'URE 2024',        cat: 'energia' },
        { name: 'Fotowoltaika (PL, krzemowa)',        value: '50\u201370',     unit: 'g CO\u2082e/kWh',   source: 'poLCA 2024',      cat: 'energia' },
        { name: 'Energia wiatrowa (onshore PL)',      value: '10\u201315',     unit: 'g CO\u2082e/kWh',   source: 'IPCC 2014',       cat: 'energia' },
        { name: '\u015arednia EU (miks elektr.)',           value: '~295',      unit: 'kg CO\u2082/MWh',   source: 'EEA 2024',        cat: 'energia' },
        { name: 'Residual mix PL (AIB)',              value: '~836',      unit: 'g CO\u2082e/kWh',   source: 'AIB 2023',        cat: 'energia' },

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
        { name: 'TIR > 32 t (pe\u0142ny)',                 value: '0,031',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Samoch\u00f3d 16\u201332 t',                    value: '0,049',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Samoch\u00f3d 7,5\u201316 t',                   value: '0,082',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Samoch\u00f3d < 7,5 t',                   value: '0,146',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Kolej elektryczna',                 value: '0,009',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Kolej spalinowa',                   value: '0,025',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Barka \u015br\u00f3dl\u0105dowa',                   value: '0,031',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },
        { name: 'Statek morski (bulk)',               value: '0,005',     unit: 'kg CO\u2082e/tkm',  source: 'DEFRA 2024',      cat: 'transport' },

        // Materiały budowlane
        { name: 'Cement CEM I 42.5',                 value: '~800',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Cement CEM II/B-S',                 value: '~600',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Cement CEM III/A',                  value: '~400',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Beton C20/25',                      value: '~200',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Beton C25/30',                      value: '~250',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Beton C30/37',                      value: '~300',      unit: 'kg CO\u2082e/m\u00b3',   source: 'EPD Polska',      cat: 'materialy' },
        { name: 'Stal EAF (PL)',                     value: '~620',      unit: 'kg CO\u2082e/t',    source: 'poLCA',           cat: 'materialy' },
        { name: 'Stal BOF (EU avg)',                  value: '~1 780',    unit: 'kg CO\u2082e/t',    source: 'ecoinvent 3.10',  cat: 'materialy' },
        { name: 'Stal zbrojeniowa (PL)',              value: '~750',      unit: 'kg CO\u2082e/t',    source: 'EPD Polska',      cat: 'materialy' },
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
        { name: 'Produkcja klinkieru (PL)',          value: '~625',      unit: 'kg CO\u2082/t',     source: 'GUS/CEMBUREAU',   cat: 'procesy' },
        { name: 'Kalcynacja CaCO\u2083 (wapna)',          value: '785',       unit: 'kg CO\u2082/t CaCO\u2083', source: 'IPCC 2006',    cat: 'procesy' },
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

            var isHighlight = f.cat === 'energia' && f.name.indexOf('Miks elektryczny PL') === 0 && f.name.indexOf('LCA') === -1;

            html += '<tr>' +
                '<td style="font-weight: 500;">' + f.name + '</td>' +
                '<td class="mono' + (isHighlight ? ' highlight' : '') + '">' + f.value + '</td>' +
                '<td class="mono" style="font-size: 0.75rem; color: var(--text-secondary);">' + f.unit + '</td>' +
                '<td style="font-size: 0.78rem; color: var(--text-tertiary);">' + f.source + '</td>' +
                '</tr>';
            count++;
        }

        if (count === 0) {
            html = '<tr><td colspan="4" style="text-align: center; color: var(--text-tertiary); padding: 2rem;">Brak wyników dla podanych kryteriów</td></tr>';
        }

        tbody.innerHTML = html;
        $('tableCount').textContent = count + ' ' + (count === 1 ? 'wskaźnik' : count < 5 ? 'wskaźniki' : 'wskaźników');
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

    // ================================================================
    // TOOL NAV — smooth scroll + active state
    // ================================================================
    var toolNavPills = document.querySelectorAll('.tool-nav-pill');

    function updateToolNav() {
        var scrollY = window.scrollY || window.pageYOffset;
        var sections = document.querySelectorAll('[id]');
        var activeId = '';

        for (var i = 0; i < sections.length; i++) {
            var rect = sections[i].getBoundingClientRect();
            if (rect.top <= 120) {
                activeId = sections[i].id;
            }
        }

        for (var i = 0; i < toolNavPills.length; i++) {
            var href = toolNavPills[i].getAttribute('href');
            if (href === '#' + activeId) {
                toolNavPills[i].classList.add('active');
            } else {
                toolNavPills[i].classList.remove('active');
            }
        }
    }

    window.addEventListener('scroll', updateToolNav, { passive: true });

    // ================================================================
    // INIT
    // ================================================================
    convertEnergy();
    convertMass();
    convertFuel();
    calcTransport();
    buildMaterialSelect();
    renderMaterialChart();
    renderEmissionTable();

})();
