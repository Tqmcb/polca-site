(function () {
    'use strict';

    var QUICK_SEARCHES = [
        { label: 'Energia elektryczna PL', query: 'electricity', region: 'PL', source: 'ecoinvent' },
        { label: 'Stal EAF', query: 'steel electric arc', region: 'PL', source: 'ecoinvent' },
        { label: 'Cement Portland', query: 'cement portland', region: 'PL', source: 'ecoinvent' },
        { label: 'Beton', query: 'concrete', region: 'PL', source: 'ecoinvent' },
        { label: 'Transport drogowy', query: 'road freight transport', region: 'PL', source: 'ecoinvent' },
        { label: 'Gaz ziemny PL', query: 'natural gas', region: 'PL', source: 'ecoinvent' },
        { label: 'Aluminium', query: 'aluminium production', region: '', source: 'ecoinvent' },
        { label: 'Szkło float', query: 'flat glass', region: '', source: 'ecoinvent' },
    ];

    function buildClimatiqUrl(query, region, source) {
        var base = 'https://www.climatiq.io/explorer';
        var params = new URLSearchParams();
        if (query) params.set('query', query);
        if (region) params.set('region', region);
        if (source) params.set('source', source);
        var qs = params.toString();
        return qs ? base + '?' + qs : base;
    }

    function openClimatiq(query, region, source) {
        var url = buildClimatiqUrl(query, region, source);
        window.open(url, '_blank', 'noopener,noreferrer');
    }

    function renderQuickSearches() {
        var container = document.getElementById('quickSearches');
        if (!container) return;

        QUICK_SEARCHES.forEach(function (item) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'topbar-btn topbar-btn-outline';
            btn.style.cssText = 'font-size: 0.78rem; padding: 0.3rem 0.75rem; height: auto;';
            btn.textContent = item.label;
            btn.addEventListener('click', function () {
                openClimatiq(item.query, item.region, item.source);
            });
            container.appendChild(btn);
        });
    }

    function initForm() {
        var form = document.getElementById('climatiqSearchForm');
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var query = document.getElementById('climatiqQuery').value.trim();
            var region = document.getElementById('climatiqRegion').value;
            var source = document.getElementById('climatiqSource').value;
            if (!query) return;
            openClimatiq(query, region, source);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        renderQuickSearches();
        initForm();
    });
}());
