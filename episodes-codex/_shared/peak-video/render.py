#!/usr/bin/env python3
"""Build independently frozen peak-series visual revisions using the proven media core.

Only this private function namespace is adapted. The puzzles renderer and every
historical source/freezer remain unchanged. The baseline MP4 is the complete
published AAC input; all packets, timestamps and decoded PCM must be identical.

python3 episodes-codex/_shared/peak-video/render.py rate-limit --freeze
python3 episodes-codex/_shared/peak-video/render.py rate-limit --render
python3 episodes-codex/_shared/peak-video/render.py rate-limit --verify
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import subprocess
from types import FunctionType, SimpleNamespace
from datetime import datetime, timezone
from fractions import Fraction
import shutil

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIBRARY = HERE.parent / 'puzzles-video/render.py'
EPISODES = ('rate-limit', 'idempotency', 'circuit-breaker', 'degradation')
BODY_FRAMES = {'rate-limit': 3271, 'idempotency': 2998, 'circuit-breaker': 2926, 'degradation': 3134}
_spec = importlib.util.spec_from_file_location('frozen_visual_revision_core', LIBRARY)
_library = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_library)

# Each cloned function sees this same private namespace, including the adapted
# context/dependency functions below. No globals in the loaded library change.
_scope = dict(vars(_library), __file__=str(Path(__file__).resolve()),
              HERE=HERE, ROOT=ROOT, EPISODES=EPISODES)
for _name, _value in vars(_library).items():
    if isinstance(_value, FunctionType) and _value.__module__ == _library.__name__:
        _scope[_name] = FunctionType(_value.__code__, _scope, _value.__name__,
                                     _value.__defaults__, _value.__closure__)
_base = {name: _scope[name] for name in ('production_inputs', 'render', 'run', 'expected_timeline', 'write', 'verify_inputs')}
_base_verify = _scope['verify']


def context(args):
    directory = ROOT / 'episodes-codex' / args.episode
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.revision):
        raise ValueError('--revision must be a single stable directory name')
    revision = ROOT / 'episodes-codex' / args.episode / 'revisions' / args.revision
    remotion = directory / 'remotion'
    entry = (remotion / args.entry).resolve()
    if not entry.is_relative_to(remotion / 'src/peak-style'):
        raise ValueError('Choose an entry under this episode\'s src/peak-style/')
    return SimpleNamespace(
        slug=args.episode, directory=directory, remotion=remotion,
        revision=revision, entry=entry, composition=args.composition,
        manifest=revision / 'source-sha256.json',
        identity=revision / 'baseline-publication.json',
        baseline=_scope['location'](args.baseline) if args.baseline else
            ROOT / 'work/peak-video-style/baseline' / f'{args.episode}.mp4',
        silent=revision / 'silent-body.mp4', normalized=revision / 'normalized-silent-body.mp4',
        body=revision / 'body.mp4', color_report=revision / 'color-encoding-check.json',
        output=revision / 'video.mp4', references=directory / 'references.json',
        artifacts=revision / 'references', result=revision / 'render-result.json',
        audio_report=revision / 'baseline-audio-check.json',
    )


def font_inputs():
    style = _scope['read'](HERE / 'style-v1.json')
    files, bindings = {}, []
    generic = {'sans-serif', 'serif', 'monospace', 'system-ui', 'cursive', 'fantasy'}
    for role, stack in style['fonts'].items():
        families = [part.strip().strip('"\'') for part in stack.split(',')]
        families = [name for name in families if name not in generic]
        if not families:
            raise ValueError(f'No explicit reproducible font family for {role}')
        for index, family in enumerate(families):
            for weight in ('regular', 'bold'):
                result = subprocess.check_output(
                    ['fc-match', '-f', '%{family}\n%{style}\n%{file}\n',
                     f'{family}:weight={weight}'], text=True).splitlines()
                if len(result) != 3:
                    raise ValueError(f'Cannot resolve actual {role} font: {family}')
                actual_family, actual_style, filename = result
                path = Path(filename).resolve()
                matched = family.casefold() in [part.strip().casefold()
                                                for part in actual_family.split(',')]
                if index == 0 and not matched:
                    raise ValueError(f'Required {role} font is unavailable: {family} -> {actual_family}')
                if index > 0 and not matched:
                    # CSS skips absent optional families; fontconfig's generic
                    # fallback for that name is not an actual selected input.
                    continue
                if not path.is_file():
                    raise ValueError(f'Missing actual font file: {path}')
                sha = _scope['digest'](path)
                files[str(path)] = sha
                bindings.append({'role': role, 'requestedFamily': family,
                                 'requestedWeight': weight,
                                 'matchedRequestedFamily': matched,
                                 'actualFamily': actual_family,
                                 'actualStyle': actual_style,
                                 'file': str(path), 'sha256': sha})
    return {'files': files, 'bindings': bindings}


def write(path, value):
    # The core's first manifest write is enriched before it reaches disk. An
    # existing manifest is never rewritten: its read-only verification below
    # rejects incomplete font coverage instead.
    if Path(path).name == 'source-sha256.json' and isinstance(value, dict) \
            and 'inputs' in value and 'externalInputs' in value:
        fonts = font_inputs()
        ctx = SimpleNamespace(silent=Path(path).parent / 'silent-body.mp4', normalized=Path(path).parent / 'normalized-silent-body.mp4')
        value = {**value, 'externalInputs': {**value['externalInputs'], **fonts['files']},
                 'fontBindings': fonts['bindings'], 'colorNormalizationCommand': normalization_command(ctx),
                 'colorEncoding': COLOR, 'toolVersions': tool_versions()}
    return _base['write'](path, value)


def verify_inputs(ctx):
    manifest = _base['verify_inputs'](ctx)
    fonts = font_inputs()
    if any(manifest.get('externalInputs', {}).get(path) != sha
           for path, sha in fonts['files'].items()) \
            or manifest.get('fontBindings') != fonts['bindings']:
        raise ValueError('Frozen revision lacks or differs from actual body/mono/brand font bindings; preserve it and choose a fresh revision')
    if manifest.get('colorNormalizationCommand') != normalization_command(ctx) or manifest.get('colorEncoding') != COLOR or manifest.get('toolVersions') != tool_versions():
        raise ValueError('Frozen color conversion command, profile or runtime versions differ')
    return manifest


def expected_timeline(ctx):
    timeline = _base['expected_timeline'](ctx)
    if timeline != {'width': 1920, 'height': 1080, 'fps': 30, 'bodyFrames': BODY_FRAMES[ctx.slug]}:
        raise ValueError('This visual revision must preserve the published peak-series episode body timeline')
    return timeline


COLOR = {'pix_fmt': 'yuv420p', 'color_range': 'tv', 'color_space': 'bt709',
         'color_transfer': 'bt709', 'color_primaries': 'bt709'}


def tool_versions():
    return {name: subprocess.check_output(command, text=True).splitlines()[0]
            for name, command in {'ffmpeg': ['ffmpeg', '-version'],
                                  'ffprobe': ['ffprobe', '-version'],
                                  'chromium': ['/usr/bin/chromium', '--version']}.items()}


def render_command(ctx, timeline):
    return ['node_modules/.bin/remotion', 'render', str(ctx.entry.relative_to(ctx.remotion)),
            ctx.composition, os.path.relpath(ctx.silent, ctx.remotion),
            '--codec=h264', '--crf=20', '--concurrency=2', '--muted',
            f'--frames=0-{timeline["bodyFrames"] - 1}',
            '--browser-executable=/usr/bin/chromium', '--bundle-cache=false']


def normalization_command(ctx):
    # Transform pixels and set per-frame color properties, rather than relabeling
    # the full-range Remotion movie. Complete AAC is added only after this step.
    return ['ffmpeg', '-v', 'error', '-n', '-i', _scope['display'](ctx.silent), '-map', '0:v:0', '-an',
            '-vf', 'scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-threads', '4',
            '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', 'bt709',
            '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-fps_mode', 'passthrough', '-video_track_timescale', '90000',
            '-map_metadata', '-1', '-movflags', '+faststart', _scope['display'](ctx.normalized)]


def first_frame_color(adapter, path):
    data = json.loads(adapter.engine.run([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-read_intervals', '%+#1', '-show_frames', '-show_entries',
        'frame=pix_fmt,color_range,color_space,color_transfer,color_primaries',
        '-of', 'json', str(path)]))
    frames = data.get('frames', [])
    if len(frames) != 1:
        raise ValueError(f'Cannot inspect the actual first decoded video frame: {_scope["display"](path)}')
    return {key: frames[0].get(key) for key in COLOR}


def color_shape(adapter, path):
    video = adapter.engine.stream(adapter.engine.probe(path), 'video')
    if any(video.get(key) != value for key, value in COLOR.items()):
        raise ValueError(f'Actual video color profile differs: {_scope["display"](path)}')
    if first_frame_color(adapter, path) != COLOR:
        raise ValueError(f'Actual first decoded frame color profile differs: {_scope["display"](path)}')
    return {key: video[key] for key in COLOR}


def presentation_timeline(adapter, path):
    # MP4 H.264 has one video packet per frame here. Sort by presentation time,
    # preserving exact rational times across potentially different track scales.
    video = adapter.engine.stream(adapter.engine.probe(path), 'video')
    data = json.loads(adapter.engine.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_packets', '-show_entries', 'packet=pts,duration', '-of', 'json', str(path)]))
    base = Fraction(video['time_base'])
    rows = sorted((Fraction(int(p['pts'])) * base, Fraction(int(p['duration'])) * base)
                  for p in data['packets'])
    if len(rows) != int(video['nb_frames']) or any(row != (Fraction(i, 30), Fraction(1, 30)) for i, row in enumerate(rows)):
        raise ValueError('Expected one packet/frame and exact continuous 30fps presentation timeline')
    return [[str(pts), str(duration)] for pts, duration in rows]


def source_inputs(ctx, adapter, *, require_identity):
    """The media core's traversal; pre-freeze QA may omit the unwritten identity."""
    if not ctx.entry.is_file():
        raise ValueError(f'Missing new visual entry: {_scope["display"](ctx.entry)}')
    required = [Path(__file__).resolve(), *adapter.dependency_files(), _scope['CHECKER'],
                _scope['CHECKER'].with_name('reference-legacy.json'),
                HERE.parent / 'requirements-reference-appendix.txt']
    if require_identity or ctx.identity.exists():
        required.append(ctx.identity)
    required += [ctx.directory / name for name in
                 ('source-sha256.json', 'storyboard.json', 'covers.json', 'words.json',
                  'script.md', 'article.mdx', 'references.json')]
    required += [ctx.remotion / name for name in
                 ('package.json', 'package-lock.json', 'remotion.config.ts', 'tsconfig.json')]
    required += [path for path in (ctx.remotion / 'src').rglob('*')
                 if path.is_file() and path.suffix in _scope['SOURCE_SUFFIXES']]
    required += [path for path in HERE.iterdir()
                 if path.is_file() and path.suffix in _scope['SOURCE_SUFFIXES']]
    public = ctx.remotion / 'public'
    if public.is_dir():
        required += [path for path in public.rglob('*') if path.is_file()
                     and path.suffix.lower() not in _scope['AUDIO_SUFFIXES']]
    pending, found = list(required), set()
    while pending:
        path = pending.pop().resolve()
        if path in found:
            continue
        if not path.is_file() or not path.is_relative_to(ROOT):
            raise ValueError(f'Missing or external production input: {_scope["display"](path)}')
        found.add(path)
        for value in _scope['local_imports'](path):
            imported = _scope['resolve_import'](path, value, ctx)
            if imported:
                pending.append(imported)
    return found


def production_inputs(ctx, adapter, *, require_identity=True):
    files = source_inputs(ctx, adapter, require_identity=require_identity)
    files.add(LIBRARY)
    files.add(HERE / 'README.md')
    origin = _scope['read'](HERE / 'style-v1.json')['origin']
    if not origin.get('coverStyle') or not origin.get('coverStyleSHA256'):
        raise ValueError('Peak style must bind its original cover style and complete SHA256')
    for field in origin:
        if field.endswith('SHA256') or field + 'SHA256' not in origin:
            continue
        path = (ROOT / origin[field]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or \
                _scope['digest'](path) != origin[field + 'SHA256']:
            raise ValueError(f'Original peak-series visual provenance differs: {field}')
        files.add(path)
    # Freeze both the historical production article and actual website article.
    # The latter may already be a documented publication derivation. No article
    # or old freeze is rewritten by this visual-only renderer.
    publication = ROOT / 'episodes' / ctx.slug
    files.add(publication / 'article.mdx')
    article = ctx.revision / 'article.mdx'
    if not article.is_file():
        raise ValueError('Save the current published article as revision/article.mdx before QA or freeze')
    files.add(article)
    pending = [ctx.references]
    for article_sources in (publication / 'article-sources.json', publication / 'article/source-evidence.json'):
        if article_sources.is_file():
            pending.append(article_sources)
    inspected = set()

    def add_evidence(value, expected=()):
        path = (ROOT / value).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f'Missing or external source evidence: {value}')
        if expected and _scope['digest'](path) not in expected:
            raise ValueError(f'Saved source evidence SHA differs: {value}')
        files.add(path)
        if path.suffix == '.json' and path not in inspected:
            pending.append(path)

    def visit(value):
        if isinstance(value, dict):
            # Evidence appears under several historical schemas, including
            # authorship and publisher records. Follow explicit retained-file
            # aliases wherever they occur, but do not reinterpret bare
            # historical path/commit records as current source bindings.
            aliases = {
                'evidence': (),
                'metadataEvidenceReused': (),
                'evidencePath': ('evidenceSHA256',),
                'rawEvidence': ('fullResponseSHA256', 'completeRawSHA256', 'rawSHA256'),
                'rawEvidencePath': ('completeRawSHA256', 'rawSHA256'),
                'publisherEvidence': ('publisherEvidenceSHA256', 'publisherSHA256', 'publisherResponseSHA256'),
                'publisherEvidencePath': ('publisherEvidenceSHA256', 'publisherSHA256', 'publisherResponseSHA256'),
                'reusedArchivePath': ('completeSHA256', 'sha256'),
            }
            for field, hashes in aliases.items():
                retained = value.get(field)
                if isinstance(retained, str) and retained.startswith(('docs/', 'episodes/', 'episodes-codex/')):
                    add_evidence(retained, [value[key] for key in hashes if value.get(key)])
            # Explicit successful saved GET records bind path+sha256. Their
            # path is a retained response, unlike a prior commit's bare path.
            retained = value.get('path')
            if isinstance(retained, str) and retained.startswith(('docs/', 'episodes/', 'episodes-codex/')) \
                    and (value.get('httpStatus') == 200 or value.get('status') == 200) \
                    and isinstance(value.get('sha256'), str):
                add_evidence(retained, [value['sha256']])
            # Saved files, as distinguished from historical path/commit records,
            # are actual retained inputs. Preserve their full bytes and check
            # the complete response/record SHA where the record supplies one.
            expected = [value.get(key) for key in (
                'sha256', 'recordSHA256', 'responseSha256', 'responseSHA256',
                'fileSHA256', 'completeResponseSHA256', 'completeSHA256',
                'completeRawSHA256', 'fullResponseSHA256')]
            for key, digest_field in (
                    ('get', 'sha256'), ('originalRetrieval', 'sha256'),
                    ('copiedOriginalBinding', 'completeSHA256')):
                record = value.get(key)
                if isinstance(record, dict):
                    expected.append(record.get(digest_field))
            expected = [item for item in expected if item]
            for key in ('savedPath', 'savedResponsePath', 'archivePath',
                        'savedCapturePath', 'savedCompleteResponse'):
                if isinstance(value.get(key), str):
                    if not expected:
                        raise ValueError(f'Saved source evidence lacks a complete SHA binding: {value[key]}')
                    add_evidence(value[key], expected)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    while pending:
        evidence = pending.pop().resolve()
        if evidence in inspected:
            continue
        if not evidence.is_relative_to(ROOT) or not evidence.is_file():
            raise ValueError(f'Missing or external article/reference source: {evidence}')
        inspected.add(evidence)
        files.add(evidence)
        visit(_scope['read'](evidence))
    for path in files:
        if not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f'Missing or external retained production input: {_scope["display"](path)}')
    return sorted(path.resolve() for path in files)


def run(command, *, cwd=ROOT, capture=False):
    return _base['run']([str(value) for value in command], cwd=cwd, capture=capture)


def render(ctx, adapter):
    _scope['source_preflight'](ctx)
    manifest = verify_inputs(ctx)
    if any(path.exists() for path in (ctx.silent, ctx.normalized, ctx.body, ctx.output)):
        raise ValueError('Revision already has encoded media; use --verify or a fresh revision')
    timeline = manifest['timeline']
    baseline_info = _scope['media_shape'](adapter, ctx.baseline, timeline,
                      _scope['read'](ctx.identity)['publishedMetadata']['finalVideoFrames'])
    audio_stream = adapter.engine.stream(baseline_info, 'audio')
    if audio_stream['codec_name'] != 'aac' or float(audio_stream.get('start_time', 0)) != 0 \
            or float(audio_stream['duration']) > timeline['bodyFrames'] / 30 + 1 / 30:
        raise ValueError('Expected complete baseline AAC confined to the original body endpoint')
    run(manifest['renderCommand'], cwd=ctx.remotion)
    verify_inputs(ctx)
    raw = _scope['media_shape'](adapter, ctx.silent, timeline, timeline['bodyFrames'])
    raw_video = adapter.engine.stream(raw, 'video')
    if raw_video.get('pix_fmt') != 'yuvj420p' or raw_video.get('color_range') != 'pc' \
            or raw_video.get('color_space') != 'bt470bg' \
            or any(s['codec_type'] == 'audio' for s in raw['streams']):
        raise ValueError('Muted raw Remotion movie must be the reviewed full-range BT.601 input')
    raw_frame_color = first_frame_color(adapter, ctx.silent)
    if any(raw_frame_color.get(key) != value for key, value in
           {'pix_fmt': 'yuvj420p', 'color_range': 'pc', 'color_space': 'bt470bg'}.items()):
        raise ValueError('Actual first decoded raw frame is not full-range BT.601')
    run(manifest['colorNormalizationCommand'])
    _scope['media_shape'](adapter, ctx.normalized, timeline, timeline['bodyFrames'])
    normalized_color = color_shape(adapter, ctx.normalized)
    raw_pts = presentation_timeline(adapter, ctx.silent)
    normalized_pts = presentation_timeline(adapter, ctx.normalized)
    if raw_pts != normalized_pts:
        raise ValueError('Pixel color conversion changed video presentation times')
    run(['ffmpeg', '-v', 'error', '-n', '-i', ctx.normalized, '-i', ctx.baseline,
         '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-map_metadata', '-1',
         '-metadata', f'comment=video-studio-peak-style-body:v1:{ctx.slug}',
         '-movflags', '+faststart', ctx.body])
    _scope['media_shape'](adapter, ctx.body, timeline, timeline['bodyFrames'])
    color_shape(adapter, ctx.body)
    audio = _scope['audio_identity'](adapter, ctx.baseline, ctx.body)
    write(ctx.audio_report, audio)
    receipt = adapter.append(_scope['adapter_args'](ctx, adapter))
    verify_inputs(ctx)
    color_shape(adapter, ctx.output)
    original_pts = presentation_timeline(adapter, ctx.baseline)
    final_pts = presentation_timeline(adapter, ctx.output)
    if final_pts != original_pts:
        raise ValueError('Final video presentation times differ from original published movie')
    color_check = {'passed': True, 'rawInput': {'pix_fmt': 'yuvj420p', 'color_range': 'pc', 'color_space': 'bt470bg'},
                   'output': normalized_color, 'allRawToNormalizedPresentationTimesEqual': True,
                   'decodedFirstFrameColor': {
                       'raw': raw_frame_color,
                       **{name: first_frame_color(adapter, path) for name, path in
                          (('normalized', ctx.normalized), ('body', ctx.body), ('final', ctx.output))}},
                   'allOriginalPublishedPresentationTimesEqual': True, 'finalFrames': len(final_pts),
                   'presentationTimelineSHA256': adapter.engine.sequence_hash(final_pts),
                   'scope': 'Real pc601→tv709 pixel conversion with per-frame setparams. Pixels are lossy-converted; no original pixel-equality claim. Browser color is independently reviewed.'}
    write(ctx.color_report, color_check)
    publication = {'finalVideoFrames': receipt['finalVideoFrames'],
                   'referenceAppendix': {'kind': 'references', 'from': receipt['bodyFrames'],
                       'durationInFrames': receipt['appendix']['durationInFrames'],
                       'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    info = _scope['media_shape'](adapter, ctx.output, timeline, receipt['finalVideoFrames'])
    result = {'visualRevision': 'peak-style-v1', 'createdAtUTC': datetime.now(timezone.utc).isoformat(),
              'episode': ctx.slug, 'width': 1920, 'height': 1080, 'fps': '30/1',
              'frames': receipt['finalVideoFrames'], 'seconds': receipt['durationSeconds'],
              'bytes': ctx.output.stat().st_size, 'sha256': _scope['digest'](ctx.output),
              'bodyFrames': timeline['bodyFrames'], 'audio': 'aac',
              'audioSampleRate': int(adapter.engine.stream(info, 'audio')['sample_rate']),
              **publication, 'publicationMetadata': publication, 'presentation': 'title-author',
              'newProductionManifest': _scope['display'](ctx.manifest),
              'newProductionManifestSHA256': _scope['digest'](ctx.manifest),
              'sourceInputsVerified': len(manifest['inputs']), 'baselineAudioPreserved': audio,
              'colorEncoding': normalized_color, 'colorNormalization': color_check,
              'bodyProvenance': 'New muted pictures from the independent peak-series visual manifest, normalized once to limited BT.709 before copying the complete baseline AAC; historical inputs retain their identities.',
              'loudnessBasis': 'Complete original AAC packets/timing and decoded PCM equality; no remix or TTS.',
              'reviewScope': 'Frozen inputs, format, real color conversion, all presentation times, complete original sound and appended decoded body-frame preservation. Independent visual and actual browser review are separate.'}
    write(ctx.result, result)
    for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
        shutil.copyfile(ctx.artifacts / name, ctx.revision / name)
    return {'status': 'rendered', 'result': _scope['display'](ctx.result), **publication, 'sha256': result['sha256']}


def verify(ctx, adapter):
    result = _base_verify(ctx, adapter)
    for path in (ctx.normalized, ctx.body, ctx.output):
        color_shape(adapter, path)
    if presentation_timeline(adapter, ctx.baseline) != presentation_timeline(adapter, ctx.output):
        raise ValueError('Final video presentation timeline differs from baseline')
    color = _scope['read'](ctx.color_report)
    if color.get('passed') is not True or color.get('output') != COLOR:
        raise ValueError('Recorded color normalization differs')
    actual_first_frames = {name: first_frame_color(adapter, path) for name, path in
                           (('raw', ctx.silent), ('normalized', ctx.normalized),
                            ('body', ctx.body), ('final', ctx.output))}
    if color.get('decodedFirstFrameColor') != actual_first_frames:
        raise ValueError('Recorded first decoded frame color properties differ')
    return result


_scope.update(context=context, expected_timeline=expected_timeline,
              production_inputs=production_inputs, render_command=render_command,
              run=run, render=render, write=write, verify_inputs=verify_inputs, verify=verify)
# Expose the core's actual entry helpers for read-only independent audits.
for _name, _value in _scope.items():
    if isinstance(_value, FunctionType) and not _name.startswith('_'):
        globals()[_name] = _value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('episode', choices=EPISODES)
    stages = parser.add_mutually_exclusive_group()
    stages.add_argument('--freeze', action='store_true')
    stages.add_argument('--render', action='store_true')
    stages.add_argument('--verify', action='store_true')
    stages.add_argument('--font-inputs', action='store_true', help='Read-only actual font-file and family bindings')
    parser.add_argument('--revision', default='peak-style')
    parser.add_argument('--baseline', help='Exact published baseline MP4')
    parser.add_argument('--entry', default='src/peak-style/index.ts')
    parser.add_argument('--composition', default='Main')
    args = parser.parse_args()
    ctx, adapter = context(args), adapter_module()
    if args.font_inputs:
        result = {'status': 'font-inputs-read-only', **font_inputs()}
    elif args.freeze:
        result = freeze(ctx, adapter)
    elif args.render:
        result = render(ctx, adapter)
    elif args.verify:
        result = verify(ctx, adapter)
    else:
        timeline = expected_timeline(ctx)
        result = {'status': 'plan-only', 'episode': ctx.slug, 'timeline': timeline,
                  'baseline': display(ctx.baseline), 'revision': display(ctx.revision),
                  'renderCommand': render_command(ctx, timeline),
                  'colorNormalizationCommand': normalization_command(ctx), 'colorEncoding': COLOR,
                  'next': 'Finish peak-series visual/algorithm review, then --freeze, --render, and actual final/player review.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
