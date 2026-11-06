#!/usr/bin/env python3
"""Prepare P09 publication from the independently reviewed clarity revision.

Default prints a plan. --apply stages local publication files and a patch version;
this script never commits, pushes, creates a Release or deploys the site.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

SLUG = 'pirate-gold'
REVISION = Path('episodes/puzzles/pirate-gold/production/revisions/clarity-20261106/pirate-gold')
PUBLICATION = Path('episodes/puzzles/pirate-gold/publication')
FIGURES = {'01.jpg': 3000, '02.jpg': 4365}
SCRIPT_NOTE = ('> 本页为2026-11-06站点派生稿：旁白与原配音逐字相同，画面说明同步本轮分镜。原配音冻结脚本及完整SHA保存在本次独立修订的 `input-provenance.json`；此派生不改写历史配音输入。修订目录：`' + str(REVISION) + '`。\n\n')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(command, *, cwd, capture=False, check=True):
    result = subprocess.run([str(x) for x in command], cwd=cwd,
                            text=True, capture_output=capture)
    if check and result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {command[0]}\n'
                           + ((result.stderr or '')[-3000:] if capture else ''))
    return result


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def extract_figures(root, revision, publication, stage):
    source = revision / 'video.mp4'
    video = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                           '-show_streams', '-of', 'json', source], cwd=root,
                          capture=True).stdout)['streams'][0]
    assert video.get('color_range') == 'tv' and video.get('color_space') == 'bt709'
    article = publication / 'article.mdx'
    found = re.findall(r'<Figure\s+src="/video-studio/episodes/pirate-gold/article/([^"/]+)"[^>]*seekTo=\{([0-9.]+)\}', article.read_text())
    assert len(found) == 2, 'Expected both existing article Figure slots'
    rows = []
    target_dir = stage / 'article'
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, seconds in found:
        frame = Fraction(seconds) * 30
        assert frame.denominator == 1 and FIGURES.get(filename) == int(frame)
        assert 0 <= frame < int(video['nb_frames'])
        target = target_dir / filename
        # Exact original export-article.py matrix and integer frame selection:
        filt = (f'select=eq(n\\,{int(frame)}),scale=in_range=tv:out_range=pc:'
                'in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p')
        command = ['ffmpeg', '-v', 'error', '-y', '-i', source, '-vf', filt,
                   '-frames:v', '1', '-q:v', '2', target]
        run(command, cwd=root)
        assert target.is_file() and target.stat().st_size > 1000
        previous = publication / 'article' / filename
        rows.append({'filename': filename, 'timeSeconds': seconds, 'frame': int(frame),
                     'oldSHA256': sha(previous), 'sha256': sha(target),
                     'bytes': target.stat().st_size, 'command': [str(x) for x in command]})
    original_exporter = root / 'episodes/puzzles/pirate-gold/production/export-article.py'
    return {'sourceSHA256': sha(source), 'articleSHA256': sha(article),
            'exporterReference': str(original_exporter.relative_to(root)),
            'exporterReferenceSHA256': sha(original_exporter),
            'frameSelection': 'Decode from frame zero and select exact integer n; no approximate seek.',
            'colorOperation': 'Actual limited BT.709 to full-range BT.601 JPEG pixel conversion, not relabeling.',
            'figures': rows, 'visualReviewSeparate': True}


def validate_inputs(root, revision):
    required = ['video.mp4', 'render-result.json', 'reference-appendix.json',
                'reference-appendix-media-check.json', 'source-sha256.json',
                'storyboard.json', 'script.md', 'references.json', 'input-provenance.json']
    for name in required:
        assert (revision / name).is_file(), f'Missing actual rendered revision input: {name}'
    run(['python3', revision / 'freeze.py', '--verify'], cwd=root)
    run(['python3', revision / 'verify.py', '--final'], cwd=root)
    result = read(revision / 'render-result.json')
    receipt = read(revision / 'reference-appendix.json')
    media = read(revision / 'reference-appendix-media-check.json')
    digest = sha(revision / 'video.mp4')
    assert digest == result['sha256'] == receipt['outputSHA256'] == media['outputSHA256']
    assert media.get('passed') is True
    metadata = result['publicationMetadata']
    assert result['frames'] == receipt['finalVideoFrames'] == metadata['finalVideoFrames']
    assert metadata['referenceAppendix']['from'] == receipt['bodyFrames']
    assert receipt['bodyFrames'] == 4801 and receipt['finalVideoFrames'] == 4951
    provenance = read(revision / 'input-provenance.json')
    original = root / provenance['baselineProduction']
    assert sha(revision / 'script.md') == sha(original / 'script.md'), 'Narration script identity must stay original'
    assert sha(revision / 'voice.wav') == provenance['unchangedAudioSha256'] == sha(original / 'voice.wav')
    return result, receipt, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('/workspace/video-studio'))
    parser.add_argument('--version', default='0.105.1')
    parser.add_argument('--expected-main', help='Freshly inspected origin/main SHA; required with --apply')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    root = args.repo.resolve()
    revision, publication = root / REVISION, root / PUBLICATION
    if not args.apply:
        print(json.dumps({'action': 'plan-only', 'revision': str(revision),
                          'publication': str(publication), 'proposedVersion': args.version,
                          'preserve': ['createdAt', 'publishedAt', 'firstRelease', 'covers', 'article.mdx body'],
                          'figureFrames': FIGURES,
                          'applyRequires': 'Fresh --expected-main after reviewing upstream changes; completed independent visual/media QA remains the producer responsibility.',
                          'publishes': False}, ensure_ascii=False, indent=2))
        return
    assert args.expected_main, '--apply requires the freshly reviewed --expected-main SHA'
    run(['git', 'fetch', 'origin', 'main'], cwd=root)
    latest = run(['git', 'rev-parse', 'origin/main'], cwd=root, capture=True).stdout.strip()
    assert latest == args.expected_main, 'Upstream changed: inspect/integrate new main before staging'
    run(['git', 'merge-base', '--is-ancestor', latest, 'HEAD'], cwd=root)
    package_path, lock_path = root / 'site/package.json', root / 'site/package-lock.json'
    package, lock = read(package_path), read(lock_path)
    old_parts = [int(x) for x in package['version'].split('.')]
    desired = '.'.join(map(str, [old_parts[0], old_parts[1], old_parts[2] + 1]))
    assert args.version == desired, f'Patch version must follow current package version: {desired}'
    tag = run(['git', 'ls-remote', '--exit-code', '--tags', 'origin', 'refs/tags/v' + args.version],
              cwd=root, capture=True, check=False)
    assert tag.returncode == 2, 'Proposed version tag exists or remote version check failed'
    result, receipt, provenance = validate_inputs(root, revision)
    before_meta = read(publication / 'meta.json')
    assert before_meta['slug'] == SLUG
    before_article = sha(publication / 'article.mdx')
    cover_names = ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', 'poster.jpg', 'cover-style.json']
    cover_sha = {name: sha(publication / name) for name in cover_names}
    updated = datetime.now(ZoneInfo('Asia/Shanghai')).replace(microsecond=0).isoformat()
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%dT%H%M%S')
    stage = Path(__file__).resolve().parent / ('publication-stage-' + stamp)
    stage.mkdir(parents=True, exist_ok=False)
    before = {str(p.relative_to(publication)): sha(p) for p in publication.rglob('*') if p.is_file()}
    dump(stage / 'before.json', {'meta': before_meta, 'sha256': before})
    figure_report = extract_figures(root, revision, publication, stage)
    copies = ['video.mp4', 'storyboard.json', 'references.json', 'reference-appendix.json',
              'reference-appendix-media-check.json', 'research.md', 'research-evidence.json']
    for name in copies:
        shutil.copy2(revision / name, publication / name)
    # The source script stays byte-identical to the original measured narration.
    # Publish a clearly identified derivative note instead of implying that old
    # visual directions are the implementation of the new animation.
    original_script = (revision / 'script.md').read_text()
    directions = [s['direction'] for scene in read(revision / 'storyboard.json')['scenes'] for s in scene['shots']]
    assert len(directions) == len(re.findall(r'(?m)^画面：.*$', original_script)) == 14
    visual_rows = iter(directions)
    derived_script = re.sub(r'(?m)^画面：.*$', lambda m: '画面：' + next(visual_rows), original_script)
    assert re.findall(r'(?m)^旁白：.*$', derived_script) == re.findall(r'(?m)^旁白：.*$', original_script)
    first_line, separator, remainder = derived_script.partition('\n')
    (publication / 'script.md').write_text(first_line + '\n\n' + SCRIPT_NOTE + remainder)
    for row in figure_report['figures']:
        shutil.copy2(stage / 'article' / row['filename'], publication / 'article' / row['filename'])
    meta = dict(before_meta)
    meta.update(result['publicationMetadata'])
    meta.update(sourcePath=str(REVISION / 'remotion'), updatedAt=updated,
                targetDuration=result['seconds'], burnedInCaptions=True)
    dump(publication / 'meta.json', meta)
    package['version'] = lock['version'] = lock['packages']['']['version'] = args.version
    dump(package_path, package)
    dump(lock_path, lock)
    assert sha(publication / 'article.mdx') == before_article, 'Article body must remain byte-identical'
    assert all(sha(publication / name) == digest for name, digest in cover_sha.items())
    for field in ('createdAt', 'publishedAt', 'firstRelease'):
        assert meta.get(field) == before_meta.get(field), f'Historical {field} changed'
    after = {str(p.relative_to(publication)): sha(p) for p in publication.rglob('*') if p.is_file()}
    report = {'stagedAt': updated, 'status': 'local-publication-staged', 'deployed': False,
              'version': args.version, 'upstreamSHA': latest,
              'revision': str(REVISION), 'sourceManifestSHA256': sha(revision / 'source-sha256.json'),
              'videoSHA256': result['sha256'], 'before': before, 'after': after,
              'preservedMetadata': {k: meta.get(k) for k in ('createdAt', 'publishedAt', 'firstRelease')},
              'preservedCovers': cover_sha, 'articleBodyUnchangedSHA256': before_article,
              'narrationScript': {'identity': 'Original measured narration script reused byte-for-byte in production; publication preserves every narration line and updates visual descriptions from the revised storyboard with a derivative status note.',
                                  'sourceSHA256': sha(revision / 'script.md'),
                                  'publicationSHA256': sha(publication / 'script.md')},
              'figures': figure_report,
              'reviewScope': 'This stages verified inputs, exact-frame article images and metadata. It does not replace actual image/player review, perform a release or claim user acceptance.'}
    dump(stage / 'publication-stage.json', report)
    dump(revision / 'qa/publication-stage.json', report)
    dump(revision / 'qa/article-image-export.json', figure_report)
    run(['npm', '--prefix', 'site', 'run', 'check:references'], cwd=root)
    run(['npm', '--prefix', 'site', 'run', 'check:articles'], cwd=root)
    print(json.dumps({'staged': True, 'deployed': False, 'version': args.version,
                      'report': str(revision / 'qa/publication-stage.json'),
                      'updatedAt': updated, 'videoSHA256': result['sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
