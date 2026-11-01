#!/usr/bin/env python3
"""Ordinary canonical HTTPS GETs for the published EP10 revision."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import json
import urllib.request

D = Path(__file__).resolve().parent
R = next(p for p in D.parents if (p/'AGENTS.md').exists())
E = R/'episodes/message-queue'
BASE = 'https://linhongcun.github.io/video-studio/'
sha = lambda data: hashlib.sha256(data).hexdigest()
attempts_path = D/'online-attempts.json'
attempts = json.loads(attempts_path.read_text()) if attempts_path.exists() else []
checks = []
assets = [('episodes/message-queue/video.mp4', E/'video.mp4'),
          ('episodes/message-queue/cover-16x9.jpg', E/'cover-16x9.jpg'),
          ('episodes/message-queue/captions.vtt', R/'site/dist/episodes/message-queue/captions.vtt')]
assets += [(f'episodes/message-queue/article/{i:02d}.jpg', E/f'article/{i:02d}.jpg') for i in range(1, 5)]
pages = [
    ('episodes/message-queue/', ['mq-intro/message-queue/remotion', '提交受理', 'id="retry"', 'id="recap"']),
    ('series/message-queue/', ['可以独立观看', '/video-studio/episodes/message-queue/']),
    ('series/peak/', ['/video-studio/episodes/message-queue/']),
    ('learn/', ['/video-studio/series/message-queue/']),
    ('library/', ['peak|message-queue']),
    ('changelog/', ['v0.79.0']),
]
for suffix, target in assets + pages:
    url = BASE+suffix
    row = {'url':url, 'checkedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')}
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            body = response.read()
            row.update(status=response.status, bytes=len(body), sha256=sha(body))
        if isinstance(target, Path):
            row['expectedSHA256'] = sha(target.read_bytes())
            row['passed'] = row['status'] == 200 and row['sha256'] == row['expectedSHA256']
        else:
            text = body.decode('utf-8')
            row['requiredText'] = {token:token in text for token in target}
            row['passed'] = row['status'] == 200 and all(row['requiredText'].values())
    except Exception as error:
        row.update(passed=False, error=f'{type(error).__name__}: {error}')
    checks.append(row)
    attempts.append(row)
    attempts_path.write_text(json.dumps(attempts, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'url':url,'status':row.get('status'),'passed':row['passed']},ensure_ascii=False),flush=True)
report = {'passed':all(row['passed'] for row in checks), 'checks':checks,
          'canonicalRequests':True, 'cacheBypassUsed':False,
          'scope':'Plain canonical HTTPS GETs, full media/image/caption bytes and expected published page content. Actual player interaction is checked separately.'}
(D/'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
assert report['passed'], 'Published canonical files or page content differ; inspect retained attempt records'
