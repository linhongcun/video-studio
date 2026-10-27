#!/usr/bin/env python3
"""Ordinary CA-verified GETs for the published independent database direction."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import json
import urllib.request

D = Path(__file__).resolve().parent
R = D.parents[1]
BASE = 'https://linhongcun.github.io/video-studio/'
slugs = ['db-index', 'db-transaction', 'db-lock', 'db-replication']
targets = []
for slug in slugs:
    for name in ['video.mp4', 'cover-16x9.jpg', 'captions.vtt', 'article/01.jpg']:
        targets.append((f'episodes/{slug}/{name}', R/f'site/dist/episodes/{slug}/{name}'))
targets += [(suffix, tokens) for suffix, tokens in [
    ('', ['v0.81.0', 'track-database']),
    ('learn/', ['v0.81.0', 'id="database"']),
    ('series/database/', ['v0.81.0', 'db-replication']),
    ('library/', ['v0.81.0', 'data-track="database"']),
    ('changelog/', ['releases/tag/v0.81.0', '数据库已独立于系统原理']),
    ('series/message-queue/', ['v0.81.0', '消息队列']),
    ('episodes/degradation/', ['v0.81.0']),
    ('episodes/db-sharding/', ['v0.81.0']),
]]
targets += [(f'episodes/{slug}/', ['v0.81.0', '数据库']) for slug in slugs]
rows = []
attempt_path = D/'online-attempts.json'
attempts = json.loads(attempt_path.read_text()) if attempt_path.exists() else []
for suffix, target in targets:
    row = {'url':BASE+suffix, 'checkedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')}
    try:
        with urllib.request.urlopen(row['url'],timeout=60) as response:
            data=response.read()
            row.update(status=response.status,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        if isinstance(target,Path):
            row['expectedSHA256']=hashlib.sha256(target.read_bytes()).hexdigest()
            row['passed']=row['status']==200 and row['sha256']==row['expectedSHA256']
        else:
            content=data.decode('utf-8')
            row['tokens']={token:token in content for token in target}
            row['passed']=row['status']==200 and all(row['tokens'].values())
    except Exception as error:
        row.update(passed=False,error=str(error))
    rows.append(row);attempts.append(row)
    attempt_path.write_text(json.dumps(attempts,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'url':row['url'],'passed':row['passed']},ensure_ascii=False),flush=True)
report={'passed':all(row['passed'] for row in rows),'checks':rows,'canonicalRequests':True,'cacheBypassUsed':False,
        'scope':'Sixteen complete asset hashes and twelve published page checks. No new playback or full human listening review.'}
(D/'online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['passed'], 'Published assets/pages differ; retained attempts explain the failure'
