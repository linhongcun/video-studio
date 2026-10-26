"""Publish title/author cards while preserving every original lecture/article."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    results = []
    for row in read(OUT/'startup.json')['episodes']:
        prod, pub, rev = ROOT/row['productionDir'], ROOT/'episodes'/row['slug'], ROOT/row['newArtifacts']
        receipt, media = read(rev/'reference-appendix.json'), read(rev/'reference-appendix-media-check.json')
        output, artifacts = ROOT/row['productionOutput'], ROOT/row['artifacts']
        references = read(prod/'references.json')
        assert receipt['presentation']=='title-author' and media['passed']
        assert sha(output)==receipt['outputSHA256']==media['outputSHA256']
        assert receipt['bodyFrames']==row['bodyFrames']
        assert receipt['inputs']['bodySHA256']==row.get('recoveredBodySHA256',row['originalBodySHA256'])
        assert references['sources']==read(rev/'before-published-references.json')['sources']
        assert sha(pub/'article.mdx')==sha(rev/'before-published-article.mdx')
        assert sha(prod/'article.mdx')==sha(rev/'before-article.mdx')
        assert sha(prod/'research.md')==sha(rev/'before-research.md')
        artifacts.mkdir(parents=True,exist_ok=True)
        page_names={p['file'] for p in receipt['appendix']['pages']}
        for old in artifacts.glob('references-*.png'):
            backup=rev/('before-artifact-'+old.name)
            if not backup.exists():shutil.copyfile(old,backup)
            if old.name not in page_names:old.unlink()
        for name in ['reference-appendix.json','reference-appendix-media-check.json',*sorted(page_names)]:
            shutil.copyfile(rev/name,artifacts/name)
        for name in ['reference-appendix.json','reference-appendix-media-check.json']:
            shutil.copyfile(rev/name,prod/name)
        patch={'finalVideoFrames':receipt['finalVideoFrames'],'referenceAppendix':{
            'kind':'references','from':receipt['bodyFrames'],'durationInFrames':receipt['appendix']['durationInFrames'],
            'sources':'references.json','manifest':'reference-appendix.json'}}
        special=row['slug']=='observer-pattern'
        before=rev/('before-render-result-final.json' if special else 'before-render-result.json')
        result=read(before) if before.exists() else {}
        result.update(frames=receipt['finalVideoFrames'],seconds=receipt['durationSeconds'],decodedFrames=receipt['finalVideoFrames'],
            bytes=output.stat().st_size,sha256=sha(output),bodyFrames=receipt['bodyFrames'],sourceInputsVerified=len(read(prod/'source-sha256.json')),
            **patch,publicationMetadata=patch,presentation='title-author',bibliographyOnly=True,
            loudnessBasis='Original complete AAC packets/timing and decoded PCM preserved; no voice remix or extra audio packets.')
        result_path=prod/('render-result-final.json' if special else 'render-result.json')
        result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for name in ['references.json','source-sha256.json','reference-appendix.json','reference-appendix-media-check.json']:
            shutil.copyfile(prod/name,pub/name)
        shutil.copyfile(result_path,pub/'render-result.json')
        if special and (pub/'render-result-final.json').exists():shutil.copyfile(result_path,pub/'render-result-final.json')
        shutil.copyfile(output,pub/'video.mp4')
        meta=read(pub/'meta.json');meta.update(**patch,updatedAt=stamp,targetDuration=round(receipt['durationSeconds']))
        for key in ['slug','ep','title','createdAt','publishedAt','firstRelease','sourcePath','platforms']:
            assert meta.get(key)==row['metadata'].get(key),(row['slug'],key)
        (pub/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        results.append({'slug':row['slug'],'bodyFrames':receipt['bodyFrames'],'finalFrames':receipt['finalVideoFrames'],
            'sources':len(receipt['bibliography']),'pages':len(receipt['appendix']['pages']),
            'sha256':sha(output),'lectureAudioCodePreserved':True,'publicAndSourceArticleUnchanged':True})
    (OUT/'delivery.json').write_text(json.dumps({'checkedAt':stamp,'status':'media-complete-site-pending','episodes':results},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
