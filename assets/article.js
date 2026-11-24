(() => {
  'use strict';
  const article = document.querySelector('.portal-post');
  if (!article) return;

  const bar = document.querySelector('.reading-progress');
  const end = article.querySelector('.article-end');
  const headings = [...article.querySelectorAll('.article-prose h2[id]')];
  const links = article.querySelectorAll('.article-desktop-toc a, .article-mobile-toc a');
  let pending = false;
  let current;
  function update() {
    pending = false;
    const rect = article.getBoundingClientRect();
    const progress = Math.min(1, Math.max(0, -rect.top / Math.max(1, end.getBoundingClientRect().bottom - rect.top - innerHeight)));
    bar.style.transform = `scaleX(${progress})`;
    const threshold = innerHeight * 0.24;
    const active = headings.findLast(heading => heading.getBoundingClientRect().top <= threshold)?.id;
    if (active === current) return;
    current = active;
    links.forEach(link => {
      if (decodeURIComponent(link.hash.slice(1)) === active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  function schedule() {
    if (!pending) {
      pending = true;
      requestAnimationFrame(update);
    }
  }
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule);
  new ResizeObserver(schedule).observe(article);
  update();

  const button = article.querySelector('[data-copy-url]');
  const status = button.parentElement.querySelector('[role=status]');
  button.hidden = false;
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copyUrl);
      status.textContent = 'Skopiowano link.';
    } catch {
      status.textContent = 'Adres do skopiowania';
      const input = document.createElement('input');
      input.readOnly = true;
      input.setAttribute('aria-label', 'Adres artykułu do skopiowania');
      input.value = button.dataset.copyUrl;
      status.append(input);
      input.select();
    }
  });

  let closedQuestions = [];
  addEventListener('beforeprint', () => {
    closedQuestions = [...article.querySelectorAll('.faq-item:not([open])')];
    closedQuestions.forEach(question => { question.open = true; });
  });
  addEventListener('afterprint', () => {
    closedQuestions.forEach(question => { question.open = false; });
    closedQuestions = [];
  });
})();
