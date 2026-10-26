"""Encode only replacement bibliography pages, using immutable original bodies."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
GENERATOR=ROOT/'episodes-codex/_shared/append_references_bibliography.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def render(row):
    prod=ROOT/row['productionDir'];refs=prod/'references.json';frozen=json.loads((prod/'source-sha256.json').read_text())
    for path in [refs,GENERATOR,ROOT/'episodes-codex/_shared/render_with_references.py',ROOT/'site/scripts/check-references.mjs']:
        relative=str(path.relative_to(ROOT))
        assert any((prod/name).resolve()==path.resolve() and value==sha(path) for name,value in frozen.items()),relative
    body=ROOT/row['bodyPath'];assert sha(body)==row.get('recoveredBodySHA256',row['originalBodySHA256'])
    # A replacement output must carry its authentic earlier receipt. Preserve
    # that published/producer receipt in this revision before invoking the
    # unchanged engine's deliberate overwrite protection.
    output=ROOT/row['productionOutput'];revision=ROOT/row['newArtifacts'];manifest=revision/'reference-appendix.json'
    if output.exists() and not manifest.exists() and sha(output)!=sha(body):
        snapshots=[revision/'before-published-reference-appendix.json',revision/'before-reference-appendix.json']
        previous=next((p for p in snapshots if p.is_file() and json.loads(p.read_text())['outputSHA256']==sha(output)),None)
        if previous is None:
            raise ValueError(row['slug']+': current producer output has no matching historical receipt')
        manifest.write_bytes(previous.read_bytes())
        (revision/'receipt-migration.json').write_text(json.dumps({'source':str(previous.relative_to(ROOT)),
            'copiedReceiptSHA256':sha(previous),'previousOutputSHA256':sha(output),
            'scope':'Exact authentic historical receipt copied; not a new media proof or rewritten identity.'},indent=2)+'\n')
    log=Path('/workspace/scratch')/('title-author-'+row['slug']+'.log')
    args=['python3',str(GENERATOR),'append','--body',str(body),'--references',str(refs),
          '--output',str(ROOT/row['productionOutput']),'--artifacts',str(ROOT/row['newArtifacts'])]
    with log.open('w') as stream:
        process=subprocess.run(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    if process.returncode:
        raise RuntimeError(row['slug']+': '+log.read_text()[-2400:])
    receipt=json.loads((ROOT/row['newArtifacts']/'reference-appendix.json').read_text())
    media=json.loads((ROOT/row['newArtifacts']/'reference-appendix-media-check.json').read_text())
    assert media['passed'] and receipt['presentation']=='title-author'
    assert receipt['bodyFrames']==row['bodyFrames'] and receipt['finalVideoFrames']==row['bodyFrames']+150
    old=json.loads((ROOT/row['newArtifacts']/'before-published-reference-appendix-media-check.json').read_text())
    for field in ['bodyFrameMD5RowsSHA256','audioPacketPayloadAndTimingSHA256','decodedAudioPCM']:
        assert media[field]==old[field],(row['slug'],field)
    return {'slug':row['slug'],'bodyFrames':receipt['bodyFrames'],'finalFrames':receipt['finalVideoFrames'],
        'pages':len(receipt['appendix']['pages']),'sources':len(receipt['bibliography']),'sha256':receipt['outputSHA256'],
        'originalHistoricalFramePTSAACPCMProofMatched':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('slugs',nargs='*');parser.add_argument('--report',default='media-results.json');args=parser.parse_args()
    rows=json.loads((OUT/'startup.json').read_text())['episodes']
    if args.slugs:rows=[row for row in rows if row['slug'] in args.slugs]
    results=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks={pool.submit(render,row):row['slug'] for row in rows}
        for future in as_completed(tasks):
            result=future.result();results.append(result);print(json.dumps(result),flush=True)
    (OUT/args.report).write_text(json.dumps({'workers':3,'episodes':sorted(results,key=lambda x:x['slug'])},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
