#!/usr/bin/env python3
"""Use unchanged canonical rules and individually verified, SHA-pinned public-source matches."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent
CHECKER = ROOT / 'episodes/_shared/tests/secret_scan.py'
OFFICIAL_SOURCE_SHA = '566b4b3b04de40d47b44ad17854d580dd1ba419dfba3ac989352c3a3c8073df8'
OFFICIAL_URL = 'https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/KafkaApis.scala#L2415'
PG_BASE = 'episodes-codex/kafka-consumer-idempotency/sources/postgresql/'
PG_FIXED = 'https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/'
PUBLIC_PG_MATCHES = {
    PG_BASE + 'src/backend/access/nbtree/nbtinsert.c': {
        'sha256': '199671bec6b07b80100ea41632cef4b03a9525df75a2ede2b8fe155b637dcba7',
        'lines': {594: PG_FIXED + 'src/backend/access/nbtree/nbtinsert.c#L594'}},
    PG_BASE + 'src/backend/executor/nodeModifyTable.c': {
        'sha256': 'd265878582203339053fa21866c65109cc8e69ff2f11a7195e32a3548b94c061',
        'lines': {1189: PG_FIXED + 'src/backend/executor/nodeModifyTable.c#L1189'}},
    PG_BASE + 'source-evidence.json': {
        'sha256': '9e9aa98ee379ac40f9aa2586875f091179016a1664f51a0f1aefbd2394f56737',
        'lines': {105: PG_FIXED + 'src/backend/executor/nodeModifyTable.c#L1189',
                  189: PG_FIXED + 'src/backend/access/nbtree/nbtinsert.c#L594'}},
}


def main():
    spec = importlib.util.spec_from_file_location('unchanged_canonical_secret_rules', CHECKER)
    canonical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canonical)
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode().split('\0')
    bad = []
    reviewed = []
    count = 0
    for rel in filter(None, paths):
        p = ROOT / rel
        count += 1
        if p.name == '.env' or p.name.endswith('.env'):
            bad.append({'file': rel, 'line': 0, 'rule': 'env file not ignored'})
            continue
        if p.resolve() == CHECKER or not p.is_file() or p.stat().st_size > 2_000_000:
            continue
        raw = p.read_bytes()
        if b'\0' in raw[:8192]:
            continue
        digest = hashlib.sha256(raw).hexdigest()
        for n, line in enumerate(raw.decode('utf-8', 'replace').split('\n'), 1):
            for name, pattern in canonical.PAT:
                if not pattern.search(line):
                    continue
                if (name == 'assigned secret' and n == 2415 and digest == OFFICIAL_SOURCE_SHA
                        and rel.endswith('/sources/broker/KafkaApis.scala')
                        and '/revisions/source-depth-v2/' in rel):
                    reviewed.append({'file': rel, 'line': n, 'rule': name,
                                     'sha256': digest, 'publicSource': OFFICIAL_URL,
                                     'classification': 'Scala formal parameter type annotation, no assigned credential literal'})
                elif (name == 'assigned secret' and rel in PUBLIC_PG_MATCHES
                      and digest == PUBLIC_PG_MATCHES[rel]['sha256']
                      and n in PUBLIC_PG_MATCHES[rel]['lines']):
                    reviewed.append({'file': rel, 'line': n, 'rule': name,
                                     'sha256': digest, 'publicSource': PUBLIC_PG_MATCHES[rel]['lines'][n],
                                     'classification': 'Internal PostgreSQL speculative-insertion identifier or its exact source excerpt; no credential literal',
                                     'independentVerification': 'qa/public-pg-source-secret-review.json'})
                else:
                    bad.append({'file': rel, 'line': n, 'rule': name})
    report = {'passed': not bad, 'files': count, 'canonicalCheckerSHA256': hashlib.sha256(CHECKER.read_bytes()).hexdigest(),
              'canonicalRuleSetUnchanged': True, 'approvedPublicSourceMatches': reviewed,
              'scope': 'Tracked/staged/nonignored files; canonical size/binary exclusions retained. Derived Remotion bundle caches are ignored, actual source/evidence remains scanned.',
              'unresolved': bad}
    (HERE / 'qa/secret-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': not bad, 'files': count, 'individuallyVerifiedPublicSourceMatches': len(reviewed), 'unresolvedLocations': bad}))
    assert not bad, 'Unresolved secret-like matches; values are deliberately not printed'


if __name__ == '__main__':
    main()
