"""Copy checked original-title appendices; keep lecture/core and article anchors."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(p):
    return json.loads(p.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slugs', nargs='*')
    args = parser.parse_args()
    slugs = args.slugs or [x['slug'] for x in read(OUT/'startup.json')['episodes']]
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    rows = []
    for slug in slugs:
        d, pub = ROOT/'episodes-codex'/slug, ROOT/'episodes'/slug
        baseline = read(d/'revisions/original-titles/baseline.json')
        output = Path(baseline['productionOutput'])
        artifact = d/('revisions/observer-first/reference-appendix' if slug=='observer-pattern' else 'revisions/reference-endcards')
        receipt, media = read(artifact/'reference-appendix.json'), read(artifact/'reference-appendix-media-check.json')
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        assert receipt['presentation']=='original-title-quote' and media['passed'] is True
        assert digest==receipt['outputSHA256']==media['outputSHA256']
        patch = {'finalVideoFrames': receipt['finalVideoFrames'], 'referenceAppendix': {
            'kind':'references', 'from':receipt['bodyFrames'], 'durationInFrames':receipt['appendix']['durationInFrames'],
            'sources':'references.json', 'manifest':'reference-appendix.json'}}
        old_result = d/'revisions/original-titles'/('before-render-result-final.json' if slug=='observer-pattern' else 'before-render-result.json')
        result = read(old_result) if old_result.exists() else {}
        result.update(frames=receipt['finalVideoFrames'], seconds=receipt['durationSeconds'], sha256=digest,
            bytes=output.stat().st_size, bodyFrames=receipt['bodyFrames'], **patch, publicationMetadata=patch,
            presentation='original-title-quote', originalTitlesAndVerbatimQuotes=True,
            loudnessBasis='The complete pre-appendix AAC packets/PTS and decoded PCM are unchanged; no voice remix.')
        result_path = d/('render-result-final.json' if slug=='observer-pattern' else 'render-result.json')
        result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        for name in ('reference-appendix.json','reference-appendix-media-check.json'):
            shutil.copyfile(artifact/name,d/name)
        source, current = (d/'article.mdx').read_text(), (pub/'article.mdx').read_text()
        if slug=='observer-pattern': marker=r'^### 资料与阅读范围[^\n]*\n'
        elif slug=='http-request': marker=r'^## 公开来源与核验范围[^\n]*\n'
        elif slug in ('dns','https'): marker=r'^## 适用边界与来源[^\n]*\n'
        elif slug=='browser-cache': marker=r'^## 片尾参考资料[^\n]*\n'
        else: marker=r'^## (?:片尾)?参考资料[^\n]*\n'
        a,b = re.search(marker,source,re.M),re.search(marker,current,re.M)
        assert a,(slug,'Locate actual source section before copying')
        if b:
            current=current[:b.end()]+source[a.end():]
        else:
            assert slug=='egg-drop',(slug,'Existing reference section is required')
            current=current.rstrip()+'\n\n'+source[a.start():]
        old_article=subprocess.check_output(['git','show',baseline['baseCommit']+f':episodes/{slug}/article.mdx'],cwd=ROOT,text=True)
        assert current.split('---',2)[:2]==old_article.split('---',2)[:2]
        assert re.findall(r'\{#([\w-]+)\}',current)==re.findall(r'\{#([\w-]+)\}',old_article)
        (pub/'article.mdx').write_text(current)
        for name in ('references.json','references.md','research.md','source-sha256.json','reference-appendix.json','reference-appendix-media-check.json'):
            if (d/name).is_file():shutil.copyfile(d/name,pub/name)
        shutil.copyfile(output,pub/'video.mp4')
        shutil.copyfile(result_path,pub/'render-result.json')
        if slug=='observer-pattern' and (pub/'render-result-final.json').exists():shutil.copyfile(result_path,pub/'render-result-final.json')
        meta=read(pub/'meta.json');meta.update(**patch,updatedAt=stamp,targetDuration=round(receipt['durationSeconds']))
        for key in ('slug','title','createdAt','publishedAt','firstRelease','sourcePath','platforms'):
            assert meta.get(key)==baseline['metadata'].get(key),(slug,key)
        (pub/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        rows.append({'slug':slug,'bodyFrames':receipt['bodyFrames'],'finalFrames':receipt['finalVideoFrames'],
            'sources':len(receipt['sourceTitles']),'pages':len(receipt['appendix']['pages']),'sha256':digest,
            'lectureAndCodeCardPreserved':True,'publicArticleFrontmatterAndAnchorsPreserved':True})
    (OUT/'delivery.json').write_text(json.dumps({'checkedAt':stamp,'status':'media-complete-site-pending','episodes':rows},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
