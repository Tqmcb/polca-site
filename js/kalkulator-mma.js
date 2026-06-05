/**
 * poLCA — Kalkulator pre-qualify EPD dla mieszanek mineralno-asfaltowych (MMA)
 * Wersja 1.0
 *
 * Oszacowanie GWP A1-A3 [kg CO2eq / t MMA] zgodne z c-PCR-MMA-EPD-Polska-2026
 * v1.0-DRAFT i EN 15804+A2. Wartości domyślne: zbiór danych POLCA-MMA-LCI-DEFAULTS-2026.
 * Energia elektryczna: poLCA-EN-PL-2024 v9.1 = 0,599 kg CO2e/kWh.
 * Bitumen: Eurobitume LCA 4.0 (2025).
 *
 * Wzór:
 *   A1 = SUM(masa_skladnika_kg/t * GWP_skladnika_kg/t / 1000)   [dla RA: GWP = 0]
 *   A2 = SUM(masa_skladnika_t/t * odleglosc_km * 0.100)
 *   A3 = emisja_paliwa(technologia, paliwo, temp) + 1.50        [energia el. = 1,50 stała]
 *   GWP_A1-A3 = A1 + A2 + A3
 */
(function () {
    'use strict';

    /* ---- Stałe wartości obliczeniowe (default data) ---- */
    var GWP = {
        aggFine: 1.80,        // kruszywo naturalne: piasek / żwir
        filler: 5.50,         // filler wapienny
        fiber: 800,           // włókno celulozowe (stabilizator SMA)
        ra: 0,                // granulat asfaltowy RA — cut-off (A1 = 0)
        addWma: 1200          // dodatek WMA chemiczny
        /* bitumen i kruszywo grube — z dropdownów */
    };
    var EF_TRANSPORT = 0.100; // kg CO2eq / (t·km) — mix flot EURO5/6 PL
    var EL_A3 = 1.50;         // kg CO2e / t MMA — 2,5 kWh/t × 0,599 kg/kWh
    var FUEL_BASE = {         // emisja paliwa w temp. bazowej [kg CO2 / t MMA]
        'HMA-olej': 24.1, 'HMA-gaz': 17.0,
        'WMA-olej': 17.4, 'WMA-gaz': 12.5
    };
    var TEMP_REF = { HMA: 160, WMA: 130 }; // temperatura bazowa
    var TEMP_STEP_PCT = 0.05;              // +5% paliwa na każde 10°C powyżej bazowej

    /* ---- Presety receptur normatywnych (na 1 t = 1000 kg MMA) ---- */
    var PRESETS = {
        ac11s:    { label: 'AC 11 S (ścieralna)',  norm: 'EN 13108-1', tech: 'HMA',    fuel: 'olej', temp: 165, bitType: '530', aggType: '3.80', aggC: 670, aggF: 130, filler: 50, bitumen: 150, ra: 0,   fiber: 0, addWma: 0 },
        ac16w:    { label: 'AC 16 W (wiążąca)',     norm: 'EN 13108-1', tech: 'HMA',    fuel: 'olej', temp: 160, bitType: '530', aggType: '3.80', aggC: 555, aggF: 320, filler: 50, bitumen: 75,  ra: 0,   fiber: 0, addWma: 0 },
        ac22p:    { label: 'AC 22 P (podbudowa)',   norm: 'EN 13108-1', tech: 'HMA',    fuel: 'olej', temp: 155, bitType: '530', aggType: '3.80', aggC: 640, aggF: 290, filler: 35, bitumen: 35,  ra: 0,   fiber: 0, addWma: 0 },
        sma11s:   { label: 'SMA 11 S (ścieralna)',  norm: 'EN 13108-5', tech: 'HMA',    fuel: 'olej', temp: 170, bitType: '530', aggType: '3.99', aggC: 700, aggF: 107, filler: 50, bitumen: 140, ra: 0,   fiber: 3, addWma: 0 },
        bbtm11:   { label: 'BBTM 11 A (ścieralna)', norm: 'EN 13108-2', tech: 'HMA',    fuel: 'olej', temp: 170, bitType: '560', aggType: '3.99', aggC: 690, aggF: 69,  filler: 50, bitumen: 190, ra: 0,   fiber: 1, addWma: 0 },
        pa11:     { label: 'PA 11 (ścieralna)',     norm: 'EN 13108-7', tech: 'HMA',    fuel: 'olej', temp: 175, bitType: '560', aggType: '3.99', aggC: 760, aggF: 40,  filler: 48, bitumen: 150, ra: 0,   fiber: 2, addWma: 0 },
        ma11:     { label: 'MA 11 (asfalt lany)',   norm: 'EN 13108-6', tech: 'HMA',    fuel: 'olej', temp: 230, bitType: '530', aggType: '3.20', aggC: 480, aggF: 200, filler: 70, bitumen: 250, ra: 0,   fiber: 0, addWma: 0 },
        ac16wma:  { label: 'AC 16 W-WMA (wiążąca)', norm: 'EN 13108-1', tech: 'WMA',    fuel: 'gaz',  temp: 130, bitType: '530', aggType: '3.80', aggC: 550, aggF: 327, filler: 50, bitumen: 70,  ra: 0,   fiber: 0, addWma: 3 },
        ac16ra30: { label: 'AC 16 W-RA30 (wiążąca)',norm: 'EN 13108-1', tech: 'HMA+RA', fuel: 'olej', temp: 165, bitType: '530', aggType: '3.80', aggC: 410, aggF: 224, filler: 36, bitumen: 30,  ra: 300, fiber: 0, addWma: 0 }
    };
    var DIST_DEFAULT = { bitumen: 150, agg: 50, filler: 80, ra: 30, fiber: 200, addWma: 300 };

    /* ---- Uchwyty DOM ---- */
    var el = function (id) { return document.getElementById(id); };
    var presetSel = el('mmaPreset');
    if (!presetSel) return;

    var tempInput = el('mmaTemp');
    var bitTypeSel = el('mmaTypeBit');
    var aggTypeSel = el('mmaTypeAgg');
    var fAggC = el('mAggC'), fAggF = el('mAggF'), fFiller = el('mFiller'),
        fBitumen = el('mBitumen'), fRA = el('mRA'), fFiber = el('mFiber'), fAddWma = el('mAddWma');
    var dBitumen = el('dBitumen'), dAgg = el('dAgg'), dFiller = el('dFiller'),
        dRA = el('dRA'), dFiber = el('dFiber'), dAddWma = el('dAddWma');
    var sumWarn = el('mmaSumWarn');

    var outTotal = el('mmaTotal'), outTotalNote = el('mmaTotalNote'),
        outA1 = el('mmaA1'), outA2 = el('mmaA2'), outA3 = el('mmaA3'),
        outA1pct = el('mmaA1pct'), outA2pct = el('mmaA2pct'), outA3pct = el('mmaA3pct'),
        a1Table = el('mmaA1Table'), benchBox = el('mmaBench');

    /* ---- Pomocnicze ---- */
    function num(input) { var v = parseFloat(input.value); return isNaN(v) ? 0 : v; }
    function fmt(n, d) {
        if (d === undefined) d = 2;
        return Number(n).toLocaleString('pl-PL', { minimumFractionDigits: d, maximumFractionDigits: d });
    }
    function radioVal(name) {
        var r = document.querySelector('input[name="' + name + '"]:checked');
        return r ? r.value : null;
    }
    function setRadio(name, value) {
        var r = document.querySelector('input[name="' + name + '"][value="' + value + '"]');
        if (r) r.checked = true;
    }
    function tempRefFor(tech) { return tech === 'WMA' ? TEMP_REF.WMA : TEMP_REF.HMA; }

    /* ---- Załadowanie presetu ---- */
    function loadPreset(name) {
        var p = PRESETS[name];
        if (!p) return; // "custom" — nie zmieniaj pól
        setRadio('mmaTech', p.tech);
        setRadio('mmaFuel', p.fuel);
        tempInput.value = p.temp;
        bitTypeSel.value = p.bitType;
        aggTypeSel.value = p.aggType;
        fAggC.value = p.aggC;
        fAggF.value = p.aggF;
        fFiller.value = p.filler;
        fBitumen.value = p.bitumen;
        fRA.value = p.ra;
        fFiber.value = p.fiber;
        fAddWma.value = p.addWma;
        dBitumen.value = DIST_DEFAULT.bitumen;
        dAgg.value = DIST_DEFAULT.agg;
        dFiller.value = DIST_DEFAULT.filler;
        dRA.value = DIST_DEFAULT.ra;
        dFiber.value = DIST_DEFAULT.fiber;
        dAddWma.value = DIST_DEFAULT.addWma;
    }

    /* ---- Benchmark kategorii ---- */
    function benchmarkFor(name) {
        if (/^sma|^ma11/.test(name)) return { lo: 110, hi: 175, cat: 'SMA / MA (~110–175 kg CO₂eq/t)' };
        if (/^bbtm|^pa11/.test(name)) return { lo: 110, hi: 145, cat: 'BBTM / PA (~110–145 kg CO₂eq/t)' };
        return { lo: 45, hi: 115, cat: 'AC — betony asfaltowe (~45–115 kg CO₂eq/t)' };
    }

    /* ---- Obliczenia ---- */
    function compute() {
        var tech = radioVal('mmaTech') || 'HMA';
        var fuel = radioVal('mmaFuel') || 'olej';
        var temp = num(tempInput);
        var gwpBit = parseFloat(bitTypeSel.value) || 530;
        var gwpAggC = parseFloat(aggTypeSel.value) || 3.80;

        var m = {
            aggC:   num(fAggC),
            aggF:   num(fAggF),
            filler: num(fFiller),
            bitumen:num(fBitumen),
            ra:     num(fRA),
            fiber:  num(fFiber),
            addWma: num(fAddWma)
        };
        var d = {
            bitumen: num(dBitumen),
            agg:     num(dAgg),
            filler:  num(dFiller),
            ra:      num(dRA),
            fiber:   num(dFiber),
            addWma:  num(dAddWma)
        };

        /* A1 — surowce (RA: GWP = 0) */
        var a1items = [
            { key: 'bitumen', name: 'Bitumen',                 mass: m.bitumen, gwp: gwpBit },
            { key: 'aggC',    name: 'Kruszywo grube łamane',   mass: m.aggC,    gwp: gwpAggC },
            { key: 'aggF',    name: 'Kruszywo drobne (piasek/żwir)', mass: m.aggF, gwp: GWP.aggFine },
            { key: 'filler',  name: 'Filler wapienny',         mass: m.filler,  gwp: GWP.filler },
            { key: 'fiber',   name: 'Włókno celulozowe',       mass: m.fiber,   gwp: GWP.fiber },
            { key: 'addWma',  name: 'Dodatek WMA chemiczny',   mass: m.addWma,  gwp: GWP.addWma },
            { key: 'ra',      name: 'Granulat asfaltowy RA (cut-off)', mass: m.ra, gwp: GWP.ra }
        ];
        var a1 = 0;
        a1items.forEach(function (it) { it.em = it.mass * it.gwp / 1000; a1 += it.em; });

        /* A2 — transport (masa w tonach × km × EF) */
        var a2 =
            (m.bitumen / 1000) * d.bitumen * EF_TRANSPORT +
            ((m.aggC + m.aggF) / 1000) * d.agg * EF_TRANSPORT +
            (m.filler / 1000) * d.filler * EF_TRANSPORT +
            (m.ra / 1000) * d.ra * EF_TRANSPORT +
            (m.fiber / 1000) * d.fiber * EF_TRANSPORT +
            (m.addWma / 1000) * d.addWma * EF_TRANSPORT;

        /* A3 — paliwo (z korektą temperatury) + energia elektryczna stała */
        var techKey = (tech === 'WMA') ? 'WMA' : 'HMA';
        var fuelBase = FUEL_BASE[techKey + '-' + fuel] || FUEL_BASE['HMA-olej'];
        var refT = tempRefFor(techKey);
        var tempFactor = 1 + Math.max(0, (temp - refT) / 10) * TEMP_STEP_PCT;
        var fuelEm = fuelBase * tempFactor;
        var a3 = fuelEm + EL_A3;

        var total = a1 + a2 + a3;
        var sumMass = m.aggC + m.aggF + m.filler + m.bitumen + m.ra + m.fiber + m.addWma;

        return {
            tech: tech, fuel: fuel, temp: temp, gwpBit: gwpBit, gwpAggC: gwpAggC,
            m: m, d: d, a1items: a1items, a1: a1, a2: a2, a3: a3, fuelEm: fuelEm, el: EL_A3,
            total: total, sumMass: sumMass, tempFactor: tempFactor
        };
    }

    /* ---- Wykres słupkowy A1/A2/A3 ---- */
    var modChart = null;
    function initChart() {
        var canvas = el('mmaModChart');
        if (!canvas || !window.Chart) return;
        modChart = new window.Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['A1 — surowce', 'A2 — transport', 'A3 — produkcja'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['rgba(155,59,59,0.8)', 'rgba(196,114,26,0.75)', 'rgba(30,58,138,0.75)'],
                    borderColor: ['#9B3B3B', '#C4721A', '#1E3A8A'],
                    borderWidth: 2, borderRadius: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { duration: 400, easing: 'easeOutQuart' },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#111318', borderColor: '#1E3A8A', borderWidth: 1,
                        titleColor: '#fff', bodyColor: 'rgba(255,255,255,0.75)', padding: 10,
                        callbacks: { label: function (c) { return ' ' + fmt(c.raw) + ' kg CO₂eq/t'; } }
                    }
                },
                scales: {
                    x: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { family: "'Inter', sans-serif", size: 11 }, color: '#6B7280' } },
                    y: {
                        beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: { font: { family: "'IBM Plex Mono', monospace", size: 10 }, color: '#9CA3AF',
                                 callback: function (v) { return fmt(v, 0) + ' kg'; } }
                    }
                }
            }
        });
    }
    function updateChart(r) {
        if (!modChart) return;
        modChart.data.datasets[0].data = [r.a1, r.a2, r.a3];
        modChart.update();
    }

    /* ---- Render wyników ---- */
    function render() {
        var r = compute();
        var t = r.total > 0 ? r.total : 1;

        outTotal.textContent = fmt(r.total, 2);
        outA1.textContent = fmt(r.a1, 2);
        outA2.textContent = fmt(r.a2, 2);
        outA3.textContent = fmt(r.a3, 2);
        outA1pct.textContent = fmt(r.a1 / t * 100, 1);
        outA2pct.textContent = fmt(r.a2 / t * 100, 1);
        outA3pct.textContent = fmt(r.a3 / t * 100, 1);

        var presetName = presetSel.value;
        var pLabel = PRESETS[presetName] ? PRESETS[presetName].label : 'Własna receptura';
        var techLabel = r.tech === 'WMA' ? 'WMA' : (r.tech === 'HMA+RA' ? 'HMA + RA' : 'HMA');
        var fuelLabel = r.fuel === 'gaz' ? 'gaz ziemny' : 'olej opałowy';
        outTotalNote.textContent = pLabel + ' · ' + techLabel + ' · ' + fuelLabel + ' · ' + fmt(r.temp, 0) + '°C';

        /* tabela A1 */
        var rows = '';
        r.a1items.forEach(function (it) {
            if (it.mass <= 0 && it.key !== 'bitumen' && it.key !== 'aggC') return;
            var sharePct = r.a1 > 0 ? (it.em / r.a1 * 100) : 0;
            rows += '<tr>' +
                '<td>' + it.name + '</td>' +
                '<td class="mono">' + fmt(it.mass, it.mass % 1 === 0 ? 0 : 1) + '</td>' +
                '<td class="mono">' + (it.key === 'ra' ? '0' : fmt(it.gwp, it.gwp < 10 ? 2 : 0)) + '</td>' +
                '<td class="mono highlight">' + fmt(it.em, 3) + '</td>' +
                '<td class="mono">' + fmt(sharePct, 1) + '</td>' +
                '</tr>';
        });
        rows += '<tr style="font-weight:600;background:rgba(30,58,138,0.03);">' +
            '<td>A1 — razem</td><td class="mono">' + fmt(r.sumMass, 0) + '</td><td class="mono">—</td>' +
            '<td class="mono highlight">' + fmt(r.a1, 2) + '</td><td class="mono">100,0</td></tr>';
        a1Table.innerHTML = rows;

        /* benchmark */
        var bm = benchmarkFor(presetName);
        var msg;
        if (r.total < bm.lo) {
            msg = 'GWP ' + fmt(r.total, 1) + ' kg CO₂eq/t — poniżej dolnej granicy przedziału referencyjnego ' + bm.cat + '.';
        } else if (r.total > bm.hi) {
            msg = 'GWP ' + fmt(r.total, 1) + ' kg CO₂eq/t — powyżej górnej granicy przedziału referencyjnego ' + bm.cat + ' (sprawdź zawartość lepiszcza i temperaturę).';
        } else {
            msg = 'GWP ' + fmt(r.total, 1) + ' kg CO₂eq/t — w przedziale referencyjnym dla ' + bm.cat + '.';
        }
        benchBox.textContent = msg;

        /* walidacja sumy składników */
        var dev = Math.abs(r.sumMass - 1000) / 1000 * 100;
        if (dev <= 2) {
            sumWarn.className = 'mma-warn ok';
            sumWarn.textContent = 'Suma składników: ' + fmt(r.sumMass, 0) + ' kg/t — zgodna z jednostką deklarowaną (1000 kg ±2%).';
        } else {
            sumWarn.className = 'mma-warn bad';
            sumWarn.textContent = 'Suma składników: ' + fmt(r.sumMass, 0) + ' kg/t — odbiega od 1000 kg/t o ' + fmt(dev, 1) + '%. Skoryguj recepturę (jednostka deklarowana = 1 tona MMA).';
        }

        updateChart(r);
        return r;
    }

    /* ---- Eksport ---- */
    function buildPayload() {
        var r = compute();
        var t = r.total > 0 ? r.total : 1;
        return { r: r, share: { a1: r.a1 / t * 100, a2: r.a2 / t * 100, a3: r.a3 / t * 100 } };
    }
    function copyText(text, btn, label) {
        function done() { var o = btn.textContent; btn.textContent = 'Skopiowano!'; setTimeout(function () { btn.textContent = label; }, 2000); }
        try {
            navigator.clipboard.writeText(text).then(done, function () {
                var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); done();
            });
        } catch (e) {
            var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); done();
        }
    }
    function num6(n) { return (Math.round(n * 1e6) / 1e6); }

    function exportCsv() {
        var p = buildPayload(), r = p.r;
        var presetName = presetSel.value;
        var pLabel = PRESETS[presetName] ? PRESETS[presetName].label : 'Własna receptura';
        var lines = [];
        lines.push('Kalkulator pre-qualify EPD dla MMA — poLCA;c-PCR-MMA-EPD-Polska-2026 v1.0-DRAFT;EN 15804+A2');
        lines.push('Preset;' + pLabel);
        lines.push('Technologia;' + r.tech);
        lines.push('Paliwo wytwórni;' + (r.fuel === 'gaz' ? 'gaz ziemny' : 'olej opałowy'));
        lines.push('Temperatura produkcji [°C];' + r.temp);
        lines.push('');
        lines.push('Składnik;Masa [kg/t];GWP jedn. [kg CO2eq/t];Emisja A1 [kg CO2eq/t]');
        r.a1items.forEach(function (it) {
            lines.push('"' + it.name + '";' + num6(it.mass) + ';' + (it.key === 'ra' ? 0 : num6(it.gwp)) + ';' + num6(it.em));
        });
        lines.push('Suma składników [kg/t];' + num6(r.sumMass) + ';;');
        lines.push('');
        lines.push('Moduł;Emisja [kg CO2eq/t MMA];Udział [%]');
        lines.push('A1 — surowce;' + num6(r.a1) + ';' + num6(p.share.a1));
        lines.push('A2 — transport;' + num6(r.a2) + ';' + num6(p.share.a2));
        lines.push('A3 — produkcja (paliwo ' + num6(r.fuelEm) + ' + energia el. ' + num6(r.el) + ');' + num6(r.a3) + ';' + num6(p.share.a3));
        lines.push('GWP A1-A3 — łącznie;' + num6(r.total) + ';100');
        lines.push('');
        lines.push('Uwaga;Oszacowanie pre-qualify — nie zastępuje pełnego EPD weryfikowanego (AVS 3+). Energia el. = poLCA-EN-PL-2024 v9.1 0,599 kg CO2e/kWh. Bitumen = Eurobitume LCA 4.0 (2025).');
        copyText(lines.join('\n'), el('mmaExportCsv'), 'Kopiuj CSV');
    }

    function exportJson() {
        var p = buildPayload(), r = p.r;
        var presetName = presetSel.value;
        var obj = {
            tool: 'poLCA — Kalkulator pre-qualify EPD dla MMA',
            standard: 'EN 15804+A2',
            pcr: 'c-PCR-MMA-EPD-Polska-2026 v1.0-DRAFT',
            note: 'Oszacowanie pre-qualify — nie zastępuje pełnego EPD weryfikowanego (AVS 3+).',
            preset: PRESETS[presetName] ? PRESETS[presetName].label : 'Własna receptura',
            declared_unit: '1 t (1000 kg) MMA',
            inputs: {
                technology: r.tech,
                plant_fuel: r.fuel === 'gaz' ? 'natural_gas' : 'fuel_oil',
                production_temp_C: r.temp,
                bitumen_GWP_kg_per_t: r.gwpBit,
                coarse_aggregate_GWP_kg_per_t: r.gwpAggC,
                recipe_kg_per_t: r.m,
                transport_distances_km: r.d
            },
            factors: {
                ef_transport_kg_per_t_km: EF_TRANSPORT,
                electricity_A3_kg_per_t: EL_A3,
                electricity_factor_kg_per_kWh: 0.599,
                fuel_base_kg_per_t: FUEL_BASE,
                temp_correction_factor: num6(r.tempFactor)
            },
            results_kg_CO2eq_per_t: {
                A1_raw_materials: num6(r.a1),
                A2_transport: num6(r.a2),
                A3_production: num6(r.a3),
                A3_breakdown: { fuel: num6(r.fuelEm), electricity: num6(r.el) },
                GWP_A1_A3_total: num6(r.total),
                shares_pct: { A1: num6(p.share.a1), A2: num6(p.share.a2), A3: num6(p.share.a3) },
                A1_components: r.a1items.map(function (it) {
                    return { component: it.name, mass_kg_per_t: num6(it.mass), gwp_kg_per_t: it.key === 'ra' ? 0 : num6(it.gwp), emission_kg_CO2eq_per_t: num6(it.em) };
                }),
                sum_components_kg_per_t: num6(r.sumMass)
            },
            timestamp: new Date().toISOString()
        };
        copyText(JSON.stringify(obj, null, 2), el('mmaExportJson'), 'Kopiuj JSON');
    }

    function xmlEsc(s) {
        return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    function downloadFile(text, filename, mime) {
        try {
            var blob = new Blob([text], { type: mime || 'application/xml;charset=utf-8' });
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url; a.download = filename;
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
            return true;
        } catch (e) { return false; }
    }

    function exportIlcdEpdXml() {
        var p = buildPayload(), r = p.r;
        var presetName = presetSel.value;
        var pLabel = PRESETS[presetName] ? PRESETS[presetName].label : 'Własna receptura';
        var tech = r.tech || 'HMA';
        var fuel = r.fuel === 'gaz' ? 'gaz ziemny' : 'olej opałowy';
        var name = 'Mieszanka mineralno-asfaltowa (MMA) — ' + pLabel + ' [' + tech + ']';
        var ts = new Date().toISOString();
        var x = [];
        x.push('<?xml version="1.0" encoding="UTF-8"?>');
        x.push('<ilcd:processDataSet xmlns:ilcd="http://lca.jrc.it/ILCD/Process" version="1.1">');
        x.push('  <!-- poLCA pre-qualify estimate — NOT a verified EPD. ILCD+EPD-compatible structure (simplified). -->');
        x.push('  <!-- Pełny EPD wymaga danych zakładowych i weryfikacji AVS 3+. Format DPP wg CEN/CENELEC EN 1821x (publikacja 2026) — zob. /o-polca/gotowosc-dpp.html -->');
        x.push('  <processInformation>');
        x.push('    <dataSetInformation>');
        x.push('      <name>' + xmlEsc(name) + '</name>');
        x.push('      <classification>Wyroby budowlane / Mieszanki mineralno-asfaltowe (EN 13108)</classification>');
        x.push('    </dataSetInformation>');
        x.push('    <quantitativeReference>');
        x.push('      <referenceFlow>1 t MMA (1000 kg, na wyjściu z wytwórni)</referenceFlow>');
        x.push('    </quantitativeReference>');
        x.push('    <geography><locationOfOperationSupplyOrProduction location="PL"/></geography>');
        x.push('    <technology>' + xmlEsc('Technologia: ' + tech + '; temperatura produkcji ' + r.temp + ' °C; paliwo wytwórni: ' + fuel) + '</technology>');
        x.push('  </processInformation>');
        x.push('  <modellingAndValidation>');
        x.push('    <complianceDeclarations>');
        x.push('      <compliance>EN 15804+A2:2019; c-PCR-MMA-EPD-Polska; ISO 14040/14044</compliance>');
        x.push('    </complianceDeclarations>');
        x.push('    <dataSourcesTreatmentAndRepresentativeness>');
        x.push('      <dataSource>POLCA-MMA-LCI-DEFAULTS-2026; poLCA-EN-PL-2024 v9.1 (0.599 kg CO2e/kWh); Eurobitume LCA 4.0 (2025)</dataSource>');
        x.push('    </dataSourcesTreatmentAndRepresentativeness>');
        x.push('  </modellingAndValidation>');
        x.push('  <exchanges>');
        x.push('    <!-- moduły EN 15804: A1, A2, A3 (GWP-total, kg CO2 eq / 1 t MMA) -->');
        x.push('    <exchange module="A1"><meanAmount>' + num6(r.a1) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        x.push('    <exchange module="A2"><meanAmount>' + num6(r.a2) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        x.push('    <exchange module="A3"><meanAmount>' + num6(r.a3) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        x.push('    <exchange module="A1-A3"><meanAmount>' + num6(r.total) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        x.push('  </exchanges>');
        x.push('  <administrativeInformation>');
        x.push('    <publicationAndOwnership>');
        x.push('      <referenceToOwnershipOfDataSet>Multicert Sp. z o.o. / EPD Polska</referenceToOwnershipOfDataSet>');
        x.push('      <dataSetVersion>poLCA-pre-qualify-2026.1</dataSetVersion>');
        x.push('      <generatedAt>' + xmlEsc(ts) + '</generatedAt>');
        x.push('    </publicationAndOwnership>');
        x.push('  </administrativeInformation>');
        x.push('</ilcd:processDataSet>');
        var xml = x.join('\n');
        var btn = el('mmaExportXml');
        if (downloadFile(xml, 'polca-mma-pre-qualify.xml', 'application/xml;charset=utf-8')) {
            var lbl = 'Eksport ILCD+EPD XML';
            btn.textContent = 'Pobrano XML';
            setTimeout(function () { btn.textContent = lbl; }, 2000);
        } else {
            copyText(xml, btn, 'Eksport ILCD+EPD XML');
        }
    }

    /* ---- Listenery ---- */
    presetSel.addEventListener('change', function () { loadPreset(presetSel.value); render(); });

    var inputs = [tempInput, bitTypeSel, aggTypeSel, fAggC, fAggF, fFiller, fBitumen, fRA, fFiber, fAddWma,
                  dBitumen, dAgg, dFiller, dRA, dFiber, dAddWma];
    inputs.forEach(function (i) {
        i.addEventListener('input', function () { presetSel.value = 'custom'; render(); });
        i.addEventListener('change', function () { presetSel.value = 'custom'; render(); });
    });
    document.querySelectorAll('input[name="mmaTech"], input[name="mmaFuel"]').forEach(function (rb) {
        rb.addEventListener('change', function () {
            /* zmiana technologii — dostosuj domyślną temperaturę bazową jeśli była standardowa */
            if (rb.name === 'mmaTech') {
                var cur = num(tempInput);
                if (rb.value === 'WMA' && (cur === 160 || cur >= 150)) tempInput.value = 130;
                if ((rb.value === 'HMA' || rb.value === 'HMA+RA') && cur < 140) tempInput.value = 160;
            }
            presetSel.value = 'custom';
            render();
        });
    });

    var btnCsv = el('mmaExportCsv'), btnJson = el('mmaExportJson'), btnXml = el('mmaExportXml');
    if (btnCsv) btnCsv.addEventListener('click', exportCsv);
    if (btnJson) btnJson.addEventListener('click', exportJson);
    if (btnXml) btnXml.addEventListener('click', exportIlcdEpdXml);

    /* ---- Init ---- */
    function init() { initChart(); loadPreset(presetSel.value); render(); }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else { init(); }
})();
