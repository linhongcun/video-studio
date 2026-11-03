#!/usr/bin/env python3
"""Ordinary canonical GET checks; no cache-busting or browser-result claims."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, subprocess, urllib.request
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
D=Path(__file__).resolve().parents[1]
P=D.parent/'publication'
BASE='https://linhongcun.github.io/video-studio'
spec=importlib.util.spec_from_file_location('served_html_checks',ROOT/'scripts/verify-online.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);a=ap.parse_args()
    checks=[]
    def get(path):
        url=BASE+path
        with urllib.request.urlopen(url,timeout=120) as r:
            body=r.read();checks.append({'url':url,'status':r.status,'bytes':len(body),'sha256':sha(body)});assert r.status==200
        return body
    meta=json.loads((P/'meta.json').read_text());sb=json.loads((P/'storyboard.json').read_text())
    for name in [meta['video'],meta['poster'],'article/01.jpg','article/02.jpg']:
        assert sha(get('/episodes/birthday-paradox/'+name))==sha((P/name).read_bytes()),name
    vtt,groups,frames=module.frozen_vtt_and_chapters(sb)
    assert get('/episodes/birthday-paradox/captions.vtt')==vtt
    page=module.Page(get('/episodes/birthday-paradox/'))
    assert page.h1==meta['title'] and len(page.chapters)==4
    for actual,group in zip(page.chapters,groups):
        assert actual['id'] in group['ids'] and abs(actual['start']-group['start'])<1e-6
    assert f'https://github.com/linhongcun/video-studio/tree/main/{meta["sourcePath"]}' in page.links
    assert meta['finalVideoFrames']==frames+150
    for path in ['/series/puzzles/','/episodes/','/rss.xml']:
        assert 'birthday-paradox' in get(path).decode()
    changelog=module.Page(get('/changelog/'));assert changelog.contains_version(a.version)
    assert f'https://github.com/linhongcun/video-studio/releases/tag/{a.version}' in changelog.links, 'real release link missing from changelog'
    release=json.loads(subprocess.check_output(['gh','api',f'repos/linhongcun/video-studio/releases/tags/{a.version}'],text=True))
    assert release['tag_name']==a.version and not release['draft']
    result={'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':True,'httpChecks':checks,'captions':22,'chapters':page.chapters,'bodyFrames':frames,'finalFrames':meta['finalVideoFrames'],'release':{k:release[k] for k in ['tag_name','html_url','published_at','target_commitish']},'scope':'Full HTTP bytes, frozen captions/chapters, source link, series/index/RSS and true release changelog. Browser playback and actual reading checked separately.'}
    (D/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'canonicalGETs':len(checks),'videoSHA256':checks[0]['sha256'],'release':release['html_url']},ensure_ascii=False))
if __name__=='__main__':main()
