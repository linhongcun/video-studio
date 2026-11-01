# MQ15 real Kafka 4.4.0 runtime

The accepted finite run is
[`runs/20261101T092613950298Z/post-validation/report.json`](runs/20261101T092613950298Z/post-validation/report.json).
It is actual Kafka traffic and replica-file evidence, separate from the animation model, teaching assumptions, independent source review, and final-media QA.

Kafka is the freshly downloaded official `kafka_2.13-4.4.0.tgz`, verified against the official SHA512 in the parent runtime `dependencies/` archive. The running client reports version `4.4.0` and commit `1156b2752aaa28ea`; fixed full source commit is `1156b2752aaa28eafc0b4c4d387e63356793268d`. The exact executed Java and Python sources are copied into the accepted run and hash-bound by its original receipt.

The three isolated combined broker/controller JVMs use three distinct listeners. Clients connect directly to `CLIENT`; follower replication uses owned loopback proxies on `REPLICATION`; controllers communicate directly on `CONTROLLER`. Actual Kafka request headers identify follower clients as `broker-<id>-fetcher-0`. A targeted gate closes an existing matching connection before a send and rejects subsequent matching requests. The accepted run does not pause an entire JVM while testing slow replicas or reduced ISR. These data gates preserve the controller and client listeners; the two leader-kill tests leave the surviving two controllers to elect cleanly.

All topics start with one empty partition explicitly assigned to brokers `[1,2,3]`, RF3, `min.insync.replicas=2`, and unclean election disabled. The official `kafka-features.sh describe` output explicitly reports `eligible.leader.replicas.version` at `FinalizedVersionLevel: 0`. This is saved because the Admin API's finalized map omits zero-level entries. Producers explicitly disable idempotence, set retries0 and max in flight1, use no compression, and send one `E01`/order7042/key7042 per independent topic. The actual `prepare` responses retain the rest of the finite timeout configuration.

| Real branch | Observed result |
|---|---|
| Healthy ISR3, acks1 | Send returns offset0; the later healthy snapshot contains the record on all three replicas. This does not mean acks1 waited for all three. |
| Healthy ISR3, acks all | Send returns offset0; all three physical copies and leader HW1 are observed. |
| Third replica gated but still ISR3 | Physical LEO is `{1:1,2:1,3:0}`, HW0, Future pending. Opening follower3's data gate permits its copy, HW1 and successful Future. |
| Stable ISR2 `[1,2]` | acks all succeeds with physical LEO `{1:1,2:1,3:0}` and HW1. |
| Stable ISR1 `[1]` | acks all returns `NotEnoughReplicasException`; all physical LEOs remain0 before and after. |
| Already successful acks all, leader1 killed | Clean leader2/ISR `[2,3]` retains E01 and HW1; the real observer reads E01@0. |
| acks1 while both follower paths are gated | Future succeeds with only old leader1 containing E01, ISR still3 and HW0. The gate stays closed while leader1 is killed. Clean leader2 has LEO/HW0 and no readable E01; offline old leader1 still physically contains E01. |

`probe.jsonl` contains actual commands and responses. `assertions.jsonl` contains34 passed real-run assertions and the retained later dump failure. `snapshots/*/observation.json` separates metadata ISR/leader, physical batch-derived LEO, and `read_uncommitted` consumer `endOffsets`. The latter is the leader HW, as independently traced in the parent `runtime/hw-source-evidence/chain-audit.json` through the fixed `Partition.scala` implementation. It is not used as a substitute for physical LEO.

All33 empty and nonempty replica segment snapshots were subsequently checked by the official `DumpLogSegments` reader. The21 nonempty batches have valid CRCs, offset0 and the expected E01 payload; every official physical LEO matches the captured observation. The byte-identical-copy mapping, actual command, stdout and empty stderr are in `post-validation/`.

Three failure boundaries remain intact:

1. `failures/compile-appinfoparser-v1/`: Kafka4.4 moved `AppInfoParser` into `utils.internals`; the original failed runtime source and compiler error remain. Only this runtime probe was corrected.
2. `runs/20261101T092135857476Z/`: the first whole-JVM pause caused an observer metadata call to reach a paused CLIENT listener and timeout. That run remains failed, and all its own services were stopped. The accepted second run replaces whole-JVM pauses with per-follower data gates.
3. The accepted run's original `report.json` remains `pass:false`: the final optional dump step rejected a copied basename `node1-0.log`, because official log segments require a numeric base-offset filename. Original failure output is unchanged. The derived `post-validation/report.json` closes exactly this audit gap using byte-identical numeric-name copies and a successful full official decode. No broker was rerun, nor was an experiment outcome changed, to repair the file-naming issue.

Raw broker errors include the deliberately exercised ISR1 rejection and `NotControllerException` on `wantShutDown=true` requests while the final combined nodes were stopped sequentially. These errors are retained; the report does not call service shutdown error-free. Every tracked JVM exited, every proxy closed, all12 owned listener ports were independently checked closed, and only the marked owned temporary data tree was removed. Replica snapshots and all raw evidence remain here.

Run `python3 verify_records.py` from this directory for a read-only hash and receipt check. It starts no services and writes no output files. Reproducing the cluster starts owned temporary processes and is unnecessary for consuming this evidence. The original executed harness is preserved even where its final dump naming needs the documented post-validation step.

This is neither a benchmark nor a machine power-loss test. It demonstrates these finite local configurations and gates; it does not promise identical outcomes for arbitrary failures or establish distributed exactly-once business effects.
