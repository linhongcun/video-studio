#!/usr/bin/env python3
"""Read-only independent checks against the renderer's actual frozen closure."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import importlib.util
import json

ROOT=next(parent for parent in Path(__file__).resolve().parents if (parent/'.git').exists())
OUT=ROOT/'work/peak-video-style/independent'
SLUGS=('rate-limit','idempotency','circuit-breaker','degradation')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
path=ROOT/'episodes-codex/_shared/peak-video/render.py'
spec=importlib.util.spec_from_file_location('independent_actual_renderer',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
rows={}
for slug in SLUGS:
    ctx=module.context(SimpleNamespace(episode=slug,revision='peak-style',baseline=None,entry='src/peak-style/index.ts',composition='Main'))
    actual=module.production_inputs(ctx,module.adapter_module())
    manifest=json.loads(ctx.manifest.read_text())
    expected=set(manifest['inputs'])
    closure={str(p.relative_to(ROOT)) for p in actual}
    needed={
        'episodes-codex/_shared/peak-video/render.py',
        'episodes-codex/_shared/peak-video/references.py',
        'episodes-codex/_shared/peak-video/Frame.tsx',
        'episodes-codex/_shared/peak-video/theme.ts',
        'episodes-codex/_shared/peak-video/style-v1.json',
        'episodes-codex/_shared/peak-covers/style-v1.json',
        'episodes-codex/_shared/puzzles-video/render.py',
        'episodes-codex/_shared/puzzles-video/references.py',
        f'episodes-codex/{slug}/remotion/src/Main.tsx',
        f'episodes-codex/{slug}/remotion/src/data.ts',
        f'episodes-codex/{slug}/remotion/src/peak-style/Main.tsx',
        f'episodes-codex/{slug}/storyboard.json',
        f'episodes-codex/{slug}/words.json',
        f'episodes-codex/{slug}/script.md',
        f'episodes-codex/{slug}/references.json',
        f'episodes-codex/{slug}/source-sha256.json',
        f'episodes-codex/{slug}/article.mdx',
        f'episodes-codex/{slug}/revisions/peak-style/article.mdx',
        f'episodes-codex/{slug}/revisions/peak-style/baseline-publication.json',
        f'episodes/{slug}/article.mdx',
    }
    if slug=='circuit-breaker':needed|={
        'episodes-codex/_shared/peak-video/branch-map.ts',
        'episodes-codex/_shared/branch-map/index.ts',
        'episodes-codex/circuit-breaker/remotion/src/branch-map.ts',
        'episodes-codex/circuit-breaker/remotion/src/motion.ts'}
    mismatches=[]
    for name,expected_sha in {**manifest['inputs'],**manifest['externalInputs']}.items():
        source=Path(name) if Path(name).is_absolute() else ROOT/name
        if not source.is_file() or sha(source)!=expected_sha:mismatches.append(name)
    check={'actual_closure_matches_frozen_set':closure==expected,
           'all_required_dependencies_present':needed<=closure,
           'all_recorded_actual_input_SHA256_match':not mismatches,
           'normalization_command_has_pixel_conversion_and_per_frame_setparams':
               any('scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709'==v for v in manifest['colorNormalizationCommand']),
           'render_muted_and_exact_original_frames':'--muted' in manifest['renderCommand'] and f'--frames=0-{manifest["timeline"]["bodyFrames"]-1}' in manifest['renderCommand']}
    rows[slug]={'status':'pass' if all(check.values()) else 'fail','checks':check,'manifestSHA256':sha(ctx.manifest),'inputCount':len(expected),'externalInputCount':len(manifest['externalInputs']),'missing':sorted(needed-closure),'recordedButNotActual':sorted(expected-closure),'actualButNotRecorded':sorted(closure-expected),'hashMismatches':mismatches,'inputs':manifest['inputs'],'fontBindings':manifest['fontBindings']}
result={'schemaVersion':1,'status':'pass' if all(v['status']=='pass' for v in rows.values()) else 'fail','scope':'Read-only frozen dependency, command and SHA checks; actual encoded samples and browser decode reviewed separately.','episodes':rows}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'renderer-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'episodes':{k:{'status':v['status'],'checks':v['checks'],'inputCount':v['inputCount'],'missing':v['missing']} for k,v in rows.items()}},indent=2))
