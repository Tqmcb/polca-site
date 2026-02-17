/**
 * poLCA v4.0 — Editorial Scroll Animations
 * Staggered reveals with intersection observer
 */
(function() {
    'use strict';

    // Main fade-in observer
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Once visible, stop observing for performance
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.08,
        rootMargin: '0px 0px -60px 0px'
    });

    document.querySelectorAll('.fade-in').forEach(function(el) {
        observer.observe(el);
    });

    // Comparison bars — animate width on scroll
    var barObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var bars = entry.target.querySelectorAll('.comp-bar-fill');
                bars.forEach(function(bar, i) {
                    var targetWidth = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(function() {
                        bar.style.width = targetWidth;
                    }, 200 + (i * 150));
                });
                barObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2
    });

    document.querySelectorAll('.comp-bar-group').forEach(function(el) {
        // Find the parent that contains bar groups
        if (el.parentElement && !el.parentElement._barObserved) {
            barObserver.observe(el.parentElement);
            el.parentElement._barObserved = true;
        }
    });
})();
