#!/usr/bin/env python3
"""New-episode render entry: checked sources -> frozen body -> references.

The episode's render:body script must write remotion/out/body.mp4, including
any existing code card. This wrapper never edits narration, timing or metadata.
It uses the unchanged appendix renderer and emits a publication metadata patch
in render-result.json. Independent source and visual review remain required.

  python3 episodes-codex/_shared/render_with_references.py episodes-codex/SLUG
  python3 episodes-codex/_shared/render_with_references.py episodes-codex/SLUG --verify
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
APPENDER = ROOT / 'episodes-codex/_shared/append_references.py'
CHECKER = ROOT / 'site/scripts/check-references.mjs'
BODY_GUARD = 'VIDEO_STUDIO_REFERENCE_BODY_RENDER'


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def verify_freeze(directory: Path) -> None:
    """Read the real manifest; never regenerate it to bless changed inputs."""
    manifest = read(directory / 'source-sha256.json')
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError('Missing nonempty source-sha256.json; freeze production inputs first')
    paths = {}
    for relative, expected in manifest.items():
        path = (directory / relative).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError(f'Frozen input outside repository: {relative}')
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f'Frozen input changed: {relative}')
        paths[path] = expected
    required = [directory / 'references.json', directory / 'article.mdx',
                directory / 'remotion/package.json', Path(__file__).resolve(), APPENDER, CHECKER,
                APPENDER.with_name('requirements-reference-appendix.txt'),
                ROOT / 'episodes/_shared/theme/pageTheme.ts']
    references = read(directory / 'references.json')
    required += [ROOT / source['verification']['evidence'] for source in references['sources']]
    missing = [str(p.relative_to(ROOT)) for p in required if p.resolve() not in paths]
    if missing:
        raise ValueError('Freeze reference production inputs before rendering: ' + ', '.join(missing))
    outputs = [directory / name for name in ('video.mp4', 'render-result.json',
               'reference-appendix.json', 'reference-appendix-media-check.json')]
    outputs.append(directory / 'remotion/out/body.mp4')
    if any(p.resolve() in paths for p in outputs):
        raise ValueError('Rendered outputs must not be included in the production-input freeze')


def run(directory: Path, verify_only: bool = False) -> dict:
    directory = directory.resolve()
    if not directory.is_relative_to(ROOT / 'episodes-codex'):
        raise ValueError('Choose an episodes-codex production directory')
    if not verify_only and os.environ.get(BODY_GUARD):
        raise ValueError('Recursive render:body: it must not invoke render or render_with_references.py')
    subprocess.run(['node', str(CHECKER), '--sources', str(directory)], cwd=ROOT, check=True)
    verify_freeze(directory)
    # Check Python/font/codec dependencies before starting an expensive body render.
    spec = importlib.util.spec_from_file_location('reference_appendix_renderer', APPENDER)
    appender = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(appender)
    for executable in ('ffmpeg', 'ffprobe', 'npm'):
        if not shutil.which(executable):
            raise ValueError(f'Missing production executable: {executable}')
    for font in (appender.DEFAULT_FONT, appender.DEFAULT_BOLD):
        if not font.is_file():
            raise ValueError(f'Missing reference-card font: {font}')
    args = SimpleNamespace(body=directory / 'remotion/out/body.mp4',
                           references=directory / 'references.json',
                           output=directory / 'video.mp4',
                           artifacts=directory / 'revisions/reference-endcards',
                           seconds=5, font=appender.DEFAULT_FONT, bold_font=appender.DEFAULT_BOLD)
    if verify_only:
        report = appender.verify(args)
        verify_delivery(directory, read(args.artifacts / 'reference-appendix.json'), report)
        return report
    package = read(directory / 'remotion/package.json')
    if not package.get('scripts', {}).get('render:body', '').strip():
        raise ValueError('Define render:body to render/mix the complete body into out/body.mp4')
    args.body.parent.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, **{BODY_GUARD: str(directory)})
    subprocess.run(['npm', 'run', 'render:body'], cwd=directory / 'remotion', env=environment, check=True)
    verify_freeze(directory)
    if not args.body.is_file():
        raise ValueError('render:body did not produce remotion/out/body.mp4')
    appender.append(args)
    verify_freeze(directory)
    receipt = read(args.artifacts / 'reference-appendix.json')
    for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
        shutil.copyfile(args.artifacts / name, directory / name)
    publication = {'finalVideoFrames': receipt['finalVideoFrames'],
                   'referenceAppendix': {'kind': 'references', 'from': receipt['bodyFrames'],
                       'durationInFrames': receipt['appendix']['durationInFrames'],
                       'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    result_path = directory / 'render-result.json'
    result = read(result_path) if result_path.exists() else {}
    result.update(frames=receipt['finalVideoFrames'], seconds=receipt['durationSeconds'],
                  sha256=receipt['outputSHA256'], bytes=args.output.stat().st_size,
                  bodyFrames=receipt['bodyFrames'], **publication,
                  publicationMetadata=publication,
                  reviewScope='Automatic stream preservation and full decode passed; source meaning, visual legibility and player review are separate required checks.')
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return {'status': 'rendered-with-references', **publication, 'sha256': receipt['outputSHA256']}


def verify_delivery(directory: Path, receipt: dict, report: dict) -> None:
    """Check the files copied for publication without rewriting stale metadata."""
    if read(directory / 'reference-appendix.json') != receipt:
        raise ValueError('Publication appendix receipt differs from verified production receipt')
    media = read(directory / 'reference-appendix-media-check.json')
    fields = ('bodySHA256', 'outputSHA256', 'bodyFrames', 'appendedFrames', 'finalFrames',
              'bodyDecodedFramesAndTimestampsEqual', 'outputVideoTimelineContinuous',
              'audioPacketsAndTimingEqual', 'bodyFrameMD5RowsSHA256',
              'audioPacketPayloadAndTimingSHA256', 'decodedAudioPCM')
    if media.get('passed') is not True or any(media.get(key) != report.get(key) for key in fields):
        raise ValueError('Publication media-check receipt differs from verified final media')
    result = read(directory / 'render-result.json')
    publication = {'finalVideoFrames': receipt['finalVideoFrames'],
                   'referenceAppendix': {'kind': 'references', 'from': receipt['bodyFrames'],
                       'durationInFrames': receipt['appendix']['durationInFrames'],
                       'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    if (result.get('sha256') != receipt['outputSHA256']
            or result.get('frames') != receipt['finalVideoFrames']
            or result.get('bodyFrames') != receipt['bodyFrames']
            or result.get('seconds') != receipt['durationSeconds']
            or result.get('bytes') != (directory / 'video.mp4').stat().st_size
            or result.get('publicationMetadata') != publication
            or any(result.get(key) != value for key, value in publication.items())):
        raise ValueError('render-result.json publication metadata differs from verified final media')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode', type=Path)
    parser.add_argument('--verify', action='store_true',
                        help='Verify frozen inputs and final media; writes only the media-check report')
    args = parser.parse_args()
    print(json.dumps(run(args.episode, args.verify), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
