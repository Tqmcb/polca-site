/* poLCA — zestawienie materiałów budowlanych */
(function () {
    'use strict';

    function $(id) { return document.getElementById(id); }
    if (!$('materialSelect') || !$('materialChart')) return;

    var materials = [
        { id: 'cement_i',     name: 'Cement CEM I (SPC 2025, netto)', gwp: 584,   unit: 'kg CO\u2082e/t',  cat: 'Spoiwa',    checked: true },
        { id: 'cement_ii',    name: 'Cement CEM II (SPC 2025, netto)', gwp: 473,   unit: 'kg CO\u2082e/t',  cat: 'Spoiwa',    checked: false },
        { id: 'cement_iii',   name: 'Cement CEM III (SPC 2025, netto)', gwp: 398,   unit: 'kg CO\u2082e/t',  cat: 'Spoiwa',    checked: false },
        { id: 'concrete_25', name: 'Beton C25/30', gwp: 216.5, unit: 'kg CO₂e/m³', source: 'mediana deklaracji ITB, wariant brutto', cat: 'Beton', checked: true },
        { id: 'concrete_30', name: 'Beton C30/37', gwp: 210.9, unit: 'kg CO₂e/m³', source: 'mediana deklaracji ITB, wariant brutto', cat: 'Beton', checked: false },
        { id: 'steel_bof',    name: 'Stal BOF (EU avg)',      gwp: 1780,  unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: true },
        { id: 'rebar',        name: 'Stal zbrojeniowa (mediana EPD PL)', gwp: 790,   unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: true },
        { id: 'alu_prim',     name: 'Aluminium (pierwotne)', gwp: 8000,  unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'alu_rec',      name: 'Aluminium (recykling)', gwp: 600,   unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'glass',        name: 'Szk\u0142o p\u0142askie',          gwp: 1200,  unit: 'kg CO\u2082e/t',  cat: 'Inne',      checked: false },
        { id: 'brick',        name: 'Ceg\u0142a ceramiczna',       gwp: 200,   unit: 'kg CO\u2082e/t',  cat: 'Ceramika',  checked: false },
        { id: 'aac',          name: 'Beton kom\u00f3rkowy (ABK)',   gwp: 300,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Ceramika',  checked: false },
        { id: 'mw',           name: 'We\u0142na mineralna',       gwp: 1300,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: false },
        { id: 'eps',          name: 'EPS (styropian)',        gwp: 3200,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: true },
        { id: 'xps',          name: 'XPS',                   gwp: 4500,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: false },
        { id: 'pir',          name: 'PIR/PUR',               gwp: 3800,  unit: 'kg CO\u2082e/t',  cat: 'Izolacja',  checked: false },
        { id: 'timber',       name: 'Drewno iglaste (C24)',  gwp: -750,  unit: 'kg CO\u2082e/m\u00b3', cat: 'Drewno',    checked: true },
        { id: 'plywood',      name: 'Sklejka',               gwp: 400,   unit: 'kg CO\u2082e/m\u00b3', cat: 'Drewno',    checked: false },
        { id: 'gypsum',       name: 'P\u0142yta g-k',              gwp: 250,   unit: 'kg CO\u2082e/t',  cat: 'Wyko\u0144czenie', checked: false },
        { id: 'copper',       name: 'Mied\u017a (pierwotna)',      gwp: 3500,  unit: 'kg CO\u2082e/t',  cat: 'Metale',    checked: false },
        { id: 'pvc_pipe',     name: 'Rura PVC',              gwp: 2000,  unit: 'kg CO\u2082e/t',  cat: 'Tworzywa',  checked: false },
        { id: 'pe_pipe',      name: 'Rura PE',               gwp: 1800,  unit: 'kg CO\u2082e/t',  cat: 'Tworzywa',  checked: false }
    ];

    function buildMaterialSelect() {
        var container = $('materialSelect');
        var html = '';
        for (var i = 0; i < materials.length; i++) {
            var m = materials[i];
            html += '<label class="material-chip' + (m.checked ? ' active' : '') + '">' +
                '<input type="checkbox" value="' + m.id + '"' + (m.checked ? ' checked' : '') + '>' +
                '<span class="material-chip-name">' + m.name + '</span>' +
                '<span class="material-chip-cat">' + m.cat + '</span>' +
                '</label>';
        }
        container.innerHTML = html;

        container.addEventListener('change', function (e) {
            if (e.target.type === 'checkbox') {
                var label = e.target.closest('.material-chip');
                if (e.target.checked) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
                renderMaterialChart();
            }
        });
    }

    function renderMaterialChart() {
        var container = $('materialChart');
        var checkboxes = $('materialSelect').querySelectorAll('input[type="checkbox"]:checked');
        var selected = [];

        for (var i = 0; i < checkboxes.length; i++) {
            var id = checkboxes[i].value;
            for (var j = 0; j < materials.length; j++) {
                if (materials[j].id === id) {
                    selected.push(materials[j]);
                    break;
                }
            }
        }

        if (selected.length === 0) {
            container.innerHTML = '<div class="tool-empty-state">Zaznacz materiały do porównania</div>';
            return;
        }

        var html = '<table class="polca-table"><thead><tr><th>Materiał</th><th>Wartość A1–A3</th><th>Jednostka</th></tr></thead><tbody>';
        selected.forEach(function (m) {
            var source = m.source ? '<br><small>' + m.source + '</small>' : '';
            html += '<tr><td>' + m.name + source + '</td><td class="mono">' + m.gwp.toLocaleString('pl-PL') + '</td><td>' + m.unit + '</td></tr>';
        });
        container.innerHTML = html + '</tbody></table><p class="calc-note">Wartości mają różne jednostki odniesienia i założenia. Porównanie wyrobów wymaga tej samej funkcji, granic cyklu życia i metody oceny. Ujemna wartość dla drewna obejmuje założenie o węglu biogenicznym w etapie produkcji.</p>';
    }

    buildMaterialSelect();
    renderMaterialChart();
})();
