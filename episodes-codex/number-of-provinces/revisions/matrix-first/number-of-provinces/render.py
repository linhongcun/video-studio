"""Default new-voice render, using the existing LeetCode bibliography adapter.

Only orchestration and the new body's provenance live here. The retained shared
renderer supplies title/credit layout, palette, appendix encoding and all media
preservation checks. Shared audio, onset and rendering algorithms are unchanged.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
EP = Path(__file__).resolve().parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
RENDERER = ROOT / 'episodes-codex/_shared/leetcode-video/references.py'
read = lambda p: json.loads(p.read_text())
save = lambda p, v: p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
subprocess.run([sys.executable, str(EP / 'freeze.py'), '--verify'], check=True)
subprocess.run(['node', str(ROOT / 'site/scripts/check-references.mjs'), '--sources', str(EP)], check=True)
spec = importlib.util.spec_from_file_location('retained_leetcode_bibliography', RENDERER)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
args = SimpleNamespace(body=EP / 'remotion/out/body.mp4', references=EP / 'references.json',
    output=EP / 'video.mp4', artifacts=EP / 'revisions/reference-endcards', seconds=5,
    font=adapter.DEFAULT_FONT, bold_font=adapter.DEFAULT_BOLD)
adapter.load_references(args.references)
if '--verify' in sys.argv:
    report = adapter.verify(args)
    assert read(EP / 'reference-appendix.json') == read(args.artifacts / 'reference-appendix.json')
    result = read(EP / 'render-result.json')
    assert result['sha256'] == report['outputSHA256']
    assert result['frames'] == report['finalFrames']
    print(json.dumps({'status': 'verified', 'sha256': result['sha256'], 'frames': result['frames']}, indent=2))
else:
    subprocess.run(['npm', 'run', 'render:body'], cwd=EP / 'remotion', check=True)
    subprocess.run([sys.executable, str(EP / 'freeze.py'), '--verify'], check=True)
    adapter.append(args)
    receipt_path = args.artifacts / 'reference-appendix.json'
    receipt = read(receipt_path)
    receipt['bodyProductionInputs'] = ('New 13-shot matrix-first body rendered from this independent production freeze; '
        'six new narration takes and twenty exact-text historical takes were assembled by the unchanged shared voice builder. '
        'All body pictures and the complete Python card were rendered anew; historical inputs and media remain unchanged.')
    save(receipt_path, receipt)
    for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
        shutil.copy2(args.artifacts / name, EP / name)
    publication = {'finalVideoFrames': receipt['finalVideoFrames'], 'referenceAppendix': {
        'kind': 'references', 'from': receipt['bodyFrames'], 'durationInFrames': receipt['appendix']['durationInFrames'],
        'sources': 'references.json', 'manifest': 'reference-appendix.json'}}
    result = read(EP / 'body-render-result.json')
    result.update(frames=receipt['finalVideoFrames'], seconds=receipt['durationSeconds'],
        sha256=receipt['outputSHA256'], bytes=args.output.stat().st_size, bodyFrames=receipt['bodyFrames'],
        **publication, publicationMetadata=publication,
        reviewScope='Shared body full decode and shared styled appendix media-preservation checks passed; independent visual, audio and browser reviews are separate.')
    save(EP / 'render-result.json', result)
    subprocess.run([sys.executable, str(EP / 'freeze.py'), '--verify'], check=True)
    print(json.dumps({'status': 'rendered', 'sha256': result['sha256'], 'frames': result['frames']}, indent=2))
