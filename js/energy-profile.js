/* Scale the published 2025 profile; retain source method, units and status. */
(function () {
  'use strict';
  var root = document.getElementById('energy-calculation');
  if (!root) return;
  var profile = JSON.parse(document.getElementById('energy-profile-data').textContent);
  var quantity = document.getElementById('energy-quantity');
  var unit = document.getElementById('energy-unit');
  var error = document.getElementById('energy-error');
  var summary = document.getElementById('energy-summary');
  var climateTotal = root.querySelector('[data-energy-climate-total]');
  var climateParts = root.querySelectorAll('[data-energy-climate-part]');
  var buttons = root.querySelectorAll('[data-energy-download]');
  var result = null;
  var amountFormat = new Intl.NumberFormat('pl-PL', { maximumSignificantDigits: 12 });
  function panelNumber(value) {
    if (value === 0) return '0';
    var parts = value.toExponential(5).split('e');
    var exponent = Number(parts[1]);
    if (exponent >= -4 && exponent < 6) {
      return Number(parts.join('e')).toFixed(5 - exponent).replace('.', ',');
    }
    var power = String(exponent).replace(/[-0-9]/g, function (digit) {
      return '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'['-0123456789'.indexOf(digit)];
    });
    return parts[0].replace('.', ',') + '·10' + power;
  }
  function calculate() {
    var amount = quantity.valueAsNumber;
    var factor = {kWh: 1, MWh: 1000, MJ: 1/3.6}[unit.value];
    var valid = quantity.value !== '' && Number.isFinite(amount) && amount >= 0 && amount <= 1e12 && Number.isFinite(factor);
    quantity.setAttribute('aria-invalid', String(!valid));
    error.hidden = valid;
    buttons.forEach(function (b) { b.disabled = !valid; });
    if (!valid) {
      result = null;
      summary.textContent = 'Uzupełnij poprawne zużycie energii.';
      root.querySelectorAll('[data-energy-result]').forEach(function (el) { el.textContent = '—'; });
      if (climateTotal) climateTotal.textContent = '—';
      climateParts.forEach(function (el) { el.textContent = '—'; });
      return;
    }
    var kWh = amount * factor;
    var indicators = profile.indicators.map(function (item) {
      var value = kWh * item.value_per_kWh;
      root.querySelector('[data-energy-result="' + item.code + '"]').textContent = panelNumber(value);
      return {code: item.code, name_pl: item.name_pl, source_value_per_kWh: item.value_per_kWh, value: value, impact_unit: item.impact_unit};
    });
    result = {
      schema_version: '1.0', calculation: 'electricity_contribution_only',
      source_profile_url: 'https://polca.org.pl/data/energia-pl-2025-v4/profil-37.json',
      model_id: profile.model_id, variant: profile.variant, package_version: profile.package_version,
      reference_year: profile.reference_year, electricity_mix_type: profile.electricity_mix_type,
      voltage_scope: profile.voltage_scope, status: profile.status,
      source_attribution: profile.source_attribution,
      terms_url: 'https://polca.org.pl/data/energia-pl-2025-v4/WARUNKI-WYKORZYSTANIA.txt',
      quantity: {value: amount, unit: unit.value, equivalent_kWh: kWh},
      scope_pl: 'Wyłącznie wkład podanej ilości energii; bez przypisania do rzeczywistego wyrobu, modułu lub jednostki wyrobu.',
      indicators: indicators
    };
    var valuesByCode = new Map(indicators.map(function (item) { return [item.code, item.value]; }));
    var total = panelNumber(valuesByCode.get('GWP-total'));
    if (climateTotal) climateTotal.textContent = total;
    climateParts.forEach(function (el) {
      var kilograms = valuesByCode.get(el.dataset.energyClimatePart);
      el.textContent = panelNumber(kilograms * 1000);
    });
    summary.textContent = 'Wpływ na klimat dla ' + amountFormat.format(kWh) + ' kWh wynosi ' + total + ' kg równoważnika CO₂.';
  }
  function csvCell(value) { return '"' + String(value).replace(/"/g, '""') + '"'; }
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      calculate();
      if (!result) return;
      var ext = button.getAttribute('data-energy-download');
      var content = ext === 'json' ? JSON.stringify(result, null, 2) + '\n' : '\ufeff' + [
        ['model_id','package_version','quantity_kWh','code','name_pl','value_per_kWh','value','impact_unit','scope','status','terms_url','source_attribution','source_profile_url','production_approved','formal_EN15804_qualification'],
        ...result.indicators.map(function (i) { return [result.model_id,result.package_version,result.quantity.equivalent_kWh,i.code,i.name_pl,i.source_value_per_kWh,i.value,i.impact_unit,result.calculation,result.status.state,result.terms_url,result.source_attribution,result.source_profile_url,result.status.production_approved,result.status.formal_EN15804_qualification]; })
      ].map(function (row) { return row.map(csvCell).join(';'); }).join('\r\n') + '\r\n';
      var blob = new Blob([content], {type: ext === 'json' ? 'application/json;charset=utf-8' : 'text/csv;charset=utf-8'});
      var url = URL.createObjectURL(blob);
      var link = document.createElement('a'); link.href = url; link.download = 'polca-energia-2025-wklad.' + ext;
      document.body.appendChild(link); link.click(); link.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
  });
  quantity.addEventListener('input', calculate); unit.addEventListener('change', calculate);
  document.getElementById('energy-form').addEventListener('submit', function (event) { event.preventDefault(); calculate(); });
  calculate();
})();
