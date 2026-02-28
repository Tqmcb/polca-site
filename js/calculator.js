/**
 * poLCA Calculator — multi-indicator comparison
 * poLCA-EN-PL, KOBiZE, AIB Residual Mix for 2023 and 2024
 */
(function () {
    'use strict';

    var FACTORS = {
        '2024': { polca: 718, kobize: 553, aib: 808 },
        '2023': { polca: 780, kobize: 597, aib: 788 }
    };

    var energyInput = document.getElementById('energyInput');
    var yearSelect  = document.getElementById('yearSelect');

    if (!energyInput) return;

    function fmt(n) {
        return Math.round(n).toLocaleString('pl-PL');
    }

    function calculate() {
        var energy = parseFloat(energyInput.value) || 0;
        var year   = yearSelect ? yearSelect.value : '2024';
        var f      = FACTORS[year] || FACTORS['2024'];

        var rPolca  = energy * f.polca;
        var rKobize = energy * f.kobize;
        var rAib    = energy * f.aib;

        var set = function (id, val) {
            var el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        set('resultPolca',  fmt(rPolca));
        set('resultKobize', fmt(rKobize));
        set('resultAib',    fmt(rAib));
        set('factorPolca',  f.polca);
        set('factorKobize', f.kobize);
        set('factorAib',    f.aib);

        var diffBox = document.getElementById('calcDiff');
        if (diffBox && rKobize > 0) {
            var pctPK  = Math.round(((rPolca  - rKobize) / rKobize) * 100);
            var pctAK  = Math.round(((rAib    - rKobize) / rKobize) * 100);
            diffBox.innerHTML =
                'Rozpi\u0119to\u015b\u0107 wynik\u00f3w: poLCA jest o <strong>+' + pctPK +
                '%</strong> wy\u017csze od KOBiZE, AIB o <strong>+' + pctAK + '%</strong>.';
        }
    }

    energyInput.addEventListener('input', calculate);
    if (yearSelect) yearSelect.addEventListener('change', calculate);
    calculate();
}());
