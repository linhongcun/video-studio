#!/usr/bin/env python3
"""Review only exact runtime matches from the preserved failed scan against pinned Kafka enums."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
A = ROOT / 'docs/archive/2026-11/mq05-consumer-replay'
Q = Path(__file__).resolve().parent
OLD = ROOT / 'docs/archive/2026-11/mq08-15-implementation/qa/public-protocol-identifier-review'
SOURCE_SHA = '674b62140ac3075e5748f37e8d7b6d63290a83c1d17afcad5ab4dc53ec57cdb8'
OLD_REVIEW_SHA = 'e1ed6968af98fe755a4465725dd75a3ff0b99667bd24a7f04fa3dc415d92fee5'
COMMIT = '1156b2752aaa28eafc0b4c4d387e63356793268d'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    target = Q / 'review.json'
    assert not target.exists(), 'Preserve this exact reviewed pin set; use a deliberate new evidence revision'
    failed_path = A / 'qa/secret-review-source-stage.json'
    failed_raw = failed_path.read_bytes()
    failed = json.loads(failed_raw)
    assert failed['passed'] is False and len(failed['approvedPublicSourceMatches']) == 48
    assert sha(OLD / 'review.json') == OLD_REVIEW_SHA
    old = json.loads((OLD / 'review.json').read_text())
    assert old['fixedCommit'] == COMMIT and old['sourceSHA256'] == SOURCE_SHA
    source = OLD / 'ApiKeys.java'
    assert sha(source) == SOURCE_SHA
    declarations = {}
    for n, line in enumerate(source.read_text().splitlines(), 1):
        match = re.match(r'\s*([A-Z][A-Z0-9_]+)\(ApiMessageType\.\1\b', line)
        if match:
            declarations[match[1]] = {'line': n, 'text': line.strip()}
    checker = ROOT / 'episodes/_shared/tests/secret_scan.py'
    spec = importlib.util.spec_from_file_location('canonical_secret_patterns_readonly', checker)
    canonical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canonical)
    patterns = dict(canonical.PAT)
    prefix = A.relative_to(ROOT).as_posix() + '/runtime/'
    files, used, derived = {}, set(), []
    for row in failed['unresolved']:
        if not row['file'].startswith(prefix):
            assert '/remotion/qa-' in row['file'] and '/bundle/' in row['file'], 'Non-runtime/non-derived match needs separate review'
            derived.append(row)
            continue
        assert row['rule'] == 'assigned secret', 'No waiver for other secret rules'
        path = ROOT / row['file']
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        line = raw.decode('utf-8').split('\n')[row['line'] - 1]
        matches = list(patterns[row['rule']].finditer(line))
        assert matches
        names = []
        for match in matches:
            enum = re.fullmatch(r'apiKey=([A-Z][A-Z0-9_]+)', match.group(0))
            assert enum and enum[1] in declarations, 'Unknown matching literal: location retained in original failed scan; do not print potential credentials'
            names.append(enum[1]); used.add(enum[1])
        item = files.setdefault(row['file'], {'path': row['file'], 'sha256': digest,
                 'bytes': len(raw), 'matches': []})
        assert item['sha256'] == digest, 'Runtime log is still changing'
        item['matches'].append({'line': row['line'], 'lineSHA256': hashlib.sha256(line.encode()).hexdigest(),
            'rule': row['rule'], 'actualMatchedLiterals': [m.group(0) for m in matches],
            'publicEnumNames': names, 'canonicalMatchCount': len(matches)})
    for path, item in files.items():
        assert sha(ROOT / path) == item['sha256']
        assert len({x['line'] for x in item['matches']}) == len(item['matches'])
    assert failed_path.read_bytes() == failed_raw
    before = Q / 'secret-review.before-runtime-pins.py.txt'
    assert not before.exists()
    shutil.copy2(A / 'secret-review.py', before)
    result = {'kind': 'exact-runtime-public-protocol-match-review',
        'reviewedAtUTC': datetime.now(timezone.utc).isoformat(),
        'originatingFailure': {'file': failed_path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(failed_raw).hexdigest(), 'passed': False,
            'legacyRecognizedMatches': 48, 'unresolvedLocations': len(failed['unresolved'])},
        'canonicalCheckerSHA256': sha(checker),
        'fixedCommit': COMMIT, 'sourceFile': source.relative_to(ROOT).as_posix(),
        'sourceSHA256': SOURCE_SHA, 'sourceURL': old['sourceURL'],
        'priorSourceAcquisitionProof': {'file': (OLD / 'review.json').relative_to(ROOT).as_posix(), 'sha256': OLD_REVIEW_SHA},
        'publicEnumEvidence': {name: declarations[name] for name in sorted(used)},
        'logFiles': sorted(files.values(), key=lambda x: x['path']),
        'runtimeFiles': len(files), 'runtimeLineLocations': sum(len(x['matches']) for x in files.values()),
        'individualMatchedLiterals': sum(m['canonicalMatchCount'] for x in files.values() for m in x['matches']),
        'derivedBundleLocationsNotWaived': derived,
        'classification': 'Exact public ApiKeys enum in these fixed local runtime log bytes; not an assigned credential.',
        'helperBeforeChange': {'file': before.relative_to(ROOT).as_posix(), 'sha256': sha(before)},
        'constraints': ['Exact path, whole-file SHA, line number, line SHA, canonical rule and complete finditer literal list must all match.',
            'A changed file or another matching literal, line, path or secret rule remains rejected.',
            'Derived bundles get no source waiver. Actual source, params and runtime code remain scanned.',
            'Equals characters in serialized JSON strings use Unicode escapes; JSON decoding recovers the exact literal without generating a new self-match in the scanner.']}
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2).replace('=', '\\u003d') + '\n')
    print(json.dumps({'file': str(target), 'sha256': sha(target), 'runtimeFiles': len(files),
                      'runtimeLineLocations': result['runtimeLineLocations'], 'publicEnumCount': len(used),
                      'derivedLocationsNotWaived': len(derived)}))


if __name__ == '__main__':
    main()
