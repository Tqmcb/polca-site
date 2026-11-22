(function () {
  'use strict';

  const panel = document.getElementById('woda');
  const choices = panel.querySelector('fieldset');
  const rows = document.querySelector('#tabela-wskaznikow');
  const volumePerKwh = Number(rows.querySelector('[data-code="FW"]').dataset.value);
  const impactPerKwh = Number(rows.querySelector('[data-code="WDP"]').dataset.value);
  const format = new Intl.NumberFormat('pl-PL', {
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 3
  });
  const litres = document.getElementById('woda-litry');
  const cubicMetres = document.getElementById('woda-metry');
  const impact = document.getElementById('woda-wplyw');
  const announcement = panel.querySelector('[role="status"]');

  function render(announce) {
    const kwh = Number(choices.querySelector(':checked').value);
    const volume = kwh * volumePerKwh;
    litres.textContent = format.format(volume * 1000);
    cubicMetres.textContent = format.format(volume);
    impact.textContent = format.format(kwh * impactPerKwh);
    if (announce) {
      announcement.textContent = 'Dostawa ' + kwh + ' kWh. Zużycie netto wody słodkiej: ' +
        litres.textContent + ' l. Potencjał pozbawienia wody: ' + impact.textContent +
        ' m³ równoważnika światowego.';
    }
  }

  render(false);
  choices.addEventListener('change', function () { render(true); });
  window.addEventListener('pageshow', function () { render(false); });
  panel.querySelector('.en25-water-default').hidden = true;
  choices.hidden = false;
}());
