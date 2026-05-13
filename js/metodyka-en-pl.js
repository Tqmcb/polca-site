/**
 * poLCA — metodyka-en-pl.js v1.0
 * Ładuje data/polca-en-pl-2024.json i renderuje stronę dokumentu metodologicznego.
 */
(function () {
  'use strict';

  var FORMSPREE_ENDPOINT = 'https://formspree.io/f/YOUR_FORM_ID';
  var DATA_URL = 'data/polca-en-pl-2024.json';

  /* ── INIT ───────────────────────────────────────────────────────── */

  function init() {
    fetch(DATA_URL)
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        renderHero(data);
        renderSections(data);
        buildNav(data.sections);
        initForm(data.sections);
      })
      .catch(function (err) {
        document.getElementById('doc-content').innerHTML =
          '<div class="callout callout-warning" style="max-width:600px;">' +
          '<div class="callout-label">Błąd ładowania dokumentu</div>' +
          '<p class="callout-body">Nie udało się załadować pliku danych (<code>' + DATA_URL + '</code>).<br>' +
          'Spróbuj odświeżyć stronę lub skontaktuj się z <a href="mailto:info@epd.org.pl">info@epd.org.pl</a>.</p>' +
          '</div>';
        console.error('[metodyka-en-pl]', err);
      });
  }

  /* ── HERO ───────────────────────────────────────────────────────── */

  function renderHero(data) {
    var m = data.meta;
    var r = data.result;

    document.getElementById('hero-code').textContent = m.code;
    document.title = m.code + ' — Dokumentacja metodologiczna — poLCA';

    var statusEl = document.getElementById('hero-status');
    statusEl.textContent = m.version + ' · ' + m.status;

    var statsEl = document.getElementById('hero-stats');
    statsEl.innerHTML =
      heroStat(r.value.toString().replace('.', ','), r.unit, 'poLCA-EN-PL ' + r.year, 'var(--accent)') +
      heroStat(r.value_prev.toString().replace('.', ','), r.unit, 'poLCA-EN-PL ' + r.year_prev, 'var(--text-secondary)') +
      heroStat((r.change_pct > 0 ? '+' : '') + r.change_pct.toString().replace('.', ',') + '%', 'zmiana r/r', 'Redukcja emisji', 'var(--func-green)');

    var metaEl = document.getElementById('hero-meta');
    metaEl.innerHTML =
      '<span>Operator: ' + esc(m.operator) + '</span>' +
      '<span>Program: ' + esc(m.program) + '</span>' +
      '<span>Data wydania: ' + esc(m.issued) + '</span>' +
      (m.machine_schema_version ? '<span>Schemat danych: ' + esc(m.machine_schema_version) + '</span>' : '');
  }

  function heroStat(num, unit, label, color) {
    return '<div>' +
      '<div class="doc-hero-stat-num" style="color:' + color + '">' + esc(num) + '</div>' +
      '<div class="doc-hero-stat-unit">' + esc(unit) + '</div>' +
      '<div class="doc-hero-stat-label">' + esc(label) + '</div>' +
      '</div>';
  }

  /* ── SECTIONS ───────────────────────────────────────────────────── */

  function renderSections(data) {
    var container = document.getElementById('doc-content');
    var html = '';
    data.sections.forEach(function (sec) {
      html += renderSection(sec);
    });
    container.innerHTML = html;
  }

  function renderSection(sec) {
    var body = '';
    switch (sec.type) {
      case 'text':        body = renderText(sec);        break;
      case 'table':       body = renderTable(sec);       break;
      case 'equation':    body = renderEquation(sec);    break;
      case 'steps':       body = renderSteps(sec);       break;
      case 'comparison':  body = renderComparison(sec);  break;
      case 'uncertainty': body = renderUncertainty(sec); break;
      default:
        body = renderText(sec);
        console.warn('[metodyka-en-pl] Nieznany typ sekcji:', sec.type, sec.id);
    }
    return '<div class="doc-section fade-in" id="' + esc(sec.id) + '">' +
      '<h2 class="doc-section-title">' + esc(sec.title) + '</h2>' +
      '<div class="doc-section-body">' + body + '</div>' +
      '</div>';
  }

  /* ── TEXT ───────────────────────────────────────────────────────── */

  function renderText(sec) {
    if (!sec.content || !sec.content.length) return '';
    return sec.content.map(function (p) {
      return '<p>' + esc(p) + '</p>';
    }).join('');
  }

  /* ── TABLE ──────────────────────────────────────────────────────── */

  function renderTable(sec) {
    var h = '<div style="overflow-x:auto;">' +
      '<table class="polca-table" style="width:100%;">' +
      '<thead><tr>' +
      sec.headers.map(function (th) { return '<th>' + esc(th) + '</th>'; }).join('') +
      '</tr></thead><tbody>' +
      sec.rows.map(function (row) {
        return '<tr>' + row.map(function (cell, i) {
          return '<td' + (i === 0 ? ' style="font-weight:600"' : '') + '>' + esc(cell) + '</td>';
        }).join('') + '</tr>';
      }).join('') +
      '</tbody></table></div>';
    if (sec.note) {
      h += '<p class="comp-note" style="margin-top:0.5rem;font-size:0.78rem;color:var(--text-tertiary);font-style:italic;">' + esc(sec.note) + '</p>';
    }
    return h;
  }

  /* ── EQUATION ───────────────────────────────────────────────────── */

  function renderEquation(sec) {
    return '<div class="equation-block">' +
      '<div class="equation-formula">' + esc(sec.formula) + '</div>' +
      (sec.numeric ? '<div class="equation-numeric">' + escNl(sec.numeric) + '</div>' : '') +
      (sec.note ? '<div class="equation-note">' + esc(sec.note) + '</div>' : '') +
      '</div>';
  }

  function equationHtml(eq) {
    if (!eq) return '';
    return '<div class="equation-block" style="margin-top:0.75rem;">' +
      '<div class="equation-formula">' + esc(eq.formula) + '</div>' +
      (eq.numeric ? '<div class="equation-numeric">' + escNl(eq.numeric) + '</div>' : '') +
      (eq.note ? '<div class="equation-note">' + esc(eq.note) + '</div>' : '') +
      '</div>';
  }

  /* ── STEPS ──────────────────────────────────────────────────────── */

  function renderSteps(sec) {
    var items = sec.steps.map(function (s) {
      return '<li class="doc-step-item">' +
        '<div class="doc-step-num">' + esc(s.num) + '</div>' +
        '<div class="doc-step-content">' +
        '<div class="doc-step-title">' + esc(s.title) + '</div>' +
        '<p class="doc-step-text">' + esc(s.text) + '</p>' +
        equationHtml(s.equation) +
        '</div></li>';
    }).join('');
    return '<ul class="doc-step-list">' + items + '</ul>';
  }

  /* ── COMPARISON ─────────────────────────────────────────────────── */

  function renderComparison(sec) {
    var h = '<div style="overflow-x:auto;">' +
      '<table class="polca-table" style="width:100%;">' +
      '<thead><tr>' +
      sec.headers.map(function (th) { return '<th>' + esc(th) + '</th>'; }).join('') +
      '</tr></thead><tbody>' +
      sec.rows.map(function (row) {
        var isPolca = row[0] && row[0].indexOf('poLCA') !== -1;
        return '<tr' + (isPolca ? ' style="font-weight:700;background:var(--accent-subtle);"' : '') + '>' +
          row.map(function (cell, ci) {
            return '<td' + (ci === 0 ? ' style="font-weight:600"' : '') + '>' + esc(cell) + '</td>';
          }).join('') + '</tr>';
      }).join('') +
      '</tbody></table></div>';
    if (sec.note) {
      h += '<p class="comp-note" style="margin-top:0.5rem;font-size:0.78rem;color:var(--text-tertiary);font-style:italic;">' + esc(sec.note) + '</p>';
    }
    return h;
  }

  /* ── UNCERTAINTY ────────────────────────────────────────────────── */

  function renderUncertainty(sec) {
    var h = renderTable(sec);
    if (sec.sensitivity) {
      var s = sec.sensitivity;
      h += '<h3 style="font-size:0.95rem;font-weight:600;margin:1.5rem 0 0.75rem;color:var(--ink);">' +
        esc(s.title) + '</h3>';
      h += renderTable({ headers: s.headers, rows: s.rows });
    }
    if (sec.note) {
      h += '<p class="comp-note" style="margin-top:0.5rem;font-size:0.78rem;color:var(--text-tertiary);font-style:italic;">' + esc(sec.note) + '</p>';
    }
    return h;
  }

  /* ── NAV ────────────────────────────────────────────────────────── */

  function buildNav(sections) {
    var nav = document.getElementById('doc-nav');
    var pills = sections.map(function (sec) {
      return '<a href="#' + esc(sec.id) + '" class="tool-nav-pill">' + esc(sec.title) + '</a>';
    }).join('');
    pills += '<a href="#komentarze" class="tool-nav-pill">Uwagi i komentarze</a>';
    nav.innerHTML = pills;

    // IntersectionObserver — podświetla aktywną sekcję
    var pillEls = nav.querySelectorAll('.tool-nav-pill');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var id = entry.target.id;
          pillEls.forEach(function (p) {
            p.classList.toggle('active', p.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });

    sections.forEach(function (sec) {
      var el = document.getElementById(sec.id);
      if (el) observer.observe(el);
    });
    var komentarze = document.getElementById('komentarze');
    if (komentarze) observer.observe(komentarze);
  }

  /* ── FORM ───────────────────────────────────────────────────────── */

  function initForm(sections) {
    var select = document.getElementById('cf-section');
    sections.forEach(function (sec) {
      var opt = document.createElement('option');
      opt.value = sec.id;
      opt.textContent = sec.title;
      select.appendChild(opt);
    });

    var form = document.getElementById('comment-form');
    var submitBtn = document.getElementById('cf-submit');
    var errorEl = document.getElementById('cf-error');
    var successEl = document.getElementById('cf-success');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      errorEl.hidden = true;

      var email = document.getElementById('cf-email').value.trim();
      var message = document.getElementById('cf-message').value.trim();

      if (!email) {
        errorEl.textContent = 'Podaj adres e-mail.';
        errorEl.hidden = false;
        return;
      }
      if (!message) {
        errorEl.textContent = 'Wpisz treść uwagi.';
        errorEl.hidden = false;
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Wysyłanie…';

      fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({
          name: document.getElementById('cf-name').value,
          email: email,
          section: document.getElementById('cf-section').value,
          message: message,
          _subject: 'Uwaga do poLCA-EN-PL-2024: ' + (document.getElementById('cf-section').value || 'ogólna')
        })
      })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.ok) {
          form.hidden = true;
          successEl.hidden = false;
        } else {
          throw new Error(data.error || 'Błąd serwera');
        }
      })
      .catch(function (err) {
        errorEl.textContent = 'Nie udało się wysłać uwagi. Spróbuj ponownie lub napisz bezpośrednio na info@epd.org.pl.';
        errorEl.hidden = false;
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Wyślij uwagę <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';
        console.error('[metodyka-en-pl form]', err);
      });
    });
  }

  /* ── HELPERS ────────────────────────────────────────────────────── */

  function esc(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escNl(str) {
    return esc(str).replace(/\n/g, '<br>');
  }

  /* ── START ──────────────────────────────────────────────────────── */
  init();

})();
