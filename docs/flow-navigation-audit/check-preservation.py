"""Verify the unchanged narration/timeline and unrelated published movies."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

P = argparse.ArgumentParser()
P.add_argument('--encoded', action='store_true')
P.add_argument('--report', required=True)
P.add_argument('--upstream', help='Preserve this integrated main revision, including its authorized concurrent updates')
A = P.parse_args()
R = Path(__file__).resolve().parents[2]
INDEX = json.loads((Path(__file__).parent / 'index.json').read_text())
BASE = INDEX['baselineCommit']

def blob(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=R)

def digest(data):
    return hashlib.sha256(data).hexdigest()

reports = []
for slug in INDEX['selected']:
    d = R / 'episodes-codex' / slug
    relative = d.relative_to(R)
    protected = []
    for name in ['voice.wav', 'remotion/public/audio/voice.wav', 'script.md', 'words.json']:
        expected = blob(relative / name)
        assert (d / name).read_bytes() == expected, (slug, name)
        protected.append({'file': name, 'sha256': digest(expected)})
    previous = json.loads(blob(relative / 'storyboard.json'))
    current = json.loads((d / 'storyboard.json').read_text())
    for field in ['width', 'height', 'fps', 'durationInFrames', 'timingSource']:
        assert current['meta'].get(field) == previous['meta'].get(field), (slug, field)
    old = [s for c in previous['scenes'] for s in c['shots']]
    new = [s for c in current['scenes'] for s in c['shots']]
    assert len(old) == len(new), slug
    for a, b in zip(old, new):
        for field in ['id', 'from', 'durationInFrames', 'narration', 'subtitles', 'voice', 'timing']:
            assert a.get(field) == b.get(field), (slug, a['id'], field)
        for field in ['sentences', 'term', 'labels']:
            assert a.get('cueFrames', {}).get(field) == b.get('cueFrames', {}).get(field), (slug, a['id'], field)
    row = {'slug': slug, 'frames': current['meta']['durationInFrames'],
           'shots': len(new), 'timedCaptions': sum(len(s.get('subtitles', [])) for s in new),
           'narrationAndTimelinePreserved': True, 'unchangedFiles': protected}
    if A.encoded:
        movie = (d / 'video.mp4').read_bytes()
        old_result = next(r for r in INDEX['movieBaseline'] if r['slug'] == slug)
        assert digest(movie) != old_result['sha256'], slug
        assert (R / 'episodes' / slug / 'video.mp4').read_bytes() == movie, slug
        row['finalMovieSha256'] = digest(movie)
        row['publishedCopyMatched'] = True
    reports.append(row)

untouched = []
upstream_updates = []
for row in INDEX['movieBaseline']:
    if row['selectedForRemake']:
        continue
    actual = (R / 'episodes' / row['slug'] / 'video.mp4').read_bytes()
    expected = row['sha256']
    if A.upstream:
        incoming = subprocess.check_output([
            'git', 'show', f"{A.upstream}:episodes/{row['slug']}/video.mp4"], cwd=R)
        expected = digest(incoming)
        if expected != row['sha256']:
            upstream_updates.append({'slug': row['slug'], 'baselineSha256': row['sha256'],
                                     'preservedUpstreamSha256': expected})
    assert digest(actual) == expected, row['slug']
    untouched.append(row['slug'])

if A.upstream:
    published_changes = subprocess.check_output([
        'git', 'diff', '--name-only', A.upstream, '--', 'episodes'], cwd=R, text=True).splitlines()
    for changed in published_changes:
        assert changed.split('/')[1] in INDEX['selected'], changed

result = {'status': 'passed', 'baselineCommit': BASE, 'encoded': A.encoded,
          'episodes': reports, 'otherBaselineMoviesPreserved': untouched,
          'integratedUpstream': A.upstream, 'authorizedConcurrentMovieUpdatesPreserved': upstream_updates,
          'scope': 'Narration bytes, original subtitle/voice/shot timeline and unrelated movies; animation expression and live delivery checked separately.'}
Path(A.report).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(f"Preserved {len(reports)} narration/timelines and {len(untouched)} unrelated movies.")
