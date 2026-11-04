#!/usr/bin/env python3
"""Read-only P10 cover source, copy and old-episode preservation verification."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

D = Path(__file__).resolve().parent.parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    baseline_path = D / 'qa/covers-prior-baseline.json'
    baseline = json.loads(baseline_path.read_text())
    mismatches = []
    for name, expected in baseline['files'].items():
        p = ROOT / name
        if not p.is_file():
            mismatches.append({'path': name, 'error': 'missing'})
        elif p.stat().st_size != expected['bytes'] or sha(p) != expected['sha256']:
            mismatches.append({'path': name, 'error': 'changed'})
    additions = []
    excluded = set(baseline.get('excludedDirectoryNames', []))
    for slug in baseline['priorSlugs']:
        for directory, dirs, names in os.walk(ROOT / 'episodes/puzzles' / slug):
            dirs[:] = sorted(n for n in dirs if n not in excluded)
            for name in sorted(names):
                path = Path(directory) / name
                if not path.is_file():
                    continue
                relative = str(path.relative_to(ROOT))
                if relative not in baseline['files']:
                    additions.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': sha(path)})
    render = json.loads((D / 'cover-render-report.json').read_text())
    style = json.loads((D / 'cover-style.json').read_text())
    assert render['inputs'] == style['sourceSha256']
    inputs = {name: sha(ROOT / name) == value for name, value in render['inputs'].items()}
    outputs = {}
    for image in render['images']:
        for ext in ['svg', 'png', 'jpg']:
            name = f"cover-{image['size']}.{ext}"
            outputs[name] = sha(D / name) == image[f'{ext}Sha256']
    outputs['poster.jpg'] = sha(D / 'poster.jpg') == render['posterSha256'] == sha(D / 'cover-3x4.jpg')
    copies = {name: sha(D / name) == sha(D.parent / 'publication' / name)
        for name in ['cover-16x9.jpg', 'cover-3x4.jpg', 'cover-4x3.jpg', 'poster.jpg', 'cover-style.json', 'covers.json']}
    report = {'schemaVersion': 1, 'episode': 'prisoners-light', 'checkedAt': datetime.now(timezone.utc).isoformat(),
        'baselineCommit': baseline['baselineCommit'], 'baselineSha256': sha(baseline_path),
        'scope': baseline['scope'], 'protectedEpisodes': baseline['priorSlugs'],
        'protectedFileCount': baseline['fileCount'], 'protectedBytes': baseline['totalBytes'],
        'unchangedFiles': baseline['fileCount'] - len(mismatches), 'mismatches': mismatches,
        'newExistingFilesAfterBaseline': additions, 'newFilesNotTreatedAsOldByteMutations': True,
        'currentSourceInputs': inputs, 'currentOutputs': outputs, 'publicationCopies': copies,
        'passed': not mismatches and all(inputs.values()) and all(outputs.values()) and all(copies.values())}
    (D / 'qa/covers-preservation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['protectedFileCount', 'protectedBytes', 'unchangedFiles', 'mismatches', 'passed']}))
    assert report['passed'], 'Cover source/output/copy preservation failure'


if __name__ == '__main__':
    main()
