/* poLCA — Narzędzia LCA | polca.org.pl
   Przelicznik jednostek i kalkulator transportu */

(function () {
    'use strict';

    // ================================================================
    // HELPERS
    // ================================================================
    function $(id) { return document.getElementById(id); }

    function nonnegative(id, label, errors) {
        var input = $(id), raw = input.value.trim();
        var value = raw === '' ? NaN : Number(raw);
        var valid = Number.isFinite(value) && value >= 0;
        input.setAttribute('aria-invalid', String(!valid));
        if (!valid) errors.push(label + ': wpisz skończoną liczbę nieujemną; puste pole nie oznacza zera');
        return value;
    }
    function choice(id, allowed, label, errors) {
        var input = $(id), valid = allowed.indexOf(input.value) !== -1;
        input.setAttribute('aria-invalid', String(!valid));
        if (!valid) errors.push(label + ': wybierz pozycję z listy');
        return input.value;
    }
    function showError(id, errors, resultIds) {
        var warning = $(id);
        warning.textContent = errors.length ? 'Popraw dane: ' + errors.join('; ') + '. Obliczenie jest wstrzymane.' : '';
        warning.hidden = !errors.length;
        if (errors.length) resultIds.forEach(function (resultId) { $(resultId).textContent = '—'; });
        return errors.length > 0;
    }
    function finiteResults(values, errors) {
        if (!values.every(Number.isFinite)) errors.push('Wartości są zbyt duże do obliczenia skończonego wyniku');
    }

    // ================================================================
    // 01 — UNIT CONVERTER
    // ================================================================
    var energyFactors = {
        'kWh':  1,
        'MWh':  1000,
        'GJ':   1000 / 3.6,
        'MJ':   1 / 3.6,
        'kcal': 4.1868 / 3600
    };

    var massFactors = {
        'g':  0.001,
        'kg': 1,
        't':  1000
    };

    var fuelData = {
        'gas_nm3':  { kWh: 10.55,  label: 'Nm³ gazu ziemnego' },
        'coal_t':   { kWh: 6322,   label: 't węgla kamiennego' },
        'diesel_l': { kWh: 10.0,   label: 'L oleju napędowego' },
        'petrol_l': { kWh: 8.89,   label: 'L benzyny' },
        'lpg_l':    { kWh: 6.67,   label: 'L LPG' },
        'pellet_t': { kWh: 4800,   label: 't pelletu drzewnego' }
    };

    var converterFormat = new Intl.NumberFormat('pl-PL', { maximumSignificantDigits: 10 });

    function convertUnit(value, from, to, factors) {
        return value * factors[from] / factors[to];
    }

    function formatConverted(value) {
        return converterFormat.format(value);
    }

    function renderUnits(prefix, value, from, units, factors, errors) {
        var results = units.map(function (unit) { return convertUnit(value, from, unit, factors); });
        if (!errors.length) finiteResults(results, errors);
        if (showError(prefix + 'Error', errors, [prefix + 'Results'])) return;

        $(prefix + 'Results').innerHTML = units.map(function (unit, index) {
            var label = unit === 't' ? 't (Mg)' : unit;
            return '<div class="tool-conv-item"><span class="tool-conv-val">' + formatConverted(results[index]) +
                '</span><span class="tool-conv-unit">' + label + '</span></div>';
        }).join('');
    }

    function convertQuantity(prefix, factors, quantityLabel, unitLabel) {
        var units = Object.keys(factors);
        var errors = [];
        var value = nonnegative(prefix + 'Val', quantityLabel, errors);
        var from = choice(prefix + 'From', units, unitLabel, errors);
        renderUnits(prefix, value, from, units.filter(function (unit) { return unit !== from; }), factors, errors);
    }

    function convertFuel() {
        var errors = [];
        var value = nonnegative('convFuelVal', 'Ilość paliwa', errors);
        var from = choice('convFuelFrom', Object.keys(fuelData), 'Rodzaj paliwa', errors);
        if (showError('convFuelError', errors, ['convFuelResults'])) return;
        renderUnits('convFuel', value * fuelData[from].kWh, 'kWh', ['kWh', 'MWh', 'GJ', 'MJ'], energyFactors, errors);
    }

    // ================================================================
    // 02 — TRANSPORT CALCULATOR
    // ================================================================
    function formatTransport(value, decimals) {
        if (value > 0 && value < 0.5 * Math.pow(10, -decimals)) return formatConverted(value);
        return value.toLocaleString('pl-PL', { maximumFractionDigits: decimals });
    }

    function calcTransport() {
        var errors = [];
        var distance = nonnegative('transDistance', 'Odległość [km]', errors);
        var mass = nonnegative('transMass', 'Masa [t]', errors);
        var factor = Number(choice('transMode', ['0.031', '0.049', '0.082', '0.146', '0.009', '0.025', '0.005'], 'Środek transportu', errors));
        var returnFactor = Number(choice('transReturn', ['1', '1.5', '2'], 'Przebieg powrotny', errors));
        if (showError('transInputWarn', errors, ['transResult', 'transPerTon', 'transPerTkm'])) return;

        var total = distance * mass * factor * returnFactor;
        var perTon = mass > 0 ? total / mass : 0;
        var perTkm = distance > 0 && mass > 0 ? total / (distance * mass) : 0;

        finiteResults([total, perTon, perTkm], errors);
        if (showError('transInputWarn', errors, ['transResult', 'transPerTon', 'transPerTkm'])) return;
        $('transResult').textContent = formatTransport(total, 1);
        $('transPerTon').textContent = formatTransport(perTon, 2);
        $('transPerTkm').textContent = formatTransport(perTkm, 3);
    }

    function bindInputs(ids, update) {
        if (!$(ids[0])) return;
        ids.forEach(function (id) {
            $(id).addEventListener('input', update);
            $(id).addEventListener('change', update);
        });
        update();
    }

    if (typeof module === 'object' && module.exports) {
        module.exports = { convertUnit, formatConverted, energyFactors, massFactors };
        return;
    }

    bindInputs(['convEnergyVal', 'convEnergyFrom'], function () {
        convertQuantity('convEnergy', energyFactors, 'Ilość energii', 'Jednostka energii');
    });
    bindInputs(['convMassVal', 'convMassFrom'], function () {
        convertQuantity('convMass', massFactors, 'Masa', 'Jednostka masy');
    });
    bindInputs(['convFuelVal', 'convFuelFrom'], convertFuel);
    bindInputs(['transDistance', 'transMass', 'transMode', 'transReturn'], calcTransport);
})();
