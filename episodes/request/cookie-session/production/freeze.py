"""Freeze or verify actual production inputs; never validates an earlier MP4."""

# Resolve episode storage independently of its series and revision depth.
import sys as _layout_sys
from pathlib import Path as _LayoutPath
_layout_root = next(parent for parent in _LayoutPath(__file__).resolve().parents
                    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
_layout_sys.path.insert(0, str(_layout_root / 'episodes/_shared'))
from episode_paths import production_directory, publication_directory, resolve_repo_path, episode_slug, resolve_frozen_path
from pathlib import Path
import hashlib,json,os,shutil,sys
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify' in sys.argv:
 m=json.loads((D/'source-sha256.json').read_text()); bad=[p for p,h in m.items() if not (resolve_frozen_path(D/'source-sha256.json', p)).is_file() or sha(resolve_frozen_path(D/'source-sha256.json', p))!=h]
 print('Frozen input verification:',len(m),'files;', 'OK' if not bad else bad)
 sys.exit(1 if bad else 0)
sb=json.loads((D/'storyboard.json').read_text());w=json.loads((D/'words.json').read_text())
assert w['scriptSha256']==sha(D/'script.md') and w['audioSha256']==sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes()==(D/'remotion/public/audio/voice.wav').read_bytes()
assert sb['meta']['durationInFrames']==w['durationFrames'] and not sb['meta']['pendingAudio']
snapshot=D/f'storyboard.{sha(D/"storyboard.json")[:8]}.json';shutil.copy2(D/'storyboard.json',snapshot)
(D/'remotion/src/placeholders').mkdir(parents=True,exist_ok=True)
shutil.copy2(D/'storyboard.json',D/'remotion/src/placeholders/storyboard.json')
files=[D/p for p in ['episode.json','script.md','article.mdx','research.md','pronunciation.md','assemble.py','freeze.py','preflight.py','visual-direction.md','knoll-props.md','storyboard.json','words.json','covers.json','voice.wav','voice/params.json','voice/picks.json','voice/sents.json','voice/build.json','voice/substitutions.md','remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts','remotion/tsconfig.json','remotion/public/audio/voice.wav']]
files += [snapshot]+[p for p in (D/'remotion/src').rglob('*') if p.is_file()]+[p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
picks=json.loads((D/'voice/picks.json').read_text())
for row in json.loads((D/'voice/sents.json').read_text()):
 stem=f"{row['id']}-{picks.get(row['id'],'a')}"
 files += [D/'voice/takes'/f'{stem}.wav',D/'voice/takes'/f'{stem}.txt.json']
files += [D/'../../../_shared'/p for p in ['onset_rule.py','voice/prep.py','voice/gen.py','voice/build.py','voice/common.py','tts/mimo_say.py','theme/pageTheme.ts','music/mix_bgm.py','music/Wallpaper.mp3']]
# Keep the original voiced-body timeline; the appendix declares its own final frames.
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
files += [D/'references.json',
    ROOT/'episodes/_shared/render_with_references.py',
    ROOT/'episodes/_shared/append_references.py',
    ROOT/'episodes/_shared/requirements-reference-appendix.txt',
    ROOT/'site/scripts/check-references.mjs',
          ROOT / 'episodes/_shared/episode_paths.py',
          ROOT / 'site/scripts/episode-paths.mjs']
# Article, package.json and shared pageTheme.ts are already included above.
for source in json.loads((D/'references.json').read_text())['sources']:
    files.append(resolve_repo_path(source['verification']['evidence'], root=ROOT))
# Original-title/quotation production inputs; legacy media provenance stays archived.
files += [D/'references.json', D/'article.mdx', D/'remotion/package.json',
    ROOT/'episodes/_shared/append_references_original.py',
    ROOT/'episodes/_shared/append_references.py',
    ROOT/'episodes/_shared/render_with_references.py',
    ROOT/'episodes/_shared/requirements-reference-appendix.txt',
    ROOT/'site/scripts/check-references.mjs',
    ROOT/'episodes/_shared/theme/pageTheme.ts',
          ROOT / 'episodes/_shared/episode_paths.py',
          ROOT / 'site/scripts/episode-paths.mjs']
for source in json.loads((D/'references.json').read_text())['sources']:
    evidence_paths = [source['verification']['evidence'], source['titleEvidence']['evidence']]
    if 'quotation' in source:
        evidence_paths.append(source['quotation']['evidence'])
    files.extend(resolve_repo_path(evidence, root=ROOT) for evidence in evidence_paths)
files += [ROOT/'episodes/_shared/append_references_bibliography.py']
m={os.path.relpath(p,D):sha(p) for p in sorted(set(files))};(D/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print('Frozen',len(m),'inputs; storyboard',sha(D/'storyboard.json'))
