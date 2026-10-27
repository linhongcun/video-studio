#!/usr/bin/env python3
"""Check canonical Pages assets and version after the standalone-MQ release."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import urllib.request
from zoneinfo import ZoneInfo

D = Path(__file__).resolve().parent
R = D.parents[1]
BASE = 'https://linhongcun.github.io/video-studio/'
assets = ['video.mp4', 'cover-16x9.jpg', 'captions.vtt']
assets += [f'article/{i:02d}.jpg' for i in range(1, 5)]
targets = [(f'episodes/message-queue/{name}', R/f'site/dist/episodes/message-queue/{name}') for name in assets]
targets += [(suffix, tokens) for suffix, tokens in [
    ('', ['v0.80.0', 'track-message-queue']),
    ('learn/', ['v0.80.0', 'id="message-queue"']),
    ('series/message-queue/', ['v0.80.0', '可以独立观看']),
    ('series/peak/', ['v0.80.0']),
    ('episodes/message-queue/', ['v0.80.0', 'EP.10', '消息队列']),
    ('library/', ['v0.80.0', 'data-track="message-queue"']),
    ('changelog/', ['releases/tag/v0.80.0', '独立的消息队列系列']),
]]
rows = []
attempt_path = D/'online-attempts.json'
attempts = json.loads(attempt_path.read_text()) if attempt_path.exists() else []
for suffix, target in targets:
    row = {'url': BASE+suffix, 'checkedAt': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')}
    try:
        with urllib.request.urlopen(row['url'], timeout=60) as response:
            data = response.read()
            row.update(status=response.status, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        if isinstance(target, Path):
            row['expectedSHA256'] = hashlib.sha256(target.read_bytes()).hexdigest()
            row['passed'] = row['status'] == 200 and row['sha256'] == row['expectedSHA256']
        else:
            content = data.decode('utf-8')
            row['tokens'] = {token: token in content for token in target}
            row['passed'] = row['status'] == 200 and all(row['tokens'].values())
    except Exception as error:
        row.update(passed=False, error=str(error))
    rows.append(row)
    attempts.append(row)
    attempt_path.write_text(json.dumps(attempts, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'url':row['url'],'passed':row['passed']},ensure_ascii=False),flush=True)
report = {'passed':all(row['passed'] for row in rows),'checks':rows,
          'canonicalRequests':True,'cacheBypassUsed':False,
          'scope':'CA-verified canonical GETs, seven complete asset hashes and seven published pages. Actual classification interactions are checked separately.'}
(D/'online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['passed'], 'Published files/pages did not match; inspect retained attempts'
