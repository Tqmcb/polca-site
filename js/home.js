/* An illustrative calculation using the public model supplied by the page. */
(function () {
  'use strict';

  var root = document.querySelector('[data-home-calculator]');
  if (!root) return;

  var input = root.querySelector('#home-energy-use');
  var result = root.querySelector('#home-energy-result');
  var announcement = root.querySelector('#home-energy-announcement');
  var error = root.querySelector('#home-energy-error');
  var editor = root.querySelector('.home-energy-editor');
  var staticValue = root.querySelector('.home-energy-static');
  var presets = root.querySelector('.home-energy-presets');
  var factorText = root.getAttribute('data-factor');
  var factor = Number(factorText);

  // Keep the complete static example if progressive enhancement is unavailable.
  if (!input || !result || !announcement || !error || !editor || !staticValue || !presets ||
      !factorText || !factorText.trim() || !Number.isFinite(factor) || factor <= 0) return;

  var resultFormatter;
  var quantityFormatter;
  try {
    resultFormatter = new Intl.NumberFormat('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    quantityFormatter = new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 20 });
  } catch (formatError) {
    return;
  }

  var lastAnnouncement = null;
  var buttons = Array.prototype.slice.call(presets.querySelectorAll('[data-energy-preset]'));

  function parseQuantity(text) {
    var normalized = text.trim().replace(/[\u00a0\u202f]/g, ' ');
    // A space may separate thousands; a comma or dot is the decimal separator.
    // Reject partial numbers, exponent notation and malformed groups explicitly.
    if (!/^(?:\d+|\d{1,3}(?: \d{3})+)(?:[.,]\d+)?$/.test(normalized)) return null;
    var quantity = Number(normalized.replace(/ /g, '').replace(',', '.'));
    return Number.isFinite(quantity) && quantity >= 0 ? quantity : null;
  }

  function render(shouldAnnounce) {
    var quantity = parseQuantity(input.value);
    var calculated = quantity === null ? null : quantity * factor;
    var invalid = calculated === null || !Number.isFinite(calculated);
    var message;

    if (invalid) {
      result.textContent = '—';
      error.textContent = input.value.trim()
        ? 'Wpisz nieujemną liczbę, np. 100 lub 1 000,5. Podana wartość jest nieprawidłowa albo zbyt duża.'
        : 'Wpisz zużycie energii w kWh.';
      error.hidden = false;
      input.setAttribute('aria-invalid', 'true');
      message = error.textContent;
    } else {
      var formattedResult = resultFormatter.format(calculated);
      result.textContent = formattedResult;
      error.textContent = '';
      error.hidden = true;
      input.removeAttribute('aria-invalid');
      message = 'Dla ' + quantityFormatter.format(quantity) + ' kWh wpływ na klimat wynosi ' +
        formattedResult + ' kg ekwiwalentu dwutlenku węgla.';
    }

    if (shouldAnnounce && message !== lastAnnouncement) {
      announcement.textContent = message;
      lastAnnouncement = message;
    }
  }

  var describedBy = (input.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
  if (describedBy.indexOf(error.id) === -1) describedBy.push(error.id);
  input.setAttribute('aria-describedby', describedBy.join(' '));

  input.addEventListener('input', function () {
    // Visual feedback is immediate; spoken feedback waits until editing ends.
    if (announcement.textContent) announcement.textContent = '';
    lastAnnouncement = null;
    render(false);
  });
  input.addEventListener('change', function () { render(true); });
  input.addEventListener('blur', function () { render(true); });

  buttons.forEach(function (button) {
    var preset = button.getAttribute('data-energy-preset');
    if (parseQuantity(preset || '') === null) return;
    button.addEventListener('click', function (event) {
      event.preventDefault();
      input.value = preset;
      render(true);
    });
  });

  render(false);
  editor.hidden = false;
  presets.hidden = false;
  staticValue.hidden = true;
}());
