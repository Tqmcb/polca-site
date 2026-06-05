/**
 * poLCA — Kalkulator pre-qualify EPD dla kruszyw budowlanych
 * Wersja 1.0
 *
 * Oszacowanie GWP A1-A3 [kg CO2eq / t kruszywa] zgodne z c-PCR-AGG-EPD-Polska v0.9-DRAFT,
 * EN 12620 / EN 13242 i EN 15804+A2. Wartości domyślne: datasety POLCA-AGG-PL-*.
 * Energia elektryczna: poLCA-EN-PL-2024 v9.1 = 0,599 kg CO2e/kWh (cross-compliance).
 * Olej napędowy: 3,17 kg CO2e/L (KOBiZE 2024). Materiały wybuchowe: ~0,5 kg CO2e/kg.
 *
 * Tryb uproszczony: typ kruszywa -> wartość referencyjna GWP A1-A3 (+ opcjonalny A4).
 * Tryb zaawansowany (parametry zakładu):
 *   base = energia_kruszenia * 0.599 + paliwo * 3.17 + (wybuchowe * 0.5 jeśli skała lita)
 *        + (0.5 kWh/t * 0.599 jeśli płukanie) + transport_A2 * 0.100
 *   GWP_A1-A3 = base * (1 - rc%/100) + 2.50 * (rc%/100)         [dla rock='rc': base bez surowca]
 *   (+ opcjonalny A4 = transport_A4 * 0.100, raportowany osobno)
 */
(function () {
    'use strict';

    /* ---- Stałe wartości obliczeniowe (default data) ---- */
    var EF_EL = 0.599;          // kg CO2e / kWh — poLCA-EN-PL-2024 v9.1
    var EF_DIESEL = 3.17;       // kg CO2e / L — KOBiZE 2024
    var EF_EXPLOSIVE = 0.5;     // kg CO2e / kg materiału wybuchowego (ANFO / emulsja)
    var EF_TRANSPORT = 0.100;   // kg CO2e / (t·km) — mix flot EURO5/6 PL
    var WASH_KWH = 0.5;         // dodatkowe kWh/t przy płukaniu
    var GWP_RC = 2.50;          // GWP A1-A3 frakcji recyklingowej RC [kg CO2eq/t]

    /* ---- Domyślne parametry zakładu wg typu skały ---- */
    var ROCK_DEFAULTS = {
        hard:    { energy: 6, diesel: 0.4, explosive: 0.1, lita: true,  rcPct: 0,   label: 'skała lita twarda' },
        soft:    { energy: 3, diesel: 0.4, explosive: 0.1, lita: true,  rcPct: 0,   label: 'skała lita miękka (wapień)' },
        natural: { energy: 1, diesel: 0.3, explosive: 0,   lita: false, rcPct: 0,   label: 'kruszywo naturalne (piasek, żwir)' },
        rc:      { energy: 4, diesel: 0.4, explosive: 0,   lita: false, rcPct: 100, label: 'kruszywo recyklingowe RC' }
    };

    /* ---- Etykiety i benchmarki dla trybu uproszczonego ---- */
    var SIMPLE_LABELS = {
        '5.50': 'kruszywo łamane twarde (conservative default poLCA)',
        '3.99': 'kruszywo bazaltowe łamane (ITB EPD 706/2024 Trzuskawica)',
        '4.50': 'kruszywo granitowe łamane lub dolomitowe',
        '3.20': 'kruszywo wapienne łamane (Gruber et al. 2023)',
        '1.80': 'kruszywo naturalne — piasek, żwir',
        '3.80': 'kruszywo — średnia ważona PL (mix bazalt + granit + wapień)',
        '2.50': 'kruszywo recyklingowe RC (cut-off)'
    };

    /* ---- Uchwyty DOM ---- */
    var el = function (id) { return document.getElementById(id); };
    if (!el('aggTotal')) return;

    var paneSimple = el('paneSimple'), paneAdvanced = el('paneAdvanced');
    var sType = el('aggSimpleType'), sA4 = el('aggSimpleA4'), sEf = el('aggSimpleEf');
    var aRock = el('aggRock'), aEnergy = el('aggEnergy'), aDiesel = el('aggDiesel'),
        aExpl = el('aggExplosive'), aA2 = el('aggA2km'), aRc = el('aggRcPct'),
        aRcVal = el('aggRcPctVal'), aA4 = el('aggA4km');
    var inputWarn = el('aggInputWarn');

    var outTotal = el('aggTotal'), outTotalNote = el('aggTotalNote'), outA4Note = el('aggA4Note'),
        outCEnergy = el('aggCEnergy'), outCDiesel = el('aggCDiesel'), outCExpl = el('aggCExpl'),
        outCTrans = el('aggCTrans'), outCWash = el('aggCWash'),
        outCEnergyPct = el('aggCEnergyPct'), outCDieselPct = el('aggCDieselPct'),
        outCExplPct = el('aggCExplPct'), outCTransPct = el('aggCTransPct'), outCWashPct = el('aggCWashPct'),
        compTable = el('aggCompTable'), benchBox = el('aggBench');

    /* ---- Pomocnicze ---- */
    function num(input) { var v = parseFloat(input.value); return isNaN(v) ? 0 : v; }
    function fmt(n, d) {
        if (d === undefined) d = 2;
        return Number(n).toLocaleString('pl-PL', { minimumFractionDigits: d, maximumFractionDigits: d });
    }
    function num6(n) { return (Math.round(n * 1e6) / 1e6); }
    function radioVal(name) {
        var r = document.querySelector('input[name="' + name + '"]:checked');
        return r ? r.value : null;
    }
    function setRadio(name, value) {
        var r = document.querySelector('input[name="' + name + '"][value="' + value + '"]');
        if (r) r.checked = true;
    }
    function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

    /* ---- Załadowanie domyślnych parametrów po wyborze typu skały ---- */
    function loadRockDefaults(rock) {
        var d = ROCK_DEFAULTS[rock] || ROCK_DEFAULTS.hard;
        aEnergy.value = d.energy;
        aDiesel.value = d.diesel;
        aExpl.value = d.explosive;
        aExpl.disabled = !d.lita;
        setRadio('aggWash', 'no');
        aRc.value = d.rcPct;
        aRcVal.textContent = d.rcPct + '%';
        aA2.value = 2;
    }

    /* ---- Obliczenia ---- */
    function compute() {
        var mode = radioVal('aggMode') || 'simple';

        if (mode === 'simple') {
            var ref = parseFloat(sType.value) || 0;
            var a4km = clamp(num(sA4), 0, 500);
            var a4ef = parseFloat(sEf.value) || EF_TRANSPORT;
            var a4 = a4km * a4ef;
            // W trybie uproszczonym całość A1-A3 traktujemy jako "surowiec + przeróbka"
            // bez rozbicia parametrycznego; transport A2 wewnętrzny zawarty w wartości referencyjnej.
            var optType = sType.options[sType.selectedIndex];
            var label = (optType ? optType.text.split(' — ')[0] : '') ;
            return {
                mode: 'simple', ref: ref, a4km: a4km, a4ef: a4ef, a4: a4,
                total: ref, simpleLabel: label,
                comp: { energy: 0, diesel: 0, explosive: 0, transport: 0, wash: 0, refbase: ref }
            };
        }

        // ---- tryb zaawansowany ----
        var rock = aRock.value || 'hard';
        var rd = ROCK_DEFAULTS[rock] || ROCK_DEFAULTS.hard;
        var isLita = rd.lita;
        var isRC = (rock === 'rc');

        var energy = clamp(num(aEnergy), 0, 15);
        var diesel = clamp(num(aDiesel), 0, 2);
        var explosive = isLita ? clamp(num(aExpl), 0, 1) : 0;
        var washOn = (radioVal('aggWash') === 'yes');
        var a2km = clamp(num(aA2), 0, 50);
        var rcPct = clamp(num(aRc), 0, 100);
        var a4km = clamp(num(aA4), 0, 500);

        var cEnergy = energy * EF_EL;
        var cDiesel = diesel * EF_DIESEL;
        var cExpl = explosive * EF_EXPLOSIVE;            // tylko skała lita
        var cWash = washOn ? WASH_KWH * EF_EL : 0;       // dodatkowa energia płukania
        var cTrans = a2km * EF_TRANSPORT;

        var base = cEnergy + cDiesel + cExpl + cWash + cTrans;
        // Dla skał litych/naturalnych base obejmuje surowiec + przeróbkę + transport A2.
        // Dla RC surowiec ma zerowe obciążenie A1 (cut-off) — base to przeróbka + transport,
        // a domyślne rcPct = 100% (typ RC). Mieszanie frakcji: total = base*(1-rc/100) + GWP_RC*(rc/100).
        var total = base * (1 - rcPct / 100) + GWP_RC * (rcPct / 100);
        var a4 = a4km * EF_TRANSPORT;

        return {
            mode: 'advanced', rock: rock, rockLabel: rd.label, isLita: isLita, isRC: isRC,
            energy: energy, diesel: diesel, explosive: explosive, washOn: washOn,
            a2km: a2km, rcPct: rcPct, a4km: a4km, a4: a4,
            base: base, total: total,
            comp: { energy: cEnergy, diesel: cDiesel, explosive: cExpl, wash: cWash, transport: cTrans }
        };
    }

    /* ---- Wykres słupkowy komponentów ---- */
    var modChart = null;
    function initChart() {
        var canvas = el('aggModChart');
        if (!canvas || !window.Chart) return;
        modChart = new window.Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Energia\nkruszenia', 'Paliwo\nmaszyn', 'Materiały\nwybuchowe', 'Transport\nA2', 'Płukanie'],
                datasets: [{
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: ['rgba(30,58,138,0.78)', 'rgba(196,114,26,0.78)', 'rgba(155,59,59,0.78)', 'rgba(11,93,51,0.72)', 'rgba(99,102,241,0.68)'],
                    borderColor: ['#1E3A8A', '#C4721A', '#9B3B3B', '#0B5D33', '#6366F1'],
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
                        callbacks: {
                            title: function (items) { return items[0].label.replace(/\n/g, ' '); },
                            label: function (c) { return ' ' + fmt(c.raw) + ' kg CO₂eq/t'; }
                        }
                    }
                },
                scales: {
                    x: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { family: "'Inter', sans-serif", size: 10 }, color: '#6B7280', maxRotation: 0, autoSkip: false } },
                    y: {
                        beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: { font: { family: "'IBM Plex Mono', monospace", size: 10 }, color: '#9CA3AF',
                                 callback: function (v) { return fmt(v, 1) + ' kg'; } }
                    }
                }
            }
        });
    }
    function updateChart(r) {
        if (!modChart) return;
        var c = r.comp;
        if (r.mode === 'simple') {
            modChart.data.labels = ['Wartość\nreferencyjna A1-A3'];
            modChart.data.datasets[0].data = [r.ref];
            modChart.data.datasets[0].backgroundColor = ['rgba(155,59,59,0.78)'];
            modChart.data.datasets[0].borderColor = ['#9B3B3B'];
        } else {
            modChart.data.labels = ['Energia\nkruszenia', 'Paliwo\nmaszyn', 'Materiały\nwybuchowe', 'Transport\nA2', 'Płukanie'];
            modChart.data.datasets[0].data = [c.energy, c.diesel, c.explosive, c.transport, c.wash];
            modChart.data.datasets[0].backgroundColor = ['rgba(30,58,138,0.78)', 'rgba(196,114,26,0.78)', 'rgba(155,59,59,0.78)', 'rgba(11,93,51,0.72)', 'rgba(99,102,241,0.68)'];
            modChart.data.datasets[0].borderColor = ['#1E3A8A', '#C4721A', '#9B3B3B', '#0B5D33', '#6366F1'];
        }
        modChart.update();
    }

    /* ---- Benchmark ---- */
    function benchmark(r) {
        // Conservative defaults poLCA per kategoria
        var ref;
        if (r.mode === 'simple') {
            var v = r.ref;
            if (v >= 5.0) ref = { v: 5.5, cat: 'kruszyw łamanych twardych (conservative default poLCA 5,5)' };
            else if (v <= 2.0) ref = { v: 1.8, cat: 'kruszyw naturalnych (default ~1,8)' };
            else if (v <= 3.4) ref = { v: 3.2, cat: 'kruszyw wapiennych (default ~3,2)' };
            else ref = { v: 3.8, cat: 'kruszyw — średnia ważona PL (~3,8)' };
        } else {
            if (r.isRC) ref = { v: GWP_RC, cat: 'kruszyw recyklingowych RC (~2,5)' };
            else if (r.rock === 'natural') ref = { v: 1.8, cat: 'kruszyw naturalnych (default ~1,8)' };
            else if (r.rock === 'soft') ref = { v: 3.2, cat: 'kruszyw wapiennych (default ~3,2)' };
            else ref = { v: 5.5, cat: 'kruszyw łamanych twardych (conservative default poLCA 5,5)' };
        }
        var t = r.total;
        var diff = t - ref.v;
        var rel = ref.v > 0 ? Math.abs(diff) / ref.v * 100 : 0;
        var dir;
        if (Math.abs(diff) < 0.05) dir = 'na poziomie';
        else if (diff < 0) dir = 'niżej (o ' + fmt(rel, 0) + '%) niż';
        else dir = 'wyżej (o ' + fmt(rel, 0) + '%) niż';
        return 'GWP ' + fmt(t, 2) + ' kg CO₂eq/t — to ' + dir + ' conservative default poLCA dla ' + ref.cat + '.';
    }

    /* ---- Render ---- */
    function render() {
        var r = compute();
        var c = r.comp;

        outTotal.textContent = fmt(r.total, 2);

        // notki
        if (r.mode === 'simple') {
            outTotalNote.textContent = 'Tryb uproszczony · ' + r.simpleLabel;
        } else {
            var rcTxt = r.rcPct > 0 ? ' · ' + fmt(r.rcPct, 0) + '% frakcji RC' : '';
            var washTxt = r.washOn ? ' · płukanie' : '';
            outTotalNote.textContent = 'Tryb zaawansowany · ' + r.rockLabel + rcTxt + washTxt;
        }
        if (r.a4 > 0) {
            outA4Note.style.display = 'block';
            outA4Note.textContent = '+ moduł A4 (transport do budowy) = ' + fmt(r.a4, 2) + ' kg CO₂eq/t · razem A1-A4 ≈ ' + fmt(r.total + r.a4, 2) + ' kg CO₂eq/t (A4 raportowane osobno).';
        } else {
            outA4Note.style.display = 'none';
            outA4Note.textContent = '';
        }

        // kafelki komponentów
        function setMod(valEl, pctEl, val, denom) {
            valEl.textContent = fmt(val, 2);
            pctEl.textContent = denom > 0 ? fmt(val / denom * 100, 1) : '0,0';
        }
        if (r.mode === 'simple') {
            outCEnergy.textContent = '—'; outCEnergyPct.textContent = '—';
            outCDiesel.textContent = '—'; outCDieselPct.textContent = '—';
            outCExpl.textContent = '—'; outCExplPct.textContent = '—';
            outCTrans.textContent = '—'; outCTransPct.textContent = '—';
            outCWash.textContent = '—'; outCWashPct.textContent = '—';
        } else {
            // udziały liczone względem base (bez RC blendingu) — bardziej czytelne
            var denom = r.base > 0 ? r.base : 1;
            setMod(outCEnergy, outCEnergyPct, c.energy, denom);
            setMod(outCDiesel, outCDieselPct, c.diesel, denom);
            setMod(outCExpl, outCExplPct, c.explosive, denom);
            setMod(outCTrans, outCTransPct, c.transport, denom);
            setMod(outCWash, outCWashPct, c.wash, denom);
        }

        // tabela
        var rows = '';
        if (r.mode === 'simple') {
            var optType = sType.options[sType.selectedIndex];
            rows += '<tr><td>Wartość referencyjna A1-A3</td><td class="mono">' + (optType ? optType.text.split(' — ')[0] : '') + '</td><td class="mono">' + fmt(r.ref, 2) + ' kg CO₂eq/t</td><td class="mono highlight">' + fmt(r.ref, 2) + '</td><td class="mono">100,0</td></tr>';
            if (r.a4 > 0) {
                rows += '<tr><td>Transport A4 do budowy (poza A1-A3)</td><td class="mono">' + fmt(r.a4km, 0) + ' km</td><td class="mono">' + fmt(r.a4ef, 3) + ' kg/(t·km)</td><td class="mono highlight">' + fmt(r.a4, 2) + '</td><td class="mono">—</td></tr>';
            }
        } else {
            var dn = r.base > 0 ? r.base : 1;
            var items = [
                { n: 'Energia el. kruszenia / przesiewania', p: fmt(r.energy, r.energy % 1 === 0 ? 0 : 1) + ' kWh/t', ef: '0,599 kg/kWh', em: c.energy },
                { n: 'Olej napędowy maszyn (koparki, ładowarki)', p: fmt(r.diesel, 2) + ' L/t', ef: '3,17 kg/L', em: c.diesel },
                { n: 'Materiały wybuchowe' + (r.isLita ? '' : ' (n/d — nie skała lita)'), p: fmt(r.explosive, 2) + ' kg/t', ef: '0,5 kg/kg', em: c.explosive },
                { n: 'Płukanie kruszywa' + (r.washOn ? '' : ' (wyłączone)'), p: r.washOn ? '+0,5 kWh/t' : '0', ef: '0,599 kg/kWh', em: c.wash },
                { n: 'Transport wewnętrzny A2', p: fmt(r.a2km, r.a2km % 1 === 0 ? 0 : 1) + ' km', ef: '0,100 kg/(t·km)', em: c.transport }
            ];
            items.forEach(function (it) {
                rows += '<tr><td>' + it.n + '</td><td class="mono">' + it.p + '</td><td class="mono">' + it.ef + '</td><td class="mono highlight">' + fmt(it.em, 3) + '</td><td class="mono">' + fmt(it.em / dn * 100, 1) + '</td></tr>';
            });
            rows += '<tr style="font-weight:600;background:rgba(30,58,138,0.03);"><td>Suma komponentów (frakcja pierwotna)</td><td class="mono">—</td><td class="mono">—</td><td class="mono highlight">' + fmt(r.base, 2) + '</td><td class="mono">100,0</td></tr>';
            if (r.rcPct > 0) {
                rows += '<tr><td>Frakcja recyklingowa RC (' + fmt(r.rcPct, 0) + '%)</td><td class="mono">' + fmt(r.rcPct, 0) + '%</td><td class="mono">' + fmt(GWP_RC, 2) + ' kg CO₂eq/t</td><td class="mono highlight">' + fmt(GWP_RC * (r.rcPct / 100), 2) + '</td><td class="mono">—</td></tr>';
                rows += '<tr style="font-weight:600;background:rgba(155,59,59,0.04);"><td>GWP A1-A3 — wynik mieszany</td><td class="mono">—</td><td class="mono">—</td><td class="mono highlight">' + fmt(r.total, 2) + '</td><td class="mono">—</td></tr>';
            }
            if (r.a4 > 0) {
                rows += '<tr><td>Transport A4 do budowy (poza A1-A3)</td><td class="mono">' + fmt(r.a4km, 0) + ' km</td><td class="mono">0,100 kg/(t·km)</td><td class="mono highlight">' + fmt(r.a4, 2) + '</td><td class="mono">—</td></tr>';
            }
        }
        compTable.innerHTML = rows;

        benchBox.textContent = benchmark(r);

        // walidacja zakresów (tryb zaawansowany)
        var probs = [];
        if (r.mode === 'advanced') {
            if (num(aEnergy) < 0 || num(aEnergy) > 15) probs.push('energia kruszenia poza zakresem 0–15 kWh/t');
            if (num(aDiesel) < 0 || num(aDiesel) > 2) probs.push('olej napędowy poza zakresem 0–2 L/t');
            if (r.isLita && (num(aExpl) < 0 || num(aExpl) > 1)) probs.push('materiały wybuchowe poza zakresem 0–1 kg/t');
            if (num(aA2) < 0 || num(aA2) > 50) probs.push('transport A2 poza zakresem 0–50 km');
        }
        if (num(r.mode === 'simple' ? sA4 : aA4) < 0 || num(r.mode === 'simple' ? sA4 : aA4) > 500) probs.push('transport A4 poza zakresem 0–500 km');
        if (probs.length) {
            inputWarn.className = 'agg-warn bad';
            inputWarn.textContent = 'Uwaga: ' + probs.join('; ') + ' — wartości zostały ograniczone do dopuszczalnego zakresu w obliczeniach.';
        } else {
            inputWarn.className = 'agg-warn ok';
            inputWarn.textContent = r.mode === 'simple'
                ? 'Tryb uproszczony — wynik to wartość referencyjna GWP A1-A3 wg datasetów POLCA-AGG-PL.'
                : 'Parametry w dopuszczalnych zakresach.';
        }

        updateChart(r);
        return r;
    }

    /* ---- Eksport ---- */
    function copyText(text, btn, label) {
        function done() { btn.textContent = 'Skopiowano!'; setTimeout(function () { btn.textContent = label; }, 2000); }
        try {
            navigator.clipboard.writeText(text).then(done, function () {
                var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); done();
            });
        } catch (e) {
            var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); done();
        }
    }

    function exportCsv() {
        var r = compute();
        var lines = [];
        lines.push('Kalkulator pre-qualify EPD dla kruszyw — poLCA;c-PCR-AGG-EPD-Polska v0.9-DRAFT;EN 12620 / EN 13242;EN 15804+A2');
        lines.push('Jednostka deklarowana;1 t kruszywa na bramie kopalni / zakładu przeróbki');
        lines.push('Tryb;' + (r.mode === 'simple' ? 'uproszczony' : 'zaawansowany'));
        if (r.mode === 'simple') {
            lines.push('Typ kruszywa;' + r.simpleLabel);
            lines.push('GWP A1-A3 referencyjne [kg CO2eq/t];' + num6(r.ref));
            if (r.a4 > 0) {
                lines.push('Transport A4 do budowy [km];' + num6(r.a4km));
                lines.push('EF transportu A4 [kg CO2eq/(t·km)];' + num6(r.a4ef));
                lines.push('Emisja A4 [kg CO2eq/t];' + num6(r.a4));
            }
        } else {
            lines.push('Typ skały / surowca;' + r.rockLabel);
            lines.push('Energia el. kruszenia [kWh/t];' + num6(r.energy));
            lines.push('Olej napędowy maszyn [L/t];' + num6(r.diesel));
            lines.push('Materiały wybuchowe [kg/t];' + num6(r.explosive));
            lines.push('Płukanie;' + (r.washOn ? 'tak (+0,5 kWh/t)' : 'nie'));
            lines.push('Transport wewnętrzny A2 [km];' + num6(r.a2km));
            lines.push('Zawartość frakcji RC [%];' + num6(r.rcPct));
            lines.push('Transport A4 do budowy [km];' + num6(r.a4km));
            lines.push('');
            lines.push('Komponent;Emisja [kg CO2eq/t];Udział w sumie komponentów [%]');
            var dn = r.base > 0 ? r.base : 1;
            var c = r.comp;
            lines.push('Energia kruszenia (' + num6(r.energy) + ' kWh/t × 0,599);' + num6(c.energy) + ';' + num6(c.energy / dn * 100));
            lines.push('Paliwo maszyn (' + num6(r.diesel) + ' L/t × 3,17);' + num6(c.diesel) + ';' + num6(c.diesel / dn * 100));
            lines.push('Materiały wybuchowe (' + num6(r.explosive) + ' kg/t × 0,5);' + num6(c.explosive) + ';' + num6(c.explosive / dn * 100));
            lines.push('Transport A2 (' + num6(r.a2km) + ' km × 0,100);' + num6(c.transport) + ';' + num6(c.transport / dn * 100));
            lines.push('Płukanie (' + (r.washOn ? '+0,5 kWh/t × 0,599' : '0') + ');' + num6(c.wash) + ';' + num6(c.wash / dn * 100));
            lines.push('Suma komponentów (frakcja pierwotna);' + num6(r.base) + ';100');
            if (r.rcPct > 0) {
                lines.push('Frakcja RC (' + num6(r.rcPct) + '% × 2,50);' + num6(GWP_RC * (r.rcPct / 100)) + ';');
            }
            if (r.a4 > 0) lines.push('Transport A4 do budowy;' + num6(r.a4) + ';');
        }
        lines.push('');
        lines.push('GWP A1-A3 — łącznie [kg CO2eq/t];' + num6(r.total) + ';');
        if (r.a4 > 0) lines.push('GWP A1-A4 — łącznie (A4 raportowane osobno) [kg CO2eq/t];' + num6(r.total + r.a4) + ';');
        lines.push('');
        lines.push('Uwaga;Oszacowanie pre-qualify — nie zastępuje pełnego EPD weryfikowanego (AVS 3+). Energia el. = poLCA-EN-PL-2024 v9.1 0,599 kg CO2e/kWh. Olej napędowy = 3,17 kg CO2e/L (KOBiZE 2024). Materiały wybuchowe = ~0,5 kg CO2e/kg. Kruszywo to składnik masowy — pierwszeństwo mają EPD kopalni.');
        copyText(lines.join('\n'), el('aggExportCsv'), 'Kopiuj CSV');
    }

    function exportJson() {
        var r = compute();
        var c = r.comp;
        var obj = {
            tool: 'poLCA — Kalkulator pre-qualify EPD dla kruszyw',
            standard: ['EN 15804+A2', 'EN 12620', 'EN 13242'],
            pcr: 'c-PCR-AGG-EPD-Polska v0.9-DRAFT',
            note: 'Oszacowanie pre-qualify — nie zastępuje pełnego EPD weryfikowanego (AVS 3+). Kruszywo to składnik masowy — pierwszeństwo mają EPD kopalni.',
            declared_unit: '1 t kruszywa na bramie kopalni / zakładu przeróbki',
            mode: r.mode,
            factors: {
                electricity_factor_kg_per_kWh: EF_EL,
                diesel_factor_kg_per_L: EF_DIESEL,
                explosive_factor_kg_per_kg: EF_EXPLOSIVE,
                ef_transport_kg_per_t_km: EF_TRANSPORT,
                wash_extra_kWh_per_t: WASH_KWH,
                rc_fraction_GWP_kg_per_t: GWP_RC,
                electricity_source: 'poLCA-EN-PL-2024 v9.1',
                diesel_source: 'KOBiZE 2024'
            }
        };
        if (r.mode === 'simple') {
            obj.inputs = {
                aggregate_type: r.simpleLabel,
                reference_GWP_A1_A3_kg_per_t: num6(r.ref),
                transport_A4_km: num6(r.a4km),
                transport_A4_ef_kg_per_t_km: num6(r.a4ef)
            };
            obj.results_kg_CO2eq_per_t = {
                GWP_A1_A3_total: num6(r.total),
                A4_transport_to_site: num6(r.a4),
                GWP_A1_A4_total: num6(r.total + r.a4)
            };
        } else {
            obj.inputs = {
                rock_type: r.rock,
                rock_label: r.rockLabel,
                is_solid_rock: r.isLita,
                is_recycled: r.isRC,
                crushing_electricity_kWh_per_t: num6(r.energy),
                machinery_diesel_L_per_t: num6(r.diesel),
                explosives_kg_per_t: num6(r.explosive),
                washing: r.washOn,
                internal_transport_A2_km: num6(r.a2km),
                rc_fraction_pct: num6(r.rcPct),
                transport_A4_km: num6(r.a4km)
            };
            obj.results_kg_CO2eq_per_t = {
                components: {
                    crushing_energy: num6(c.energy),
                    machinery_fuel: num6(c.diesel),
                    explosives: num6(c.explosive),
                    transport_A2: num6(c.transport),
                    washing: num6(c.wash)
                },
                primary_fraction_base: num6(r.base),
                rc_fraction_contribution: num6(GWP_RC * (r.rcPct / 100)),
                GWP_A1_A3_total: num6(r.total),
                A4_transport_to_site: num6(r.a4),
                GWP_A1_A4_total: num6(r.total + r.a4)
            };
        }
        obj.timestamp = new Date().toISOString();
        copyText(JSON.stringify(obj, null, 2), el('aggExportJson'), 'Kopiuj JSON');
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
        var r = compute();
        var c = r.comp || {};
        var a2 = (typeof c.transport === 'number') ? c.transport : 0;
        var a1a3 = r.total;
        var a13 = a1a3 - a2; // A1+A3 łącznie (pozyskanie + przeróbka, bez transportu wewnętrznego)
        var label = r.mode === 'simple' ? (r.simpleLabel || 'kruszywo') : (r.rockLabel || 'kruszywo');
        var name = 'Kruszywo budowlane — ' + label + (r.mode === 'simple' ? ' (tryb uproszczony)' : ' (tryb zaawansowany)');
        var tech = r.mode === 'simple'
            ? 'Wartość referencyjna GWP A1-A3 wg datasetów POLCA-AGG-PL'
            : ('Pozyskanie i przeróbka: energia kruszenia ' + num6(r.energy) + ' kWh/t; olej napędowy ' + num6(r.diesel) + ' L/t; materiały wybuchowe ' + num6(r.explosive) + ' kg/t; płukanie: ' + (r.washOn ? 'tak' : 'nie') + '; transport wewnętrzny ' + num6(r.a2km) + ' km' + (r.rcPct > 0 ? '; frakcja recyklingowa RC ' + num6(r.rcPct) + '%' : ''));
        var ts = new Date().toISOString();
        var x = [];
        x.push('<?xml version="1.0" encoding="UTF-8"?>');
        x.push('<ilcd:processDataSet xmlns:ilcd="http://lca.jrc.it/ILCD/Process" version="1.1">');
        x.push('  <!-- poLCA pre-qualify estimate — NOT a verified EPD. ILCD+EPD-compatible structure (simplified). -->');
        x.push('  <!-- Pełny EPD wymaga danych zakładowych i weryfikacji AVS 3+. Format DPP wg CEN/CENELEC EN 1821x (publikacja 2026) — zob. /o-polca/gotowosc-dpp.html -->');
        x.push('  <processInformation>');
        x.push('    <dataSetInformation>');
        x.push('      <name>' + xmlEsc(name) + '</name>');
        x.push('      <classification>Wyroby budowlane / Kruszywa (EN 12620, EN 13242)</classification>');
        x.push('    </dataSetInformation>');
        x.push('    <quantitativeReference>');
        x.push('      <referenceFlow>1 t kruszywa (na bramie kopalni / zakładu przeróbki)</referenceFlow>');
        x.push('    </quantitativeReference>');
        x.push('    <geography><locationOfOperationSupplyOrProduction location="PL"/></geography>');
        x.push('    <technology>' + xmlEsc(tech) + '</technology>');
        x.push('  </processInformation>');
        x.push('  <modellingAndValidation>');
        x.push('    <complianceDeclarations>');
        x.push('      <compliance>EN 15804+A2:2019; c-PCR-AGG-EPD-Polska; ISO 14040/14044</compliance>');
        x.push('    </complianceDeclarations>');
        x.push('    <dataSourcesTreatmentAndRepresentativeness>');
        x.push('      <dataSource>POLCA-AGG-LCI-DEFAULTS-2026; poLCA-EN-PL-2024 v9.1 (0.599 kg CO2e/kWh); KOBiZE 2024 (olej napędowy 3.17 kg CO2e/L)</dataSource>');
        x.push('    </dataSourcesTreatmentAndRepresentativeness>');
        x.push('  </modellingAndValidation>');
        x.push('  <exchanges>');
        x.push('    <!-- moduły EN 15804: A1+A3 (pozyskanie + przeróbka), A2 (transport wewnętrzny), A1-A3 GWP-total, kg CO2 eq / 1 t kruszywa -->');
        x.push('    <exchange module="A1-A3-acquisition-processing"><meanAmount>' + num6(a13) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        x.push('    <exchange module="A2"><meanAmount>' + num6(a2) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        x.push('    <exchange module="A1-A3"><meanAmount>' + num6(a1a3) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        if (r.a4 > 0) {
            x.push('    <!-- A4 transport na budowę — raportowane osobno, poza A1-A3 -->');
            x.push('    <exchange module="A4"><meanAmount>' + num6(r.a4) + '</meanAmount><unit>kg CO2 eq</unit></exchange>');
        }
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
        var btn = el('aggExportXml');
        if (downloadFile(xml, 'polca-kruszywa-pre-qualify.xml', 'application/xml;charset=utf-8')) {
            var lbl = 'Eksport ILCD+EPD XML';
            btn.textContent = 'Pobrano XML';
            setTimeout(function () { btn.textContent = lbl; }, 2000);
        } else {
            copyText(xml, btn, 'Eksport ILCD+EPD XML');
        }
    }

    /* ---- Przełączanie trybu ---- */
    function applyMode() {
        var mode = radioVal('aggMode') || 'simple';
        if (mode === 'simple') {
            paneSimple.classList.add('active');
            paneAdvanced.classList.remove('active');
        } else {
            paneSimple.classList.remove('active');
            paneAdvanced.classList.add('active');
        }
        render();
    }

    /* ---- Listenery ---- */
    document.querySelectorAll('input[name="aggMode"]').forEach(function (rb) {
        rb.addEventListener('change', applyMode);
    });
    aRock.addEventListener('change', function () { loadRockDefaults(aRock.value); render(); });
    aRc.addEventListener('input', function () { aRcVal.textContent = num(aRc) + '%'; render(); });

    var advInputs = [aEnergy, aDiesel, aExpl, aA2, aA4];
    advInputs.forEach(function (i) {
        i.addEventListener('input', render);
        i.addEventListener('change', render);
    });
    document.querySelectorAll('input[name="aggWash"]').forEach(function (rb) {
        rb.addEventListener('change', render);
    });
    var simpleInputs = [sType, sA4, sEf];
    simpleInputs.forEach(function (i) {
        i.addEventListener('input', render);
        i.addEventListener('change', render);
    });

    var btnCsv = el('aggExportCsv'), btnJson = el('aggExportJson'), btnXml = el('aggExportXml');
    if (btnCsv) btnCsv.addEventListener('click', exportCsv);
    if (btnJson) btnJson.addEventListener('click', exportJson);
    if (btnXml) btnXml.addEventListener('click', exportIlcdEpdXml);

    /* ---- Init ---- */
    function init() {
        initChart();
        loadRockDefaults(aRock.value);
        applyMode();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else { init(); }
})();
