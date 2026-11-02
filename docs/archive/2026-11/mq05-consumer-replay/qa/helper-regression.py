#!/usr/bin/env python3
"""Offline synthetic orchestration checks; never exercises real media or publication."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

sys.dont_write_bytecode = True
A = Path(__file__).resolve().parent.parent
ROOT = next(p for p in A.parents if (p / 'AGENTS.md').is_file())
REAL_P = ROOT / 'episodes/message-queue/kafka-consumer-idempotency/publication'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def inventory(directory):
    return {str(p.relative_to(directory)): (sha(p), p.stat().st_mtime_ns)
            for p in directory.rglob('*') if p.is_file()}


def fixture(base):
    spec = importlib.util.spec_from_file_location('synthetic_revision_install', A / 'install.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ROOT = base / 'repo'
    m.HERE = m.ROOT / 'docs/archive/fixture'
    m.D = m.ROOT / 'episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2'
    m.P = m.D.parents[2] / 'publication'
    m.RECEIPT = m.HERE / 'publication-files.json'
    for d in [m.HERE, m.D, m.P, m.ROOT / 'site']:
        d.mkdir(parents=True)
    old = json.loads((REAL_P / 'meta.json').read_text())
    old['platforms'] = {'example': 'https://example.invalid/original'}
    m.write(m.P / 'meta.json', old)
    original_bytes = (m.P / 'meta.json').read_bytes()
    baseline = 'b' * 40
    m.write(m.HERE / 'startup.json', {'baseline': baseline, 'originalTitle': old['title']})
    m.write(m.ROOT / 'site/package.json', {'version': '0.98.1'})
    (m.P / 'video.mp4').write_bytes(b'old synthetic video')
    (m.P / 'article').mkdir()
    (m.P / 'article/old-01.jpg').write_bytes(b'old synthetic JPEG')
    for name in m.COVERS:
        payload = ('original ' + name).encode()
        (m.P / name).write_bytes(payload)
        (m.D / name).write_bytes(payload)
    for name in m.FILES:
        (m.D / name).write_bytes(('new synthetic ' + name).encode())
    video = sha(m.D / 'video.mp4')
    figures = []
    for i in range(4):
        rel = f'article/consumer-replay-{i + 1:02}-fixture.jpg'
        (m.D / rel).parent.mkdir(exist_ok=True)
        (m.D / rel).write_bytes(f'synthetic JPEG {i}'.encode())
        figures.append({'file': rel, 'frame': i, 'seconds': i / 30, 'sha256': sha(m.D / rel)})
    m.write(m.D / 'article-figure-plan.json', {'figures': figures})
    m.write(m.D / 'article-figures-export.json', {'videoSHA256': video, 'visualReviewed': True, 'figures': figures})
    m.write(m.D / 'episode-config.json', {'slug': m.SLUG, 'title': old['title'], 'episodePart': old['episodePart']})
    m.write(m.D / 'render-result.json', {'sha256': video, 'bodyFrames': 10, 'finalVideoFrames': 160,
            'publicationMetadata': {'finalVideoFrames': 160, 'referenceAppendix': {'from': 10}}})
    m.write(m.D / 'reference-appendix.json', {'outputSHA256': video})
    m.write(m.D / 'reference-appendix-media-check.json', {'outputSHA256': video, 'passed': True,
            'bodyDecodedFramesAndTimestampsEqual': True, 'audioPacketsAndTimingEqual': True})
    m.write(m.D / 'source-sha256.json', {'syntheticFixtureOnly': True})
    final = m.D / 'qa-final-independent/review.json'
    final.parent.mkdir()
    m.write(final, {'pass': True, 'visualReviewed': True, 'videoSHA256': video,
                   'frozenManifestSHA256': sha(m.D / 'source-sha256.json')})
    calls = []
    original_run, original_output = m.subprocess.run, m.subprocess.check_output
    def output(command, **kwargs):
        path = command[-1].split(':', 1)[1]
        return original_bytes if path.endswith('/meta.json') else (m.P / Path(path).name).read_bytes()
    m.subprocess.check_output = output
    m.subprocess.run = lambda command, **kwargs: calls.append(command)
    args = SimpleNamespace(final_review=final, backup_dir=base / 'outside-repo-backup',
                           local_qa=m.HERE / 'local-report.json', release='v0.98.1')
    return m, args, old, calls, (original_run, original_output)


def rejected(action):
    try:
        action()
    except (AssertionError, KeyError):
        return
    raise AssertionError('Expected the invalid synthetic state to be rejected')


def execute(name, action):
    with tempfile.TemporaryDirectory(prefix='mq05-helper-synthetic-') as t:
        m, args, old, calls, originals = fixture(Path(t))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                action(m, args, old)
            assert all(command[1:] == [str(m.D / 'freeze.py'), '--verify'] for command in calls)
        finally:
            m.subprocess.run, m.subprocess.check_output = originals
    return {'name': name, 'passed': True, 'scope': 'temporary synthetic fixture only'}


def cover_rejection(m, args, old):
    before = inventory(m.P)
    (m.D / m.COVERS[0]).write_bytes(b'changed cover')
    rejected(lambda: m.stage(args))
    assert inventory(m.P) == before and not args.backup_dir.exists() and not m.RECEIPT.exists()


def final_rejection(m, args, old):
    before = inventory(m.P)
    value = m.read(args.final_review); value['visualReviewed'] = False; m.write(args.final_review, value)
    rejected(lambda: m.stage(args))
    assert inventory(m.P) == before and not args.backup_dir.exists() and not m.RECEIPT.exists()


def old_figure_rejection(m, args, old):
    before = inventory(m.P)
    for name in ['article-figure-plan.json', 'article-figures-export.json']:
        value = m.read(m.D / name); value['figures'][0]['file'] = 'article/old-01.jpg'; m.write(m.D / name, value)
    rejected(lambda: m.stage(args))
    assert inventory(m.P) == before and not args.backup_dir.exists()


def stage_publish(m, args, old):
    before = inventory(m.P)
    m.stage(args)
    staged = m.read(m.P / 'meta.json')
    assert all(staged[k] == old[k] for k in m.IDENTITY + ['updatedAt', 'poster'])
    assert staged['sourcePath'] == (m.D / 'remotion').relative_to(m.ROOT).as_posix()
    assert (m.P / 'article/old-01.jpg').read_bytes() == b'old synthetic JPEG'
    assert all(inventory(m.P)[rel] == before[rel] for rel in m.COVERS)
    m.write(args.local_qa, {'revisionPreview': True, 'pass': True, 'visualReviewed': False,
            'videoSha256': sha(m.P / 'video.mp4'), 'errors': [], 'checks': [1], 'exactFrames': [1]})
    rejected(lambda: m.publish(args))
    assert m.read(m.P / 'meta.json') == staged
    qa = m.read(args.local_qa); qa['visualReviewed'] = True; m.write(args.local_qa, qa)
    m.publish(args)
    stamped = m.read(m.P / 'meta.json')
    assert {k: v for k, v in stamped.items() if k != 'updatedAt'} == {k: v for k, v in staged.items() if k != 'updatedAt'}
    assert stamped['updatedAt'] != old['updatedAt'] and stamped['firstRelease'] == 'v0.97.0'
    rejected(lambda: m.publish(args))


def rollback(m, args, old):
    before = inventory(m.P)
    m.stage(args)
    rejected(lambda: m.stage(args))
    m.restore()
    assert inventory(m.P) == before


def changed_asset(m, args, old):
    m.stage(args)
    before = (m.P / 'meta.json').read_bytes()
    (m.P / 'video.mp4').write_bytes(b'unexpected subsequent change')
    rejected(lambda: m.publish(args))
    assert (m.P / 'meta.json').read_bytes() == before


if __name__ == '__main__':
    before = inventory(REAL_P)
    tests = [execute(name, check) for name, check in [
        ('changed legacy cover rejects before writes', cover_rejection),
        ('missing actual final visual proof rejects before writes', final_rejection),
        ('old Figure URL rejects without touching old JPEG', old_figure_rejection),
        ('stage preserves history; publish gates visual and changes only updatedAt; restamp rejects', stage_publish),
        ('fresh-stage guard and full byte/mtime rollback preserve old JPEGs', rollback),
        ('changed staged media rejects timestamp publication', changed_asset),
    ]]
    assert inventory(REAL_P) == before
    report = {'kind': 'offline-synthetic-publication-helper-semantic-regression',
              'passed': True, 'checks': tests, 'realPublicationFilesUnchanged': len(before),
              'realMediaVoiceBrowserNetworkActionsExecuted': False,
              'limits': 'Synthetic orchestration fixtures are not production QA, encoding, source validation or actual preview acceptance.'}
    target = A / 'qa/helper-regression.json'
    assert not target.exists(), 'Preserve the earlier offline attempt'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
