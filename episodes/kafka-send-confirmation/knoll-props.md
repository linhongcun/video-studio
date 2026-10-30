# MQ04 drawing inventory

- Immutable Kafka series background and original Kafka brand component, credited in the component's adjacent license/source files.
- Persistent caller panel: E01/order7042, original F1, callback and new F2 only when a new application send exists.
- Per-partition P0 batch queue and separate Sender inflight panel. One moving B1 card has one position; the queue/inflight memberships come from model.json. Producer identity appears at initial drain, then remains attached.
- Broker P0 log slots with actual teaching-model offsets and next-position count; a distinct recent producer-state area records identity, epoch/range and original offset. A log record copy and a client inflight batch represent different structures.
- Request/response dots cross the narrow client–Broker gap. Blocked successful responses are visibly marked and do not complete F1. No arrow crosses the header or panel title text.
- Grouped identity detail: current sending identity A·0 (producerId501/epoch0) and full partition batch range0..0. The duplicate decision leaves log count/end unchanged. New B uses PID902, not a changed business eventId.
- Reset card for independent unknown/local-failure contrasts. Summary cards refer to evidence, rather than simulating another send.

All objects are procedural React/SVG/HTML. They are a source-constrained finite teaching trace, not screenshots of a running Broker, benchmark, packet capture or failure-injection experiment. The official source-class unit fixture is separately scoped in experiments/result.json.
