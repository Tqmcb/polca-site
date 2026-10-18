/* poLCA — progressive navigation and static catalog filtering; no network dependency. */
(function () {
    'use strict';

    function initNavigation() {
        var header = document.querySelector('.portal-header');
        var button = header && header.querySelector('.portal-menu-toggle');
        var nav = button && document.getElementById(button.getAttribute('aria-controls'));
        if (!header || !button || !nav) return;
        function close(returnFocus) {
            header.classList.remove('is-open');
            button.setAttribute('aria-expanded', 'false');
            if (returnFocus) button.focus();
        }
        button.hidden = false;
        button.setAttribute('aria-expanded', 'false');
        button.addEventListener('click', function () {
            var open = button.getAttribute('aria-expanded') !== 'true';
            button.setAttribute('aria-expanded', String(open));
            header.classList.toggle('is-open', open);
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') close(true);
        });
        nav.addEventListener('click', function (event) {
            if (event.target.closest('a')) close(false);
        });
        document.addEventListener('click', function (event) {
            if (!header.contains(event.target)) close(false);
        });
        if (window.matchMedia) {
            var wide = window.matchMedia('(min-width: 851px)');
            var onResize = function (event) { if (event.matches) close(false); };
            if (wide.addEventListener) wide.addEventListener('change', onResize);
            else if (wide.addListener) wide.addListener(onResize);
        }
        document.body.classList.add('portal-js');
    }

    function normalize(value) {
        return String(value == null ? '' : value)
            .normalize('NFKD').replace(/[łŁ]/g, 'l')
            .replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }
    function words(value) {
        var tokens = normalize(value).replace(/([a-z])([0-9])/g, '$1 $2').replace(/([0-9])([a-z])/g, '$1 $2').match(/[a-z0-9]+/g) || [];
        var stop = new Set(['czy','jak','do','dla','moge','mozna','mam','sie','w','na','z','i','a','to','co','jest','sa','o','czym','obliczyc','policzyc','wyliczyc','obliczam','policze','oblicze','wybrac','uzyc','stosowac','potrzebuje','chce','ktore','jakie','jaki','jaka']);
        var families = {
            produkt: ['produkt','produktu','produkty','produktow','wyrob','wyrobu','wyroby','wyrobow'],
            energia: ['energia','energii','energie','prad','pradu','pradem'],
            weglow: ['weglowy','weglowego','weglowym','weglowe','weglowych'],
            srodowisk: ['srodowiskowy','srodowiskowego','srodowiskowym','srodowiskowe','srodowiskowych'],
            budyn: ['budynek','budynku','budynki','budynkow'],
            slad: ['slad','sladu','slady','sladow']
        };
        return tokens.filter(function (token) { return !stop.has(token); }).map(function (token) {
            return Object.keys(families).find(function (key) { return families[key].indexOf(token) !== -1; }) || token;
        });
    }
    function textValue(value) {
        if (Array.isArray(value)) return value.map(textValue).join(' ');
        if (value && typeof value === 'object') return textValue(value.label || value.name || value.id || '');
        return value == null ? '' : String(value);
    }
    function searchableText(record) {
        return words([
            record.id, record.title, record.description, record.keywords,
            record.category, record.category_id, record.category_label,
            record.indicator, record.indicator_id, record.indicator_label,
            record.boundary, record.year, record.status_label, record.source_name
        ].map(textValue).join(' ')).join(' ');
    }

    function initCatalog() {
        var main = document.querySelector('main[data-catalog-mode]');
        var form = document.getElementById('catalog-filters');
        var dataNode = document.getElementById('portal-search-data');
        var resultList = document.getElementById('catalog-results');
        if (!main || !form || !dataNode || !resultList) return;
        var count = document.getElementById('result-count');
        var empty = document.getElementById('catalog-empty');
        var records;
        try {
            var parsed = JSON.parse(dataNode.textContent);
            records = Array.isArray(parsed) ? parsed : [].concat(parsed.datasets || [], parsed.resources || []);
            if (!Array.isArray(records) || !records.length) return;
        } catch (error) {
            // Retain the complete, useful server-rendered list if enhancement cannot start.
            if (count) count.textContent = 'Widoczna pełna lista. Filtrowanie jest chwilowo niedostępne.';
            return;
        }
        var byId = new Map();
        records.forEach(function (record) {
            if (record && record.id != null) byId.set(String(record.id), record);
        });
        var rows = Array.prototype.slice.call(resultList.querySelectorAll('.portal-result[data-record-id]'));
        if (!rows.length || rows.some(function (row) { return !byId.has(row.getAttribute('data-record-id')); })) return;
        var items = rows.map(function (row) {
            var record = byId.get(row.getAttribute('data-record-id'));
            return { element: row, record: record, text: searchableText(record) };
        });
        var names = ['q', 'category', 'year', 'status', 'kind'];
        var controls = {};
        names.forEach(function (name) {
            var control = form.elements.namedItem(name);
            if (control) controls[name] = control;
        });
        if (!controls.q) return;

        function value(name) { return controls[name] ? controls[name].value.trim() : ''; }
        function activeFilter(name) {
            var selected = value(name);
            return selected === 'all' ? '' : selected;
        }
        function readUrl() {
            var params = new URLSearchParams(window.location.search);
            names.forEach(function (name) {
                var control = controls[name];
                if (!control) return;
                var requested = params.get(name) || '';
                if (control.tagName === 'SELECT') {
                    var options = Array.prototype.slice.call(control.options);
                    var matches = options.some(function (option) { return option.value === requested; });
                    control.value = matches ? requested : (options.find(function (option) { return option.value === '' || option.value === 'all'; }) || options[0]).value;
                } else control.value = requested;
            });
        }
        function writeUrl() {
            var url = new URL(window.location.href);
            names.forEach(function (name) {
                if (!controls[name]) return;
                var current = name === 'q' ? value(name) : activeFilter(name);
                if (current) url.searchParams.set(name, current);
                else url.searchParams.delete(name);
            });
            try { window.history.replaceState(window.history.state, '', url.pathname + url.search + url.hash); }
            catch (error) { /* Local previews can disallow history writes; filtering still works. */ }
        }
        function matchesFilter(record, name, field) {
            var selected = activeFilter(name);
            return !selected || String(record[field] == null ? '' : record[field]) === selected;
        }
        function render(persist) {
            var tokens = words(value('q'));
            var visible = 0;
            var question = /^(jak|czy|co|ktore|jakie|jaki|jaka|czym)\b/.test(normalize(value('q')));
            items.forEach(function (item) {
                var match = tokens.every(function (token) { return item.text.indexOf(token) !== -1; }) &&
                    matchesFilter(item.record, 'category', 'category_id') &&
                    matchesFilter(item.record, 'year', 'year') &&
                    matchesFilter(item.record, 'status', 'status_id') &&
                    matchesFilter(item.record, 'kind', 'kind');
                item.element.hidden = !match;
                if (match) visible++;
            });
            if (main.getAttribute('data-catalog-mode') === 'all') {
                items.map(function (item, index) {
                    var title = words(item.record.title).join(' ');
                    var score = tokens.reduce(function (sum, token) { return sum + (title.indexOf(token) !== -1 ? 2 : 0); }, 0);
                    if (question && item.record.status_id === 'guide') score += 10;
                    return {item: item, index: index, score: score};
                }).sort(function (a, b) { return b.score - a.score || a.index - b.index; }).forEach(function (rank) { resultList.appendChild(rank.item.element); });
            }
            if (count) count.textContent = 'Wyniki: ' + visible + ' z ' + items.length + (value('q') ? ' · „' + value('q') + '”' : '');
            if (empty) empty.hidden = visible !== 0;
            if (persist) writeUrl();
        }
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            render(true);
        });
        form.addEventListener('change', function (event) {
            if (event.target.tagName === 'SELECT' || event.target === controls.q) render(true);
        });
        controls.q.addEventListener('input', function () { render(true); });
        form.addEventListener('reset', function (event) {
            event.preventDefault();
            names.forEach(function (name) {
                var control = controls[name];
                if (!control) return;
                if (control.tagName === 'SELECT') {
                    var options = Array.prototype.slice.call(control.options);
                    control.value = (options.find(function (option) { return option.value === '' || option.value === 'all'; }) || options[0]).value;
                } else control.value = '';
            });
            render(true);
        });
        if (empty) empty.querySelectorAll('[data-reset-filters]').forEach(function (button) {
            button.addEventListener('click', function () { form.reset(); controls.q.focus(); });
        });
        window.addEventListener('popstate', function () { readUrl(); render(false); });
        readUrl();
        render(false);
        main.classList.add('portal-catalog-ready');
    }

    function init() { initNavigation(); initCatalog(); }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
