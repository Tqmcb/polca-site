(() => {
  'use strict';
  const guide = document.querySelector('.aggregate-guide');
  if (!guide) return;

  const cases = [...guide.querySelectorAll('.aggregate-case')];
  const choices = [...guide.querySelectorAll('.aggregate-choice')];
  const factorFormat = new Intl.NumberFormat('pl-PL', {maximumFractionDigits: 6});
  const resultFormat = new Intl.NumberFormat('pl-PL', {minimumFractionDigits: 2, maximumFractionDigits: 2});

  function show(section, step) {
    for (const entry of cases) {
      entry.hidden = entry !== section;
      for (const panel of entry.querySelectorAll('.aggregate-panel')) {
        const active = entry === section && panel.dataset.step === step;
        panel.querySelector('.aggregate-result').setAttribute('aria-live', active ? 'polite' : 'off');
      }
    }
    for (const choice of choices) {
      const current = choice.hash === '#' + section.id;
      if (current) choice.setAttribute('aria-current', 'true');
      else choice.removeAttribute('aria-current');
    }
    for (const member of section.querySelectorAll('.aggregate-panel, .aggregate-point')) {
      const current = member.dataset.step === step;
      if (member.matches('.aggregate-panel')) member.hidden = !current;
      else if (current) member.setAttribute('aria-current', 'true');
      else member.removeAttribute('aria-current');
    }
  }

  function selectTarget(target) {
    const section = target?.closest('.aggregate-case');
    if (!section || !guide.contains(section)) return false;
    const step = target.closest('[data-step]')?.dataset.step || '1';
    show(section, step);
    if (target.matches('details')) target.open = true;
    return true;
  }

  function restoreLocation() {
    const target = document.getElementById(location.hash.slice(1));
    if (!selectTarget(target)) show(cases[0], '1');
  }

  function setOutputs(elements, text) {
    for (const element of elements) element.textContent = text;
  }

  function update(panel) {
    const field = panel.querySelector('[data-param]');
    const section = panel.closest('.aggregate-case');
    const point = section.querySelector('.aggregate-point[data-step="' + panel.dataset.step + '"]');
    const material = field.matches('select');
    const entered = field.value.trim().replace(',', '.');
    const quantity = material ? 1 : (/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(entered) ? Number(entered) : NaN);
    const option = material ? field.selectedOptions[0] : null;
    const factor = Number(option ? option.dataset.factor : panel.dataset.factor);
    const result = quantity * factor;
    const valid = Number.isFinite(result);
    const value = valid ? resultFormat.format(result) : '—';
    setOutputs(panel.querySelectorAll('[data-output]'), value);
    setOutputs(point.querySelectorAll('[data-output]'), value);
    point.setAttribute('aria-label', point.dataset.markerName + ', ' +
      (valid ? value + ' ' + panel.dataset.resultUnit : 'brak wyniku'));
    panel.querySelector('[data-error]').hidden = valid;
    panel.querySelector('.aggregate-equation').hidden = !valid;
    if (valid) {
      field.removeAttribute('aria-invalid');
      field.removeAttribute('aria-describedby');
    } else {
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', panel.querySelector('[data-error]').id);
    }
    if (option) {
      panel.querySelector('a[data-source]').href = option.dataset.source;
      setOutputs(panel.querySelectorAll('[data-factor-value]'), factorFormat.format(factor));
    }
    if (!material && valid) panel.querySelector('[data-quantity]').textContent = entered.replace('.', ',');
  }

  function updateFromField(field) {
    const name = field.dataset.param;
    if (!name) return;
    // The material and the trip can be compared with exactly the same assumptions in either use.
    for (const input of guide.querySelectorAll('[data-param="' + name + '"]')) {
      if (input !== field) input.value = field.value;
      update(input.closest('.aggregate-panel'));
    }
  }

  guide.addEventListener('input', event => {
    if (event.target.matches('input[data-param]')) updateFromField(event.target);
  });
  guide.addEventListener('change', event => {
    if (event.target.matches('select[data-param]')) updateFromField(event.target);
  });
  guide.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.altKey || event.ctrlKey || event.shiftKey) return;
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    let target = document.getElementById(link.hash.slice(1));
    if (link.matches('.aggregate-choice') && target) {
      const active = guide.querySelector('.aggregate-case:not([hidden]) .aggregate-point[aria-current="true"]');
      if (active && active.dataset.step !== '1') {
        target = target.querySelector('.aggregate-panel[data-step="' + active.dataset.step + '"]');
      }
    }
    if (!selectTarget(target)) return;
    event.preventDefault();
    const nextHash = '#' + target.id;
    if (location.hash !== nextHash) history.pushState(null, '', nextHash);
    // Preserve the diagram's position for pointer and touch selection. Keyboard users
    // land on the selected explanation, ready to adjust its parameter.
    if (event.detail === 0 && !link.matches('.aggregate-choice') && target.classList.contains('aggregate-panel')) {
      target.focus({preventScroll: true});
      const rect = target.getBoundingClientRect();
      if (rect.top < 0 || rect.top >= window.innerHeight) target.scrollIntoView({block: 'nearest'});
    }
  });

  for (const control of guide.querySelectorAll('[data-param]')) control.disabled = false;
  for (const link of [...choices, ...guide.querySelectorAll('.aggregate-point')]) {
    link.setAttribute('aria-controls', link.hash.slice(1));
  }
  restoreLocation();
  guide.classList.add('is-interactive');
  window.addEventListener('hashchange', restoreLocation);
  window.addEventListener('popstate', restoreLocation);
  window.addEventListener('pageshow', () => {
    restoreLocation();
    for (const panel of guide.querySelectorAll('.aggregate-panel')) update(panel);
  });
})();
