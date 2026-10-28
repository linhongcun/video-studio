#!/usr/bin/env python3
"""Build independently frozen MySQL visual revisions using the proven media core.

Only this private function namespace is adapted. The puzzles renderer and every
historical source/freezer remain unchanged. The baseline MP4 is the complete
published AAC input; all packets, timestamps and decoded PCM must be identical.

python3 episodes-codex/_shared/mysql-video/render.py db-index --freeze
python3 episodes-codex/_shared/mysql-video/render.py db-index --render
python3 episodes-codex/_shared/mysql-video/render.py db-index --verify
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import FunctionType, SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIBRARY = HERE.parent / 'puzzles-video/render.py'
EPISODES = ('db-index', 'db-transaction', 'db-lock', 'db-replication')
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
_base = {name: _scope[name] for name in ('production_inputs', 'render', 'run')}


def context(args):
    directory = ROOT / 'episodes-codex' / args.episode
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.revision):
        raise ValueError('--revision must be a single stable directory name')
    revision = directory / 'revisions' / args.revision
    remotion = directory / 'remotion'
    entry = (remotion / args.entry).resolve()
    if not entry.is_relative_to(remotion / 'src/mysql-style'):
        raise ValueError('Choose an entry under this episode\'s src/mysql-style/')
    return SimpleNamespace(
        slug=args.episode, directory=directory, remotion=remotion,
        revision=revision, entry=entry, composition=args.composition,
        manifest=revision / 'source-sha256.json',
        identity=revision / 'baseline-publication.json',
        baseline=_scope['location'](args.baseline) if args.baseline else
            ROOT / 'work/mysql-video-style/baseline' / f'{args.episode}.mp4',
        silent=revision / 'silent-body.mp4', body=revision / 'body.mp4',
        output=revision / 'video.mp4', references=directory / 'references.json',
        artifacts=revision / 'references', result=revision / 'render-result.json',
        audio_report=revision / 'baseline-audio-check.json',
    )


def production_inputs(ctx, adapter):
    files = set(_base['production_inputs'](ctx, adapter))
    files.add(LIBRARY)
    files.update(HERE.parent / 'database-identity' / name for name in
                 ('source.json', 'LICENSE.txt', 'mysql-original.svg'))
    # A scoped publication article may be prepared before encoding while the
    # original frozen production article remains at its historical path.
    article = ctx.revision / 'article.mdx'
    if article.is_file():
        files.add(article)
    article_sources = ROOT / 'episodes' / ctx.slug / 'article-sources.json'
    if article_sources.is_file():
        pending, inspected = [article_sources], set()

        def add_evidence(value, expected=()):
            path = (ROOT / value).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                raise ValueError(f'Missing or external article evidence: {value}')
            if expected and any(_scope['digest'](path) != digest for digest in expected):
                raise ValueError(f'Saved article evidence SHA differs: {value}')
            files.add(path)
            if path.suffix == '.json' and path not in inspected:
                pending.append(path)

        def visit(value):
            if isinstance(value, dict):
                for field in ('verification', 'titleEvidence', 'quotation'):
                    record = value.get(field)
                    if isinstance(record, dict) and isinstance(record.get('evidence'), str):
                        add_evidence(record['evidence'])
                saved = [value[key] for key in
                         ('savedPath', 'savedResponsePath', 'archivePath', 'savedCapturePath')
                         if isinstance(value.get(key), str)]
                if saved:
                    expected = [value.get('sha256'), value.get('recordSHA256')]
                    for key, digest_field in (
                            ('get', 'sha256'), ('originalRetrieval', 'sha256'),
                            ('copiedOriginalBinding', 'completeSHA256')):
                        record = value.get(key)
                        if isinstance(record, dict):
                            expected.append(record.get(digest_field))
                    expected = [digest for digest in expected if digest]
                    if not expected:
                        raise ValueError(f'Saved article evidence lacks a complete SHA binding: {saved}')
                    for name in saved:
                        add_evidence(name, expected)
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
                raise ValueError(f'Missing or external article source: {evidence}')
            inspected.add(evidence)
            files.add(evidence)
            visit(_scope['read'](evidence))
    return sorted(path.resolve() for path in files)


def run(command, *, cwd=ROOT, capture=False):
    command = [str(value) for value in command]
    command = [value.replace('comment=video-studio-puzzles-continuity-body:v1:',
                             'comment=video-studio-mysql-style-body:v1:')
               for value in command]
    return _base['run'](command, cwd=cwd, capture=capture)


def render(ctx, adapter):
    outcome = _base['render'](ctx, adapter)
    result = _scope['read'](ctx.result)
    result['visualRevision'] = 'mysql-style-v1'
    result['bodyProvenance'] = (
        'New muted MySQL-scoped pictures were rendered from the independent '
        'mysql-style revision manifest. Complete published baseline AAC was '
        'stream copied; original timing and historical freezes are unchanged.')
    _scope['write'](ctx.result, result)
    return outcome


_scope.update(context=context, production_inputs=production_inputs,
              run=run, render=render)
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
    parser.add_argument('--revision', default='mysql-style')
    parser.add_argument('--baseline', help='Exact published baseline MP4')
    parser.add_argument('--entry', default='src/mysql-style/index.ts')
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
        result = {'status': 'plan-only', 'episode': ctx.slug, 'timeline': timeline,
                  'baseline': display(ctx.baseline), 'revision': display(ctx.revision),
                  'renderCommand': render_command(ctx, timeline),
                  'next': 'Finish MySQL scope/visual review, then --freeze, --render, and actual final/player review.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
