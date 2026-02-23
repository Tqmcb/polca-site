(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var topbar = document.querySelector('.polca-topbar');
        var btn    = document.querySelector('.nav-hamburger');
        var nav    = document.querySelector('.polca-topnav');
        if (!btn || !topbar || !nav) return;

        function openMenu() {
            topbar.classList.add('nav-open');
            btn.setAttribute('aria-expanded', 'true');
            btn.setAttribute('aria-label', 'Zamknij menu');
        }

        function closeMenu() {
            topbar.classList.remove('nav-open');
            btn.setAttribute('aria-expanded', 'false');
            btn.setAttribute('aria-label', 'Otwórz menu');
        }

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            topbar.classList.contains('nav-open') ? closeMenu() : openMenu();
        });

        /* Zamknij po kliknięciu linku */
        nav.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', closeMenu);
        });

        /* Zamknij po kliknięciu poza menu */
        document.addEventListener('click', function (e) {
            if (topbar.classList.contains('nav-open') && !topbar.contains(e.target)) {
                closeMenu();
            }
        });

        /* Zamknij po ESC */
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeMenu();
        });
    });

    /* Cień topbara po zjechaniu ze szczytu strony */
    var topbarEl = document.querySelector('.polca-topbar');
    if (topbarEl) {
        var onScroll = function () {
            topbarEl.classList.toggle('scrolled', window.scrollY > 4);
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }
}());
