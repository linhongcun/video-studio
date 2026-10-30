#!/usr/bin/env python3
"""Install checked final media as drafts, or mark them ready for the publication workflow."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent
SUMMARIES = {
    'kafka-consumer-idempotency': '从同键的并发竞争、返回行判断与本地事务，解释重读怎样避免重复增加积分。',
    'kafka-message-ordering': '沿同Key路由、分区日志与客户端交付，解释为何还要让同一订单的业务按序完成。',
    'kafka-message-backlog': '从两分区的归属形成、串行通知步骤与逐区积压变化，解释增加实例为何可能无法提速。',
}
FILES = ['video.mp4', 'references.json', 'reference-appendix.json', 'reference-appendix-media-check.json',
         'article.mdx', 'article-sources.json', 'script.md', 'storyboard.json', 'words.json', 'pronunciation.md']


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def publication_batch(receipt, info, now):
    """Validate the whole draft batch before the caller writes any timestamps."""
    assert receipt['status'] == 'installed-as-unpublished-drafts'
    assert [e['slug'] for e in receipt['episodes']] == [e['slug'] for e in info['episodes']]
    prepared = []
    for ep, expected in zip(receipt['episodes'], info['episodes']):
        p = ROOT / 'episodes' / ep['slug']
        assert all(sha(p / rel) == h for rel, h in ep['files'].items())
        m = read(p / 'meta.json')
        assert m['slug'] == expected['slug'] and m['ep'] == expected['ep'] and m['title'] == expected['title']
        assert m['createdAt'] == info['startedAtBeijing']
        assert m['sourcePath'] == f"episodes-codex/{ep['slug']}/remotion"
        assert m.get('platforms') == {} and m['series'] == 'message-queue'
        assert m['draft'] is True and not m.get('publishedAt') and not m.get('firstRelease')
        assert datetime.fromisoformat(now) >= datetime.fromisoformat(m['createdAt'])
        prepared.append((p / 'meta.json', m))
    return prepared


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--publish', action='store_true')
    ap.add_argument('--release')
    args = ap.parse_args()
    assert args.publish == bool(args.release), '--publish and --release are used together'
    info = read(HERE / 'episodes.json')
    now = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    if args.publish:
        receipt = read(HERE / 'publication-files.json')
        prepared = publication_batch(receipt, info, now)
        for path, m in prepared:
            m.update(draft=False, publishedAt=now, firstRelease=args.release)
            write(path, m)
        receipt.update(status='prepared-for-first-site-publication', publicationWorkflowStartedAt=now, release=args.release)
        write(HERE / 'publication-files.json', receipt)
        print('First-publication metadata stamped at actual publication-workflow start; rebuild production site next.')
        return
    target = HERE / 'publication-files.json'
    assert not target.exists(), 'Preserve an earlier install receipt and review before reinstalling'
    report = {'status': 'installed-as-unpublished-drafts', 'installedAtBeijing': now, 'episodes': []}
    for expected in info['episodes']:
        slug = expected['slug']
        d = ROOT / 'episodes-codex' / slug
        p = ROOT / 'episodes' / slug
        m = read(p / 'meta.json')
        assert m['draft'] is True and m['createdAt'] == info['startedAtBeijing']
        assert m['title'] == expected['title'] and m['ep'] == expected['ep']
        assert m.get('platforms') == {} and not m.get('publishedAt') and not m.get('firstRelease')
        config = read(d / 'episode-config.json')
        assert config['episodePart'] == m['episodePart']
        subprocess.run([sys.executable, str(d / 'freeze.py'), '--verify'], cwd=ROOT, check=True)
        result = read(d / 'render-result.json')
        appendix = read(d / 'reference-appendix.json')
        exports = read(d / 'article-figures-export.json')
        assert sha(d / 'video.mp4') == result['sha256'] == appendix['outputSHA256'] == exports['videoSHA256']
        assert exports['visualReviewed'] is True, 'Review actual JPEGs before install'
        copied = {}
        for rel in FILES:
            src = d / rel
            if rel == 'article-sources.json' and not src.exists():
                continue
            assert src.is_file()
            shutil.copyfile(src, p / rel)
            copied[rel] = sha(p / rel)
        for fig in exports['figures']:
            rel = fig['file']
            assert sha(d / rel) == fig['sha256']
            (p / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(d / rel, p / rel)
            copied[rel] = sha(p / rel)
        for rel in ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', 'poster.jpg', 'cover-style.json']:
            assert sha(p / rel) == sha(d / rel), ('Existing checked new cover mismatch', slug, rel)
            copied[rel] = sha(p / rel)
        m.update(summary=SUMMARIES[slug], description=SUMMARIES[slug], updatedAt=now,
                 sourcePath=f'episodes-codex/{slug}/remotion', targetDuration=result['finalVideoFrames'] / 30,
                 burnedInCaptions=True, **result['publicationMetadata'])
        write(p / 'meta.json', m)
        report['episodes'].append({'slug': slug, 'ep': m['ep'], 'title': m['title'],
                                    'createdAt': m['createdAt'], 'draftAtInstall': True,
                                    'productionArticleSHA256': sha(d / 'article.mdx'),
                                    'publishedArticleSHA256': sha(p / 'article.mdx'),
                                    'articleDerivation': 'none; exact frozen production bytes', 'files': copied})
    write(target, report)
    print('Installed three checked episodes as drafts; use SHOW_DRAFTS=1 for local preview, not first-publication timestamps.')


if __name__ == '__main__':
    main()
