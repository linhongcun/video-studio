"""Append a new bibliography section while preserving all previous source prose."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds');rows=[]
    for slug in read(OUT/'startup.json')['selection']:
        prod,pub=ROOT/'episodes-codex'/slug,ROOT/'episodes'/slug;rev=prod/'revisions/reference-endcards'
        baseline,receipt,media=[read(rev/name) for name in ['baseline.json','reference-appendix.json','reference-appendix-media-check.json']]
        output=ROOT/baseline['productionOutput'];assert receipt['presentation']=='title-author' and media['passed']
        assert sha(output)==receipt['outputSHA256']==media['outputSHA256']
        assert receipt['inputs']['bodySHA256']==baseline['originalBodySHA256'] and receipt['bodyFrames']==baseline['bodyFrames']
        source=(prod/'article.mdx').read_text();old_source=(rev/'before-article.mdx').read_text();prefix=old_source.rstrip()
        assert source.startswith(prefix),(slug,'original source prose changed')
        addition=source[len(prefix):].strip()
        assert addition.startswith('## 片尾参考资料'),(slug,'new reference section must be explicit')
        old_article=(rev/'before-published-article.mdx').read_text();article=old_article.rstrip()+'\n\n'+addition+'\n'
        assert article.split('---',2)[:2]==old_article.split('---',2)[:2]
        assert re.findall(r'\{#([\w-]+)\}',article)==re.findall(r'\{#([\w-]+)\}',old_article)
        (pub/'article.mdx').write_text(article)
        patch={'finalVideoFrames':receipt['finalVideoFrames'],'referenceAppendix':{
            'kind':'references','from':receipt['bodyFrames'],'durationInFrames':receipt['appendix']['durationInFrames'],
            'sources':'references.json','manifest':'reference-appendix.json'}}
        result=read(rev/'before-render-result.json') if (rev/'before-render-result.json').exists() else {}
        result.update(frames=receipt['finalVideoFrames'],seconds=receipt['durationSeconds'],decodedFrames=receipt['finalVideoFrames'],
            bytes=output.stat().st_size,sha256=sha(output),bodyFrames=receipt['bodyFrames'],
            sourceInputsVerified=len(read(prod/'source-sha256.json')),**patch,publicationMetadata=patch,
            presentation='title-author',bibliographyOnly=True,
            bodyProvenance='Exact immutable original Git-published movie; no body rerender or new source-to-body equivalence claim.',
            loudnessBasis='Complete original AAC packet/timing and PCM identity passed; no remix or new audio packets.')
        (prod/'render-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for name in ['reference-appendix.json','reference-appendix-media-check.json']:shutil.copyfile(rev/name,prod/name)
        for name in ['references.json','references.md','research.md','source-sha256.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json']:
            shutil.copyfile(prod/name,pub/name)
        shutil.copyfile(output,pub/'video.mp4');meta=read(pub/'meta.json')
        meta.update(**patch,updatedAt=stamp,targetDuration=round(receipt['durationSeconds']))
        for key in ['slug','ep','title','createdAt','publishedAt','firstRelease','sourcePath','platforms']:
            assert meta.get(key)==baseline['metadata'].get(key),(slug,key)
        (pub/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        rows.append({'slug':slug,'bodyFrames':receipt['bodyFrames'],'finalFrames':receipt['finalVideoFrames'],
            'sources':len(receipt['bibliography']),'pages':len(receipt['appendix']['pages']),
            'sha256':sha(output),'originalLectureAudioPreserved':True,'allOriginalArticleAndFootnotesPreserved':True})
    (OUT/'delivery.json').write_text(json.dumps({'checkedAt':stamp,'status':'media-complete-site-pending','episodes':rows},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
