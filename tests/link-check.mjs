import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const origin = new URL('https://polca.org.pl');
const missing = [];
let pages = 0;
let links = 0;

function checkDirectory(dir) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
        if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
        const path = join(dir, entry.name);
        if (entry.isDirectory()) {
            checkDirectory(path);
            continue;
        }
        if (!entry.isFile() || !entry.name.endsWith('.html')) continue;

        pages++;
        const page = relative(root, path);
        const base = new URL(page, origin);
        const markup = readFileSync(path, 'utf8').replace(/<!--[\s\S]*?-->|(<script\b[^>]*>)[\s\S]*?<\/script>/gi, '$1');
        for (const match of markup.matchAll(/\shref\s*=\s*(["'])(.*?)\1/gi)) {
            const href = match[2].trim();
            if (!href || href.startsWith('#')) continue;
            const url = new URL(href, base);
            if (!['http:', 'https:'].includes(url.protocol)) continue;
            if (![origin.hostname, 'www.polca.org.pl'].includes(url.hostname)) continue;
            if (!url.pathname.endsWith('.html')) continue;
            links++;
            const target = resolve(root, '.' + decodeURIComponent(url.pathname));
            if (!statSync(target, { throwIfNoEntry: false })?.isFile()) missing.push(page + ' → ' + href);
        }
    }
}

checkDirectory(root);
if (missing.length) {
    console.error(missing.join('\n'));
    process.exitCode = 1;
}
console.log(`Sprawdzono ${pages} stron i ${links} odsyłaczy do plików HTML. Brakujące cele: ${missing.length}.`);
