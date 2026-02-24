/**
 * poLCA Calculator
 */
(function() {
    'use strict';

    var energyInput = document.getElementById('energyInput');
    var sourceSelect = document.getElementById('sourceSelect');
    var resultMain = document.getElementById('resultMain');
    var resultEU = document.getElementById('resultEU');
    var calcDiff = document.getElementById('calcDiff');
    var FACTOR_EU = 210;

    if (!energyInput || !sourceSelect) return;

    function formatNumber(n) {
        return Math.round(n).toLocaleString('pl-PL');
    }

    function calculate() {
        var energy = parseFloat(energyInput.value) || 0;
        var factor = parseFloat(sourceSelect.value) || 0;
        var emissionMain = energy * factor;
        var emissionEU = energy * FACTOR_EU;

        resultMain.textContent = formatNumber(emissionMain);
        resultEU.textContent = formatNumber(emissionEU);

        if (emissionEU > 0 && factor > 0) {
            var diff = ((emissionMain - emissionEU) / emissionEU) * 100;
            if (diff > 0) {
                calcDiff.textContent = 'Różnica: +' + Math.round(diff) + '% przy zastosowaniu danych polskich';
                calcDiff.style.color = '#0E7C6B';
            } else if (diff < 0) {
                calcDiff.textContent = 'Różnica: ' + Math.round(diff) + '% względem średniej europejskiej';
                calcDiff.style.color = '#555555';
            } else {
                calcDiff.textContent = 'Wartości zbieżne ze średnią europejską';
                calcDiff.style.color = '#757575';
            }
        } else {
            calcDiff.textContent = '—';
            calcDiff.style.color = '#757575';
        }
    }

    energyInput.addEventListener('input', calculate);
    sourceSelect.addEventListener('change', calculate);
    calculate();
})();

/* =========================================================
   KALKULATOR MATERIAŁÓW BUDOWLANYCH
   ========================================================= */
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

    function calcMat() {
        var m = getCurrent();
        if (!m) return;
        var qty = parseFloat(matQty.value) || 0;
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
            if (!m) return;
            var qty = parseFloat(matQty.value) || 0;
            var total = m.gwp * qty;
            var csv = [
                'Materiał;GWP [kg CO₂e/' + m.unit + '];Ilość [' + m.unit + '];GWP łączny [kg CO₂e];Kategoria;Źródło',
                [
                    '"' + m.name + '"',
                    m.gwp,
                    qty,
                    Math.round(total),
                    '"' + m.cat + '"',
                    '"poLCA v7.6 / EN 15804+A2"'
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
