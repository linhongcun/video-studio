#!/usr/bin/env python3
"""Read-only full GET checks after deployment; requires the final local site build."""
import concurrent.futures, datetime, hashlib, json, pathlib, subprocess, urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(subprocess.check_output(['git','rev-parse','--show-toplevel'], cwd=pathlib.Path(__file__).parent, text=True).strip())
PUB = ROOT / 'episodes/leetcode/three-sum/publication'
BASE = 'https://linhongcun.github.io/video-studio'
OUT = ROOT / 'work/lc15-v0.109.0-publication-verification.json'
started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
OUT.parent.mkdir(parents=True, exist_ok=True)

class PageData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chapters, self.rewatch = [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-chapters' in attrs:
            self.chapters = json.loads(attrs['data-chapters'])
        if tag == 'a' and 'data-seek' in attrs:
            self.rewatch.append(attrs['data-seek'])

expected_page = PageData()
expected_page.feed((ROOT/'site/dist/episodes/three-sum/index.html').read_text())
assert {c['id'] for c in expected_page.chapters} == {'question','scan','dedup','close'}

def get(path):
    url = BASE + path
    with urllib.request.urlopen(urllib.request.Request(url, headers={'Cache-Control':'no-cache'}), timeout=90) as r:
        data = r.read()
        return dict(url=url, status=r.status, bytes=len(data),
                    contentType=r.headers.get('Content-Type'), sha256=hashlib.sha256(data).hexdigest()), data

files = ['video.mp4','cover-16x9.jpg','article/01.svg']
checks = []
def check_file(name):
    info, data = get('/episodes/three-sum/' + name)
    info['expectedSha256'] = hashlib.sha256((PUB/name).read_bytes()).hexdigest()
    info['passed'] = info['status'] == 200 and info['sha256'] == info['expectedSha256']
    return info

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    checks.extend(pool.map(check_file, files))
page_info, page = get('/episodes/three-sum/')
html = page.decode('utf-8')
sources = json.loads((PUB/'references.json').read_text())['sources']
page_info['checks'] = {t: t in html for t in ['三数之和','LC.15','Sorting Techniques','3Sum','article/01.svg'] + [s['url'] for s in sources]}
page_info['passed'] = page_info['status'] == 200 and all(page_info['checks'].values())
checks.append(page_info)
for path, expected in [('/','三数之和'),('/library/','三数之和'),('/changelog/','v0.109.0')]:
    info, data = get(path)
    info['contains'] = expected
    info['passed'] = info['status'] == 200 and expected in data.decode('utf-8')
    if path == '/changelog/':
        info['releaseLinkPresent'] = 'https://github.com/linhongcun/video-studio/releases/tag/v0.109.0' in data.decode('utf-8')
        info['passed'] = info['passed'] and info['releaseLinkPresent']
    checks.append(info)
info, data = get('/episodes/three-sum/captions.vtt')
info['expectedSha256'] = hashlib.sha256((ROOT/'site/dist/episodes/three-sum/captions.vtt').read_bytes()).hexdigest()
info['passed'] = info['status'] == 200 and data.startswith(b'WEBVTT') and info['sha256'] == info['expectedSha256']
checks.append(info)
parsed = PageData()
parsed.feed(html)
checks.append(dict(kind='chapters-and-article-rewatch-links', chapters=parsed.chapters, ids=parsed.rewatch,
                   passed=parsed.chapters == expected_page.chapters and {c['id'] for c in expected_page.chapters} <= set(parsed.rewatch)))
media = json.loads((PUB/'render-result.json').read_text())
appendix = media['referenceAppendix']
checks.append(dict(kind='reference-appendix-via-identical-complete-media', appendix=appendix,
                   passed=checks[0]['passed'] and appendix['from'] == 5648 and appendix['durationInFrames'] == 150 and media['finalVideoFrames'] == 5798))
finished = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
report = dict(episode='LC.15 三数之和', issue='https://github.com/linhongcun/video-studio/issues/490',
              pr='https://github.com/linhongcun/video-studio/pull/499',version='v0.109.0',
              startedAt=started, checkedAt=finished,
              productionStartedAt='2026-11-15T13:46:00+08:00',
              elapsedMinutes=round((datetime.datetime.fromisoformat(finished)-datetime.datetime.fromisoformat('2026-11-15T13:46:00+08:00')).total_seconds()/60,2),
              productionTiming=json.loads((PUB.parent/'production/qa/production-timing.json').read_text()),
              sourceManifestSha256=hashlib.sha256((PUB.parent/'production/source-sha256.json').read_bytes()).hexdigest(),
              media=media,
              publishedCommit='0735641d4773c050d7326a8f41a7d28eea6b82a9',
              postReleaseDeployment='https://github.com/linhongcun/video-studio/actions/runs/43688172126',
              checks=checks, passed=all(c['passed'] for c in checks),
              browserCoverage='Local final-media desktop Chromium and 390px mobile emulation; see PR acceptance evidence.',
              limitations=['No post-deployment browser playback','No physical mobile device or iOS/Safari','No human verbatim audio audit; automatic cross-ASR has homophone limitations'])
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(passed=report['passed'],checks=len(checks),elapsedMinutes=report['elapsedMinutes'],failed=[c for c in checks if not c['passed']],output=str(OUT)),ensure_ascii=False,indent=2))
raise SystemExit(0 if report['passed'] else 1)
