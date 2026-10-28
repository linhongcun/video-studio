#!/usr/bin/env python3
"""Build a cover-continuity revision without rewriting historical freezes.

Run from any directory; repository-relative paths are resolved from this file.
The default action prints a plan.  Explicit --freeze, --render and --verify are
separate stages.  --verify changes no production artifacts (temporary full-file
media comparisons may be created by the reference adapter).

    python3 episodes-codex/_shared/puzzles-video/render.py bridge-torch --freeze
    python3 episodes-codex/_shared/puzzles-video/render.py bridge-torch --render
    python3 episodes-codex/_shared/puzzles-video/render.py bridge-torch --verify

The baseline is the exact published MP4 in
work/puzzles-video-style/baseline/<slug>.mp4.  New pictures keep its complete AAC
packet sequence, PTS/DTS/durations and decoded PCM.  Narration, subtitles, timing,
old source-sha256.json and the existing Remotion entry remain historical inputs.
All new outputs stay in revisions/<revision>/ until separately reviewed/installed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPISODES = ('horse-racing', 'bridge-torch', 'water-jug', 'monty-hall', 'egg-drop')
SCHEMA = 1
CHECKER = ROOT / 'site/scripts/check-references.mjs'
SOURCE_SUFFIXES = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.css', '.svg'}
AUDIO_SUFFIXES = {'.wav', '.mp3', '.aac', '.m4a', '.flac', '.ogg'}
EXTENSIONS = ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.json', '.css', '.svg')


def read(path: Path):
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def run(command, *, cwd=ROOT, capture=False) -> str:
    result = subprocess.run([str(part) for part in command], cwd=cwd,
                            text=True, capture_output=capture)
    if result.returncode:
        detail = (result.stderr or '')[-6000:] if capture else ''
        raise RuntimeError(f'Command failed ({result.returncode}): {command[0]}\n{detail}')
    return result.stdout if capture else ''


def display(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def location(value: str) -> Path:
    path = Path(value)
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def adapter_module():
    spec = importlib.util.spec_from_file_location('puzzles_reference_adapter', HERE / 'references.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def context(args) -> SimpleNamespace:
    directory = ROOT / 'episodes-codex' / args.episode
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.revision):
        raise ValueError('--revision must be a single stable directory name')
    revision = directory / 'revisions' / args.revision
    remotion = directory / 'remotion'
    entry = (remotion / args.entry).resolve()
    if not entry.is_relative_to(remotion / 'src/cover-continuity'):
        raise ValueError('Choose an entry under this episode\'s src/cover-continuity/')
    return SimpleNamespace(
        slug=args.episode, directory=directory, remotion=remotion, revision=revision,
        entry=entry, composition=args.composition,
        manifest=revision / 'source-sha256.json', identity=revision / 'baseline-publication.json',
        baseline=location(args.baseline) if args.baseline else
            ROOT / 'work/puzzles-video-style/baseline' / f'{args.episode}.mp4',
        silent=revision / 'silent-body.mp4', body=revision / 'body.mp4',
        output=revision / 'video.mp4', references=directory / 'references.json',
        artifacts=revision / 'references', result=revision / 'render-result.json',
        audio_report=revision / 'baseline-audio-check.json',
    )


def expected_timeline(ctx) -> dict:
    storyboard = read(ctx.directory / 'storyboard.json')
    frames = sum(shot['durationInFrames'] for scene in storyboard['scenes'] for shot in scene['shots'])
    if not isinstance(frames, int) or frames < 1:
        raise ValueError('Storyboard must describe a positive integer body timeline')
    return {'width': 1920, 'height': 1080, 'fps': 30, 'bodyFrames': frames}


def source_preflight(ctx) -> None:
    # This checks recorded source evidence, not a new reading of those sources.
    run(['node', CHECKER, '--sources', ctx.directory])


def publication_identity(ctx, timeline) -> dict:
    publication = ROOT / 'episodes' / ctx.slug
    meta, receipt = read(publication / 'meta.json'), read(publication / 'reference-appendix.json')
    if meta['slug'] != ctx.slug or receipt['episode'] != ctx.slug:
        raise ValueError('Baseline publication belongs to a different episode')
    if receipt['outputSHA256'] != digest(ctx.baseline):
        raise ValueError('Baseline MP4 SHA differs from the current published receipt')
    if receipt['bodyFrames'] != timeline['bodyFrames'] or meta['referenceAppendix']['from'] != timeline['bodyFrames']:
        raise ValueError('Current storyboard and published baseline body boundary differ')
    if receipt['inputs']['referencesSHA256'] != digest(ctx.references):
        raise ValueError('Current reference source identity differs from baseline publication')
    return {'recordedAtUTC': datetime.now(timezone.utc).isoformat(),
            'baselineCommit': run(['git', 'rev-parse', 'HEAD'], capture=True).strip(),
            'baselinePath': display(ctx.baseline), 'baselineSHA256': digest(ctx.baseline),
            'publishedMetadata': meta, 'publishedReferenceReceipt': receipt,
            'scope': 'Published input identities captured before replacement. No old validation result is reassigned to new pictures.'}


def local_imports(path: Path) -> list[str]:
    if path.suffix not in {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}:
        return []
    text = path.read_text()
    patterns = (r'\b(?:import|export)\s+(?:type\s+)?[^;]*?\bfrom\s*[\'\"]([^\'\"]+)[\'\"]',
                r'(?:^|[;\n])\s*import\s*[\'\"]([^\'\"]+)[\'\"]',
                r'\b(?:import|require)\s*\(\s*[\'\"]([^\'\"]+)[\'\"]')
    return [match for pattern in patterns for match in re.findall(pattern, text)]


def resolve_import(importer: Path, value: str, ctx) -> Path | None:
    aliases = {'@storyboard': ctx.directory / 'storyboard.json', '@covers': ctx.directory / 'covers.json'}
    if value in aliases:
        candidate = aliases[value]
    elif value.startswith('.'):
        candidate = importer.parent / value
    else:
        # npm dependencies are pinned by package-lock.json, not local source files.
        return None
    choices = [candidate] if candidate.suffix else [candidate, *[Path(str(candidate) + ext) for ext in EXTENSIONS],
                                                   *[candidate / ('index' + ext) for ext in EXTENSIONS]]
    for choice in choices:
        if choice.is_file():
            resolved = choice.resolve()
            if not resolved.is_relative_to(ROOT):
                raise ValueError(f'Local source import escapes repository: {importer}: {value}')
            return resolved
    raise ValueError(f'Missing actual local import: {display(importer)} -> {value}')


def production_inputs(ctx, adapter) -> list[Path]:
    if not ctx.entry.is_file():
        raise ValueError(f'Missing new visual entry: {display(ctx.entry)}')
    required = [Path(__file__).resolve(), *adapter.dependency_files(), CHECKER,
                CHECKER.with_name('reference-legacy.json'),
                HERE.parent / 'requirements-reference-appendix.txt', ctx.identity]
    # Preserve the old freeze itself as historical evidence.  Its old voice-take
    # paths are not claims about newly consumed inputs: audio comes from baseline MP4.
    required += [ctx.directory / name for name in
                 ('source-sha256.json', 'storyboard.json', 'covers.json', 'words.json',
                  'script.md', 'article.mdx', 'references.json')]
    required += [ctx.remotion / name for name in
                 ('package.json', 'package-lock.json', 'remotion.config.ts', 'tsconfig.json')]
    # Original and new visual sources are retained together; closure traversal
    # below also follows reused models and shared modules outside the episode.
    required += [path for path in (ctx.remotion / 'src').rglob('*')
                 if path.is_file() and path.suffix in SOURCE_SUFFIXES]
    required += [path for path in HERE.iterdir() if path.is_file() and path.suffix in SOURCE_SUFFIXES]
    public = ctx.remotion / 'public'
    if public.is_dir():
        required += [path for path in public.rglob('*') if path.is_file()
                     and path.suffix.lower() not in AUDIO_SUFFIXES]
    refs = read(ctx.references)
    for source in refs['sources']:
        for field in ('verification', 'titleEvidence', 'quotation'):
            evidence = source.get(field, {}).get('evidence')
            if evidence:
                required.append(ROOT / evidence)
    pending, found = list(required), set()
    while pending:
        path = pending.pop().resolve()
        if path in found:
            continue
        if not path.is_file():
            raise ValueError(f'Missing production input: {display(path)}')
        if not path.is_relative_to(ROOT):
            raise ValueError(f'Production source outside repository: {path}')
        found.add(path)
        for value in local_imports(path):
            imported = resolve_import(path, value, ctx)
            if imported:
                pending.append(imported)
    return sorted(found)


def render_command(ctx, timeline) -> list[str]:
    # Commands are frozen relative to their recorded repository-local cwd, so
    # checking out the same revision elsewhere does not change their identity.
    return ['node_modules/.bin/remotion', 'render', str(ctx.entry.relative_to(ctx.remotion)),
            ctx.composition, str(Path('..') / ctx.silent.relative_to(ctx.directory)),
            '--codec=h264', '--crf=20', '--concurrency=2', '--muted',
            f'--frames=0-{timeline["bodyFrames"] - 1}',
            '--browser-executable=/usr/bin/chromium', '--bundle-cache=false']


def freeze(ctx, adapter) -> dict:
    source_preflight(ctx)
    if ctx.manifest.exists():
        manifest = verify_inputs(ctx)
        return {'status': 'already-frozen', 'manifest': display(ctx.manifest),
                'inputCount': len(manifest['inputs'])}
    if any(path.exists() for path in (ctx.silent, ctx.body, ctx.output, ctx.result)):
        raise ValueError('Revision already has media without a manifest; preserve it and choose a fresh --revision')
    timeline = expected_timeline(ctx)
    identity = publication_identity(ctx, timeline)
    if ctx.identity.exists() and read(ctx.identity).get('baselineSHA256') != identity['baselineSHA256']:
        raise ValueError('Existing baseline snapshot differs; choose a fresh revision')
    if not ctx.identity.exists():
        write(ctx.identity, identity)
    inputs = production_inputs(ctx, adapter)
    fonts = [adapter.DEFAULT_FONT, adapter.DEFAULT_BOLD]
    manifest = {'schemaVersion': SCHEMA, 'episode': ctx.slug,
                'createdAtUTC': datetime.now(timezone.utc).isoformat(),
                'timeline': timeline, 'entry': display(ctx.entry), 'composition': ctx.composition,
                'baseline': {'path': display(ctx.baseline), 'sha256': digest(ctx.baseline)},
                'inputs': {display(path): digest(path) for path in inputs},
                'externalInputs': {str(path): digest(path) for path in fonts},
                'renderCommand': render_command(ctx, timeline),
                'renderWorkingDirectory': display(ctx.remotion),
                'audioPolicy': 'Render muted pictures, then copy the complete published baseline AAC; require packet/timing and decoded PCM identity.',
                'historicalFreezePolicy': 'Original source-sha256.json is retained, never rewritten or used to claim new pictures were previously encoded.'}
    write(ctx.manifest, manifest)
    verify_inputs(ctx)
    return {'status': 'frozen', 'manifest': display(ctx.manifest), 'inputCount': len(inputs),
            'bodyFrames': timeline['bodyFrames']}


def verify_inputs(ctx) -> dict:
    manifest = read(ctx.manifest)
    if manifest.get('schemaVersion') != SCHEMA or manifest.get('episode') != ctx.slug:
        raise ValueError('New revision manifest schema/episode differs')
    if manifest['entry'] != display(ctx.entry) or manifest['composition'] != ctx.composition:
        raise ValueError('CLI entry/composition differs from the frozen new revision')
    if manifest['timeline'] != expected_timeline(ctx):
        raise ValueError('Frozen storyboard timeline changed')
    for name, expected in {**manifest['inputs'], **manifest['externalInputs']}.items():
        path = location(name)
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f'New revision input changed: {name}')
    baseline = manifest['baseline']
    if location(baseline['path']) != ctx.baseline.resolve() or digest(ctx.baseline) != baseline['sha256']:
        raise ValueError('Published baseline audio input changed')
    if manifest['renderCommand'] != render_command(ctx, manifest['timeline']):
        raise ValueError('Frozen render command differs')
    return manifest


def audio_identity(adapter, before: Path, after: Path) -> dict:
    engine = adapter.engine
    left, right = engine.audio_packets(before), engine.audio_packets(after)
    if left != right:
        raise ValueError('AAC packet payload or PTS/DTS/duration changed')
    pcm_before, pcm_after = engine.audio_hash(before), engine.audio_hash(after)
    if pcm_before != pcm_after:
        raise ValueError('Decoded baseline PCM changed')
    return {'passed': True, 'baselineSHA256': digest(before), 'bodySHA256': digest(after),
            'audioPacketCount': len(left),
            'audioPacketPayloadAndTimingSHA256': engine.sequence_hash(left),
            'audioPacketsAndTimingEqual': True, 'decodedAudioPCM': pcm_after,
            'scope': 'Complete baseline AAC packets, PTS/DTS/duration and decoded PCM; no TTS or remix.'}


def media_shape(adapter, path: Path, timeline: dict, expected_frames: int) -> dict:
    info = adapter.engine.probe(path)
    video = adapter.engine.stream(info, 'video')
    if (video['codec_name'] != 'h264' or int(video['width']) != timeline['width']
            or int(video['height']) != timeline['height']
            or Fraction(video['r_frame_rate']) != timeline['fps']
            or Fraction(video['avg_frame_rate']) != timeline['fps']
            or int(video.get('nb_frames', -1)) != expected_frames):
        raise ValueError(f'Actual media format/frame count differs: {display(path)}')
    return info


def adapter_args(ctx, adapter):
    return SimpleNamespace(body=ctx.body, references=ctx.references, output=ctx.output,
                           artifacts=ctx.artifacts, seconds=5,
                           font=adapter.DEFAULT_FONT, bold_font=adapter.DEFAULT_BOLD)


def render(ctx, adapter) -> dict:
    source_preflight(ctx)
    manifest = verify_inputs(ctx)
    if ctx.output.exists():
        raise ValueError('Final revision media already exists; use --verify or choose a fresh revision')
    if not (ctx.remotion / manifest['renderCommand'][0]).is_file():
        raise ValueError('Install this episode\'s exact lock with npm ci before rendering')
    timeline = manifest['timeline']
    baseline_info = media_shape(adapter, ctx.baseline, timeline,
                                read(ctx.identity)['publishedMetadata']['finalVideoFrames'])
    baseline_audio = adapter.engine.stream(baseline_info, 'audio')
    if baseline_audio['codec_name'] != 'aac' or float(baseline_audio.get('start_time', 0)) != 0:
        raise ValueError('Expected published AAC starting at zero')
    # Do not trim/re-encode packets.  Existing bibliography baselines have no
    # added audio; their original AAC endpoint may extend less than one frame.
    if float(baseline_audio['duration']) > timeline['bodyFrames'] / timeline['fps'] + 1 / timeline['fps']:
        raise ValueError('Baseline has audio beyond its original body boundary; explicit review required')
    run(manifest['renderCommand'], cwd=ctx.remotion)
    verify_inputs(ctx)
    media_shape(adapter, ctx.silent, timeline, timeline['bodyFrames'])
    if any(stream['codec_type'] == 'audio' for stream in adapter.engine.probe(ctx.silent)['streams']):
        raise ValueError('Muted render unexpectedly contains an audio stream')
    run(['ffmpeg', '-v', 'error', '-y', '-i', ctx.silent, '-i', ctx.baseline,
         '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-map_metadata', '-1',
         '-metadata', f'comment=video-studio-puzzles-continuity-body:v1:{ctx.slug}',
         '-movflags', '+faststart', ctx.body])
    media_shape(adapter, ctx.body, timeline, timeline['bodyFrames'])
    audio = audio_identity(adapter, ctx.baseline, ctx.body)
    write(ctx.audio_report, audio)
    receipt = adapter.append(adapter_args(ctx, adapter))
    verify_inputs(ctx)
    publication = {'finalVideoFrames': receipt['finalVideoFrames'],
                   'referenceAppendix': {'kind': 'references', 'from': receipt['bodyFrames'],
                       'durationInFrames': receipt['appendix']['durationInFrames'],
                       'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    info = media_shape(adapter, ctx.output, timeline, receipt['finalVideoFrames'])
    result = {'visualRevision': 'cover-continuity-v1',
              'createdAtUTC': datetime.now(timezone.utc).isoformat(),
              'episode': ctx.slug, 'width': timeline['width'], 'height': timeline['height'],
              'fps': '30/1', 'frames': receipt['finalVideoFrames'],
              'seconds': receipt['durationSeconds'], 'bytes': ctx.output.stat().st_size,
              'sha256': digest(ctx.output), 'bodyFrames': timeline['bodyFrames'],
              'audio': adapter.engine.stream(info, 'audio')['codec_name'],
              'audioSampleRate': int(adapter.engine.stream(info, 'audio')['sample_rate']),
              **publication, 'publicationMetadata': publication,
              'presentation': 'title-author', 'bibliographyOnly': True,
              'newProductionManifest': display(ctx.manifest),
              'newProductionManifestSHA256': digest(ctx.manifest),
              'sourceInputsVerified': len(manifest['inputs']),
              'baselineAudioPreserved': audio,
              'bodyProvenance': 'New muted pictures were rendered from the independent cover-continuity manifest. The complete baseline AAC was stream copied; original timing and historical source freezes remain unchanged.',
              'loudnessBasis': 'Complete AAC packet/timing and decoded PCM identity to published baseline; no remix or new audio packets.',
              'reviewScope': 'Input identities, media format, complete baseline audio identity and full appendix stream preservation. Independent visual/motion, actual player and publication review are separate checks.'}
    write(ctx.result, result)
    for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
        shutil.copyfile(ctx.artifacts / name, ctx.revision / name)
    return {'status': 'rendered', 'result': display(ctx.result), **publication,
            'sha256': result['sha256']}


def verify(ctx, adapter) -> dict:
    source_preflight(ctx)
    manifest = verify_inputs(ctx)
    receipt = read(ctx.artifacts / 'reference-appendix.json')
    result = read(ctx.result)
    if result.get('newProductionManifestSHA256') != digest(ctx.manifest):
        raise ValueError('Final result was recorded against a different new revision manifest')
    media_shape(adapter, ctx.body, manifest['timeline'], manifest['timeline']['bodyFrames'])
    media_shape(adapter, ctx.output, manifest['timeline'], receipt['finalVideoFrames'])
    audio = audio_identity(adapter, ctx.baseline, ctx.body)
    if read(ctx.audio_report) != audio or result.get('baselineAudioPreserved') != audio:
        raise ValueError('Recorded baseline audio report differs from actual media')
    adapter.verify(adapter_args(ctx, adapter))
    for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
        if read(ctx.artifacts / name) != read(ctx.revision / name):
            raise ValueError(f'Revision delivery copy differs: {name}')
    publication = {'finalVideoFrames': receipt['finalVideoFrames'],
                   'referenceAppendix': {'kind': 'references', 'from': receipt['bodyFrames'],
                       'durationInFrames': receipt['appendix']['durationInFrames'],
                       'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    if (result['sha256'] != digest(ctx.output) or result['sha256'] != receipt['outputSHA256']
            or result['bytes'] != ctx.output.stat().st_size
            or result['frames'] != receipt['finalVideoFrames']
            or result['bodyFrames'] != receipt['bodyFrames']
            or result['seconds'] != receipt['durationSeconds']
            or result['publicationMetadata'] != publication
            or any(result.get(key) != value for key, value in publication.items())):
        raise ValueError('Recorded final metadata differs from verified production media')
    return {'status': 'verified-read-only', 'episode': ctx.slug, 'sha256': result['sha256'],
            'inputCount': len(manifest['inputs']), **publication}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode', choices=EPISODES)
    stages = parser.add_mutually_exclusive_group()
    stages.add_argument('--freeze', action='store_true')
    stages.add_argument('--render', action='store_true')
    stages.add_argument('--verify', action='store_true')
    parser.add_argument('--revision', default='cover-continuity')
    parser.add_argument('--baseline', help='Exact published baseline MP4; default work/puzzles-video-style/baseline/<slug>.mp4')
    parser.add_argument('--entry', default='src/cover-continuity/index.ts')
    parser.add_argument('--composition', default='Main')
    args = parser.parse_args()
    ctx, adapter = context(args), adapter_module()
    if args.freeze:
        result = freeze(ctx, adapter)
    elif args.render:
        result = render(ctx, adapter)
    elif args.verify:
        result = verify(ctx, adapter)
    else:
        timeline = expected_timeline(ctx)
        result = {'status': 'plan-only', 'episode': ctx.slug,
                  'timeline': timeline, 'baseline': display(ctx.baseline),
                  'revision': display(ctx.revision), 'renderCommand': render_command(ctx, timeline),
                  'next': 'Finish source/motion preflight, then --freeze; render and independent final/player review follow.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
