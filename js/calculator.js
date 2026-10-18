/** poLCA — kalkulator energii, zestaw historyczny 2024. */
(function () {
    'use strict';
    var energyInput = document.getElementById('energyInput');
    var sourceSelect = document.getElementById('sourceSelect');
    if (!energyInput || !sourceSelect) return;
    function invalid(message) {
        document.getElementById('energyInputWarn').textContent = message;
        document.getElementById('energyInputWarn').hidden = !message;
        energyInput.setAttribute('aria-invalid', String(!!message));
        ['matExportCsv', 'matExportJson'].forEach(function (id) { document.getElementById(id).disabled = !!message; });
        if (message) {
            document.getElementById('resultMain').textContent = '—';
            document.getElementById('resultUnit').textContent = '';
            document.getElementById('resultScope').textContent = 'Popraw dane, aby obliczyć i wyeksportować wynik.';
        }
        return null;
    }
    function payload() {
        var raw = energyInput.value.trim();
        var energy = raw === '' ? NaN : Number(raw);
        if (raw === '' || !Number.isFinite(energy) || energy < 0) return invalid('Zużycie energii: wpisz liczbę nieujemną w MWh. Puste pole nie oznacza zera.');
        if (['599', '202', '279', '344', '0'].indexOf(sourceSelect.value) < 0) return invalid('Wybierz źródło energii z listy.');
        var option = sourceSelect.options[sourceSelect.selectedIndex];
        var factor = Number(sourceSelect.value);
        if (!Number.isFinite(energy * factor)) return invalid('Zużycie energii jest zbyt duże do obliczenia skończonego wyniku. Zmniejsz wartość.');
        invalid('');
        var electricity = option.getAttribute('data-scope') === 'fossil-lca';
        return {
            schema: 'polca-energy-calculation/2.0',
            source: option.text,
            energy_MWh: energy,
            factor_kg_per_MWh: factor,
            result_kg: energy * factor,
            unit: electricity ? 'kg CO2e' : 'kg CO2',
            indicator: electricity ? 'GWP-fossil' : 'direct fossil CO2',
            scope: electricity ? 'Historyczny profil poLCA-EN-PL-2024 v9.1, część kopalna cyklu życia' : 'Historyczne założenie kalkulatora: CO2 kopalny ze spalania, bez dostaw paliwa',
            reference: electricity ? 'data/polca-en-pl-2024.json' : 'Założenia kalkulatora paliw; wartości nie zastępują danych paliwa i instalacji',
            timestamp: new Date().toISOString()
        };
    }
    function calculate() {
        var r = payload();
        if (!r) return;
        document.getElementById('resultMain').textContent = Math.round(r.result_kg).toLocaleString('pl-PL');
        document.getElementById('resultUnit').textContent = r.unit.replace('2', '₂');
        document.getElementById('resultScope').textContent = r.scope;
    }
    function copy(text, btn, label) {
        function fallback() {
            var ta = document.createElement('textarea'); ta.value = text;
            document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
        }
        function done() { btn.textContent = 'Skopiowano'; setTimeout(function () { btn.textContent = label; }, 2000); }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(done, function () { fallback(); done(); });
        } else { fallback(); done(); }
    }
    var csvBtn = document.getElementById('matExportCsv');
    csvBtn.addEventListener('click', function () {
        var r = payload();
        if (!r) return;
        var quote = function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; };
        var csv = 'Źródło;Energia [MWh];Wskaźnik [kg/MWh];Wynik [kg];Jednostka;Rodzaj wskaźnika;Zakres\n' +
            [r.source, r.energy_MWh, r.factor_kg_per_MWh, r.result_kg, r.unit, r.indicator, r.scope].map(quote).join(';');
        copy(csv, csvBtn, 'Kopiuj CSV');
    });
    var jsonBtn = document.getElementById('matExportJson');
    jsonBtn.addEventListener('click', function () { var data = payload(); if (data) copy(JSON.stringify(data, null, 2), jsonBtn, 'Kopiuj JSON'); });
    energyInput.addEventListener('input', calculate);
    sourceSelect.addEventListener('change', calculate);
    calculate();
})();

(function () {
    'use strict';

    var MAT_DATA = [
        { id: 'cement_i',    name: 'Cement CEM I 42.5',      gwp: 800,   unit: 't',  cat: 'Spoiwa' },
        { id: 'cement_ii',   name: 'Cement CEM II/B-S',      gwp: 600,   unit: 't',  cat: 'Spoiwa' },
        { id: 'cement_iii',  name: 'Cement CEM III/A',       gwp: 400,   unit: 't',  cat: 'Spoiwa' },
        { id: 'concrete_20', name: 'Beton C20/25',            gwp: 200,   unit: 'm³', cat: 'Beton' },
        { id: 'concrete_25', name: 'Beton C25/30',            gwp: 250,   unit: 'm³', cat: 'Beton' },
        { id: 'concrete_30', name: 'Beton C30/37',            gwp: 300,   unit: 'm³', cat: 'Beton' },
        { id: 'steel_eaf',   name: 'Stal EAF (PL)',           gwp: 620,   unit: 't',  cat: 'Metale' },
        { id: 'steel_bof',   name: 'Stal BOF (EU avg)',       gwp: 1780,  unit: 't',  cat: 'Metale' },
        { id: 'rebar',       name: 'Stal zbrojeniowa (PL)',   gwp: 750,   unit: 't',  cat: 'Metale' },
        { id: 'alu_prim',    name: 'Aluminium (pierwotne)',   gwp: 8000,  unit: 't',  cat: 'Metale' },
        { id: 'alu_rec',     name: 'Aluminium (recykling)',   gwp: 600,   unit: 't',  cat: 'Metale' },
        { id: 'glass',       name: 'Szkło płaskie',           gwp: 1200,  unit: 't',  cat: 'Inne' },
        { id: 'brick',       name: 'Cegła ceramiczna',        gwp: 200,   unit: 't',  cat: 'Ceramika' },
        { id: 'aac',         name: 'Beton komórkowy (ABK)',   gwp: 300,   unit: 'm³', cat: 'Ceramika' },
        { id: 'mw',          name: 'Wełna mineralna',         gwp: 1300,  unit: 't',  cat: 'Izolacja' },
        { id: 'eps',         name: 'EPS (styropian)',          gwp: 3200,  unit: 't',  cat: 'Izolacja' },
        { id: 'xps',         name: 'XPS',                     gwp: 4500,  unit: 't',  cat: 'Izolacja' },
        { id: 'pir',         name: 'PIR/PUR',                 gwp: 3800,  unit: 't',  cat: 'Izolacja' },
        { id: 'timber',      name: 'Drewno iglaste (C24)',    gwp: -750,  unit: 'm³', cat: 'Drewno' },
        { id: 'plywood',     name: 'Sklejka',                 gwp: 400,   unit: 'm³', cat: 'Drewno' },
        { id: 'gypsum',      name: 'Płyta g-k',               gwp: 250,   unit: 't',  cat: 'Wykończenie' },
        { id: 'copper',      name: 'Miedź (pierwotna)',        gwp: 3500,  unit: 't',  cat: 'Metale' },
        { id: 'pvc_pipe',    name: 'Rura PVC',                gwp: 2000,  unit: 't',  cat: 'Tworzywa' },
        { id: 'pe_pipe',     name: 'Rura PE',                 gwp: 1800,  unit: 't',  cat: 'Tworzywa' }
    ];

    var matSelect  = document.getElementById('matSelect');
    var matQty     = document.getElementById('matQty');
    var matUnit    = document.getElementById('matUnit');
    var matGwpUnit = document.getElementById('matGwpUnit');
    var matResult  = document.getElementById('matResult');
    var matRef     = document.getElementById('matRef');
    var matCat     = document.getElementById('matCat');
    var matBar     = document.getElementById('matBar');
    var matExport  = document.getElementById('matExport');

    if (!matSelect) return;

    function getCurrent() {
        var id = matSelect.value;
        for (var i = 0; i < MAT_DATA.length; i++) {
            if (MAT_DATA[i].id === id) return MAT_DATA[i];
        }
        return null;
    }

    function catStats(cat) {
        var items = MAT_DATA.filter(function(m) { return m.cat === cat; });
        var vals = items.map(function(m) { return m.gwp; });
        var min = Math.min.apply(null, vals);
        var max = Math.max.apply(null, vals);
        var avg = Math.round(vals.reduce(function(a,b){return a+b;},0) / vals.length);
        return { min: min, max: max, avg: avg };
    }

    function fmt(n) {
        return (n < 0 ? '−' : '') + Math.abs(Math.round(n)).toLocaleString('pl-PL');
    }

    function materialQuantity(m) {
        var raw = matQty.value.trim();
        var qty = raw === '' ? NaN : Number(raw);
        var valid = !!m && Number.isFinite(qty) && qty >= 0 && Number.isFinite(qty * m.gwp);
        matQty.setAttribute('aria-invalid', String(!valid));
        matQty.setCustomValidity(valid ? '' : 'Wpisz skończoną, nieujemną ilość materiału.');
        if (matExport) matExport.disabled = !valid;
        if (!valid) { matResult.textContent = '—'; matRef.textContent = 'Wpisz poprawną ilość materiału i wybierz materiał.'; }
        return valid ? qty : null;
    }
    function calcMat() {
        var m = getCurrent();
        var qty = materialQuantity(m);
        if (qty === null) return;
        var total = m.gwp * qty;
        var stats = catStats(m.cat);

        matUnit.textContent = m.unit;
        matGwpUnit.textContent = 'kg CO₂e/' + m.unit;
        matResult.textContent = fmt(total);
        matCat.textContent = m.cat;

        // Ref: GWP per unit
        matRef.textContent = fmt(m.gwp) + ' kg CO₂e/' + m.unit;

        // Bar relative to max in category
        var maxAbs = Math.max(Math.abs(stats.max), Math.abs(stats.min));
        var pct = maxAbs > 0 ? Math.min(100, Math.abs(m.gwp) / maxAbs * 100) : 0;
        matBar.style.width = pct + '%';
        matBar.style.background = m.gwp < 0 ? '#22c55e' : '#0DBF9F';

        // Color result for negative (carbon sink)
        matResult.parentElement.style.color = m.gwp < 0 ? '#22c55e' : '';
    }

    matSelect.addEventListener('change', calcMat);
    matQty.addEventListener('input', calcMat);

    if (matExport) {
        matExport.addEventListener('click', function() {
            var m = getCurrent();
            var qty = materialQuantity(m);
            if (qty === null) return;
            var total = m.gwp * qty;
            var csv = [
                'Materiał;GWP [kg CO₂e/' + m.unit + '];Ilość [' + m.unit + '];GWP łączny [kg CO₂e];Kategoria;Źródło',
                [
                    '"' + m.name + '"',
                    m.gwp,
                    qty,
                    Math.round(total),
                    '"' + m.cat + '"',
                    '"Historyczne wartości orientacyjne kalkulatora poLCA"'
                ].join(';')
            ].join('\n');
            try {
                navigator.clipboard.writeText(csv).then(function() {
                    matExport.textContent = 'Skopiowano!';
                    setTimeout(function() { matExport.textContent = 'Kopiuj CSV'; }, 2000);
                });
            } catch(e) {
                var ta = document.createElement('textarea');
                ta.value = csv;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                matExport.textContent = 'Skopiowano!';
                setTimeout(function() { matExport.textContent = 'Kopiuj CSV'; }, 2000);
            }
        });
    }

    calcMat();
})();
