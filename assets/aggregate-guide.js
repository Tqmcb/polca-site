(() => {
  const guide = document.querySelector('.aggregate-guide');
  if (!guide) return;

  const points = Array.from(guide.querySelectorAll('.aggregate-points a'));
  const stages = Array.from(guide.querySelectorAll('.aggregate-stages > li'));

  function selectFromHash() {
    const hash = window.location.hash;
    const selected = points.find(point => point.hash === hash || '#' + point.id === hash);
    for (const point of points) {
      if (point === selected) {
        point.setAttribute('aria-current', 'location');
      } else {
        point.removeAttribute('aria-current');
      }
    }
    for (const stage of stages) {
      stage.classList.toggle('is-current', selected?.hash === '#' + stage.id);
    }
  }

  guide.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.defaultPrevented) return;
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;

    // When the diagram and its key are alongside each other, keep both in view.
    // An off-screen destination is reached by ordinary fragment navigation.
    const bounds = target.getBoundingClientRect();
    if (bounds.top < 4 || bounds.bottom > window.innerHeight - 4) return;
    event.preventDefault();
    if (location.hash !== link.hash) history.pushState(null, '', link.hash);
    target.focus({preventScroll: true});
    selectFromHash();
  });

  window.addEventListener('hashchange', selectFromHash);
  window.addEventListener('pageshow', selectFromHash);
  selectFromHash();
})();
