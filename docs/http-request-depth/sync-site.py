"""Copy approved EP.01 artifacts; run only after the parent reports final media QA passed."""
import argparse
import json
import shutil
from datetime import datetime, timedelta, timezone
from facts import PUBLIC_FILES, PRODUCTION, CANONICAL, OUT, read_json, sha, utc_now

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--approved-final-media', action='store_true', required=True)
args = parser.parse_args()
config = read_json(PRODUCTION / 'production.json')
rendered = read_json(PRODUCTION / 'render-result.json')
sb = read_json(PRODUCTION / 'storyboard.json')
assert rendered['frames'] == sb['meta']['durationInFrames']
assert sha((PRODUCTION / 'video.mp4').read_bytes()) == rendered['sha256']
for name in PUBLIC_FILES:
    assert (PRODUCTION / name).is_file(), name
hashes = {name: sha((PRODUCTION / name).read_bytes()) for name in PUBLIC_FILES}
for name in PUBLIC_FILES:
    shutil.copyfile(PRODUCTION / name, CANONICAL / name)
meta = read_json(CANONICAL / 'meta.json')
updated = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
meta.update(summary=config['summary'], description=config['summary'], updatedAt=updated,
            finalVideoFrames=rendered['frames'], targetDuration=round(rendered['frames'] / 30),
            tags=['网络基础', 'HTTP', 'TCP', 'TLS'], sourcePath='episodes-codex/http-request/remotion')
(CANONICAL / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
manifest = {'copiedAtUTC': utc_now(), 'source': 'episodes-codex/http-request',
            'scope': 'Approved technical-depth revision; site only, historical platform links retained',
            'filesSHA256': hashes, 'frames': rendered['frames']}
(CANONICAL / 'site-integration.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(OUT / 'delivery-copy.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': 'copied', 'files': len(hashes), 'frames': rendered['frames'],
                  'videoSha256': rendered['sha256']}, ensure_ascii=False))
