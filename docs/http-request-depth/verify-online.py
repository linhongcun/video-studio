"""Verify explicit released EP01 tag and its successful post-Release deployment."""
import argparse
import json
import subprocess
import time
import urllib.request
from facts import (ROOT, OUT, BASE, REPOSITORY, SLUG, CANONICAL, DIST, Document, facts,
                   check_identity, check_episode, check_rss, date_version, request_slugs, sha, utc_now, commit_id)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--revision-tag', required=True)
parser.add_argument('--deployment-run', required=True, type=int)
parser.add_argument('--preservation-base', required=True)
args = parser.parse_args()
records, apis = [], []
attempts_path = OUT / 'online-attempts.json'
history = json.loads(attempts_path.read_text()) if attempts_path.exists() else {'attempts': []}
attempt = {'startedAtUTC': utc_now(), 'revisionTag': args.revision_tag,
           'deploymentRun': args.deployment_run, 'preservationBaseline': args.preservation_base, 'status': 'running'}
history['attempts'].append(attempt)

def api(path):
    value = json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPOSITORY}/{path}'], cwd=ROOT))
    apis.append({'path': path, 'source': 'GitHub CLI API', 'checkedAtUTC': utc_now()})
    return value


def get(path):
    request = urllib.request.Request(BASE + path, headers={'User-Agent': 'video-studio-ep01-depth-verify', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=60) as response:
        assert response.status == 200
        body = response.read()
        records.append({'url': response.url, 'status': response.status, 'bytes': len(body), 'sha256': sha(body)})
    return body

try:
    tag = args.revision_tag
    tagged_commit = commit_id(tag)
    assert subprocess.check_output(['git', 'cat-file', '-t', tag], cwd=ROOT, text=True).strip() == 'tag'
    release = api('releases/tags/' + tag)
    assert not release['draft'] and release['tag_name'] == tag
    deploy = api(f'actions/runs/{args.deployment_run}')
    assert deploy['status'] == 'completed' and deploy['conclusion'] == 'success'
    assert deploy['event'] == 'workflow_dispatch' and deploy['head_branch'] == 'main'
    assert deploy['path'] == '.github/workflows/deploy.yml'
    assert deploy['head_sha'] == tagged_commit
    assert release['published_at'] <= deploy['created_at']
    data = facts()
    files = check_identity(data, args.preservation_base, tagged_commit)
    local_qa = json.loads((OUT / 'qa-site.json').read_text())
    assert local_qa['status'] == 'passed' and local_qa['revisionTag'] == tag
    assert local_qa['files']['video.mp4'] == files['video.mp4']
    for name in (data['meta']['video'], data['meta']['poster']):
        assert get(f'episodes/{SLUG}/{name}') == (CANONICAL / name).read_bytes()
    vtt = get(f'episodes/{SLUG}/captions.vtt')
    assert vtt == (DIST / 'episodes' / SLUG / 'captions.vtt').read_bytes()
    episode = check_episode(Document(get(f'episodes/{SLUG}/').decode()), vtt, data, tag)
    directory = [f'/video-studio/episodes/{slug}/' for slug in request_slugs()]
    series = Document(get('series/request/').decode())
    library = Document(get('library/').decode())
    assert set(directory) <= set(series.links)
    assert directory[0] in library.links and date_version(data['meta']['updatedAt']) in library.text
    rss_check = check_rss(get('rss.xml'), data)
    home = Document(get('').decode())
    assert tag in home.text
    changelog = Document(get('changelog/').decode())
    items = [item for item in changelog.list_items if release['html_url'] in item['links']]
    assert len(items) == 1
    associated = {href for href in items[0]['links'] if href.startswith('/video-studio/episodes/')}
    assert associated == {f'/video-studio/episodes/{SLUG}/'}, associated
    report = {'status': 'passed', 'checkedAtUTC': utc_now(), 'revisionTag': tag,
              'taggedCommit': tagged_commit, 'preservationBaseline': args.preservation_base,
              'release': {key: release[key] for key in ('tag_name', 'html_url', 'published_at')},
              'deployment': {key: deploy[key] for key in ('id', 'html_url', 'head_sha', 'status', 'conclusion', 'event', 'created_at')},
              'files': files, 'episode': episode, 'httpRecords': records, 'apiRecords': apis,
              'requestSeries': request_slugs(), 'releaseChangelogAssociatedOnlyEP01': True,
              'rss': rss_check, 'cardDateVersionMatches': True,
              'nonTaskCanonicalPreserved': True,
              'limits': 'Online complete bytes and serialized HTML/VTT; actual player behavior is covered by the local qa-site report. No listening or learning-outcome claim.'}
    (OUT / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    attempt.update(status='passed', finishedAtUTC=utc_now(), completeHTTPResponses=len(records))
    print(json.dumps({'status': 'passed', 'revisionTag': tag, 'completeHTTPResponses': len(records),
                      'videoSha256': files['video.mp4']['sha256']}, ensure_ascii=False))
except Exception as error:
    attempt.update(status='failed', finishedAtUTC=utc_now(), error=type(error).__name__, message=str(error))
    raise
finally:
    attempt.update(httpRecords=records, apiRecords=apis)
    attempts_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n')
