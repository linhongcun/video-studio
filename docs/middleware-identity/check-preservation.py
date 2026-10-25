"""Check this batch's protected baseline, frozen inputs and original AAC bytes."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

P = argparse.ArgumentParser()
P.add_argument('--encoded', action='store_true')
P.add_argument('--upstream', help='Latest integrated main commit for unrelated media.')
P.add_argument('--report', required=True)
A = P.parse_args()
R = Path(__file__).resolve().parents[2]
I = json.loads((Path(__file__).parent / 'index.json').read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(path, ref):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=R)


def audio(path):
    # MP4 demuxing needs a seekable input when its moov atom is at the end.
    run = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0',
                          '-vn', '-c:a', 'copy', '-f', 'adts', 'pipe:1'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    assert len(run.stdout) > 10000 and not run.stderr, (path, run.stderr.decode())
    timing = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
        'stream=codec_name,sample_rate,channels,start_time,duration,time_base,start_pts,duration_ts',
        '-of', 'json', str(path)]))['streams'][0]
    return {'sha256': sha(run.stdout), 'bytes': len(run.stdout), 'timing': timing}


for path, expected in I['protectedInputs'].items():
    assert (R / path).is_file() and sha((R / path).read_bytes()) == expected, path
for path, expected in I['newSharedAssetSha256'].items():
    assert (R / path).is_file() and sha((R / path).read_bytes()) == expected, path

rows = []
for slug in I['selected']:
    old = next(row for row in I['originalMovies'] if row['slug'] == slug)
    meta_path = f'episodes/{slug}/meta.json'
    previous_meta = json.loads(blob(meta_path, I['baselineCommit']))
    meta = json.loads((R / meta_path).read_text())
    for key in I['historicalMetadataFields']:
        assert meta.get(key) == previous_meta.get(key), (slug, key)
    d = R / meta['sourcePath']
    episode = d.parent
    manifest = json.loads((episode / 'source-sha256.json').read_text())
    for relative, expected in manifest.items():
        assert sha((episode / relative).read_bytes()) == expected, (slug, relative)
    row = {'slug': slug, 'protectedInputsPreserved': True,
           'historicalMetadataPreserved': True, 'frozenInputs': len(manifest)}
    if A.encoded:
        result = json.loads((episode / 'render-result.json').read_text())
        movie = (episode / 'video.mp4').read_bytes()
        assert sha(movie) == result['sha256'] != old['sha256'], slug
        assert len(movie) == result['bytes'] and result['frames'] == old['frames'], slug
        assert movie == (R / old['path']).read_bytes(), (slug, 'published copy')
        current_audio = audio(episode / 'video.mp4')
        assert current_audio['sha256'] == old['originalAac']['sha256'], (slug, 'AAC bytes')
        assert current_audio['bytes'] == old['originalAac']['bytes'], (slug, 'AAC length')
        assert current_audio['timing'] == old['originalAac']['timing'], (slug, 'AAC container timing')
        row.update({'sha256': result['sha256'], 'bytes': result['bytes'],
                    'frames': result['frames'], 'siteCopyMatched': True,
                    'originalAacBytesPreserved': True, 'audio': current_audio})
    rows.append(row)

# Match the actual integrated upstream, not stale original hashes for unrelated films.
reference = A.upstream or I['baselineCommit']
unrelated = []
for p in sorted((R / 'episodes').glob('*/meta.json')):
    slug = p.parent.name
    if slug in I['selected'] or not (p.parent / 'video.mp4').exists():
        continue
    path = f'episodes/{slug}/video.mp4'
    expected = sha(blob(path, reference))
    assert sha((p.parent / 'video.mp4').read_bytes()) == expected, path
    unrelated.append({'slug': slug, 'sha256': expected})

changed = subprocess.check_output([
    'git', 'diff', '--name-only', I['baselineCommit'], '--',
    *[f'episodes-codex/{slug}/remotion/src' for slug in I['selected']]], cwd=R, text=True).splitlines()
untracked = subprocess.check_output([
    'git', 'ls-files', '--others', '--exclude-standard', '--',
    *[f'episodes-codex/{slug}/remotion/src' for slug in I['selected']]], cwd=R, text=True).splitlines()
changed = sorted(set(changed + untracked))
assert set(changed) <= set(I['changedEpisodeSourceAllowlist']), changed
report = {'status': 'passed', 'baselineCommit': I['baselineCommit'],
          'unrelatedMediaReference': reference, 'encoded': A.encoded,
          'protectedInputCount': len(I['protectedInputs']),
          'newSharedAssetCount': len(I['newSharedAssetSha256']),
          'changedEpisodeSource': changed, 'episodes': rows,
          'totalFrozenInputs': sum(row['frozenInputs'] for row in rows),
          'unrelatedMovieCopiesPreserved': unrelated,
          'scope': 'Byte/hash, metadata, declared frozen-input and optional AAC verification; no visual or listening claim.'}
Path(A.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(f"Protected {len(rows)} episodes, {len(unrelated)} unrelated movies; "
      f"{len(I['protectedInputs'])} baseline inputs and {report['totalFrozenInputs']} frozen entries verified.")
