#!/usr/bin/env python3
"""Bounded independent review of the pinned MQ05 runtime public-enum guard.

Only the 16 proof-listed logs and 48 previously classified locations are read.
No repository inventory, helper main, network, process, or full secret scan runs.
Synthetic negative strings exist in memory only; output contains no log lines.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from copy import deepcopy
import ast
import hashlib
import importlib.util
import json
import re
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
A = HERE.parents[1]
HELPER = A / 'secret-review.py'
PROOF = HERE / 'review.json'
OUT = HERE / 'independent.json'
EXPECTED_PROOF_SHA = '748e0e7b88669e5638cf3cbbc03ae32cfc34f356cbe72fa4323c5dc1462b6464'
checks = []
protected = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_bytes(path):
    path = path.resolve()
    raw = path.read_bytes()
    current = {'sha256': sha(raw), 'mtimeNS': path.stat().st_mtime_ns}
    prior = protected.setdefault(path, current)
    assert prior == current, 'A reviewed input changed during bounded checks'
    return raw


def check(condition, name):
    assert condition, name
    checks.append(name)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def legacy_approval_nodes(tree):
    result = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or not node.body:
            continue
        test = ast.unparse(node.test)
        first = node.body[0]
        if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call)
                and ast.unparse(first.value.func) == 'reviewed.append'
                and any(part in test for part in
                        ['OFFICIAL_SOURCE_SHA', 'PUBLIC_PG_MATCHES', 'rel in protocol'])):
            result.append((ast.dump(node.test), ast.dump(first)))
    return sorted(result)


def main():
    assert not OUT.exists(), 'Preserve any earlier independent report'
    report = {'kind': 'bounded-independent-runtime-public-enum-guard-review',
              'startedAtUTC': datetime.now(timezone.utc).isoformat(),
              'passed': False, 'checks': checks,
              'scope': '16 proof-listed current runtime logs, 234 exact locations, eight public enums, and 48 preserved legacy classifications; not a final repository scan.',
              'notRun': ['helper main', 'canonical main', 'git file inventory',
                         'network', 'runtime processes', 'repository-wide scan']}
    try:
        helper_raw = load_bytes(HELPER)
        proof_raw = load_bytes(PROOF)
        check(sha(proof_raw) == EXPECTED_PROOF_SHA, 'Exact new proof bytes match the requested SHA')
        proof = json.loads(proof_raw)
        guard = module(HELPER, 'mq05_bounded_public_enum_guard')
        checker_raw = load_bytes(guard.CHECKER)
        canonical = module(guard.CHECKER, 'mq05_bounded_canonical_patterns')
        check(sha(checker_raw) == proof['canonicalCheckerSHA256'], 'Unchanged actual canonical checker SHA matches proof')
        check(guard.RUNTIME_PROTOCOL_RECORD == PROOF and guard.RUNTIME_PROTOCOL_SHA256 == EXPECTED_PROOF_SHA,
              'Guard binds this exact new proof')
        source_path = ROOT / proof['sourceFile']
        source_raw = load_bytes(source_path)
        check(sha(source_raw) == proof['sourceSHA256'], 'Actual fixed ApiKeys source bytes match proof')
        source_lines = source_raw.decode('utf-8').splitlines()
        declarations = {}
        for number, line in enumerate(source_lines, 1):
            match = re.fullmatch(r'\s*([A-Z][A-Z0-9_]+)\(ApiMessageType\.\1(?:,.*)?\),\s*', line)
            if match:
                declarations[match[1]] = (number, line.strip())
        check(len(proof['publicEnumEvidence']) == 8, 'Exactly eight enum names are reviewed')
        for name, evidence in proof['publicEnumEvidence'].items():
            check(declarations.get(name) == (evidence['line'], evidence['text']),
                  'Exact official enum declaration: ' + name)
        previous_path = ROOT / proof['priorSourceAcquisitionProof']['file']
        previous_raw = load_bytes(previous_path)
        check(sha(previous_raw) == proof['priorSourceAcquisitionProof']['sha256'] == guard.PROTOCOL_REVIEW_SHA256,
              'Old source-acquisition proof remains exact')
        previous = json.loads(previous_raw)
        check(previous['fixedCommit'] == proof['fixedCommit'] == '1156b2752aaa28eafc0b4c4d387e63356793268d'
              and previous['sourceSHA256'] == sha(source_raw), 'Source acquisition belongs to the fixed Kafka 4.4.0 commit')
        failure_path = ROOT / proof['originatingFailure']['file']
        failure_raw = load_bytes(failure_path)
        check(sha(failure_raw) == proof['originatingFailure']['sha256'], 'First FAIL raw report is retained byte for byte')
        failure = json.loads(failure_raw)
        check(failure['passed'] is False and len(failure['approvedPublicSourceMatches']) == 48
              and len(failure['unresolved']) == proof['originatingFailure']['unresolvedLocations'],
              'Original FAIL and its 48 legacy classifications are not relabeled as passed')
        before_path = ROOT / proof['helperBeforeChange']['file']
        before_raw = load_bytes(before_path)
        check(sha(before_raw) == proof['helperBeforeChange']['sha256'], 'Before-helper snapshot retains exact bytes')
        before_tree, after_tree = ast.parse(before_raw), ast.parse(helper_raw)
        named = ['OFFICIAL_SOURCE_SHA', 'OFFICIAL_URL', 'EXACT_KAFKA_TYPE_COPIES',
                 'PG_BASE', 'PG_FIXED', 'PUBLIC_PG_MATCHES', 'PROTOCOL_RECORD', 'PROTOCOL_REVIEW_SHA256']
        def definitions(tree):
            return {node.targets[0].id: ast.dump(node.value) for node in tree.body
                    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        before_defs, after_defs = definitions(before_tree), definitions(after_tree)
        check(all(before_defs[name] == after_defs[name] for name in named), 'All eight legacy exact-definition ASTs are unchanged')
        check(legacy_approval_nodes(before_tree) == legacy_approval_nodes(after_tree)
              and len(legacy_approval_nodes(after_tree)) == 3,
              'All three old approval predicates and classification dictionaries are unchanged')
        before_fn = next(n for n in before_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verified_protocol_locations')
        after_fn = next(n for n in after_tree.body if isinstance(n, ast.FunctionDef) and n.name == before_fn.name)
        check(ast.dump(before_fn) == ast.dump(after_fn), 'Old protocol-proof loader is unchanged')
        old_protocol = guard.verified_protocol_locations()
        patterns = dict(canonical.PAT)
        assigned = patterns['assigned secret']
        legacy_categories = Counter()
        legacy_files = {}
        for item in failure['approvedPublicSourceMatches']:
            rel, number, rule = item['file'], item['line'], item['rule']
            raw = legacy_files.setdefault(rel, load_bytes(ROOT / rel))
            digest = sha(raw)
            line = raw.decode('utf-8', 'replace').split('\n')[number - 1]
            check(rule == 'assigned secret' and digest == item['sha256'] and assigned.search(line) is not None,
                  'Legacy exact location and canonical rule retained: ' + rel + ':' + str(number))
            if number == 2415 and digest == guard.OFFICIAL_SOURCE_SHA and rel in guard.EXACT_KAFKA_TYPE_COPIES:
                legacy_categories['exact-kafka-type-copy'] += 1
            elif (rel in guard.PUBLIC_PG_MATCHES and digest == guard.PUBLIC_PG_MATCHES[rel]['sha256']
                  and number in guard.PUBLIC_PG_MATCHES[rel]['lines']):
                legacy_categories['exact-postgresql-source'] += 1
            elif rel in old_protocol and digest == old_protocol[rel]['sha256'] and number in old_protocol[rel]['lines']:
                legacy_categories['exact-old-protocol-location'] += 1
            else:
                raise AssertionError('A preserved legacy location lost its unchanged classification')
        check(sum(legacy_categories.values()) == 48, 'All 48 old exact locations retain their previous definitions')
        pins = guard.verified_runtime_protocol_locations()
        runtime_index_path = A / 'runtime/runtime-files-sha256.json'
        runtime_index_raw = load_bytes(runtime_index_path)
        runtime_index = json.loads(runtime_index_raw)
        check(len(runtime_index) == 200, 'Immutable runtime index contains 200 entries; only the 16 log entries below are rechecked here')
        check(len(proof['logFiles']) == 16 and len(pins) == proof['runtimeLineLocations'] == 234,
              'Proof contains exactly 16 logs and 234 unique line locations')
        actual_locations = set()
        observed_enums = set()
        runtime_files = []
        samples = []
        for item in proof['logFiles']:
            rel = item['path']
            path = ROOT / rel
            raw = load_bytes(path)
            digest = sha(raw)
            index_rel = path.relative_to(A / 'runtime').as_posix()
            check(digest == item['sha256'] == runtime_index[index_rel] and len(raw) == item['bytes'],
                  'Exact runtime whole-file bytes and immutable index: ' + rel)
            lines = raw.decode('utf-8', 'replace').split('\n')
            expected = {entry['line']: entry for entry in item['matches']}
            actual = {}
            for number, line in enumerate(lines, 1):
                for rule, pattern in canonical.PAT:
                    literals = [match.group(0) for match in pattern.finditer(line)]
                    if literals:
                        actual[(number, rule)] = literals
            check(set(actual) == {(number, 'assigned secret') for number in expected},
                  'Complete canonical finditer inventory equals the pinned locations: ' + rel)
            for number, entry in expected.items():
                line = lines[number - 1]
                literals = actual[(number, 'assigned secret')]
                check(sha(line.encode()) == entry['lineSHA256']
                      and literals == entry['actualMatchedLiterals']
                      and len(literals) == entry['canonicalMatchCount'] == len(entry['publicEnumNames']),
                      'Exact line SHA and all actual matched literals: ' + rel + ':' + str(number))
                names = [literal.split(chr(61), 1)[1] for literal in literals]
                check(names == entry['publicEnumNames'] and set(names).issubset(proof['publicEnumEvidence']),
                      'All actual literals name proven public enums: ' + rel + ':' + str(number))
                check(guard.current_runtime_public_match(pins, rel, number, 'assigned secret', digest, line, assigned),
                      'Positive guard accepts exact pinned location: ' + rel + ':' + str(number))
                actual_locations.add((rel, number, 'assigned secret'))
                observed_enums.update(names)
                samples.append((rel, number, digest, line))
            runtime_files.append({'file': rel, 'sha256': digest, 'bytes': len(raw), 'verifiedLines': len(expected)})
        check(actual_locations == set(pins) and observed_enums == set(proof['publicEnumEvidence']),
              'All 234 positives and all eight enums were independently checked')
        negatives = Counter()
        unknown_literal = 'api' + 'Key' + chr(61) + 'UNREVIEWED_RUNTIME_ENUM_1234'
        for rel, number, digest, line in samples:
            cases = [
                ('changed-file-sha', pins, rel, number, 'assigned secret', ('1' if digest[0] == '0' else '0') + digest[1:], line, assigned),
                ('changed-line-number', pins, rel, 0, 'assigned secret', digest, line, assigned),
                ('changed-path', pins, rel + '.unexpected', number, 'assigned secret', digest, line, assigned),
                ('changed-line-bytes', pins, rel, number, 'assigned secret', digest, line + ' changed', assigned),
            ]
            for label, table, path, n, rule, file_sha, text, pattern in cases:
                check(not guard.current_runtime_public_match(table, path, n, rule, file_sha, text, pattern), label + ' is rejected')
                negatives[label] += 1
            for label, addition in [('unknown-extra-literal', unknown_literal),
                                    ('second-public-match-same-line', pins[(rel, number, 'assigned secret')]['actualMatchedLiterals'][0])]:
                text = line + ' ' + addition
                shadow = dict(pins)
                shadow[(rel, number, 'assigned secret')] = {**pins[(rel, number, 'assigned secret')], 'lineSHA256': sha(text.encode())}
                check([m.group(0) for m in assigned.finditer(text)] != shadow[(rel, number, 'assigned secret')]['actualMatchedLiterals'],
                      label + ' changes the complete match sequence')
                check(not guard.current_runtime_public_match(shadow, rel, number, 'assigned secret', digest, text, assigned),
                      label + ' is rejected even with a matching synthetic line SHA')
                negatives[label] += 1
            other_rule = 'bearer token'
            text = 'Bea' + 'rer' + ' ' + ('X' * 24)
            check(patterns[other_rule].search(text) is not None, 'Other-rule synthetic text actually matches its canonical rule')
            check(not guard.current_runtime_public_match(pins, rel, number, other_rule, digest, text, patterns[other_rule]),
                  'A different canonical secret rule is rejected')
            negatives['different-secret-rule'] += 1
        original_read_bytes = Path.read_bytes
        def altered_proof_read(path):
            return proof_raw + b' ' if path.resolve() == PROOF else original_read_bytes(path)
        rejected = False
        with patch.object(Path, 'read_bytes', altered_proof_read):
            try:
                guard.verified_runtime_protocol_locations()
            except AssertionError:
                rejected = True
        check(rejected, 'Changing proof bytes only in memory is rejected by the pinned proof SHA')
        negatives['changed-proof-bytes'] = 1
        for path, before in protected.items():
            check({'sha256': sha(path.read_bytes()), 'mtimeNS': path.stat().st_mtime_ns} == before,
                  'Reviewed input bytes and mtime preserved: ' + path.relative_to(ROOT).as_posix())
        report.update(passed=True, positiveLocations=len(samples), runtimeLogFiles=len(runtime_files),
                      publicEnumNames=sorted(observed_enums), runtimeFiles=runtime_files,
                      negativeCases=dict(negatives), negativeCaseCount=sum(negatives.values()),
                      legacyLocations=48, legacyClassificationCounts=dict(legacy_categories),
                      canonicalPatterns=len(canonical.PAT), completeFinditerChecked=True,
                      bindings={'helper': {'file': HELPER.relative_to(ROOT).as_posix(), 'sha256': sha(helper_raw)},
                                'proof': {'file': PROOF.relative_to(ROOT).as_posix(), 'sha256': sha(proof_raw)},
                                'canonical': {'file': guard.CHECKER.relative_to(ROOT).as_posix(), 'sha256': sha(checker_raw)},
                                'source': {'file': source_path.relative_to(ROOT).as_posix(), 'sha256': sha(source_raw)},
                                'firstFailure': {'file': failure_path.relative_to(ROOT).as_posix(), 'sha256': sha(failure_raw)},
                                'runtimeIndex': {'file': runtime_index_path.relative_to(ROOT).as_posix(), 'sha256': sha(runtime_index_raw), 'entries': len(runtime_index)},
                                'beforeHelper': {'file': before_path.relative_to(ROOT).as_posix(), 'sha256': sha(before_raw)}})
    except Exception as error:
        report.update(errorType=type(error).__name__, error=str(error))
        raise
    finally:
        report.update(finishedAtUTC=datetime.now(timezone.utc).isoformat(),
                      independentScriptSHA256=sha(Path(__file__).read_bytes()),
                      checkCount=len(checks))
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2).replace(chr(61), '\\u003d') + '\n')
    print(json.dumps({'passed': report['passed'], 'positiveLocations': report['positiveLocations'],
                      'negativeCases': report['negativeCaseCount'], 'legacyLocations': report['legacyLocations'],
                      'report': OUT.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
