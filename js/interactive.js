'use strict';
(function () {

    /* =========================================================
       1. ANIMATED COUNTERS — liczniki wskakują gdy widoczne
       ========================================================= */
    function animateCounter(el) {
        var target = parseFloat(el.dataset.target || el.textContent.replace(/[^\d.]/g, ''));
        var suffix = el.dataset.suffix || '';
        var prefix = el.dataset.prefix || '';
        var decimals = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;
        var duration = 1400;
        var start = null;
        function step(ts) {
            if (!start) start = ts;
            var progress = Math.min((ts - start) / duration, 1);
            var ease = 1 - Math.pow(1 - progress, 3);
            var val = target * ease;
            el.textContent = prefix + (decimals > 0 ? val.toFixed(decimals) : Math.floor(val).toLocaleString('pl-PL')) + suffix;
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = prefix + (decimals > 0 ? target.toFixed(decimals) : target.toLocaleString('pl-PL')) + suffix;
        }
        requestAnimationFrame(step);
    }

    var counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            if (e.isIntersecting && !e.target.dataset.counted) {
                e.target.dataset.counted = '1';
                animateCounter(e.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-counter]').forEach(function (el) {
        counterObserver.observe(el);
    });

    /* =========================================================
       2. CHART.JS — INTERAKTYWNY WYKRES EMISJI
       ========================================================= */
    function initEmissionChart() {
        var canvas = document.getElementById('emissionChart');
        if (!canvas || !window.Chart) return;

        var ctx = canvas.getContext('2d');

        var accent   = '#0DBF9F';
        var accentDim= 'rgba(13,191,159,0.25)';
        var warm     = '#D97706';
        var warmDim  = 'rgba(217,119,6,0.25)';
        var muted    = '#6B7280';
        var mutedDim = 'rgba(107,114,128,0.18)';

        new window.Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Energia el.\nPolska\n(KOBiZE)', 'Energia el.\nŚr. EU', 'Energia el.\nNiemcy', 'Gaz\nziemny', 'Węgiel\nkamienny', 'Biomasa\n(neutrl.)'],
                datasets: [{
                    label: 'Emisja CO₂ [kg/MWh]',
                    data: [597, 295, 364, 202, 344, 0],
                    backgroundColor: [accent, mutedDim, mutedDim, mutedDim, warmDim, 'rgba(34,197,94,0.2)'],
                    borderColor:     [accent, muted,    muted,    muted,    warm,    '#22c55e'],
                    borderWidth: 2,
                    borderRadius: 6,
                    hoverBackgroundColor: [accentDim, 'rgba(107,114,128,0.35)', 'rgba(107,114,128,0.35)', 'rgba(107,114,128,0.35)', warmDim, 'rgba(34,197,94,0.35)'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0d1a18',
                        borderColor: accent,
                        borderWidth: 1,
                        titleColor: '#fff',
                        bodyColor: 'rgba(255,255,255,0.75)',
                        padding: 12,
                        callbacks: {
                            label: function(ctx) {
                                var v = ctx.raw;
                                var suffix = v === 0 ? ' kg CO₂/MWh (neutralna)' : ' kg CO₂/MWh';
                                return v + suffix;
                            },
                            afterLabel: function(ctx) {
                                var vals = [597, 295, 364, 202, 344, 0];
                                var pl = vals[0];
                                var v = ctx.raw;
                                if (v === 0) return 'Biomasa — neutralna węglowo (EU ETS)';
                                var diff = ((v / pl) * 100).toFixed(0);
                                if (ctx.dataIndex === 0) return '← Dane poLCA (KOBiZE 2024)';
                                return 'vs Polska: ' + diff + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: {
                            color: 'rgba(255,255,255,0.38)',
                            font: { family: "'IBM Plex Mono', monospace", size: 11 }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 700,
                        grid: { color: 'rgba(255,255,255,0.06)' },
                        ticks: {
                            color: 'rgba(255,255,255,0.38)',
                            font: { family: "'IBM Plex Mono', monospace", size: 11 },
                            callback: function(v) { return v + ' kg'; }
                        }
                    }
                },
                animation: {
                    delay: function(ctx) { return ctx.dataIndex * 80; },
                    duration: 800,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /* =========================================================
       3. DONUT CHART — struktura GWP betonu
       ========================================================= */
    function initDonutChart() {
        var canvas = document.getElementById('donutChart');
        if (!canvas || !window.Chart) return;
        var ctx = canvas.getContext('2d');

        new window.Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Cement (klinkier)', 'Energia el. (mieszanie)', 'Transport surowców', 'Kruszywo naturalne', 'Woda procesowa'],
                datasets: [{
                    data: [74, 13, 7, 4, 2],
                    backgroundColor: ['#0DBF9F','#D97706','#2d7dd2','#7c4dcc','#6B7280'],
                    borderColor: '#071714',
                    borderWidth: 3,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: 'rgba(255,255,255,0.6)',
                            font: { family: "'Inter', sans-serif", size: 12 },
                            padding: 14,
                            boxWidth: 12,
                            boxHeight: 12,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0d1a18',
                        borderColor: '#0DBF9F',
                        borderWidth: 1,
                        titleColor: '#fff',
                        bodyColor: 'rgba(255,255,255,0.75)',
                        padding: 12,
                        callbacks: {
                            label: function(ctx) {
                                return ' ' + ctx.raw + '% udziału w GWP';
                            }
                        }
                    }
                },
                animation: { animateRotate: true, duration: 900, easing: 'easeOutQuart' }
            }
        });
    }

    /* =========================================================
       4. HOTSPOT DIAGRAM — beton, interaktywne tooltips
       ========================================================= */
    function initHotspots() {
        var container = document.querySelector('.hotspot-diagram');
        if (!container) return;

        var tooltip = document.createElement('div');
        tooltip.className = 'hotspot-tooltip';
        document.body.appendChild(tooltip);

        container.querySelectorAll('.hotspot').forEach(function (hs) {
            hs.addEventListener('mouseenter', function (e) {
                var title = hs.dataset.title || '';
                var val   = hs.dataset.value || '';
                var desc  = hs.dataset.desc  || '';
                tooltip.innerHTML =
                    '<div class="htt-title">' + title + '</div>' +
                    '<div class="htt-value">' + val + '</div>' +
                    '<div class="htt-desc">' + desc + '</div>';
                tooltip.classList.add('visible');
                positionTooltip(e);
            });
            hs.addEventListener('mousemove', positionTooltip);
            hs.addEventListener('mouseleave', function () {
                tooltip.classList.remove('visible');
            });
            hs.addEventListener('click', function () {
                container.querySelectorAll('.hotspot').forEach(function (h) { h.classList.remove('active'); });
                hs.classList.toggle('active');
            });
        });

        function positionTooltip(e) {
            var x = e.clientX + 16;
            var y = e.clientY - 10;
            if (x + 240 > window.innerWidth) x = e.clientX - 256;
            tooltip.style.left = x + 'px';
            tooltip.style.top  = y + 'px';
        }
    }

    /* =========================================================
       5. SECTOR DEVIATION CHART — PL vs EU avg per sektor
       ========================================================= */
    function initSectorChart() {
        var canvas = document.getElementById('sectorChart');
        if (!canvas || !window.Chart) return;
        var ctx = canvas.getContext('2d');

        var labels = [
            'Stal EAF (PL vs BOF EU avg)',
            'Cement CEM I (alt. paliwa PL)',
            'Aluminium pierwotne',
            'Beton C30/37',
            'Miks energetyczny PL'
        ];
        var values = [-65, -6, 14, 15, 102];

        var bgColors = values.map(function(v) {
            return v < 0 ? 'rgba(13,191,159,0.75)' : 'rgba(217,119,6,0.80)';
        });
        var bdColors = values.map(function(v) {
            return v < 0 ? '#0DBF9F' : '#D97706';
        });

        new window.Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Odchylenie PL vs EU avg [%]',
                    data: values,
                    backgroundColor: bgColors,
                    borderColor: bdColors,
                    borderWidth: 2,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0d1a18',
                        borderColor: '#0DBF9F',
                        borderWidth: 1,
                        titleColor: '#fff',
                        bodyColor: 'rgba(255,255,255,0.75)',
                        padding: 12,
                        callbacks: {
                            label: function(c) {
                                var v = c.raw;
                                return (v > 0 ? '+' : '') + v + '% względem danych europejskich';
                            },
                            afterLabel: function(c) {
                                return c.raw < 0
                                    ? '✓ Dane EU zawyżają ślad węglowy — PL jest lepszy'
                                    : '⚠ Dane EU zaniżają ślad węglowy — PL jest gorszy';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        min: -80, max: 115,
                        grid: { color: 'rgba(255,255,255,0.06)' },
                        ticks: {
                            color: 'rgba(255,255,255,0.38)',
                            font: { family: "'IBM Plex Mono', monospace", size: 11 },
                            callback: function(v) { return (v > 0 ? '+' : '') + v + '%'; }
                        }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: {
                            color: 'rgba(255,255,255,0.65)',
                            font: { family: "'Inter', sans-serif", size: 12 }
                        }
                    }
                },
                animation: {
                    delay: function(c) { return c.dataIndex * 110; },
                    duration: 900,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /* =========================================================
       6. WORKFLOW — animacja strzałek faz A1-A5
       ========================================================= */
    function initWorkflow() {
        var steps = document.querySelectorAll('.wf-step');
        if (!steps.length) return;
        var obs = new IntersectionObserver(function (entries) {
            if (entries[0].isIntersecting) {
                steps.forEach(function (s, i) {
                    setTimeout(function () { s.classList.add('wf-visible'); }, i * 120);
                });
                obs.disconnect();
            }
        }, { threshold: 0.3 });
        obs.observe(steps[0].closest('.workflow-row') || steps[0]);
    }

    /* =========================================================
       6. INIT — po załadowaniu Chart.js z CDN
       ========================================================= */
    function initAll() {
        initEmissionChart();
        initDonutChart();
        initSectorChart();
        initHotspots();
        initWorkflow();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }

})();
