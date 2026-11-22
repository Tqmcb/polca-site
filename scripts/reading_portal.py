"""Render the shared chapter index and reading layout for informational pages."""


def build(content, page, links, sections):
    chapters = content['sections']
    index = links([
        {'label': section['title'], 'href': '#' + section.get('id', f'sekcja-{i}')}
        for i, section in enumerate(chapters, start=1)
    ], 'reading-index-list')
    body = f'''<div class="reading-layout">
    <nav class="reading-index" aria-label="Spis treści">
      <div class="reading-desktop-index"><p>Spis treści</p>{index}</div>
      <details class="reading-mobile-index"><summary>Spis treści</summary>{index}</details>
    </nav>
    <div class="reading-chapters">{sections(chapters, responsive_tables=True)}</div>
    </div>'''
    page(content['path'], content['title'], content['lead'], body,
         head_extra='<link rel="stylesheet" href="/assets/guide-reading.css?v=1">')
