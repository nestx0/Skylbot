"""Check HTML asset links with both root and subdirectory static hosting."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for key in ('href', 'src'):
            if d.get(key):
                self.attrs.append((tag, key, d[key]))

checked = 0
for page in ROOT.rglob('*.html'):
    links = Links()
    links.feed(page.read_text(encoding='utf-8'))
    for tag, attr, url in links.attrs:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path or url.startswith('#'):
            continue
        assert not parsed.path.startswith('/'), f'Ruta absoluta en {page.relative_to(ROOT)}: {url}'
        target = (page.parent / unquote(parsed.path)).resolve()
        assert target.is_relative_to(ROOT.resolve()), f'Ruta fuera de web: {url}'
        if parsed.path.endswith('/'):
            target /= 'index.html'
        assert target.is_file(), f'Enlace local roto: {page.relative_to(ROOT)} -> {url}'
        checked += 1
    if page.name != '404.html':
        assert 'assets/css/styles.css' in page.read_text()
print(f'OK: {checked} enlaces locales verificados en las páginas HTML.')
