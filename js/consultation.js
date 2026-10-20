/* Local-only consultation helpers: no network requests or persistent storage. */
(function () {
  'use strict';

  var root = document.querySelector('[data-consultation]');
  if (!root) return;

  var explainer = root.querySelector('.consult-explainer');
  var steps = Array.prototype.slice.call(explainer.querySelectorAll('[data-step]'));
  var selectors = Array.prototype.slice.call(explainer.querySelectorAll('[data-step-select]'));
  var playButton = explainer.querySelector('[data-play]');
  var allButton = explainer.querySelector('[data-show-all]');
  var previousButton = explainer.querySelector('[data-step-prev]');
  var nextButton = explainer.querySelector('[data-step-next]');
  var stepStatus = document.getElementById('consult-step-status');
  var progress = explainer.querySelector('[data-step-progress] > span');
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var currentStep = 0;
  var showingAll = false;
  var playing = false;
  var timer = null;
  var animation = null;
  var keyboardPlayback = false;

  function stopPlayback() {
    window.clearTimeout(timer);
    timer = null;
    playing = false;
    playButton.textContent = 'Odtwórz kroki';
    playButton.setAttribute('aria-pressed', 'false');
  }

  function renderStep(index, animate) {
    currentStep = Math.max(0, Math.min(index, steps.length - 1));
    explainer.setAttribute('data-model-focus', showingAll ? 'all' : (['inputs', 'model', 'output'][currentStep] || 'all'));
    if (animation) {
      animation.cancel();
      animation = null;
    }
    steps.forEach(function (step, position) {
      step.hidden = !showingAll && position !== currentStep;
    });
    selectors.forEach(function (button, position) {
      if (position === currentStep && !showingAll) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    previousButton.disabled = currentStep === 0 || showingAll;
    nextButton.disabled = currentStep === steps.length - 1 || showingAll;
    progress.style.transform = 'scaleX(' + ((currentStep + 1) / steps.length) + ')';
    stepStatus.textContent = showingAll
      ? 'Cały opis: wszystkie sześć kroków.'
      : 'Krok ' + (currentStep + 1) + ' z ' + steps.length + ': ' + steps[currentStep].querySelector('h3').textContent;
    if (animate && !showingAll && !reducedMotion.matches && typeof steps[currentStep].animate === 'function') {
      animation = steps[currentStep].animate(
        [{ opacity: 0.45 }, { opacity: 1 }],
        { duration: 180, easing: 'cubic-bezier(.23,1,.32,1)' }
      );
    }
  }

  function setAll(show) {
    showingAll = show;
    explainer.classList.toggle('is-showing-all', show);
    allButton.setAttribute('aria-expanded', String(show));
    allButton.textContent = show ? 'Pokaż krok po kroku' : 'Pokaż cały opis';
  }

  function inputMode(event) {
    var keyboard = event.detail === 0;
    explainer.setAttribute('data-input-mode', keyboard ? 'keyboard' : 'pointer');
    return keyboard;
  }

  function choose(index, event) {
    stopPlayback();
    var keyboard = inputMode(event);
    setAll(false);
    renderStep(index, !keyboard);
  }

  function scheduleNext() {
    timer = window.setTimeout(function () {
      if (!playing) return;
      if (currentStep >= steps.length - 1) {
        stopPlayback();
        return;
      }
      renderStep(currentStep + 1, !keyboardPlayback);
      scheduleNext();
    }, 8000);
  }

  selectors.forEach(function (button, index) {
    button.addEventListener('click', function (event) { choose(index, event); });
  });
  previousButton.addEventListener('click', function (event) { choose(currentStep - 1, event); });
  nextButton.addEventListener('click', function (event) { choose(currentStep + 1, event); });
  allButton.addEventListener('click', function (event) {
    stopPlayback();
    inputMode(event);
    setAll(!showingAll);
    renderStep(currentStep, false);
  });
  playButton.addEventListener('click', function (event) {
    if (playing) {
      stopPlayback();
      return;
    }
    if (reducedMotion.matches) return;
    keyboardPlayback = inputMode(event);
    setAll(false);
    if (currentStep === steps.length - 1) currentStep = 0;
    playing = true;
    playButton.textContent = 'Wstrzymaj';
    playButton.setAttribute('aria-pressed', 'true');
    renderStep(currentStep, !keyboardPlayback);
    scheduleNext();
  });
  explainer.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') stopPlayback();
  });
  explainer.querySelector('.consult-steps').addEventListener('focusin', stopPlayback);
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stopPlayback();
  });
  function updateMotionPreference() {
    if (reducedMotion.matches) {
      stopPlayback();
      if (animation) animation.cancel();
    }
    playButton.disabled = reducedMotion.matches;
    explainer.querySelector('[data-motion-note]').hidden = !reducedMotion.matches;
  }
  if (typeof reducedMotion.addEventListener === 'function') {
    reducedMotion.addEventListener('change', updateMotionPreference);
  } else if (typeof reducedMotion.addListener === 'function') {
    reducedMotion.addListener(updateMotionPreference);
  }
  explainer.classList.add('is-ready');
  ['[data-player-controls]', '[data-step-navigation]', '[data-step-progress]', '[data-step-arrows]'].forEach(function (selector) {
    explainer.querySelector(selector).hidden = false;
  });
  updateMotionPreference();
  renderStep(0, false);

  var form = document.getElementById('consultation-form');
  var fieldset = document.getElementById('consult-form-fields');
  var topic = document.getElementById('consult-topic');
  var section = document.getElementById('consult-section');
  var comment = document.getElementById('consult-comment');
  var source = document.getElementById('consult-source');
  var proposal = document.getElementById('consult-proposal');
  var signature = document.getElementById('consult-signature');
  var output = document.getElementById('consult-message');
  var preview = document.getElementById('consult-preview');
  var formStatus = document.getElementById('consult-form-status');
  var questionStatus = document.getElementById('consult-question-status');
  var version = root.getAttribute('data-package-version');
  var modelId = root.getAttribute('data-model-id');
  var recipient = 'info@epd.org.pl';
  fieldset.disabled = false;

  // The controls intentionally have no name attributes: even an interrupted
  // enhancement cannot put comment text in a GET query.
  form.addEventListener('submit', function (event) { event.preventDefault(); });
  form.addEventListener('input', function () {
    formStatus.textContent = '';
    preview.hidden = true;
    output.value = '';
  });

  function updateQuestionSelection() {
    root.querySelectorAll('[data-question-select]').forEach(function (button) {
      var chosen = button.getAttribute('data-question-select') === topic.value;
      button.setAttribute('aria-pressed', String(chosen));
      button.closest('.consult-question').setAttribute('data-selected', String(chosen));
    });
  }
  root.querySelectorAll('[data-question-select]').forEach(function (button) {
    button.hidden = false;
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', function () {
      topic.value = button.getAttribute('data-question-select');
      updateQuestionSelection();
      preview.hidden = true;
      output.value = '';
      formStatus.textContent = '';
      questionStatus.textContent = 'Wybrano temat „' + topic.options[topic.selectedIndex].textContent + '”. Uzupełnij uwagę w formularzu poniżej.';
      // Selecting a question never scrolls the document or moves focus.
    });
  });
  topic.addEventListener('change', updateQuestionSelection);

  function preparedMessage() {
    comment.setCustomValidity(comment.value.trim() ? '' : 'Wpisz treść uwagi.');
    if (!form.reportValidity()) return null;
    var text = [
      'Uwaga do konsultacji poLCA — energia Polska 2025',
      'Pakiet: ' + version,
      'Model: ' + modelId,
      '',
      'Temat: ' + topic.options[topic.selectedIndex].textContent,
      'Fragment dokumentu: ' + (section.value.trim() || 'Nie wskazano'),
      '',
      'UWAGA',
      comment.value.trim(),
      '',
      'ŹRÓDŁO LUB DOWÓD',
      source.value.trim() || 'Nie podano',
      '',
      'PROPONOWANA POPRAWKA',
      proposal.value.trim() || 'Nie podano',
      '',
      'PODPIS DO PUBLIKACJI',
      signature.value.trim() || 'Anonimowo'
    ].join('\n');
    output.value = text;
    preview.hidden = false;
    return text;
  }
  comment.addEventListener('input', function () { comment.setCustomValidity(''); });

  root.querySelector('[data-copy]').addEventListener('click', async function () {
    var text = preparedMessage();
    if (text === null) return;
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text);
      formStatus.textContent = 'Skopiowano treść. Wklej ją do wiadomości i wyślij na ' + recipient + '.';
    } catch (error) {
      output.focus({ preventScroll: true });
      output.select();
      formStatus.textContent = 'Automatyczne kopiowanie jest niedostępne. Treść poniżej została zaznaczona — skopiuj ją skrótem klawiaturowym lub z menu przeglądarki.';
    }
  });

  root.querySelector('[data-download]').addEventListener('click', function () {
    var text = preparedMessage();
    if (text === null) return;
    var blob = new Blob(['\uFEFF' + text + '\n'], { type: 'text/plain;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'uwaga-polca-energia-2025-' + version.replace(/[^0-9.-]/g, '') + '.txt';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    formStatus.textContent = 'Przygotowano plik tekstowy do pobrania. Dołącz go do wiadomości lub wklej jego treść i wyślij na ' + recipient + '.';
  });

  root.querySelector('[data-mail]').addEventListener('click', function () {
    var text = preparedMessage();
    if (text === null) return;
    var subject = 'poLCA — uwaga do energii 2025, pakiet ' + version;
    var base = 'mailto:' + recipient + '?subject=' + encodeURIComponent(subject);
    var full = base + '&body=' + encodeURIComponent(text);
    var longMessage = full.length > 1800;
    formStatus.textContent = longMessage
      ? 'Treść jest długa. Otwieramy wiadomość z samym tematem. Użyj „Kopiuj treść”, a następnie wklej ją do wiadomości. Wysłanie odbywa się w Twoim programie pocztowym.'
      : 'Wybrano otwarcie programu pocztowego. Sprawdź treść i wyślij wiadomość samodzielnie. Jeśli poczta się nie otworzy, skopiuj treść poniżej.';
    var anchor = document.createElement('a');
    anchor.href = longMessage ? base : full;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  });
}());
