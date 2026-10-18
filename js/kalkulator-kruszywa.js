/** poLCA — kalkulator kruszyw. Historyczny zestaw założeń; eksport własny poLCA 2.0. */
(function () {
    'use strict';

    /* ---- Stałe wartości obliczeniowe (default data) ---- */
    var EF_EL = 0.599;          // kg CO2e / kWh — poLCA-EN-PL-2024 v9.1
    var EF_DIESEL = 3.17;       // kg CO2e / L — historyczne założenie kalkulatora
    var EF_EXPLOSIVE = 0.5;     // kg CO2e / kg materiału wybuchowego (ANFO / emulsja)
    var EF_TRANSPORT = 0.100;   // kg CO2e / (t·km) — historyczne założenie kalkulatora
    var WASH_KWH = 0.5;         // dodatkowe kWh/t przy płukaniu
    var GWP_RC = 2.50;          // Oszacowanie A1-A3 frakcji recyklingowej RC [kg CO2eq/t]

    /* ---- Domyślne parametry zakładu wg typu skały ---- */
    var ROCK_DEFAULTS = {
        hard:    { energy: 6, diesel: 0.4, explosive: 0.1, lita: true,  rcPct: 0,   label: 'skała lita twarda' },
        soft:    { energy: 3, diesel: 0.4, explosive: 0.1, lita: true,  rcPct: 0,   label: 'skała lita miękka (wapień)' },
        natural: { energy: 1, diesel: 0.3, explosive: 0,   lita: false, rcPct: 0,   label: 'kruszywo naturalne (piasek, żwir)' },
        rc:      { energy: 4, diesel: 0.4, explosive: 0,   lita: false, rcPct: 100, label: 'kruszywo recyklingowe RC' }
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
    function num(input) { return input.value.trim() === '' ? NaN : Number(input.value); }
    function fmt(n, d) {
        if (d === undefined) d = 2;
        return Number(n).toLocaleString('pl-PL', { minimumFractionDigits: d, maximumFractionDigits: d });
    }
    function num6(n) { return Math.abs(n) > Number.MAX_VALUE / 1e6 ? n : Math.round(n * 1e6) / 1e6; }
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

    function syncPrimaryInputs() {
        var fixed = radioVal('aggMode') === 'advanced' && clamp(num(aRc), 0, 100) === 100;
        [aEnergy, aDiesel, aA2].forEach(function (input) { input.disabled = fixed; });
        var rock = ROCK_DEFAULTS[aRock.value] || ROCK_DEFAULTS.hard;
        aExpl.disabled = fixed || !rock.lita;
        document.querySelectorAll('input[name="aggWash"]').forEach(function (input) { input.disabled = fixed; });
        var note = el('aggRcScope');
        if (note) note.hidden = radioVal('aggMode') !== 'advanced';
        if (note) note.textContent = fixed
            ? 'RC = 100%: stały wariant 2,50 kg CO₂e/t. Energia, paliwo, materiały wybuchowe, płukanie i transport wewnętrzny nie zmieniają tego wyniku. Transport do budowy A4 jest liczony osobno.'
            : 'Parametry procesu dotyczą 1 t frakcji pierwotnej. Jej wkład jest mnożony przez udział (100% − RC). Wkład RC wynosi 2,50 kg CO₂e/t × udział RC.';
    }
    function contributions(r) {
        if (r.mode === 'simple') return { reference: r.ref };
        var share = 1 - r.rcPct / 100;
        return { energy: r.comp.energy * share, diesel: r.comp.diesel * share,
            explosive: r.comp.explosive * share, transport: r.comp.transport * share,
            wash: r.comp.wash * share, recycled: GWP_RC * r.rcPct / 100 };
    }

    function checkNumber(input, label, min, max, errors) {
        var raw = input.value.trim();
        var value = raw === '' ? NaN : Number(raw);
        var valid = Number.isFinite(value) && value >= min && (max === null || value <= max);
        input.setAttribute('aria-invalid', String(!valid));
        if (!valid) errors.push(label + ': ' + (max === null ? 'wpisz skończoną liczbę nie mniejszą niż ' + min : 'wpisz liczbę od ' + min + ' do ' + max));
        return value;
    }
    function checkChoice(input, choices, label, errors) {
        var valid = choices.indexOf(input.value) !== -1;
        input.setAttribute('aria-invalid', String(!valid));
        if (!valid) errors.push(label + ': wybierz pozycję z listy');
    }
    function inputErrors() {
        var errors = [];
        var mode = radioVal('aggMode');
        if (['simple', 'advanced'].indexOf(mode) < 0) return ['Wybierz tryb obliczeń'];
        [sType, sA4, sEf, aRock, aEnergy, aDiesel, aExpl, aA2, aRc, aA4].forEach(function (input) { input.setAttribute('aria-invalid', 'false'); });
        if (mode === 'simple') {
            checkChoice(sType, ['5.50', '3.99', '4.50', '3.20', '1.80', '3.80', '2.50'], 'Typ kruszywa', errors);
            checkChoice(sEf, ['0.100', '0.031', '0.049', '0.082'], 'Współczynnik transportu', errors);
            checkNumber(sA4, 'Transport A4 [km]', 0, 500, errors);
        } else {
            checkChoice(aRock, Object.keys(ROCK_DEFAULTS), 'Typ skały', errors);
            var rc = checkNumber(aRc, 'Udział RC [%]', 0, 100, errors);
            checkNumber(aA4, 'Transport A4 [km]', 0, 500, errors);
            if (rc !== 100) {
                checkNumber(aEnergy, 'Energia [kWh/t]', 0, 15, errors);
                checkNumber(aDiesel, 'Olej napędowy [L/t]', 0, 2, errors);
                checkNumber(aA2, 'Transport wewnętrzny [km]', 0, 50, errors);
                if (ROCK_DEFAULTS[aRock.value] && ROCK_DEFAULTS[aRock.value].lita) checkNumber(aExpl, 'Materiały wybuchowe [kg/t]', 0, 1, errors);
                if (['yes', 'no'].indexOf(radioVal('aggWash')) < 0) errors.push('Wybierz wariant płukania');
            }
        }
        return errors;
    }
    function setValidation(errors) {
        ['aggExportCsv', 'aggExportJson', 'aggExportXml'].forEach(function (id) { el(id).disabled = errors.length > 0; });
        if (!errors.length) return;
        inputWarn.className = 'agg-warn bad';
        inputWarn.textContent = 'Popraw dane: ' + errors.join('; ') + '. Obliczenie i eksport są wstrzymane.';
        [outTotal, outCEnergy, outCDiesel, outCExpl, outCTrans, outCWash, outCEnergyPct, outCDieselPct, outCExplPct, outCTransPct, outCWashPct].forEach(function (node) { node.textContent = '—'; });
        outTotalNote.textContent = 'Brak wyniku dla niepoprawnych lub niekompletnych danych.';
        outA4Note.textContent = ''; outA4Note.style.display = 'none';
        compTable.textContent = ''; benchBox.textContent = '';
        if (modChart) { modChart.data.datasets[0].data = []; modChart.update(); }
    }

    /* ---- Obliczenia ---- */
    function compute() {
        syncPrimaryInputs();
        var errors = inputErrors();
        setValidation(errors);
        if (errors.length) return null;
        var mode = radioVal('aggMode');

        if (mode === 'simple') {
            var ref = Number(sType.value);
            var a4km = num(sA4);
            var a4ef = Number(sEf.value);
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

        var rcPct = num(aRc);
        var fixed = rcPct === 100;
        var energy = fixed ? 0 : num(aEnergy);
        var diesel = fixed ? 0 : num(aDiesel);
        var explosive = !fixed && isLita ? num(aExpl) : 0;
        var washOn = !fixed && radioVal('aggWash') === 'yes';
        var a2km = fixed ? 0 : num(aA2);
        var a4km = num(aA4);

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
        var c = contributions(r);
        var labels = r.mode === 'simple' ? ['Wartość historyczna A1-A3'] : ['Energia', 'Paliwo', 'Wybuchowe', 'Transport A2', 'Płukanie', 'Frakcja RC'];
        modChart.data.labels = labels;
        modChart.data.datasets[0].data = Object.keys(c).map(function (k) { return c[k]; });
        modChart.data.datasets[0].backgroundColor = ['#1E3A8A', '#C4721A', '#9B3B3B', '#0B5D33', '#6366F1', '#64748B'];
        modChart.data.datasets[0].borderColor = ['#1E3A8A', '#C4721A', '#9B3B3B', '#0B5D33', '#6366F1', '#64748B'];
        modChart.update();
    }
    function benchmark(r) {
        return 'Historyczne założenia kalkulatora kruszyw. Energia: GWP-fossil poLCA-EN-PL-2024 v9.1. Pozostałe składniki mają własne założenia. Wynik służy do analizy scenariuszy.';
    }

    /* ---- Render ---- */
    function render() {
        syncPrimaryInputs();
        var r = compute();
        if (!r) return null;
        var c = contributions(r);

        outTotal.textContent = fmt(r.total, 2);

        // notki
        if (r.mode === 'simple') {
            outTotalNote.textContent = 'Tryb uproszczony · ' + r.simpleLabel;
        } else {
            var rcTxt = r.rcPct > 0 ? ' · ' + fmt(r.rcPct, 0) + '% frakcji RC' : '';
            var washTxt = r.washOn && r.rcPct < 100 ? ' · płukanie frakcji pierwotnej' : '';
            outTotalNote.textContent = 'Tryb zaawansowany · ' + r.rockLabel + rcTxt + washTxt;
        }
        if (r.a4 > 0) {
            outA4Note.style.display = 'block';
            outA4Note.textContent = '+ moduł A4 (transport do budowy) = ' + fmt(r.a4, 2) + ' kg CO₂eq/t · oszacowanie z A4 ≈ ' + fmt(r.total + r.a4, 2) + ' kg CO₂eq/t (A4 raportowane osobno).';
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
            // Wkłady ważone udziałem frakcji pierwotnej; udział RC pokazują tabela i wykres.
            var denom = r.total > 0 ? r.total : 1;
            setMod(outCEnergy, outCEnergyPct, c.energy, denom);
            setMod(outCDiesel, outCDieselPct, c.diesel, denom);
            setMod(outCExpl, outCExplPct, c.explosive, denom);
            setMod(outCTrans, outCTransPct, c.transport, denom);
            setMod(outCWash, outCWashPct, c.wash, denom);
        }

        var rows = '';
        var names = { reference: 'Wartość historyczna wybranego wariantu', energy: 'Energia kruszenia', diesel: 'Paliwo maszyn', explosive: 'Materiały wybuchowe', transport: 'Transport wewnętrzny', wash: 'Płukanie', recycled: 'Frakcja recyklingowa RC' };
        Object.keys(c).forEach(function (key) {
            if (r.mode === 'advanced' && r.rcPct === 100 && key !== 'recycled') return;
            var share = r.mode === 'simple' ? 1 : (key === 'recycled' ? r.rcPct / 100 : 1 - r.rcPct / 100);
            rows += '<tr><td>' + names[key] + '</td><td class="mono">' + fmt(share * 100, 0) + '% masy</td><td class="mono">' +
                (share > 0 ? fmt(c[key] / share, 3) : '—') + '</td><td class="mono highlight">' + fmt(c[key], 3) + '</td><td class="mono">' + (r.total > 0 ? fmt(c[key] / r.total * 100, 1) : '0,0') + '</td></tr>';
        });
        rows += '<tr><td>Oszacowanie A1-A3 — suma wkładów</td><td>—</td><td>—</td><td class="mono highlight">' + fmt(r.total, 2) + '</td><td>100,0</td></tr>';
        if (r.a4 > 0) rows += '<tr><td>Transport do budowy A4 — osobno</td><td>' + fmt(r.a4km, 0) + ' km</td><td>' + fmt(r.mode === 'simple' ? r.a4ef : EF_TRANSPORT, 3) + ' kg/(t·km)</td><td class="mono">' + fmt(r.a4, 2) + '</td><td>—</td></tr>';
        compTable.innerHTML = rows;

        benchBox.textContent = benchmark(r);

        inputWarn.className = 'agg-warn ok';
        inputWarn.textContent = r.mode === 'simple'
            ? 'Tryb uproszczony — wybrana historyczna wartość kalkulatora kruszyw.'
            : (r.rcPct === 100 ? 'RC = 100% — stały wariant 2,50 kg CO₂e/t. Parametry frakcji pierwotnej są wyłączone.' : 'Parametry frakcji pierwotnej w zakresach kalkulatora.');

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

    function calculationData() {
        var r = compute();
        if (!r) return null;
        var fixed = r.mode === 'advanced' && r.rcPct === 100;
        var data = {
            schema: 'polca-aggregate-calculation/2.0', tool: 'poLCA — Kalkulator kruszyw',
            assumptions_version: 'historyczny zestaw kruszyw 2026.1; energia 2024 v9.1',
            indicator: 'Orientacyjne oszacowanie klimatyczne z historycznych współczynników o różnych zakresach',
            note: 'Energia: GWP-fossil poLCA-EN-PL-2024 v9.1. Zastosowanie w EPD wymaga oceny danych i metody przez jej autora i weryfikatora.',
            reference_unit: '1 t kruszywa', mode: r.mode,
            fixed_recycled_variant: fixed,
            factors: { electricity_fossil_kg_CO2e_per_kWh: EF_EL, diesel_kg_CO2e_per_L: EF_DIESEL,
                explosive_kg_CO2e_per_kg: EF_EXPLOSIVE, transport_kg_CO2e_per_t_km: EF_TRANSPORT,
                washing_extra_kWh_per_t: WASH_KWH, recycled_variant_kg_CO2e_per_t: GWP_RC },
            inputs: r.mode === 'simple'
                ? { aggregate_variant: r.simpleLabel, reference_estimate_kg_CO2e_per_t: r.ref, transport_A4_km: r.a4km, transport_A4_factor: r.a4ef }
                : { rock: r.rock, primary_fraction: 1 - r.rcPct / 100, recycled_fraction_pct: r.rcPct,
                    primary_process: fixed ? null : { electricity_kWh_per_t: r.energy, diesel_L_per_t: r.diesel,
                        explosive_kg_per_t: r.explosive, washing: r.washOn, internal_transport_km: r.a2km },
                    transport_A4_km: r.a4km },
            results_kg_CO2e_per_t: { weighted_contributions: contributions(r),
                climate_estimate_A1_A3: num6(r.total), A4_transport: num6(r.a4),
                climate_estimate_with_A4: num6(r.total + r.a4) },
            timestamp: new Date().toISOString()
        };
        return data;
    }
    function exportCsv() {
        var data = calculationData();
        if (!data) return;
        var r = data.results_kg_CO2e_per_t;
        var quote = function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; };
        var lines = ['Kalkulator kruszyw poLCA;Własny format 2.0;Historyczne założenia kalkulatora',
            'Zakres;' + quote(data.indicator), 'Tryb;' + data.mode,
            'Stały wariant RC 100%;' + data.fixed_recycled_variant,
            'Dane zastosowane;' + quote(JSON.stringify(data.inputs)),
            'Współczynniki;' + quote(JSON.stringify(data.factors)),
            'Składnik;Ważony wkład [kg CO2e/t]'];
        Object.keys(r.weighted_contributions).forEach(function (k) { lines.push(k + ';' + num6(r.weighted_contributions[k])); });
        lines.push('Oszacowanie A1-A3;' + r.climate_estimate_A1_A3);
        lines.push('Transport A4 osobno;' + r.A4_transport);
        lines.push('Oszacowanie z A4;' + r.climate_estimate_with_A4);
        lines.push('Uwaga;' + quote(data.note));
        copyText(lines.join('\n'), el('aggExportCsv'), 'Kopiuj CSV');
    }
    function exportJson() { var data = calculationData(); if (data) copyText(JSON.stringify(data, null, 2), el('aggExportJson'), 'Kopiuj JSON'); }

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

    function exportPolcaXml() {
        var data = calculationData();
        if (!data) return;
        var r = data.results_kg_CO2e_per_t;
        var xml = '<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<polcaCalculation schema="polca-aggregate-calculation/2.0">\n' +
            '  <name>' + xmlEsc(data.tool) + '</name>\n' +
            '  <unit>kg CO2e/t kruszywa</unit>\n' +
            '  <scope>' + xmlEsc(data.indicator) + '</scope>\n' +
            '  <estimate stage="A1-A3">' + r.climate_estimate_A1_A3 + '</estimate>\n' +
            '  <estimate stage="A4">' + r.A4_transport + '</estimate>\n' +
            '  <calculationData encoding="application/json">' + xmlEsc(JSON.stringify(data)) + '</calculationData>\n' +
            '</polcaCalculation>';
        var btn = el('aggExportXml');
        if (downloadFile(xml, 'polca-kruszywa-obliczenie.xml', 'application/xml;charset=utf-8')) {
            btn.textContent = 'Pobrano XML';
            setTimeout(function () { btn.textContent = 'Pobierz XML poLCA'; }, 2000);
        } else { copyText(xml, btn, 'Pobierz XML poLCA'); }
    }

    /* ---- Przełączanie trybu ---- */
    function applyMode() {
        var mode = radioVal('aggMode');
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
    if (btnXml) btnXml.addEventListener('click', exportPolcaXml);

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
