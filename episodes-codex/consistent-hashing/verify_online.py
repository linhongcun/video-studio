#!/usr/bin/env python3
"""Ordinary canonical GETs after the Release-following Pages deployment.

Full media streams are hashed without retaining remote bodies. No Range,
cache-busting URL, forced-cache header, silent retry or manufactured UI result.
"""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import urllib.request

D=Path(__file__).resolve().parent
ROOT=D.parents[1]
BASE='https://linhongcun.github.io/video-studio/'
SLUG='consistent-hashing'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--release',required=True)
    args=ap.parse_args()
    meta=json.loads((ROOT/'episodes'/SLUG/'meta.json').read_text())
    assert meta['firstRelease']==args.release and meta['draft'] is False
    render=json.loads((D/'render-result.json').read_text())
    assert sha(D/'video.mp4')==render['sha256']
    rows=[]
    report={'status':'in-progress','checkedAtUTC':datetime.now(timezone.utc).isoformat(),
        'checkedAtBeijing':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'release':args.release,'page':BASE+'episodes/'+SLUG+'/',
        'transport':'ordinary canonical urllib GET via inherited proxy and CA trust',
        'retryCount':0,'rangeRequests':False,'cacheBusting':False,'requests':rows}
    def save(): (D/'online-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def fetch(relative,local=None):
        url=relative if relative.startswith('https://') else BASE+relative
        with urllib.request.urlopen(url,timeout=60) as response:
            status=response.status
            assert status==200,(url,status)
            digest=hashlib.sha256();count=0;body=[]
            while True:
                block=response.read(256*1024)
                if not block: break
                digest.update(block);count+=len(block)
                if local is None: body.append(block)
            item={'url':url,'finalURL':response.url,'status':status,'bytes':count,'sha256':digest.hexdigest()}
        if local is not None:
            item['localFile']=str(local.relative_to(ROOT));item['expectedSHA256']=sha(local)
            assert item['sha256']==item['expectedSHA256'],item
        rows.append(item);save();print('verified',url,flush=True)
        return b''.join(body).decode('utf-8') if local is None else item
    try:
        page=fetch('episodes/'+SLUG+'/')
        for text in [meta['title'],'工程算法','video.mp4','captions.vtt']:
            assert text in page,('page missing',text)
        sb=json.loads((D/'storyboard.json').read_text())
        chapter_ids=list(dict.fromkeys(s['chapterId'] for sc in sb['scenes'] for s in sc['shots']))
        for chapter in chapter_ids: assert ('id="'+chapter+'"') in page,chapter
        for name in ['video.mp4','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg']:
            fetch('episodes/'+SLUG+'/'+name,ROOT/'episodes'/SLUG/name)
        fetch('episodes/'+SLUG+'/captions.vtt',ROOT/'site/dist/episodes'/SLUG/'captions.vtt')
        lesson='/video-studio/episodes/'+SLUG+'/'
        for relative in ['series/engineering-algorithms/','learn/','library/','']:
            html=fetch(relative);assert lesson in html,(relative,'lesson link missing');assert '工程算法' in html
        changelog=fetch('changelog/')
        release_url='https://github.com/linhongcun/video-studio/releases/tag/'+args.release
        assert release_url in changelog,('actual release entry missing',args.release)
        release=json.loads(fetch('https://api.github.com/repos/linhongcun/video-studio/releases/tags/'+args.release))
        assert release['tag_name']==args.release and release['html_url']==release_url
        assert release['draft'] is False and release['prerelease'] is False and release['published_at']
        assert report['page'] in release['body'],'Release must identify this lesson'
        report.update(status='passed',requestCount=len(rows),chapterCount=len(chapter_ids),
            frames=render['frames'],mediaSHA256=render['sha256'],
            note='HTTP/content identity verification; actual local browser playback is reported separately.')
        save()
    except Exception as exc:
        report.update(status='failed',error=repr(exc));save();raise

if __name__=='__main__': main()
