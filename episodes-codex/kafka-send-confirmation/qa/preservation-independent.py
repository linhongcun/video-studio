#!/usr/bin/env python3
"""Read-only verification of existing Kafka production freezes and base episodes."""
import datetime, hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
QA = Path(__file__).resolve().parent
BASE = "2c54aa7c5f4e3236500728d3078b356d06625099"
SLUG = "kafka-send-confirmation"
OLD = ["episodes-codex/message-queue/revisions/kafka-intro/message-queue", "episodes-codex/kafka-consumer-groups", "episodes-codex/kafka-log-replay"]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def state(paths):
    return {str(p.relative_to(ROOT)): {"sha256": sha(p), "mtimeNs":p.stat().st_mtime_ns,"bytes":p.stat().st_size} for p in sorted(paths)}
def blob(p):
    data = os.readlink(p).encode() if p.is_symlink() else p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    paths=set(); manifests=[]
    for n in OLD:
        d=ROOT/n; manifest=d/"source-sha256.json"; m=json.loads(manifest.read_text())
        paths.add(manifest); paths.update((d/p).resolve() for p in m)
        manifests.append({"episodeDirectory":n,"frozenInputs":len(m),"manifestSHA256":sha(manifest)})
    before=state(paths); executions=[]
    # Every entry was source-reviewed: --verify branch only reads checkSources,
    # verify_freeze and extras, then returns before the manifest-writing branch.
    # -B prevents Python import bytecode from creating files in historical trees.
    for n in OLD:
        cmd=[sys.executable,"-B",str(ROOT/n/"freeze.py"),"--verify"]
        run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        executions.append({"command":["python3","-B",n+"/freeze.py","--verify"],"exitCode":run.returncode,"stdout":run.stdout,"stderr":run.stderr})
    after=state(paths)
    changed=[n for n in before if before[n]!=after[n]]
    rows=subprocess.check_output(["git","ls-tree","-r",BASE,"--","episodes"],cwd=ROOT,text=True).splitlines()
    old={r.split("\t",1)[1]:r.split("\t",1)[0].split()[2] for r in rows}
    changedOld=[]; missing=[]
    for n, expected in old.items():
        p=ROOT/n
        if not p.exists() and not p.is_symlink(): missing.append(n)
        elif blob(p)!=expected: changedOld.append(n)
    candidates=set(subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard","--","episodes"],cwd=ROOT,text=True).splitlines())
    additions=sorted(candidates-set(old)); forbidden=[n for n in additions if not n.startswith("episodes/"+SLUG+"/")]
    report={"schemaVersion":1,"startedAt":started,"finishedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"baseline":BASE,"phase":"initial-source-and-baseline-preservation" if not additions else "publication-candidate-preservation","entrySourceReviewed":True,"entryReadOnlyReason":"The actual three freeze.py verify branches run read-only checkSources/verify_freeze/extras and return before the write branch. Wrapper verify_freeze only reads real manifests, source bytes and reference declarations. Node --sources checker only reads/checks and logs. Python -B suppresses import bytecode.","oldManifests":manifests,"uniqueProtectedFilesIncludingManifests":len(paths),"executions":executions,"protectedBytesAndMtimeUnchanged":not changed,"changedProtectedFiles":changed,"basePublishedFiles":len(old),"changedOldPublishedPaths":changedOld,"missingOldPublishedPaths":missing,"newPublishedPaths":additions,"forbiddenNewPublishedPaths":forbidden,"scope":"Current worktree bytes compared with every baseline Git blob under episodes/, including metadata/articles/media; future candidate mutations require rerun. No old source/manifests written. This is freeze and preservation verification, not repeated runtime/video/Broker testing."}
    report["pass"]=all(r["exitCode"]==0 for r in executions) and not changed and not changedOld and not missing and not forbidden
    (QA/"preservation-independent.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ["pass","uniqueProtectedFilesIncludingManifests","protectedBytesAndMtimeUnchanged","basePublishedFiles","changedOldPublishedPaths","missingOldPublishedPaths","newPublishedPaths","forbiddenNewPublishedPaths"]},ensure_ascii=False))
    return 0 if report["pass"] else 1
if __name__=="__main__":
    raise SystemExit(main())
