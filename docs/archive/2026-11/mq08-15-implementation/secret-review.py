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
EXACT_KAFKA_TYPE_COPIES = {
    'episodes/message-queue/message-queue/production/revisions/source-depth-v2/sources/broker/KafkaApis.scala',
    'episodes/message-queue/kafka-replica-acks/production/examples/actual-runtime/hw-source-evidence/KafkaApis.scala',
}
PG_BASE = 'episodes/message-queue/kafka-consumer-idempotency/production/sources/postgresql/'
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
PROTOCOL_REVIEW_SHA256 = 'e1ed6968af98fe755a4465725dd75a3ff0b99667bd24a7f04fa3dc415d92fee5'


def verified_protocol_locations():
    record = HERE / 'qa/public-protocol-identifier-review/review.json'
    assert hashlib.sha256(record.read_bytes()).hexdigest() == PROTOCOL_REVIEW_SHA256
    review = json.loads(record.read_text())
    assert review['publicMatchedEnumNames'] == ['BROKER_HEARTBEAT']
    official = record.parent / 'ApiKeys.java'
    assert hashlib.sha256(official.read_bytes()).hexdigest() == review['sourceSHA256']
    assert review['fixedCommit'] == '1156b2752aaa28eafc0b4c4d387e63356793268d'
    result = {}
    for item in review['logFiles']:
        result[item['path']] = {'sha256': item['sha256'],
                                'lines': {m['line'] for m in item['matches']},
                                'classification': 'Public Kafka BROKER_HEARTBEAT request API enum in an original local Broker log; not a credential'}
    for item in review['exactAdditionalPublicSourceCopies']:
        assert item['sha256'] == OFFICIAL_SOURCE_SHA and item['line'] == 2415
        result[item['path']] = {'sha256': item['sha256'], 'lines': {item['line']},
                                'classification': item['classification']}
    return result


def main():
    spec = importlib.util.spec_from_file_location('unchanged_canonical_secret_rules', CHECKER)
    canonical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canonical)
    protocol = verified_protocol_locations()
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
                        and rel in EXACT_KAFKA_TYPE_COPIES):
                    reviewed.append({'file': rel, 'line': n, 'rule': name,
                                     'sha256': digest, 'publicSource': OFFICIAL_URL,
                                     'classification': 'Scala formal parameter type annotation, no assigned credential literal'})
                elif (name == 'assigned secret' and rel in PUBLIC_PG_MATCHES
                      and digest == PUBLIC_PG_MATCHES[rel]['sha256']
                      and n in PUBLIC_PG_MATCHES[rel]['lines']):
                    reviewed.append({'file': rel, 'line': n, 'rule': name,
                                     'sha256': digest, 'publicSource': PUBLIC_PG_MATCHES[rel]['lines'][n],
                                     'classification': 'Internal PostgreSQL speculative-insertion identifier or its exact source excerpt; no credential literal',
                                     'independentVerification': 'docs/archive/2026-10/mq05-07-implementation/qa/public-pg-source-secret-review.json; same protected source bytes after migration'})
                elif (name == 'assigned secret' and rel in protocol
                      and digest == protocol[rel]['sha256'] and n in protocol[rel]['lines']):
                    reviewed.append({'file': rel, 'line': n, 'rule': name, 'sha256': digest,
                                     'classification': protocol[rel]['classification'],
                                     'exactPinnedReview': 'qa/public-protocol-identifier-review/review.json'})
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
