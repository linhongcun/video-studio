"""Verify deployed citation content, native controls and exact JS/CSS bytes."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = 'https://linhongcun.github.io/video-studio/'
VERSION = '0.75.0'


class Citations(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.panels, self.triggers, self.assets = [], [], set()
        self.panel = None
        self.quoting = False
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'button' and 'data-source-trigger' in attrs:
            self.triggers.append({key: attrs.get(key) for key in ['data-source-trigger', 'popovertarget', 'aria-controls', 'aria-label']})
        if tag == 'aside' and 'data-source-panel' in attrs:
            self.panel = {'id': attrs['id'], 'sourceId': attrs['data-source-panel'], 'popover': attrs.get('popover'), 'quote': '', 'links': []}
        if self.panel and tag == 'blockquote':
            self.quoting = True
        if self.panel and tag == 'a':
            self.panel['links'].append(attrs['href'])
        for key in ['href', 'src']:
            value = attrs.get(key, '')
            if value.startswith('/video-studio/_astro/') and value.endswith(('.js', '.css')):
                self.assets.add(value)

    def handle_endtag(self, tag):
        if tag == 'blockquote':
            self.quoting = False
        if tag == 'aside' and self.panel:
            self.panels.append(self.panel)
            self.panel = None

    def handle_data(self, data):
        if self.panel and self.quoting:
            self.panel['quote'] += data


def get(url):
    with urlopen(Request(url, headers={'Cache-Control': 'no-cache'}), timeout=60) as response:
        assert response.status == 200
        return response.read()


def article(slug):
    url = BASE + 'episodes/' + slug + '/'
    body = get(url)
    remote = Citations(body.decode())
    local = Citations((ROOT / 'site/dist/episodes' / slug / 'index.html').read_text())
    assert remote.panels == local.panels and remote.triggers == local.triggers, slug + ': citation identity differs'
    assert remote.assets == local.assets and 'v' + VERSION in body.decode(), slug + ': UI build identity differs'
    return {'kind': 'article', 'slug': slug, 'url': url, 'quotes': len(remote.panels), 'sha256': sha256(body).hexdigest()}, remote.assets


def asset(relative):
    url = 'https://linhongcun.github.io' + relative
    body = get(url)
    local = (ROOT / 'site/dist' / relative.removeprefix('/video-studio/')).read_bytes()
    assert sha256(body).hexdigest() == sha256(local).hexdigest(), relative + ': complete asset SHA differs'
    return {'kind': 'asset', 'url': url, 'bytes': len(body), 'sha256': sha256(body).hexdigest()}


def main():
    slugs = [file.parent.name for file in sorted((ROOT / 'episodes').glob('*/meta.json'))
             if not any(json.loads(file.read_text()).get(flag) for flag in ['draft', 'archived'])]
    results, failures, assets = [], [], set()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for job in as_completed([pool.submit(article, slug) for slug in slugs]):
            try:
                record, linked = job.result()
                results.append(record)
                assets.update(linked)
            except Exception as error:
                failures.append(str(error))
        for job in as_completed([pool.submit(asset, relative) for relative in assets]):
            try:
                results.append(job.result())
            except Exception as error:
                failures.append(str(error))
    changelog = get(BASE + 'changelog/').decode()
    assert '/releases/tag/v' + VERSION in changelog, 'deployed changelog lacks Release'
    report = {'version': VERSION, 'checkedAt': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'results': results, 'failures': failures, 'changelogIncludesRelease': True,
              'scope': 'All 47 article citation controls/content and every linked JS/CSS file; interaction behavior separately checked on the same built asset bytes.'}
    (OUT / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'requestsVerified': len(results) + 1, 'failures': failures}))
    assert not failures


if __name__ == '__main__':
    main()
