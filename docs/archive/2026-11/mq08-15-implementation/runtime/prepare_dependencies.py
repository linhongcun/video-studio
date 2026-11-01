#!/usr/bin/env python3
"""Fetch the official Kafka distribution with inherited proxy and CA trust."""
from pathlib import Path
import datetime, hashlib, json, os, re, subprocess, tarfile, urllib.request, zipfile

A = Path(__file__).resolve().parent
T = Path('/tmp/mq08-15-runtime')
DEP = A / 'dependencies'
VERSION = '4.4.0'
COMMIT = '1156b2752aaa28eafc0b4c4d387e63356793268d'
NAME = f'kafka_2.13-{VERSION}.tgz'
BASE = f'https://archive.apache.org/dist/kafka/{VERSION}/'
DEP.mkdir(parents=True, exist_ok=True)
T.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
record = {'startedAtUTC': stamp, 'kind': 'fresh-official-distribution-identity',
          'version': VERSION, 'expectedSourceCommit': COMMIT,
          'proxyAndCATrust': 'Inherited unchanged; standard urllib TLS verification',
          'distributionUrl': BASE + NAME, 'checksumUrl': BASE + NAME + '.sha512'}
def get(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'MQ-runtime-evidence/1.0'})
    with urllib.request.urlopen(req, timeout=60) as response, dest.open('wb') as out:
        info = {k: response.headers.get(k) for k in ['Date', 'Content-Length', 'ETag', 'Last-Modified']}
        info.update(status=response.status, url=response.url)
        while block := response.read(1024 * 1024):
            out.write(block)
    return info
try:
    checksum = DEP / f'{NAME}.sha512'
    record['checksumHttp'] = get(BASE + NAME + '.sha512', checksum)
    pieces = re.findall(r'\b[0-9a-fA-F]{8}\b', checksum.read_text())
    expected = ''.join(pieces).lower()
    assert len(expected) == 128, 'Unexpected official SHA512 format'
    partial = T / f'{NAME}.{stamp}.partial'
    record['distributionHttp'] = get(BASE + NAME, partial)
    actual = hashlib.file_digest(partial.open('rb'), 'sha512').hexdigest()
    record.update(expectedSHA512=expected, actualSHA512=actual, bytes=partial.stat().st_size)
    assert actual == expected, 'Official SHA512 mismatch'
    archive = T / NAME
    assert not archive.exists(), 'Do not replace a previous dependency attempt'
    partial.rename(archive)
    home = T / f'kafka_2.13-{VERSION}'
    assert not home.exists(), 'Do not overwrite an existing extracted tree'
    with tarfile.open(archive) as tar:
        tar.extractall(T, filter='data')
    props = {}
    for jar in sorted((home / 'libs').glob('kafka-clients-*.jar')):
        with zipfile.ZipFile(jar) as z:
            for name in z.namelist():
                if name.endswith('kafka-version.properties'):
                    props = dict(line.split('=', 1) for line in z.read(name).decode().splitlines()
                                 if line and not line.startswith('#') and '=' in line)
    assert props.get('version') == VERSION, props
    assert COMMIT.startswith(props.get('commitId', 'missing')), props
    files = {str(p.relative_to(home)): hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()
             for p in sorted(home.rglob('*')) if p.is_file() and p.parts[-2] in ['libs', 'bin']}
    (DEP / 'kafka-distribution-files-sha256.json').write_text(json.dumps(files, indent=2) + '\n')
    compiler = subprocess.run(['java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-version'],
                              capture_output=True, text=True)
    assert compiler.returncode == 0, compiler.stderr
    record.update(pass_=True, kafkaHome=str(home), properties=props, checkedFiles=len(files),
                  compilerCommand=['java', '-m', 'jdk.compiler/com.sun.tools.javac.Main'],
                  compilerVersion=(compiler.stdout + compiler.stderr).strip())
except BaseException as exc:
    record.update(pass_=False, errorType=type(exc).__name__, error=str(exc))
    raise
finally:
    record['finishedAtUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (DEP / f'identity-{stamp}.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: record.get(k) for k in ['pass_', 'kafkaHome', 'actualSHA512', 'bytes', 'properties', 'compilerVersion']}))
