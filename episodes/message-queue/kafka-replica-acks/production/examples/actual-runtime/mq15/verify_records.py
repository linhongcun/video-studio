#!/usr/bin/env python3
"""Read-only integrity and accepted-evidence check; never starts Kafka."""
from pathlib import Path
import hashlib,json
A=Path(__file__).resolve().parent
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=json.loads((A/'files-sha256.json').read_text())
for name,h in files.items():assert sha(A/name)==h,name
R=A/'runs/20261101T092613950298Z'
raw=json.loads((R/'report.json').read_text());accepted=json.loads((R/'post-validation/report.json').read_text())
assert raw['pass'] is False and accepted['pass'] is True
assert accepted['rawRunReportSHA256']==sha(R/'report.json')
assert accepted['passedRealRunAssertions']==34
assert accepted['officialPhysicalLogValidation']['emptyAndNonemptySnapshotsValidated']==33
assert accepted['officialPhysicalLogValidation']['recordBatchCRCsValid']==21
assert accepted['officialPhysicalLogValidation']['exit']==0
assert accepted['cleanup']['allTrackedBrokersExited']
assert accepted['cleanup']['allProxyListenersClosed']
assert accepted['cleanup']['ownTemporaryDataRemoved']
assert all(x['connectRefused']for x in accepted['cleanup']['postAuditAll12PortsClosed'])
for m in json.loads((R/'post-validation/byte-identical-segment-copies.json').read_text()):
    assert sha(R/m['old'])==sha(R/m['numericCopy'])==m['sha256']
    assert (R/m['old']).read_bytes()==(R/m['numericCopy']).read_bytes()
print(json.dumps({'pass':True,'indexedFiles':len(files),'realAssertionsPassed':34,'officialPhysicalSnapshots':33,'officialValidRecordBatches':21,'acceptedReportSHA256':sha(R/'post-validation/report.json'),'servicesStarted':False,'filesWritten':False}))
