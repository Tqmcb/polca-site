/* poLCA — beton towarowy, jednostka deklarowana 1 m³. */
(function () {
    'use strict';

    const quantities = {
        cement_kg: 'Masa cementu', aggregate_kg: 'Masa kruszywa', admixtures_kg: 'Masa domieszek',
        cement_km: 'Odległość dostawy cementu', aggregate_km: 'Odległość dostawy kruszywa',
        electricity_kwh: 'Energia elektryczna', gas_m3: 'Gaz ziemny', diesel_l: 'Olej napędowy'
    };
    const resultUnit = 'kg CO₂e/m³';
    const scope = 'W obliczeniach pominięto wodę i domieszki. Katalog nie zawiera wskaźnika dla domieszek.';

    function invalid(field, message) {
        const error = new RangeError(message);
        error.field = field;
        throw error;
    }

    function calculate(inputs, config) {
        for (const [key, label] of Object.entries(quantities)) {
            if (!Number.isFinite(inputs[key]) || inputs[key] < 0) {
                invalid(key, label + ': należy podać liczbę nie mniejszą niż 0.');
            }
        }
        if (!config.cements.includes(inputs.cement)) invalid('cement', 'Należy wybrać rodzaj cementu z listy.');
        const basis = inputs.cement_basis === undefined ? 'netto' : inputs.cement_basis;
        if (!['netto', 'brutto'].includes(basis)) invalid('cement_basis', 'Należy wybrać wariant netto lub brutto.');
        if (!config.aggregates.includes(inputs.aggregate)) invalid('aggregate', 'Należy wybrać rodzaj kruszywa z listy.');
        if (!Object.hasOwn(config.references, inputs.strength_class)) {
            invalid('strength_class', 'Należy wybrać klasę wytrzymałości z listy.');
        }
        const cement = inputs.cement_kg / 1000;
        const aggregate = inputs.aggregate_kg / 1000;
        const process = config.processes;

        function component(stage, label, quantity, unit, recordId, factorKey = 'value') {
            const factor = config.factors[recordId];
            return {stage, label, quantity, unit, record_id: recordId, factor: factor[factorKey],
                factor_unit: factor.unit, emission_kg_CO2eq_per_m3: quantity * factor[factorKey]};
        }
        const breakdown = [
            component('A1', 'Cement (' + basis + ')', cement, 't', inputs.cement,
                basis === 'netto' ? 'value' : 'gwp_gross_kg_co2e'),
            component('A1', 'Kruszywo', aggregate, 't', inputs.aggregate),
            component('A2', 'Dostawa cementu', cement * inputs.cement_km, 't·km', process.truck),
            component('A2', 'Dostawa kruszywa', aggregate * inputs.aggregate_km, 't·km', process.truck),
            component('A3', 'Energia elektryczna', inputs.electricity_kwh, 'kWh', process.electricity),
            component('A3', 'Gaz ziemny', inputs.gas_m3, 'm³', process.gas),
            component('A3', 'Olej napędowy', inputs.diesel_l, 'l', process.diesel)
        ];
        const stages = {A1: 0, A2: 0, A3: 0};
        for (const item of breakdown) stages[item.stage] += item.emission_kg_CO2eq_per_m3;
        const total = stages.A1 + stages.A2 + stages.A3;
        const grossTotal = cement * config.factors[inputs.cement].gwp_gross_kg_co2e
            + breakdown[1].emission_kg_CO2eq_per_m3 + stages.A2 + stages.A3;
        if (!Number.isFinite(total) || !Number.isFinite(grossTotal)) invalid(null, 'Podane wielkości przekraczają zakres obliczeń.');
        const reference = config.references[inputs.strength_class];
        return {
            stages, total, grossTotal, basis, breakdown,
            cementShare: total > 0 ? breakdown[0].emission_kg_CO2eq_per_m3 / total * 100 : null,
            reference: {strength_class: inputs.strength_class, ...reference,
                difference_from_median: reference.median === null ? null : grossTotal - reference.median}
        };
    }

    function exportData(inputs, config, result) {
        const used = result.breakdown.map(item => item.record_id);
        const round6 = value => value === null ? null : Number(value.toFixed(6));
        const breakdown = result.breakdown.map(item => ({
            ...item, emission_kg_CO2eq_per_m3: round6(item.emission_kg_CO2eq_per_m3)
        }));
        return {
            tool: 'poLCA — Kalkulator betonu towarowego', schema: 'polca-concrete-calculation/1.1',
            assumptions_version: config.catalog_version, declared_unit: '1 m³ betonu towarowego',
            indicator: 'Oszacowanie całkowitego wpływu na klimat A1–A3', note: scope,
            inputs: {...inputs, cement_basis: result.basis},
            factors: Object.fromEntries([...new Set(used)].map(id => [id, config.factors[id]])),
            results_kg_CO2eq_per_m3: {
                A1_raw_materials: round6(result.stages.A1), A2_transport: round6(result.stages.A2),
                A3_production: round6(result.stages.A3), climate_estimate_A1_A3: round6(result.total),
                gross_A1_A3: round6(result.grossTotal),
                cement_share_pct: round6(result.cementShare), breakdown
            },
            epd_reference_kg_CO2eq_per_m3: {...result.reference,
                difference_from_median: round6(result.reference.difference_from_median)},
            timestamp: new Date().toISOString()
        };
    }

    function toCsv(data) {
        const r = data.results_kg_CO2eq_per_m3;
        const ref = data.epd_reference_kg_CO2eq_per_m3;
        const rows = [
            [data.tool, data.schema], ['Wersja danych', data.assumptions_version], ['Data zapisu', data.timestamp],
            ['Jednostka deklarowana', data.declared_unit], ['Zakres', data.note], ['Wariant cementu', data.inputs.cement_basis],
            ['Masa cementu [kg]', data.inputs.cement_kg], ['Masa kruszywa [kg]', data.inputs.aggregate_kg],
            ['Masa domieszek [kg]', data.inputs.admixtures_kg], ['Odległość dostawy cementu [km]', data.inputs.cement_km],
            ['Odległość dostawy kruszywa [km]', data.inputs.aggregate_km], [],
            ['Moduł', 'Pozycja', 'Ilość', 'Jednostka', 'Wskaźnik', 'Jednostka wskaźnika', 'Rekord poLCA', 'Wkład [kg CO₂e/m³]']
        ];
        for (const item of r.breakdown) {
            rows.push([item.stage, item.label, item.quantity, item.unit, item.factor, item.factor_unit,
                item.record_id, item.emission_kg_CO2eq_per_m3]);
        }
        rows.push([], ['Moduł', resultUnit], ['A1', r.A1_raw_materials], ['A2', r.A2_transport],
            ['A3', r.A3_production], ['A1–A3', r.climate_estimate_A1_A3], ['Udział cementu [%]', r.cement_share_pct],
            ['A1–A3 brutto', r.gross_A1_A3], ['Wariant porównania', ref.cement_basis],
            [], ['Klasa', 'Liczba deklaracji', 'Minimum', 'Mediana', 'Maksimum', 'Różnica względem mediany',
                'Minimum przed uśrednieniem', 'Maksimum przed uśrednieniem', 'Rekord mediany'],
            [ref.strength_class, ref.n, ref.min, ref.median, ref.max, ref.difference_from_median,
                ref.row_min, ref.row_max, ref.record_id]);
        if (ref.basis_note) rows.push(['basis_note', ref.basis_note]);
        function cell(value) {
            if (typeof value === 'number') return String(value).replace('.', ',');
            return '"' + String(value ?? '').replace(/"/g, '""') + '"';
        }
        return rows.map(row => row.map(cell).join(';')).join('\r\n');
    }

    const fmt = (value, digits = 2) => value.toLocaleString('pl-PL', {minimumFractionDigits: digits, maximumFractionDigits: digits});
    const number = value => value.toLocaleString('pl-PL', {maximumFractionDigits: 6});

    function comparison(result) {
        const ref = result.reference;
        const prefix = 'Do porównania z deklaracjami przyjęto wariant brutto: wynik receptury wynosi '
            + fmt(result.grossTotal) + ' ' + resultUnit + '. Klasa ' + ref.strength_class + ', liczba deklaracji: ' + ref.n + '. ';
        const basisNote = ref.basis_note ? ' ' + ref.basis_note : '';
        if (ref.median !== null) {
            const delta = ref.difference_from_median;
            const direction = delta < 0 ? 'niższy' : 'wyższy';
            const difference = Math.abs(delta) < 0.005 ? 'Wynik odpowiada medianie z dokładnością do 0,01 kg CO₂e/m³.'
                : 'Wynik receptury jest o ' + fmt(Math.abs(delta)) + ' ' + resultUnit + ' ' + direction + ' od mediany.';
            return prefix + 'Mediana: ' + fmt(ref.median, 1) + ' ' + resultUnit + '. ' + difference + basisNote;
        }
        const rawRange = number(ref.row_min) + '–' + number(ref.row_max) + ' ' + resultUnit;
        const one = ref.n === 1;
        const low = one ? ref.row_min : ref.min;
        const high = one ? ref.row_max : ref.max;
        const values = one ? 'Średnia z jedynej deklaracji wynosi ' + number(ref.min) + ' ' + resultUnit +
            '. Pojedyncze wyniki w tej deklaracji mieszczą się w przedziale ' + rawRange + '. ' :
            'Średnie z poszczególnych deklaracji mieszczą się w przedziale ' + number(low) + '–' + number(high) + ' ' + resultUnit + '. ';
        let difference = 'Wynik receptury mieści się w tym przedziale.';
        if (result.grossTotal < low) difference = 'Wynik receptury jest o ' + fmt(low - result.grossTotal) + ' ' +
            resultUnit + ' niższy od dolnej granicy przedziału.';
        if (result.grossTotal > high) difference = 'Wynik receptury jest o ' + fmt(result.grossTotal - high) + ' ' +
            resultUnit + ' wyższy od górnej granicy przedziału.';
        return prefix + values + difference + (one ? '' : ' Pojedyncze wyniki mieszczą się w przedziale ' + rawRange + '.') + basisNote;
    }

    if (typeof module === 'object' && module.exports) {
        module.exports = {calculate, comparison, exportData, toCsv};
        return;
    }

    const el = id => document.getElementById(id);
    const form = el('concrete-form');
    const config = JSON.parse(el('concrete-config').textContent);
    const fields = form.elements;
    const buttons = {csv: el('concrete-csv'), json: el('concrete-json')};

    function inputsFromForm() {
        const inputs = Object.fromEntries(new FormData(form));
        for (const key of Object.keys(quantities)) inputs[key] = fields[key].valueAsNumber;
        return inputs;
    }

    function renderBreakdown(result, inputs) {
        const body = el('concrete-breakdown');
        body.replaceChildren();
        for (const item of result.breakdown) {
            const row = body.insertRow();
            row.insertCell().textContent = item.stage;
            const link = document.createElement('a');
            const factor = config.factors[item.record_id];
            link.href = factor.href;
            link.textContent = item.stage === 'A1' ? factor.title : item.label;
            if (item.record_id === inputs.cement) link.textContent += ' (' + result.basis + ')';
            row.insertCell().append(link);
            row.insertCell().textContent = number(item.quantity) + ' ' + item.unit;
            row.insertCell().textContent = number(item.factor) + ' ' + item.factor_unit;
            row.insertCell().textContent = fmt(item.emission_kg_CO2eq_per_m3);
        }
        const row = body.insertRow(2);
        for (const label of ['A1', 'Domieszki', number(inputs.admixtures_kg) + ' kg', 'Brak wskaźnika w katalogu', 'Pominięto']) {
            row.insertCell().textContent = label;
        }
    }

    function render() {
        for (const control of form.querySelectorAll('[aria-invalid]')) {
            control.removeAttribute('aria-invalid');
            control.removeAttribute('aria-errormessage');
        }
        const inputs = inputsFromForm();
        let result;
        try {
            result = calculate(inputs, config);
        } catch (error) {
            if (!(error instanceof RangeError)) throw error;
            if (error.field) {
                for (const control of form.querySelectorAll('[name="' + error.field + '"]')) {
                    control.setAttribute('aria-invalid', 'true');
                    control.setAttribute('aria-errormessage', 'concrete-error');
                }
            }
            el('concrete-error').textContent = error.message;
        }
        for (const button of Object.values(buttons)) button.disabled = !result;
        el('concrete-total').textContent = result ? fmt(result.total) : '—';
        el('concrete-basis').textContent = result ? result.basis : '';
        el('cement-share').textContent = result && result.cementShare !== null ? fmt(result.cementShare, 1) + '%' : '—';
        for (const stage of ['A1', 'A2', 'A3']) {
            el('concrete-' + stage.toLowerCase()).textContent = result ? fmt(result.stages[stage]) + ' ' + resultUnit : '—';
        }
        el('concrete-comparison').textContent = result ? comparison(result) : '—';
        if (!result) {
            el('concrete-breakdown').replaceChildren();
            return;
        }
        el('concrete-error').textContent = '';
        renderBreakdown(result, inputs);
        return {inputs, result};
    }

    function download(format) {
        const current = render();
        if (!current) return;
        const data = exportData(current.inputs, config, current.result);
        const csv = format === 'csv';
        const blob = new Blob([csv ? '\uFEFF' + toCsv(data) : JSON.stringify(data, null, 2)],
            {type: csv ? 'text/csv;charset=utf-8' : 'application/json;charset=utf-8'});
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'polca-beton-obliczenie.' + format;
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    }

    form.addEventListener('input', render);
    form.addEventListener('change', render);
    form.addEventListener('submit', event => { event.preventDefault(); render(); });
    for (const [format, button] of Object.entries(buttons)) button.addEventListener('click', () => download(format));
    render();
})();
