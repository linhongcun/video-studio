# MQ05 consumer replay: fresh real runtime, 2026-11-02

This archive is a fresh Kafka4.4.0/Java21/PostgreSQL18.0 experiment on the MQ05 revision branch. `experiment-summary.json` binds the accepted run, actual source and selected raw observations; `runtime-files-sha256.json` freezes every retained file except itself. `verify_records.py` reads the archive without starting services or modifying evidence.

Each of three branches uses its own fresh single-partition RF1 topic, same-group sequential A then B, fresh DB schema with account17=0, and exactly one application producer.send of E01/order7042/account17/delta10 at P0offset0. Producer idempotence is enabled with retries3. Setup explicitly persists group offset0 through Admin.alterConsumerGroupOffsets and queries the broker; this is not inferred from auto.offset.reset=earliest. Metadata reports leader/replicas/ISR=[1]. Consumers use classic/Range/manual commit/max.poll.records1. Consumer on-assignment observes restored position before record delivery; actual NetworkClient FETCH requests bind topicUUID and fetchOffset.

| Branch | A before halt86 | B recovery | Final points | Group committed | Physical log |
| --- | --- | --- | --- | --- | --- |
| unsafe | DB+10 COMMIT; Kafka0 | restore0/Fetch0, same E01offset0, add10 again then commit1 | 20 | 1 | one E01offset0, LEO1 |
| safe | marker(points,E01)+10 in same local DB transaction COMMIT; Kafka0 | restore0/Fetch0, same record; insert returns0, no update; commit1 | 10, one marker | 1 | one E01offset0, LEO1 |
| early-commit | Kafka1 before any DB effect | restore1/Fetch1, bounded poll yields none | 0 | 1 | original E01offset0 retained, LEO1 |

The safe fixture begins at0 with no marker before A's first DB transaction. Its update must affect exactly one account row, otherwise the local transaction rolls back. Kafka offset commit is independent of the DB transaction in all branches. The early-commit example skips a retained record; it does not erase it.

Accepted run has15 probe JVM invocations (3setup/3A/3B/6independent snapshots), three intentional halt86 exits, and91 observed assertions. Official DumpLogSegments decodes each exact-byte retained binary segment and shows one valid record batch/record. Full original command logs, focused NetworkClient DEBUG and broker WARN logs remain retained. Opaque Kafka protocol IDs and apiKey enum labels are fixture data, not secrets.

Both owned services are stopped, all three accepted-run ports were freshly bound after cleanup, and only the owned run temporary data was removed. Verified dependency caches remain in the task private /tmp prefix. `cleanup-final.json` names the processes/ports. Earlier syntax, producer configuration and initial logging-evidence failures remain separate and are not relabeled as passes. No old scripts were rerun into historical archives; adapted toolchain helpers and their before/after identity are recorded.

This proves the specified finite recovery behavior, not a benchmark, physical powerloss, concurrent stable ownership, or atomic Kafka-and-database commit. Source facts and the video teaching model remain separate. No source production, TTS, freeze or site inputs are changed here.
