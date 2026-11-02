#!/usr/bin/env python3
"""Stage one checked revision locally; stamp only updatedAt after actual local QA."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from episode_paths import publication_directory, episode_slug

HERE = Path(__file__).resolve().parent
SLUG = 'kafka-consumer-idempotency'
D = ROOT / 'episodes/message-queue/kafka-consumer-idempotency/production/revisions/consumer-replay-v2'
P = publication_directory(SLUG, root=ROOT)
RECEIPT = HERE / 'publication-files.json'
FILES = ['video.mp4', 'references.json', 'reference-appendix.json', 'reference-appendix-media-check.json',
         'article.mdx', 'article-sources.json', 'script.md', 'storyboard.json', 'words.json', 'pronunciation.md']
COVERS = ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', 'poster.jpg', 'cover-style.json']
IDENTITY = ['slug', 'ep', 'title', 'series', 'episodePart', 'createdAt', 'publishedAt', 'firstRelease', 'platforms']
SUMMARY = '沿已提交业务与尚未保存的消费位置，解释同一条记录为何重读，以及业务幂等保护的边界。'


def read(p):
    return json.loads(p.read_text())


def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def original_metadata():
    startup = read(HERE / 'startup.json')
    baseline = startup['baseline']
    assert re.fullmatch(r'[0-9a-f]{40}', baseline)
    original = subprocess.check_output(['git', 'show', baseline + ':' + (P / 'meta.json').relative_to(ROOT).as_posix()], cwd=ROOT)
    meta = json.loads(original)
    assert meta['slug'] == SLUG and meta['ep'] == 45 and meta['title'] == startup['originalTitle']
    assert meta['firstRelease'] == 'v0.97.0' and meta['draft'] is False
    return baseline, original, meta


def preserve_identity(meta, original):
    assert all(meta.get(key) == original.get(key) for key in IDENTITY), 'Revision cannot change first-publication identity'
    assert meta['draft'] is False and meta['poster'] == original['poster']


def checked_assets(final_review):
    assert episode_slug(D) == SLUG
    config = read(D / 'episode-config.json')
    _, _, original = original_metadata()
    assert config['slug'] == SLUG and config['title'] == original['title'] and config['episodePart'] == original['episodePart']
    subprocess.run([sys.executable, str(D / 'freeze.py'), '--verify'], cwd=ROOT, check=True)
    result, appendix, media, exports = [read(D / n) for n in
        ['render-result.json', 'reference-appendix.json', 'reference-appendix-media-check.json', 'article-figures-export.json']]
    video_sha = sha(D / 'video.mp4')
    assert video_sha == result['sha256'] == appendix['outputSHA256'] == media['outputSHA256'] == exports['videoSHA256']
    assert media['passed'] is True and media['bodyDecodedFramesAndTimestampsEqual'] is True and media['audioPacketsAndTimingEqual'] is True
    review_path = final_review.resolve()
    assert review_path.is_relative_to(D), 'Use the actual independent final-media review for this revision'
    review = read(review_path)
    assert review['pass'] is True and review['visualReviewed'] is True and review['videoSHA256'] == video_sha
    assert review['frozenManifestSHA256'] == sha(D / 'source-sha256.json')
    assert exports['visualReviewed'] is True, 'Actual four exported JPEGs require visual review before staging'
    plan = read(D / 'article-figure-plan.json')['figures']
    assert len(plan) == len(exports['figures']) == 4
    pairs = []
    for rel in FILES:
        if rel == 'article-sources.json' and not (D / rel).exists():
            continue
        assert (D / rel).is_file()
        pairs.append((rel, D / rel))
    for planned, exported in zip(plan, exports['figures']):
        rel = planned['file']
        assert re.fullmatch(r'article/consumer-replay-[a-z0-9-]+\.jpg', rel), 'Use new revision-only Figure URLs; retain old publication JPEGs'
        assert exported['file'] == rel and exported['frame'] == planned['frame']
        assert type(planned['frame']) is int and 0 <= planned['frame'] < result['bodyFrames']
        assert abs(planned['seconds'] - planned['frame'] / 30) < 1e-9
        assert (D / rel).resolve().is_relative_to(D / 'article') and (P / rel).resolve().is_relative_to(P / 'article')
        assert sha(D / rel) == exported['sha256']
        pairs.append((rel, D / rel))
    assert len({rel for rel, _ in pairs}) == len(pairs)
    return result, pairs, review_path


def stage(args):
    assert not RECEIPT.exists(), 'Preserve prior staging/failed attempt and select a deliberate recovery'
    baseline, old_bytes, old = original_metadata()
    assert (P / 'meta.json').read_bytes() == old_bytes, 'Original live metadata changed since this revision baseline'
    result, pairs, review_path = checked_assets(args.final_review)
    cover_hashes = {}
    for rel in COVERS:
        old_cover = subprocess.check_output(['git', 'show', baseline + ':' + (P / rel).relative_to(ROOT).as_posix()], cwd=ROOT)
        cover_hashes[rel] = hashlib.sha256(old_cover).hexdigest()
        assert sha(P / rel) == cover_hashes[rel] == sha(D / rel), ('Preserve legacy cover bytes', rel)
    backup = (args.backup_dir or ROOT.parent / '.video-studio-preview-backups' / ('mq05-consumer-replay-' + baseline[:12])).resolve()
    assert not backup.is_relative_to(ROOT), 'Keep reversible full-media backup outside the Git worktree'
    assert not backup.exists(), 'Preserve an existing preview backup'
    original_files = {p.relative_to(P).as_posix(): {'sha256': sha(p), 'mtimeNS': p.stat().st_mtime_ns}
                      for p in P.rglob('*') if p.is_file()}
    # Validate every input before creating a backup or writing publication files.
    planned = {rel: sha(src) for rel, src in pairs}
    backup.mkdir(parents=True)
    for rel in original_files:
        dst = backup / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(P / rel, dst)
        assert sha(dst) == original_files[rel]['sha256']
    receipt = {'status': 'local-revision-staging-in-progress', 'baseline': baseline,
               'productionRevision': D.relative_to(ROOT).as_posix(), 'backupDirectory': str(backup),
               'originalFiles': original_files, 'originalMeta': old, 'legacyCoverSHA256': cover_hashes,
               'plannedFiles': planned, 'files': {}, 'finalReview': review_path.relative_to(ROOT).as_posix(),
               'finalReviewSHA256': sha(review_path)}
    write(RECEIPT, receipt)
    try:
        for rel, src in pairs:
            (P / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, P / rel)
            receipt['files'][rel] = sha(P / rel)
            write(RECEIPT, receipt)
        meta = dict(old)
        meta.update(summary=SUMMARY, description=SUMMARY, sourcePath=(D / 'remotion').relative_to(ROOT).as_posix(),
                    targetDuration=result['finalVideoFrames'] / 30, video='video.mp4', burnedInCaptions=True,
                    **result['publicationMetadata'])
        preserve_identity(meta, old)
        assert meta['updatedAt'] == old['updatedAt']
        write(P / 'meta.json', meta)
        receipt.update(status='staged-local-unpublished-revision', stagedMetaSHA256=sha(P / 'meta.json'),
                       stagedVideoSHA256=sha(P / 'video.mp4'),
                       stagedAtBeijing=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'))
        write(RECEIPT, receipt)
    except Exception as exc:
        receipt.update(status='local-revision-staging-failed', failure=repr(exc))
        write(RECEIPT, receipt)
        raise
    print('Revision staged in local publication files only; first identity and updatedAt preserved. Root may now build locally.')


def publish(args):
    receipt = read(RECEIPT)
    assert receipt['status'] == 'staged-local-unpublished-revision'
    assert re.fullmatch(r'v\d+\.\d+\.\d+', args.release) and args.release == 'v' + read(ROOT / 'site/package.json')['version']
    assert sha(P / 'meta.json') == receipt['stagedMetaSHA256']
    assert all(sha(P / rel) == digest for rel, digest in receipt['files'].items())
    assert all(sha(P / rel) == digest for rel, digest in receipt['legacyCoverSHA256'].items())
    meta = read(P / 'meta.json')
    preserve_identity(meta, receipt['originalMeta'])
    assert meta['updatedAt'] == receipt['originalMeta']['updatedAt']
    review = read(args.local_qa)
    assert review['revisionPreview'] is True and review['pass'] is True and review['visualReviewed'] is True
    assert review['videoSha256'] == sha(P / 'video.mp4') and review['errors'] == [] and review['checks'] and review['exactFrames']
    now = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    assert datetime.fromisoformat(now) >= datetime.fromisoformat(meta['updatedAt'])
    meta['updatedAt'] = now
    write(P / 'meta.json', meta)
    receipt.update(status='prepared-for-revision-site-publication', revisionRelease=args.release,
                   publicationWorkflowStartedAt=now, publishedMetaSHA256=sha(P / 'meta.json'),
                   localQA={'file':str(args.local_qa.resolve()),'sha256':sha(args.local_qa)})
    write(RECEIPT, receipt)
    print('Only updatedAt stamped at actual revision-publication workflow start; original firstRelease/publishedAt preserved.')


def restore():
    receipt = read(RECEIPT)
    assert receipt['status'] in {'staged-local-unpublished-revision', 'local-revision-staging-failed'}
    backup = Path(receipt['backupDirectory'])
    for rel, old in receipt['originalFiles'].items():
        assert sha(backup / rel) == old['sha256']
        if (P / rel).exists():
            acceptable = {old['sha256'], receipt['plannedFiles'].get(rel)}
            if rel == 'meta.json': acceptable.add(receipt.get('stagedMetaSHA256'))
            assert sha(P / rel) in acceptable, ('Unexpected subsequent change; inspect before restoring', rel)
    for rel, expected in receipt['plannedFiles'].items():
        if rel not in receipt['originalFiles'] and (P / rel).exists():
            assert sha(P / rel) == expected
            (P / rel).unlink()
    for rel, old in receipt['originalFiles'].items():
        (P / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup / rel, P / rel)
        assert sha(P / rel) == old['sha256'] and (P / rel).stat().st_mtime_ns == old['mtimeNS']
    receipt['status'] = 'local-preview-restored-original-publication'
    write(RECEIPT, receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--stage', action='store_true')
    group.add_argument('--publish', action='store_true')
    group.add_argument('--restore', action='store_true')
    parser.add_argument('--release')
    parser.add_argument('--final-review', type=Path)
    parser.add_argument('--local-qa', type=Path, default=HERE / 'site-local/report.json')
    parser.add_argument('--backup-dir', type=Path)
    args = parser.parse_args()
    assert args.publish == bool(args.release), 'Only --publish accepts and requires --release'
    if args.stage:
        assert args.final_review, '--stage requires the actual independent final-media review'
        stage(args)
    elif args.publish:
        publish(args)
    else:
        restore()


if __name__ == '__main__':
    main()
