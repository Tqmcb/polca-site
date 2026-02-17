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
    var FACTOR_EU = 295;

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
                calcDiff.style.color = '#00805A';
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
