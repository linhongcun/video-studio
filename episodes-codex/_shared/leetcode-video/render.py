#!/usr/bin/env python3
"""Build independently frozen LeetCode visual revisions using the proven media core.

Only this private function namespace is adapted. The puzzles renderer and every
historical source/freezer remain unchanged. The baseline MP4 is the complete
published AAC input; all packets, timestamps and decoded PCM must be identical.

python3 episodes-codex/_shared/leetcode-video/render.py two-sum --freeze
python3 episodes-codex/_shared/leetcode-video/render.py two-sum --render
python3 episodes-codex/_shared/leetcode-video/render.py two-sum --verify
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import subprocess
from types import FunctionType, SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIBRARY = HERE.parent / 'puzzles-video/render.py'
EPISODES = ('two-sum', 'longest-substring', 'container-most-water',
            'trapping-rain-water', 'permutations', 'climbing-stairs',
            'number-of-islands', 'reverse-linked-list', 'number-of-provinces',
            'binary-search', 'daily-temperatures')
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


def context(args):
    directory = ROOT / 'episodes-codex' / args.episode
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.revision):
        raise ValueError('--revision must be a single stable directory name')
    revision = directory / 'revisions' / args.revision
    remotion = directory / 'remotion'
    entry = (remotion / args.entry).resolve()
    if not entry.is_relative_to(remotion / 'src/leetcode-style'):
        raise ValueError('Choose an entry under this episode\'s src/leetcode-style/')
    return SimpleNamespace(
        slug=args.episode, directory=directory, remotion=remotion,
        revision=revision, entry=entry, composition=args.composition,
        manifest=revision / 'source-sha256.json',
        identity=revision / 'baseline-publication.json',
        baseline=_scope['location'](args.baseline) if args.baseline else
            ROOT / 'work/leetcode-video-style/baseline' / f'{args.episode}.mp4',
        silent=revision / 'silent-body.mp4', body=revision / 'body.mp4',
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
        value = {**value, 'externalInputs': {**value['externalInputs'], **fonts['files']},
                 'fontBindings': fonts['bindings']}
    return _base['write'](path, value)


def verify_inputs(ctx):
    manifest = _base['verify_inputs'](ctx)
    fonts = font_inputs()
    if any(manifest.get('externalInputs', {}).get(path) != sha
           for path, sha in fonts['files'].items()) \
            or manifest.get('fontBindings') != fonts['bindings']:
        raise ValueError('Frozen revision lacks or differs from actual body/code/brand font bindings; preserve it and choose a fresh revision')
    return manifest


def expected_timeline(ctx):
    timeline = _base['expected_timeline'](ctx)
    storyboard = _scope['read'](ctx.directory / 'storyboard.json')
    card = storyboard['meta']['unvoicedEndCard']
    if card['kind'] != 'full-python-solution' or card['durationInFrames'] != 150 \
            or card['from'] + card['durationInFrames'] != timeline['bodyFrames']:
        raise ValueError('The complete original five-second Python card must end the body')
    shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
    start = sum(shot['durationInFrames'] for shot in shots[:-1])
    if start + shots[-1].get('codeCardFrom', -1) != card['from']:
        raise ValueError('Original Python card boundary differs between shot and metadata')
    for field in ('codeSource', 'displaySource'):
        path = (ctx.directory / card[field]).resolve()
        if not path.is_relative_to(ctx.directory) or not path.is_file() \
                or _scope['digest'](path) != card[field + 'Sha256']:
            raise ValueError(f'Original Python card source identity differs: {field}')
    return timeline


def production_inputs(ctx, adapter):
    files = set(_base['production_inputs'](ctx, adapter))
    files.add(LIBRARY)
    card = _scope['read'](ctx.directory / 'storyboard.json')['meta']['unvoicedEndCard']
    files.update(ctx.directory / card[field] for field in ('codeSource', 'displaySource'))
    # Freeze both the historical production article and actual website article.
    # The latter may already be a documented publication derivation. No article
    # or old freeze is rewritten by this visual-only renderer.
    publication = ROOT / 'episodes' / ctx.slug
    files.add(publication / 'article.mdx')
    article = ctx.revision / 'article.mdx'
    if article.is_file():
        files.add(article)
    article_sources = publication / 'article-sources.json'
    pending = [ctx.references]
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
    return sorted(path.resolve() for path in files)


def run(command, *, cwd=ROOT, capture=False):
    command = [str(value) for value in command]
    command = [value.replace('comment=video-studio-puzzles-continuity-body:v1:',
                             'comment=video-studio-leetcode-style-body:v1:')
               for value in command]
    return _base['run'](command, cwd=cwd, capture=capture)


def render(ctx, adapter):
    outcome = _base['render'](ctx, adapter)
    result = _scope['read'](ctx.result)
    result['visualRevision'] = 'leetcode-style-v1'
    result['bodyProvenance'] = (
        'New muted LeetCode pictures, including the complete original Python code interval, were rendered from the independent '
        'leetcode-style revision manifest. Complete published baseline AAC was '
        'stream copied; original timing and historical freezes are unchanged.')
    _scope['write'](ctx.result, result)
    return outcome


_scope.update(context=context, expected_timeline=expected_timeline,
              production_inputs=production_inputs,
              run=run, render=render, write=write, verify_inputs=verify_inputs)
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
    parser.add_argument('--revision', default='leetcode-style')
    parser.add_argument('--baseline', help='Exact published baseline MP4')
    parser.add_argument('--entry', default='src/leetcode-style/index.ts')
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
                  'next': 'Finish LeetCode visual/code-card review, then --freeze, --render, and actual final/player review.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
