"""Copy an explicitly approved final film into its existing canonical publication.

This entry never renders, builds or publishes. It validates the final shared
render/appendix receipts and source freeze before changing canonical files.
"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SLUG = 'daily-temperatures'
EP = ROOT / 'episodes-codex' / SLUG
CANONICAL = ROOT / 'episodes' / SLUG
IDENTITY = ['slug', 'title', 'ep', 'problemNumber', 'firstRelease', 'createdAt', 'publishedAt', 'sourcePath']
COPIED = ['article.mdx', 'script.md', 'storyboard.json', 'video.mp4', 'references.json',
          'reference-appendix.json', 'reference-appendix-media-check.json', 'references.md',
          'research.md', 'render-result.json', 'source-sha256.json']
COVERS = ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def version(value):
    assert re.fullmatch(r'\d+\.\d+\.\d+', value)
    return tuple(map(int, value.split('.')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision-tag', required=True)
    parser.add_argument('--preservation-base', required=True)
    parser.add_argument('--approved-video-sha', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'v\d+\.\d+\.\d+', args.revision_tag)
    assert re.fullmatch(r'[0-9a-f]{64}', args.approved_video_sha)
    baseline = git('rev-parse', args.preservation_base + '^{commit}').decode().strip()
    original = json.loads(git('show', baseline + f':episodes/{SLUG}/meta.json'))
    original_version = json.loads(git('show', baseline + ':site/package.json'))['version']
    meta = read(CANONICAL / 'meta.json')
    for key in IDENTITY:
        assert meta[key] == original[key], f'Existing identity changed: {key}'
    assert meta['updatedAt'] == original['updatedAt'], 'This entry must run once for the existing revision'
    assert meta['draft'] is False and meta['series'] == 'leetcode'
    rendered = read(EP / 'render-result.json')
    publication = rendered['publicationMetadata']
    receipt = read(EP / 'reference-appendix.json')
    media_check = read(EP / 'reference-appendix-media-check.json')
    storyboard = read(EP / 'storyboard.json')
    video_sha = sha(EP / 'video.mp4')
    assert video_sha == args.approved_video_sha == rendered['sha256'] == receipt['outputSHA256'] == media_check['outputSHA256']
    assert (EP / 'video.mp4').stat().st_size == rendered['bytes']
    assert video_sha != hashlib.sha256(git('show', baseline + f':episodes/{SLUG}/video.mp4')).hexdigest()
    frames = publication['finalVideoFrames']
    appendix = publication['referenceAppendix']
    assert isinstance(frames, int) and frames == rendered['frames'] == receipt['finalVideoFrames']
    assert appendix['from'] == storyboard['meta']['durationInFrames'] == receipt['bodyFrames']
    assert appendix['kind'] == 'references' and appendix['durationInFrames'] == 150
    assert appendix['from'] + appendix['durationInFrames'] == frames
    assert media_check['passed'] is True and receipt['presentation'] == 'title-author'
    assert media_check['bodySHA256'] == receipt['inputs']['bodySHA256'] == sha(EP / 'remotion/out/body.mp4')
    assert receipt['inputs']['referencesSHA256'] == sha(EP / 'references.json')
    source_before = sha(EP / 'source-sha256.json')
    for relative, expected in read(EP / 'source-sha256.json').items():
        assert sha(EP / relative) == expected, 'Frozen input changed: ' + relative
    for name in COVERS:
        expected = hashlib.sha256(git('show', baseline + f':episodes/{SLUG}/{name}')).hexdigest()
        assert sha(CANONICAL / name) == sha(EP / name) == expected
    site_package = ROOT / 'site/package.json'
    site_lock = ROOT / 'site/package-lock.json'
    package, lock = read(site_package), read(site_lock)
    assert package['version'] == lock['version'] == lock['packages']['']['version'] == original_version
    previous = version(original_version)
    target_version = args.revision_tag.removeprefix('v')
    assert version(target_version) == (*previous[:2], previous[2] + 1), 'Film correction must use next unoccupied patch version'
    assert subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/tags/' + args.revision_tag], cwd=ROOT).returncode != 0, 'Version tag already exists locally'
    updated_at = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    assert datetime.fromisoformat(updated_at) > datetime.fromisoformat(original['updatedAt'])
    for name in COPIED:
        shutil.copy2(EP / name, CANONICAL / name)
    meta.update(publication)
    meta['summary'] = '从重复向后查找入手，保留等待中的日期；用32度解决30、31度并在35度处停止，推导末尾操作与温度不升后，再引出单调栈。'
    meta['description'] = '先交代每日气温与等待天数，再分析重复查找、保留未解决日期和只检查末尾的依据；从具体推导归纳单调栈，附5秒完整Python与参考资料。'
    meta['updatedAt'] = updated_at
    meta['targetDuration'] = math.floor(frames / storyboard['meta']['fps'] + .5)
    save(CANONICAL / 'meta.json', meta)
    package['version'] = lock['version'] = lock['packages']['']['version'] = target_version
    save(site_package, package)
    save(site_lock, lock)
    assert source_before == sha(EP / 'source-sha256.json')
    report = {'status': 'canonical-integrated-awaiting-local-qa', 'at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
              'revisionTag': args.revision_tag, 'preservationBaseline': baseline, 'frames': frames,
              'bodyFrames': appendix['from'], 'durationSeconds': frames / storyboard['meta']['fps'],
              'videoSHA256': video_sha, 'updatedAt': updated_at,
              'preservedIdentity': {key: meta[key] for key in IDENTITY},
              'copiedFiles': {name: sha(CANONICAL / name) for name in COPIED},
              'unchangedCovers': {name: sha(CANONICAL / name) for name in COVERS},
              'sourceFilesRewritten': False, 'productionRerendered': False,
              'productionFreezeSHA256': source_before, 'sitePreviousVersion': original_version}
    save(OUT / 'integration.json', report)
    print(json.dumps({key: report[key] for key in ['status', 'revisionTag', 'frames', 'bodyFrames', 'videoSHA256', 'updatedAt']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
