(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Baza wskaźników emisji GWP (kg CO2e na jednostkę)
    // Źródło: KOBiZE 2024, ecoinvent 3.10 PL/EU, poLCA v5.0
    // gwpPL  — wskaźnik dla Polski
    // gwpEU  — wskaźnik dla Europy (do porównania)
    // -------------------------------------------------------------------------
    var MATERIALS = [
        // Energia
        { id: 'elec_pl',       group: 'Energia',           name: 'Energia elektryczna — miks PL',       unit: 'MWh',  gwpPL: 597,   gwpEU: 295,   src: 'KOBiZE 2024' },
        { id: 'heat_pl',       group: 'Energia',           name: 'Ciepło z sieci ciepłowniczej (PL)',    unit: 'MWh',  gwpPL: 380,   gwpEU: 220,   src: 'KOBiZE 2024' },
        { id: 'gas',           group: 'Energia',           name: 'Gaz ziemny',                           unit: 'MWh',  gwpPL: 202,   gwpEU: 202,   src: 'KOBiZE 2024' },
        { id: 'fuel_oil',      group: 'Energia',           name: 'Olej opałowy / napędowy',              unit: 'MWh',  gwpPL: 279,   gwpEU: 279,   src: 'KOBiZE 2024' },
        { id: 'coal',          group: 'Energia',           name: 'Węgiel kamienny',                      unit: 'MWh',  gwpPL: 344,   gwpEU: 344,   src: 'KOBiZE 2024' },
        // Metale
        { id: 'steel_eaf',     group: 'Metale',            name: 'Stal — EAF (elektryczny piec łukowy)', unit: 'kg',   gwpPL: 0.55,  gwpEU: 0.37,  src: 'ecoinvent 3.10 PL' },
        { id: 'steel_bof',     group: 'Metale',            name: 'Stal — BOF (wielki piec)',              unit: 'kg',   gwpPL: 2.0,   gwpEU: 1.85,  src: 'ecoinvent 3.10 PL' },
        { id: 'al_primary',    group: 'Metale',            name: 'Aluminium pierwotne',                  unit: 'kg',   gwpPL: 9.1,   gwpEU: 8.24,  src: 'ecoinvent 3.10 PL' },
        { id: 'al_secondary',  group: 'Metale',            name: 'Aluminium wtórne (recykling)',          unit: 'kg',   gwpPL: 0.58,  gwpEU: 0.51,  src: 'ecoinvent 3.10' },
        { id: 'copper',        group: 'Metale',            name: 'Miedź (pierwotna)',                     unit: 'kg',   gwpPL: 3.2,   gwpEU: 3.0,   src: 'ecoinvent 3.10' },
        // Mineralne / spoiwa
        { id: 'cement_cem1',   group: 'Mineralne / spoiwa', name: 'Cement CEM I — Portland',             unit: 'kg',   gwpPL: 0.82,  gwpEU: 0.83,  src: 'ecoinvent 3.10 PL' },
        { id: 'cement_cem2',   group: 'Mineralne / spoiwa', name: 'Cement CEM II/A (z popiołem/żużlem)', unit: 'kg',   gwpPL: 0.65,  gwpEU: 0.66,  src: 'ecoinvent 3.10' },
        { id: 'concrete_c2025',group: 'Mineralne / spoiwa', name: 'Beton gotowy C20/25',                 unit: 'kg',   gwpPL: 0.13,  gwpEU: 0.12,  src: 'ecoinvent 3.10 PL' },
        { id: 'concrete_c3037',group: 'Mineralne / spoiwa', name: 'Beton gotowy C30/37',                 unit: 'kg',   gwpPL: 0.155, gwpEU: 0.14,  src: 'ecoinvent 3.10 PL' },
        { id: 'concrete_c4050',group: 'Mineralne / spoiwa', name: 'Beton gotowy C40/50',                 unit: 'kg',   gwpPL: 0.18,  gwpEU: 0.165, src: 'ecoinvent 3.10 PL' },
        { id: 'lime',          group: 'Mineralne / spoiwa', name: 'Wapno palone (CaO)',                  unit: 'kg',   gwpPL: 0.78,  gwpEU: 0.78,  src: 'ecoinvent 3.10' },
        { id: 'gypsum',        group: 'Mineralne / spoiwa', name: 'Gips naturalny (surowy)',              unit: 'kg',   gwpPL: 0.012, gwpEU: 0.012, src: 'ecoinvent 3.10' },
        // Ceramika / szkło
        { id: 'glass_flat',    group: 'Ceramika / szkło',  name: 'Szkło float',                          unit: 'kg',   gwpPL: 0.89,  gwpEU: 0.85,  src: 'ecoinvent 3.10 PL' },
        { id: 'glass_hollow',  group: 'Ceramika / szkło',  name: 'Szkło opakowaniowe',                   unit: 'kg',   gwpPL: 0.65,  gwpEU: 0.60,  src: 'ecoinvent 3.10' },
        { id: 'brick',         group: 'Ceramika / szkło',  name: 'Cegła ceramiczna',                     unit: 'kg',   gwpPL: 0.22,  gwpEU: 0.20,  src: 'ecoinvent 3.10 PL' },
        // Tworzywa / izolacje
        { id: 'eps',           group: 'Tworzywa / izolacje', name: 'Styropian (EPS)',                    unit: 'kg',   gwpPL: 3.35,  gwpEU: 3.29,  src: 'ecoinvent 3.10 PL' },
        { id: 'xps',           group: 'Tworzywa / izolacje', name: 'Styrodur (XPS)',                     unit: 'kg',   gwpPL: 3.50,  gwpEU: 3.42,  src: 'ecoinvent 3.10' },
        { id: 'mineral_wool',  group: 'Tworzywa / izolacje', name: 'Wełna mineralna (skalana/szklana)',  unit: 'kg',   gwpPL: 1.32,  gwpEU: 1.28,  src: 'ecoinvent 3.10 PL' },
        { id: 'pvc',           group: 'Tworzywa / izolacje', name: 'PVC (granulat)',                     unit: 'kg',   gwpPL: 2.45,  gwpEU: 2.41,  src: 'ecoinvent 3.10' },
        { id: 'pe',            group: 'Tworzywa / izolacje', name: 'Polietylen (PE)',                    unit: 'kg',   gwpPL: 1.85,  gwpEU: 1.80,  src: 'ecoinvent 3.10' },
        // Drewno / bio
        { id: 'timber',        group: 'Drewno / bio',      name: 'Drewno konstrukcyjne (sekwestracja)',  unit: 'kg',   gwpPL: -0.60, gwpEU: -0.60, src: 'ecoinvent 3.10' },
        { id: 'osb',           group: 'Drewno / bio',      name: 'Płyta OSB',                            unit: 'kg',   gwpPL: -0.30, gwpEU: -0.32, src: 'ecoinvent 3.10' },
        { id: 'plywood',       group: 'Drewno / bio',      name: 'Sklejka',                              unit: 'kg',   gwpPL: -0.25, gwpEU: -0.28, src: 'ecoinvent 3.10' },
        // Transport
        { id: 'transp_road',   group: 'Transport',         name: 'Transport drogowy (TIR / ciężarówka)', unit: 'tkm',  gwpPL: 0.089, gwpEU: 0.075, src: 'KOBiZE / ecoinvent PL' },
        { id: 'transp_rail',   group: 'Transport',         name: 'Transport kolejowy (towarowy)',         unit: 'tkm',  gwpPL: 0.025, gwpEU: 0.017, src: 'ecoinvent PL' },
        { id: 'transp_ship',   group: 'Transport',         name: 'Transport morski (kontener)',           unit: 'tkm',  gwpPL: 0.013, gwpEU: 0.013, src: 'ecoinvent 3.10' },
        // Woda / gospodarka odpadami
        { id: 'water_tap',     group: 'Inne',              name: 'Woda wodociągowa',                     unit: 'm³',   gwpPL: 0.30,  gwpEU: 0.22,  src: 'ecoinvent 3.10 PL' },
        { id: 'waste_landfill',group: 'Inne',              name: 'Składowanie odpadów przemysłowych',    unit: 'kg',   gwpPL: 0.021, gwpEU: 0.019, src: 'ecoinvent 3.10' },
    ];

    var MATERIAL_MAP = {};
    MATERIALS.forEach(function (m) { MATERIAL_MAP[m.id] = m; });

    var rowCount = 0;

    // -------------------------------------------------------------------------
    // Budowanie <select> z opcjami pogrupowanymi
    // -------------------------------------------------------------------------
    function buildSelect(selectedId) {
        var groups = {};
        MATERIALS.forEach(function (m) {
            if (!groups[m.group]) groups[m.group] = [];
            groups[m.group].push(m);
        });

        var html = '<option value="">— wybierz —</option>';
        Object.keys(groups).forEach(function (g) {
            html += '<optgroup label="' + g + '">';
            groups[g].forEach(function (m) {
                var sel = (m.id === selectedId) ? ' selected' : '';
                html += '<option value="' + m.id + '"' + sel + '>' + m.name + ' [' + m.unit + ']</option>';
            });
            html += '</optgroup>';
        });
        return html;
    }

    // -------------------------------------------------------------------------
    // Dodanie nowego wiersza
    // -------------------------------------------------------------------------
    function addRow(matId, qty) {
        var id = ++rowCount;
        var tbody = document.getElementById('materialsBody');
        var tr = document.createElement('tr');
        tr.id = 'row-' + id;
        tr.innerHTML =
            '<td><select class="mat-select" data-row="' + id + '">' + buildSelect(matId || '') + '</select></td>' +
            '<td><input type="number" class="mat-qty" data-row="' + id + '" min="0" step="any" value="' + (qty || '') + '" placeholder="0"></td>' +
            '<td><span class="mono mat-unit" id="unit-' + id + '">—</span></td>' +
            '<td><span class="epd-row-gwp" id="gwp-' + id + '">—</span></td>' +
            '<td><button class="btn-remove" data-row="' + id + '" title="Usuń wiersz" type="button">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
            '</button></td>';
        tbody.appendChild(tr);

        if (matId) updateRowDisplay(id);
    }

    // -------------------------------------------------------------------------
    // Aktualizacja wyświetlania jednego wiersza
    // -------------------------------------------------------------------------
    function updateRowDisplay(id) {
        var sel  = document.querySelector('.mat-select[data-row="' + id + '"]');
        var qtyEl = document.querySelector('.mat-qty[data-row="' + id + '"]');
        var unitEl = document.getElementById('unit-' + id);
        var gwpEl  = document.getElementById('gwp-' + id);
        if (!sel || !unitEl || !gwpEl) return;

        var mat = MATERIAL_MAP[sel.value];
        if (!mat) { unitEl.textContent = '—'; gwpEl.textContent = '—'; gwpEl.className = 'epd-row-gwp'; return; }

        unitEl.textContent = mat.unit;
        var qty = parseFloat(qtyEl ? qtyEl.value : 0) || 0;
        var total = qty * mat.gwpPL;
        gwpEl.textContent = formatGwp(total);
        gwpEl.className = 'epd-row-gwp' + (total < 0 ? ' neg' : '');
        recalcAll();
    }

    // -------------------------------------------------------------------------
    // Pełne przeliczenie i renderowanie wyników
    // -------------------------------------------------------------------------
    function recalcAll() {
        var rows = [];
        var totalPL = 0;
        var totalEU = 0;

        document.querySelectorAll('#materialsBody tr').forEach(function (tr) {
            var id = tr.id.replace('row-', '');
            var sel = tr.querySelector('.mat-select');
            var qtyEl = tr.querySelector('.mat-qty');
            if (!sel || !sel.value) return;
            var mat = MATERIAL_MAP[sel.value];
            if (!mat) return;
            var qty = parseFloat(qtyEl ? qtyEl.value : 0) || 0;
            if (qty === 0) return;
            var gwpPL = qty * mat.gwpPL;
            var gwpEU = qty * mat.gwpEU;
            totalPL += gwpPL;
            totalEU += gwpEU;
            rows.push({ name: mat.name, unit: mat.unit, qty: qty, gwpPL: gwpPL, gwpEU: gwpEU });
        });

        renderResults(rows, totalPL, totalEU);
    }

    function renderResults(rows, totalPL, totalEU) {
        var container = document.getElementById('resultsContent');
        if (rows.length === 0) {
            container.innerHTML = '<p class="result-empty">Dodaj materiały i ilości, aby zobaczyć wynik.</p>';
            return;
        }

        var productName = document.getElementById('productName').value.trim();
        var funcUnit    = document.getElementById('functionalUnit').value.trim();
        var maxAbs = 0;
        rows.forEach(function (r) { if (Math.abs(r.gwpPL) > maxAbs) maxAbs = Math.abs(r.gwpPL); });

        var diff = totalEU !== 0 ? ((totalPL - totalEU) / Math.abs(totalEU) * 100) : 0;
        var diffSign = diff >= 0 ? '+' : '';
        var diffClass = diff > 0 ? '' : ' positive';

        var barsHtml = rows.map(function (r) {
            var pct = maxAbs > 0 ? Math.abs(r.gwpPL) / maxAbs * 100 : 0;
            var isNeg = r.gwpPL < 0;
            return '<div class="breakdown-bar-row">' +
                '<span class="breakdown-bar-label" title="' + r.name + '">' + r.name + '</span>' +
                '<div class="breakdown-bar-track"><div class="breakdown-bar-fill' + (isNeg ? ' neg' : '') + '" style="width:' + pct.toFixed(1) + '%"></div></div>' +
                '<span class="breakdown-bar-val">' + formatGwp(r.gwpPL) + ' kg</span>' +
                '</div>';
        }).join('');

        var titleHtml = productName
            ? '<p style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.25rem;">Produkt: <strong>' + escHtml(productName) + '</strong>' + (funcUnit ? ' &mdash; ' + escHtml(funcUnit) : '') + '</p>'
            : '';

        container.innerHTML =
            titleHtml +
            '<div style="margin-bottom:1.25rem;">' +
                '<div style="font-size:0.72rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--text-tertiary);margin-bottom:0.4rem;">Łączny GWP (A1–A3)</div>' +
                '<span class="gwp-total-value">' + formatGwp(totalPL) + '</span>' +
                '<span class="gwp-total-unit">kg CO₂e</span>' +
            '</div>' +
            '<div class="breakdown-bar-wrap">' + barsHtml + '</div>' +
            '<div class="compare-block" style="margin-top:1.5rem;">' +
                '<div class="compare-item">' +
                    '<div class="compare-item-label">Dane poLCA — Polska</div>' +
                    '<div class="compare-item-value highlight">' + formatGwp(totalPL) + '</div>' +
                    '<div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:0.3rem;">kg CO₂e</div>' +
                '</div>' +
                '<div class="compare-item">' +
                    '<div class="compare-item-label">Dane ecoinvent — Europa</div>' +
                    '<div class="compare-item-value">' + formatGwp(totalEU) + '</div>' +
                    '<div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:0.3rem;">kg CO₂e</div>' +
                '</div>' +
            '</div>' +
            '<div class="compare-diff' + diffClass + '" style="margin-top:0.75rem;">' +
                'Różnica (PL vs EU): <strong>' + diffSign + diff.toFixed(1) + '%</strong> — ' +
                (diff > 5
                    ? 'dane polskie są wyższe głównie ze względu na węglowy miks energetyczny.'
                    : diff < -5
                        ? 'dane polskie są niższe — korzystny efekt krajowych warunków produkcji.'
                        : 'dane polskie i europejskie są zbliżone dla tego zestawu materiałów.') +
            '</div>' +
            '<p style="font-size:0.72rem;color:var(--text-tertiary);margin-top:1rem;font-style:italic;">' +
                'Wynik orientacyjny. Wartości oparte na wskaźnikach jednostkowych KOBiZE 2024 i ecoinvent 3.10. ' +
                'Certyfikowana EPD wymaga pełnego badania LCA i weryfikacji przez niezależnego eksperta.' +
            '</p>';
    }

    // -------------------------------------------------------------------------
    // Pomocnicze
    // -------------------------------------------------------------------------
    function formatGwp(val) {
        if (val === 0 || isNaN(val)) return '0';
        var abs = Math.abs(val);
        var sign = val < 0 ? '−' : '';
        if (abs >= 1000) return sign + abs.toLocaleString('pl-PL', { maximumFractionDigits: 0 });
        if (abs >= 10)   return sign + abs.toLocaleString('pl-PL', { maximumFractionDigits: 1 });
        return sign + abs.toLocaleString('pl-PL', { maximumFractionDigits: 3 });
    }

    function escHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // -------------------------------------------------------------------------
    // Inicjalizacja
    // -------------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        // Startowe wiersze
        addRow('elec_pl', '');
        addRow('steel_eaf', '');
        addRow('transp_road', '');

        document.getElementById('addRowBtn').addEventListener('click', function () {
            addRow();
        });

        document.getElementById('materialsBody').addEventListener('change', function (e) {
            var row = e.target.getAttribute('data-row');
            if (row) updateRowDisplay(row);
        });

        document.getElementById('materialsBody').addEventListener('input', function (e) {
            var row = e.target.getAttribute('data-row');
            if (row) updateRowDisplay(row);
        });

        document.getElementById('materialsBody').addEventListener('click', function (e) {
            var btn = e.target.closest('.btn-remove');
            if (!btn) return;
            var row = btn.getAttribute('data-row');
            var tr = document.getElementById('row-' + row);
            if (tr) { tr.remove(); recalcAll(); }
        });

        document.getElementById('productName').addEventListener('input', recalcAll);
        document.getElementById('functionalUnit').addEventListener('input', recalcAll);
    });

}());
