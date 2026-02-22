/**
 * poLCA – Visual Effects v1.0
 * Animated counters · 3D card tilt · scroll progress · cursor glow
 */
(function() {
    'use strict';

    var raf = window.requestAnimationFrame;

    function isDesktop() {
        return window.innerWidth >= 1024 && window.matchMedia('(hover: hover)').matches;
    }

    /* ── 1. Animated Number Counters ──
     * Psychologia zakotwiczenia (Kahneman): liczba licząca się od zera
     * buduje napięcie i sprawia że wartość końcowa wydaje się większa.
     */

    function easeOutExpo(t) {
        return t >= 1 ? 1 : 1 - Math.pow(2, -12 * t);
    }

    function parseNum(text) {
        text = text.trim();
        if (/\d\s*[–\-]\s*\d/.test(text)) return null;
        var m = text.match(/^([~≈]?)\s*([\d\s,.]+)/);
        if (!m) return null;
        var n = parseFloat(m[2].replace(/\s/g, '').replace(',', '.'));
        return (isNaN(n) || n <= 0) ? null : { val: n, prefix: m[1], orig: text };
    }

    function fmtNum(n, orig) {
        var pfx = /^[~≈]/.test(orig) ? orig.charAt(0) : '';
        if (/,\d/.test(orig)) {
            return pfx + n.toLocaleString('pl-PL', {
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            });
        }
        return pfx + Math.round(n).toLocaleString('pl-PL');
    }

    function countUp(el, target, orig, ms) {
        var t0 = null;
        function step(ts) {
            if (!t0) t0 = ts;
            var p = Math.min((ts - t0) / ms, 1);
            el.textContent = fmtNum(target * easeOutExpo(p), orig);
            if (p < 1) raf(step); else el.textContent = orig;
        }
        raf(step);
    }

    function initCounters() {
        var els = document.querySelectorAll(
            '.metric-number, .key-stat-number, .vcol-value'
        );
        if (!els.length || !('IntersectionObserver' in window)) return;

        var obs = new IntersectionObserver(function(entries) {
            entries.forEach(function(e) {
                if (!e.isIntersecting || e.target._counted) return;
                e.target._counted = true;
                var d = parseNum(e.target.textContent);
                if (d) {
                    var dur = Math.min(2200, Math.max(1200, d.val * 3));
                    countUp(e.target, d.val, d.orig, dur);
                }
                obs.unobserve(e.target);
            });
        }, { threshold: 0.3 });

        els.forEach(function(el) { obs.observe(el); });
    }

    /* ── 2. 3D Card Tilt ──
     * Efekt Stripe/Linear: subtelne 3D na hover
     * buduje poczucie premium i taktylności.
     */

    function initTilt() {
        if (!isDesktop()) return;

        var cards = document.querySelectorAll('.metric-card, .feature-card');
        cards.forEach(function(c) {
            c.addEventListener('mousemove', function(e) {
                var r = c.getBoundingClientRect();
                var nx = (e.clientX - r.left) / r.width;
                var ny = (e.clientY - r.top) / r.height;
                var rx = (0.5 - ny) * 8;
                var ry = (nx - 0.5) * 8;
                c.style.transform =
                    'perspective(600px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg) translateY(-2px)';
            });

            c.addEventListener('mouseleave', function() {
                c.style.transform = '';
            });
        });
    }

    /* ── 3. Scroll Progress Bar ──
     * Psychologia postępu (goal-gradient): wizualizacja progresu
     * motywuje do kontynuowania czytania.
     */

    function initProgress() {
        var bar = document.createElement('div');
        bar.className = 'scroll-progress';
        document.body.appendChild(bar);

        var tick = false;
        window.addEventListener('scroll', function() {
            if (tick) return;
            tick = true;
            raf(function() {
                var st = window.pageYOffset || document.documentElement.scrollTop;
                var dh = document.documentElement.scrollHeight - window.innerHeight;
                bar.style.width = (dh > 0 ? (st / dh) * 100 : 0) + '%';
                tick = false;
            });
        });
    }

    /* ── 4. Cursor Glow ──
     * Efekt odkrywania: radialny blask podąża za kursorem.
     * Nagradza eksplorację i buduje poczucie interaktywności.
     */

    function initGlow() {
        if (!isDesktop()) return;

        var sel = '.card:not(.card-dark), .metric-card, .feature-card, .dataset-card';
        var cards = document.querySelectorAll(sel);

        cards.forEach(function(c) {
            c.addEventListener('mousemove', function(e) {
                var r = c.getBoundingClientRect();
                c.style.setProperty('--glow-x', (e.clientX - r.left) + 'px');
                c.style.setProperty('--glow-y', (e.clientY - r.top) + 'px');
            });
        });
    }

    /* ── Init ── */

    function init() {
        initCounters();
        initTilt();
        initProgress();
        initGlow();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
