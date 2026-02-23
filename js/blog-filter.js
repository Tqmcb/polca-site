(function () {
  'use strict';

  function init() {
    var pills = document.querySelectorAll('.filter-pill');
    var cards = document.querySelectorAll('.blog-card, .blog-card-featured');
    var countEl = document.getElementById('filterCount');

    if (!pills.length || !cards.length) return;

    function updateCount(visible) {
      if (countEl) countEl.textContent = visible + ' artykułów';
    }

    function filterCards(tag) {
      var visible = 0;
      cards.forEach(function (card) {
        var tags = (card.getAttribute('data-tags') || '').toLowerCase();
        if (tag === 'all' || tags.indexOf(tag) !== -1) {
          card.classList.remove('hidden');
          visible++;
        } else {
          card.classList.add('hidden');
        }
      });
      updateCount(visible);
    }

    pills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        pills.forEach(function (p) { p.classList.remove('active'); });
        pill.classList.add('active');
        filterCards(pill.getAttribute('data-filter'));
      });
    });

    updateCount(cards.length);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
