#!/usr/bin/env python3
"""Freeze current real EP50 inputs once; --verify never rewrites a manifest."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,runpy,subprocess,sys
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file() and (p/'site/package.json').is_file())
PIPELINE=ROOT/'episodes/_shared/render_with_references.py'
MANIFEST=D/'source-sha256.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def files(directory):return [p for p in directory.rglob('*') if p.is_file() and not {'node_modules','out','__pycache__','target','build'}.intersection(p.relative_to(directory).parts) and p.suffix not in {'.mp4','.pyc','.class'}]
def fonts(verify=False):
    path=D/'font-environment.json'
    if verify:
        rows=json.loads(path.read_text())
        for row in rows:
            actual=subprocess.check_output(['fc-match','-f','%{file}',row['query']],text=True).strip()
            assert actual==row['file'] and sha(Path(actual))==row['sha256'],'Actual font input changed'
        return
    assert not path.exists(),'Preserve font ledger identity'
    rows=[]
    for family in ['Noto Sans CJK SC','Noto Sans Mono','DejaVu Sans']:
        for weight in ['regular','bold']:
            query=f'{family}:weight={weight}';actual=subprocess.check_output(['fc-match','-f','%{file}',query],text=True).strip()
            rows.append({'query':query,'file':actual,'sha256':sha(Path(actual))})
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
def extras():
    paths=[D/n for n in ['README.md','prepare.py','assemble.py','model.py','model.json','model-timing.json','sync_timing.py','freeze.py','verify.py','render.py','render-final.sh','references-renderer.py','pipeline-tools.py','normalize-color.py','check-references.mjs','references.json','article.mdx','article-figure-plan.json','font-environment.json','cover-board-adaptation.json','voice/input-provenance.json','qa-editorial.json']]
    paths+=[PIPELINE,ROOT/'episodes/_shared/episode_paths.py',ROOT/'site/scripts/episode-paths.mjs',ROOT/'site/scripts/check-references.mjs',ROOT/'episodes/_shared/puzzles-video/references.py',ROOT/'episodes/_shared/append_references_bibliography.py',ROOT/'episodes/_shared/append_references_original.py',ROOT/'episodes/_shared/append_references.py',ROOT/'episodes/_shared/requirements-reference-appendix.txt',ROOT/'episodes/_shared/theme/pageTheme.ts']
    for part in ['sources','examples','covers','remotion/scripts','remotion/public']:
        paths+=files(D/part)
    for part in ['redis-video','redis-covers-v3','middleware-identity']:
        paths+=files(ROOT/'episodes/_shared'/part)
    paths+=list((D/'voice').glob('jobs*.json'))
    declaration=D/'freeze-inputs.json';assert declaration.is_file(),'Root must finalize extra-input declaration before freeze'
    paths.append(declaration)
    for relative in json.loads(declaration.read_text()):
        p=Path(relative);assert not p.is_absolute()
        paths.append(ROOT/p if p.parts[0] in {'episodes','site','docs','scripts'} else D/p)
    for source in json.loads((D/'references.json').read_text())['sources']:
        for field in ['verification','titleEvidence','quotation']:
            if source.get(field,{}).get('evidence'):paths.append(ROOT/source[field]['evidence'])
    resolved=sorted(set(p.resolve() for p in paths))
    for path in resolved:
        assert path.is_relative_to(ROOT) and path.is_file(),f'Missing or external input: {path}'
        assert path.suffix!='.mp4' and path.name not in ['render-result.json','reference-appendix.json','reference-appendix-media-check.json']
    return resolved
def verify():
    fonts(True)
    spec=importlib.util.spec_from_file_location('canonical_reference_pipeline',PIPELINE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.verify_freeze(D)
    manifest=json.loads(MANIFEST.read_text());required=extras()+files(D/'remotion/src')
    absent=[os.path.relpath(p,D) for p in required if os.path.relpath(p,D) not in manifest]
    assert not absent,absent
    print(json.dumps({'passed':True,'readOnly':True,'inputs':len(manifest),'manifestSHA256':sha(MANIFEST)}))
if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    subprocess.run(['node',str(D/'check-references.mjs'),'--sources',str(D)],cwd=ROOT,check=True)
    if args.verify:verify();raise SystemExit()
    assert not MANIFEST.exists(),'Do not overwrite a historical freeze'
    if not (D/'font-environment.json').exists():fonts()
    paths=extras();canonical=ROOT/'episodes/_shared/freeze_sentence_episode.py';sys.argv=[str(canonical),str(D)];runpy.run_path(str(canonical),run_name='__main__')
    manifest=json.loads(MANIFEST.read_text());manifest.update({os.path.relpath(p,D):sha(p) for p in paths});MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())),ensure_ascii=False,indent=2)+'\n');verify()
