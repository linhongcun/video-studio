#!/usr/bin/env python3
"""Isolated helper semantics only: no network, browser, media, install or timestamps."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import html
import json
import sys
import traceback
import types

sys.dont_write_bytecode = True
A = Path(__file__).resolve().parent.parent
ROOT = next(p for p in A.parents if (p / 'AGENTS.md').is_file())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def module(name):
    p = A / name
    m = types.ModuleType('offline_fixture_helper')
    m.__file__ = str(p)
    exec(compile(p.read_text(), str(p), 'exec'), m.__dict__)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=A / 'qa/helper-offline-regression.json')
    args = ap.parse_args()
    assert not args.out.exists(), 'Preserve any earlier regression attempt'
    online, install = module('online-verify.py'), module('install.py')
    info = json.loads((A / 'episodes.json').read_text())
    slugs = [e['slug'] for e in info['episodes']]
    before = {s: sha(install.publication_directory(s, root=ROOT) / 'meta.json') for s in slugs}
    report = {'status': 'in-progress', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
              'scope': 'Synthetic HTML and in-memory helper regression; never actual production/online QA.',
              'helperSHA256': {n: sha(A / n) for n in ['install.py', 'online-verify.py']}, 'cases': []}

    def save():
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def case(name, fn, rejection=False):
        try:
            result = fn()
        except (AssertionError, KeyError, ValueError) as exc:
            assert rejection, (name, repr(exc))
            report['cases'].append({'case': name, 'result': 'expected-rejection', 'actualException': repr(exc)})
        else:
            assert not rejection and result is not False, name
            report['cases'].append({'case': name, 'result': 'passed'})
        save()

    meta = {'video': 'video.mp4', 'poster': 'cover-16x9.jpg'}
    board = {'meta': {'fps': 30}, 'scenes': [{'chapterId': 'first', 'shots': [{'durationInFrames': 30}]},
                                                   {'chapterId': 'second', 'shots': [{'durationInFrames': 30}]}]}
    figures = [{'file': 'article/01-fixture.jpg', 'frame': 15, 'seconds': .5}]
    sources = {'R1': {'quotation': {'text': 'E01 < E02 && done == false'}, 'url': 'https://fixture.invalid/source'}}
    prefix = '/video-studio/episodes/fixture-episode/'
    fixture = ('<section id="player" data-chapters="' + html.escape(json.dumps([{'id': 'first', 'start': 0}, {'id': 'second', 'start': 1}]), quote=True)
               + '"></section><video poster="' + prefix + meta['poster'] + '"></video><source src="' + prefix + 'video.mp4"><track src="' + prefix + 'captions.vtt">')
    for cid, start in [('first', 0), ('second', 1)]:
        fixture += f'<h2 id="{cid}"></h2>' + f'<a data-id="{cid}" data-start="{start}"></a>' * 2
    fixture += f'<img src="{prefix}article/01-fixture.jpg"><a href="{prefix}article/01-fixture.jpg"></a><a data-seek-time="0.5"></a>'
    fixture += '<button data-source-trigger="R1"></button><aside data-source-panel="R1"></aside><p>' + html.escape(sources['R1']['quotation']['text']) + '</p><a href="https://fixture.invalid/source"></a>'
    verify = lambda text: online.verify_episode_page(text, 'fixture-episode', meta, board, figures, ['R1'], sources)
    save()
    try:
        case('valid source/chapter/figure HTML', lambda: verify(fixture))
        failures = [
            ('stale chapter start', 'data-start="0"', 'data-start="9"'),
            ('duplicate current article anchor', '<h2 id="first"></h2>', '<h2 id="first"></h2><h2 id="first"></h2>'),
            ('missing second chapter control', '<a data-id="first" data-start="0"></a>', ''),
            ('relative Figure image URL', f'src="{prefix}article/01-fixture.jpg"', 'src="article/01-fixture.jpg"'),
            ('wrong original image link', f'href="{prefix}article/01-fixture.jpg"', 'href="wrong.jpg"'),
            ('wrong Figure replay time', 'data-seek-time="0.5"', 'data-seek-time="9"'),
            ('wrong video source', f'src="{prefix}video.mp4"', 'src="wrong.mp4"'),
            ('wrong poster source', f'poster="{prefix}cover-16x9.jpg"', 'poster="wrong.jpg"'),
            ('missing native VTT source', f'src="{prefix}captions.vtt"', 'src="wrong.vtt"'),
            ('missing source trigger', 'data-source-trigger="R1"', 'data-source-trigger="missing"'),
            ('wrong exact original quotation', html.escape(sources['R1']['quotation']['text']), 'incorrect quote'),
            ('wrong source URL', 'href="https://fixture.invalid/source"', 'href="https://fixture.invalid/wrong"'),
        ]
        for name, old, new in failures:
            assert old in fixture
            case(name, lambda old=old, new=new: verify(fixture.replace(old, new, 1)), True)
        links = ''.join(f'<a href="/video-studio/episodes/{s}/"></a>' for s in slugs)
        library = links + '<a href="/video-studio/series/message-queue/"></a>'
        learn = '<a href="/video-studio/library/"></a><script>location.replace(target)</script>'
        case('current batch entry links', lambda: online.verify_entry_pages(library, links, learn, slugs))
        case('HTTP200 stale library', lambda: online.verify_entry_pages('', links, learn, slugs), True)
        case('HTTP200 stale home', lambda: online.verify_entry_pages(library, '', learn, slugs), True)
        case('learn fallback missing JS redirect', lambda: online.verify_entry_pages(library, links, '<a href="/video-studio/library/"></a>', slugs), True)
        metas = {s: json.loads((install.publication_directory(s, root=ROOT) / 'meta.json').read_text()) for s in slugs}
        reviews = {s: {'draftPreview': True, 'pass': True, 'visualReviewed': True, 'videoSha256': 'fixture-video-sha',
                       'errors': [], 'checks': [{'fixture': True}], 'exactFrames': [{'fixture': True}]} for s in slugs}
        receipt = {'status': 'installed-as-unpublished-drafts', 'episodes': [{'slug': s, 'files': {'video.mp4': 'fixture-video-sha'}} for s in slugs]}
        writes = []
        install.read = lambda p: copy.deepcopy(metas[p.parent.parent.name] if p.name == 'meta.json' else reviews[p.parent.name])
        install.sha = lambda p: 'fixture-video-sha'
        install.write = lambda *args: writes.append(args)
        check_batch = lambda: install.publication_batch(receipt, info, datetime.now(timezone.utc).isoformat(), A / 'unwritten-fixture-local-qa')
        case('whole batch validates before timestamp writes', lambda: len(check_batch()) == len(slugs))
        install.sha = lambda p: 'bad' if p.parent.parent.name == slugs[-1] else 'fixture-video-sha'
        case('later asset mismatch rejects entire publication batch', check_batch, True)
        install.sha = lambda p: 'fixture-video-sha'
        reviews[slugs[-1]]['visualReviewed'] = False
        case('unreviewed draft screenshots reject first publication', check_batch, True)
        reviews[slugs[-1]]['visualReviewed'] = True
        reviews[slugs[-1]]['videoSha256'] = 'wrong-video'
        case('draft native report for another video rejects first publication', check_batch, True)
        assert writes == [] and len(report['cases']) == 21
        assert all(sha(install.publication_directory(s, root=ROOT) / 'meta.json') == h for s, h in before.items())
        report.update(status='passed-offline-helper-semantics-only', casesPassed=21, realMetadataUnchanged=True,
                      noProductionWriteCalls=True, noNetworkOrBrowserOrMediaExecution=True)
        save()
    except Exception:
        report.update(status='failed-offline-helper-regression', traceback=traceback.format_exc())
        save()
        raise
    print(json.dumps({'status': report['status'], 'cases': len(report['cases']), 'report': str(args.out)}))


if __name__ == '__main__':
    main()
