"""Publish verified appendix outputs without changing existing article bodies."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    rows = []
    for slug in read(OUT/'startup.json')['selection']:
        prod, pub = ROOT/'episodes-codex'/slug, ROOT/'episodes'/slug
        rev = prod/'revisions/reference-endcards'
        baseline, receipt, media = [read(rev/name) for name in ('baseline.json','reference-appendix.json','reference-appendix-media-check.json')]
        output = ROOT/baseline['productionOutput']
        assert receipt['presentation']=='original-title-quote' and media['passed']
        assert sha(output)==receipt['outputSHA256']==media['outputSHA256']
        assert receipt['bodyFrames']==baseline['bodyFrames']
        assert receipt['inputs']['bodySHA256']==baseline['originalBodySHA256']
        patch = {'finalVideoFrames':receipt['finalVideoFrames'],'referenceAppendix':{
            'kind':'references','from':receipt['bodyFrames'],'durationInFrames':receipt['appendix']['durationInFrames'],
            'sources':'references.json','manifest':'reference-appendix.json'}}
        result_path = prod/'render-result.json'
        result = read(rev/'before-render-result.json') if (rev/'before-render-result.json').exists() else {}
        result.update(frames=receipt['finalVideoFrames'],seconds=receipt['durationSeconds'],sha256=sha(output),
            bytes=output.stat().st_size,bodyFrames=receipt['bodyFrames'],decodedFrames=receipt['finalVideoFrames'],
            sourceInputsVerified=len(read(prod/'source-sha256.json')),**patch,publicationMetadata=patch,
            presentation='original-title-quote',originalTitlesAndVerbatimQuotes=True,
            loudnessBasis='Original AAC packets/timing and decoded PCM are identical; no audio remix or added packets.')
        result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for name in ('reference-appendix.json','reference-appendix-media-check.json'):
            shutil.copyfile(rev/name,prod/name)
        source = (prod/'article.mdx').read_text()
        original_source = (rev/'before-article.mdx').read_text()
        old_article = (rev/'before-published-article.mdx').read_text()
        marker = re.search(r'^## (?:片尾)?参考资料[^\n]*\n',source,re.M)
        assert marker, (slug,'Source article must expose a reference section')
        assert source[:marker.start()].rstrip()==original_source.rstrip(), (slug,'Source lecture changed')
        article = old_article.rstrip()+'\n\n'+source[marker.start():].rstrip()+'\n'
        assert article.split('---',2)[:2]==old_article.split('---',2)[:2]
        assert re.findall(r'\{#([\w-]+)\}',article)==re.findall(r'\{#([\w-]+)\}',old_article)
        (pub/'article.mdx').write_text(article)
        for name in ('references.json','references.md','research.md','source-sha256.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json'):
            shutil.copyfile(prod/name,pub/name)
        shutil.copyfile(output,pub/'video.mp4')
        meta = read(pub/'meta.json')
        meta.update(**patch,updatedAt=stamp,targetDuration=round(receipt['durationSeconds']))
        for key in ('slug','title','createdAt','publishedAt','firstRelease','sourcePath','platforms'):
            assert meta.get(key)==baseline['metadata'].get(key),(slug,key)
        (pub/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        rows.append({'slug':slug,'bodyFrames':receipt['bodyFrames'],'finalFrames':receipt['finalVideoFrames'],
            'sources':len(receipt['sourceTitles']),'pages':len(receipt['appendix']['pages']),
            'sha256':sha(output),'lectureAudioAndCodeCardPreserved':True,'originalArticleAndAnchorsPreserved':True})
    (OUT/'delivery.json').write_text(json.dumps({'checkedAt':stamp,'status':'media-complete-site-pending','episodes':rows},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
