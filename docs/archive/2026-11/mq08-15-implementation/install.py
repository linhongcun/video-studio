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
import sys
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from episode_paths import production_directory, publication_directory, episode_slug, resolve_repo_path
HERE = Path(__file__).resolve().parent
SUMMARIES = {
    'kafka-retry-dead-letter': '沿持久重试预算、应用等待与死信写入确认，解释何时停止重试以及何时提交原消息进度。',
    'kafka-replica-acks': '沿Leader追加、Follower复制进度与当前ISR，解释成功确认的依据和副本不足时的边界。',
}
FILES = ['video.mp4', 'references.json', 'reference-appendix.json', 'reference-appendix-media-check.json',
         'article.mdx', 'article-sources.json', 'script.md', 'storyboard.json', 'words.json', 'pronunciation.md']


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def publication_batch(receipt, info, now, local_qa_root):
    """Validate the whole draft batch before the caller writes any timestamps."""
    assert receipt['status'] == 'installed-as-unpublished-drafts'
    assert [e['slug'] for e in receipt['episodes']] == [e['slug'] for e in info['episodes']]
    prepared = []
    for ep, expected in zip(receipt['episodes'], info['episodes']):
        p = publication_directory(ep['slug'], root=ROOT)
        assert all(sha(p / rel) == h for rel, h in ep['files'].items())
        m = read(p / 'meta.json')
        assert m['slug'] == expected['slug'] and m['ep'] == expected['ep'] and m['title'] == expected['title']
        assert m['createdAt'] == info['startedAtBeijing']
        assert m['sourcePath'] == (production_directory(ep['slug'], root=ROOT) / 'remotion').relative_to(ROOT).as_posix()
        assert m.get('platforms') == {} and m['series'] == 'message-queue'
        assert m['draft'] is True and not m.get('publishedAt') and not m.get('firstRelease')
        assert datetime.fromisoformat(now) >= datetime.fromisoformat(m['createdAt'])
        review = read(local_qa_root / ep['slug'] / 'report.json')
        assert review['draftPreview'] is True and review['pass'] is True and review['visualReviewed'] is True
        assert review['videoSha256'] == sha(p / 'video.mp4') and review['errors'] == []
        assert review['checks'] and review['exactFrames'], 'Actual native draft preview and image review required'
        prepared.append((p / 'meta.json', m))
    return prepared


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--publish', action='store_true')
    ap.add_argument('--release')
    ap.add_argument('--local-qa-root', type=Path, default=HERE / 'site-local')
    args = ap.parse_args()
    assert args.publish == bool(args.release), '--publish and --release are used together'
    info = read(HERE / 'episodes.json')
    now = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    if args.publish:
        receipt = read(HERE / 'publication-files.json')
        prepared = publication_batch(receipt, info, now, args.local_qa_root.resolve())
        for path, m in prepared:
            m.update(draft=False, publishedAt=now, firstRelease=args.release)
            write(path, m)
        receipt.update(status='prepared-for-first-site-publication', publicationWorkflowStartedAt=now, release=args.release,
                       localDraftQA=[{'slug': ep['slug'], 'reportSHA256': sha(args.local_qa_root / ep['slug'] / 'report.json')}
                                     for ep in receipt['episodes']])
        write(HERE / 'publication-files.json', receipt)
        print('First-publication metadata stamped at actual publication-workflow start; rebuild production site next.')
        return
    target = HERE / 'publication-files.json'
    assert not target.exists(), 'Preserve an earlier install receipt and review before reinstalling'
    report = {'status': 'installed-as-unpublished-drafts', 'installedAtBeijing': now, 'episodes': []}
    for expected in info['episodes']:
        slug = expected['slug']
        d = production_directory(slug, root=ROOT)
        p = publication_directory(slug, root=ROOT)
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
        plan = read(d / 'article-figure-plan.json')['figures']
        assert [f['file'] for f in exports['figures']] == [f['file'] for f in plan]
        assert all(x['frame'] == y['frame'] for x, y in zip(exports['figures'], plan))
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
                 sourcePath=(d / 'remotion').relative_to(ROOT).as_posix(), targetDuration=result['finalVideoFrames'] / 30,
                 video='video.mp4', poster='cover-16x9.jpg', burnedInCaptions=True, **result['publicationMetadata'])
        write(p / 'meta.json', m)
        report['episodes'].append({'slug': slug, 'ep': m['ep'], 'title': m['title'],
                                    'createdAt': m['createdAt'], 'draftAtInstall': True,
                                    'productionArticleSHA256': sha(d / 'article.mdx'),
                                    'publishedArticleSHA256': sha(p / 'article.mdx'),
                                    'articleDerivation': 'none; exact frozen production bytes', 'files': copied})
    write(target, report)
    print('Installed batch checked episodes as drafts; use SHOW_DRAFTS=1 for local preview, not first-publication timestamps.')


if __name__ == '__main__':
    main()
