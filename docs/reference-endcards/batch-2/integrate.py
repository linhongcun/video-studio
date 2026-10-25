"""Publish only the verified reference appendix outputs; preserve original body inputs."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGETS = ('http-request', 'cdn', 'cookie-session')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    spec = importlib.util.spec_from_file_location('reference_pipeline', ROOT/'episodes-codex/_shared/render_with_references.py')
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    rows = []
    for slug in TARGETS:
        source, published = ROOT/'episodes-codex'/slug, ROOT/'episodes'/slug
        rev = source/'revisions/reference-endcards'
        baseline, previous = read(rev/'baseline.json'), read(rev/'body-source-sha256.json')
        changed = [name for name, expected in previous.items() if sha(source/name) != expected]
        assert set(changed) <= {'research.md', 'article.mdx', 'freeze.py', 'remotion/package.json'}, (slug, changed)
        wrapper.verify_freeze(source)
        receipt, media = read(rev/'reference-appendix.json'), read(rev/'reference-appendix-media-check.json')
        assert media['passed'] and receipt['outputSHA256'] == sha(source/'video.mp4') == media['outputSHA256']
        original = read(rev/'body-render-result.json')
        patch = {'finalVideoFrames': receipt['finalVideoFrames'], 'referenceAppendix': {
            'kind': 'references', 'from': receipt['bodyFrames'],
            'durationInFrames': receipt['appendix']['durationInFrames'],
            'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
        result = dict(original)
        result.update(frames=receipt['finalVideoFrames'], seconds=receipt['durationSeconds'],
                      sha256=receipt['outputSHA256'], bytes=(source/'video.mp4').stat().st_size,
                      bodyFrames=receipt['bodyFrames'], **patch, publicationMetadata=patch,
                      checks='Actual appendix encoding and full decoded body/timestamp/AAC/PCM preservation passed; independent visual and player review are recorded separately.',
                      loudnessBasis='Original decoded audio PCM is exactly unchanged; retain original loudness measurement without remixing.')
        (source/'render-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
            shutil.copyfile(rev/name, source/name)
        wrapper.verify_delivery(source, receipt, media)
        text = (source/'article.mdx').read_text()
        current = (published/'article.mdx').read_text()
        old_article = subprocess.check_output(['git', 'show', baseline['baseCommit']+f':episodes/{slug}/article.mdx'], cwd=ROOT, text=True)
        if slug == 'http-request':
            marker = r'^## 公开来源与核验范围[^\n]*\n'
            a, b = re.search(marker, text, re.M), re.search(marker, current, re.M)
            assert a and b, 'Keep the existing HTTP source section and its anchor'
            current = current[:b.end()] + text[a.end():]
        else:
            marker = re.search(r'^## 参考资料\s*\n', text, re.M)
            assert marker, 'Append one explicit reference section to the source article'
            assert not re.search(r'^## 参考资料\s*\n', current, re.M), 'Do not append twice'
            current = current.rstrip()+'\n\n'+text[marker.start():]
        assert current.split('---', 2)[:2] == old_article.split('---', 2)[:2]
        assert re.findall(r'\{#([\w-]+)\}', current) == re.findall(r'\{#([\w-]+)\}', old_article)
        (published/'article.mdx').write_text(current)
        for name in ('video.mp4', 'render-result.json', 'research.md', 'references.json', 'references.md',
                     'source-sha256.json', 'reference-appendix.json', 'reference-appendix-media-check.json'):
            shutil.copyfile(source/name, published/name)
        meta = read(published/'meta.json')
        meta.update(**patch, updatedAt=stamp, targetDuration=round(receipt['durationSeconds']))
        for key in ('slug', 'title', 'createdAt', 'publishedAt', 'firstRelease', 'sourcePath', 'platforms'):
            assert meta[key] == baseline['publishedMetadata'][key], (slug, key)
        (published/'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n')
        rows.append({'slug': slug, 'bodyFrames': receipt['bodyFrames'], 'finalFrames': receipt['finalVideoFrames'],
                     'seconds': receipt['durationSeconds'], 'referenceCount': len(receipt['appendix']['sourceIds']),
                     'referencePages': len(receipt['appendix']['pages']), 'finalSHA256': receipt['outputSHA256'],
                     'bodySHA256': receipt['inputs']['bodySHA256'], 'originalBodyInputsPreserved': True,
                     'publicArticleFrontmatterAndAnchorsPreserved': True,
                     'sourceFreezeCount': len(read(source/'source-sha256.json'))})
    (OUT/'delivery.json').write_text(json.dumps({'checkedAt': stamp, 'status': 'media-complete-site-pending', 'episodes': rows}, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
