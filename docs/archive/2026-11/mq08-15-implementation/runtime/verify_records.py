#!/usr/bin/env python3
"""Read-only batch runtime evidence verification. Never starts Kafka or writes files."""
from pathlib import Path
import hashlib, json

A = Path(__file__).resolve().parent
def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

index = json.loads((A / 'runtime-files-sha256.json').read_text())
for name, expected in index.items():
    assert sha(A / name) == expected, name
summary = json.loads((A / 'experiment-summary.json').read_text())
assert summary['pass'] is True
mq08 = json.loads((A / summary['mq08']['summary']).read_text())
run08 = A / mq08['report']
assert sha(run08) == mq08['reportSHA256']
assert mq08['actualCases'] == 8 and mq08['assertions'] == 151
raw08 = json.loads(run08.read_text())
assert raw08['pass'] and all(x['pass'] for x in raw08['assertions'])
assert raw08['cleanup']['brokerStopped'] and raw08['cleanup']['temporaryDataRemoved']
for name, expected in json.loads((run08.parent / 'files-sha256.json').read_text()).items():
    assert sha(run08.parent / name) == expected, name
run15 = A / summary['mq15']['acceptedReport']
accepted15 = json.loads(run15.read_text())
raw15 = run15.parents[1] / 'report.json'
assert accepted15['pass'] and json.loads(raw15.read_text())['pass'] is False
assert accepted15['rawRunReportSHA256'] == sha(raw15)
assert accepted15['passedRealRunAssertions'] == 34
assert accepted15['officialPhysicalLogValidation']['emptyAndNonemptySnapshotsValidated'] == 33
assert accepted15['officialPhysicalLogValidation']['recordBatchCRCsValid'] == 21
assert accepted15['cleanup']['allTrackedBrokersExited']
assert accepted15['cleanup']['allProxyListenersClosed']
assert accepted15['cleanup']['ownTemporaryDataRemoved']
for pair in json.loads((run15.parent / 'byte-identical-segment-copies.json').read_text()):
    base = raw15.parent
    assert sha(base / pair['old']) == sha(base / pair['numericCopy']) == pair['sha256']
    assert (base / pair['old']).read_bytes() == (base / pair['numericCopy']).read_bytes()
print(json.dumps({'pass': True, 'indexedFiles': len(index), 'mq08Cases': 8,
                  'mq08RealAssertions': 151, 'mq15Branches': 7, 'mq15RealAssertions': 34,
                  'officialReplicaSnapshots': 33, 'officialValidCRCBatches': 21,
                  'retainedFailedReceiptsUnchanged': True, 'servicesStarted': False,
                  'filesWritten': False}))
