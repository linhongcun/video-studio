# Redis EP50–52 independent editorial gate

Reviewer: `/root/redis_editorial`. Prepared 2026-11-02. This document records review requirements, not an approval of unwritten scripts.

Read repository AGENTS, RULES and pipeline; lessons L027, L045–L052, L060; practices S021–S023. Fixed implementation baseline is Redis 8.4.0, commit `60ba86f3c8b4e1ec96451171753a0a38e5c45a0c` in all three saved tag responses. Redis docs snapshots are independent current documentation and require a version boundary where they mention newer releases.

## EP50 Sentinel

- Identify data master, data replicas and monitoring Sentinels as separate actors before voting. Two different decisions: diagnose unreachable master; authorize one Sentinel to run failover.
- ODOWN is a local Sentinel's SDOWN plus enough recent peer reports; it is weak agreement over a time window, not simultaneous unanimous agreement.
- Five known Sentinels/quorum2: two reports pass diagnosis; two votes do not pass majority3. A Sentinel may count its own vote. Majority is based on known members, not current online members; when configured quorum is above majority it also constrains authorization.
- Explicitly reset or restore conditions before showing success, to keep two-Sentinel failure and majority success separate.
- Elected Sentinel filters replicas before ordering: unavailable/stale/priority0 excluded; lower priority preferred, then greater processed replication offset, then lexicographically smaller runid. Votes do not target data replicas.
- Promotion/reconfiguration follows authorization and candidate choice; asynchronous replication does not guarantee zero lost acknowledged writes.

Read saved `sentinel-fixed.c`:4594–4632,4738–4857,5020–5119 and saved docs:930–1066,1074–1108.

## EP51 Cluster automatic failover

- First establish three slot-serving masters and each replica's replication relationship; failure detection, election and slot ownership are separate changes.
- PFAIL is local suspicion. FAIL uses recent master reports, including self only when eligible, then propagation. It is not the authorization vote itself.
- Replica must have an eligible failed master with slots and acceptable data age; rank affects start delay, it does not guarantee the freshest replica wins.
- Voters are slot-serving masters; three masters require two ACKs. Replicas do not vote for themselves and online subset does not redefine majority.
- Election request epoch and voter lastVoteEpoch prevent old/repeated votes from becoming a new authorization; same epoch should not be counted twice.
- Successful candidate updates configEpoch and slot ownership; distinguish currentEpoch from configEpoch and automatic flow from FORCE/TAKEOVER.
- Do not animate slots as classic consistent-hashing ring; promotion does not constitute resharding. No zero-loss promise under asynchronous replication.

Read saved `redis-cluster-legacy.c`:1900–1930,4042–4165,4292–4460 and docs:711–774,812–884. Source comment near4051 claiming quorum=size+1 is misleading; executable code uses size/2+1.

## EP52 approximate LRU

- Establish capacity pressure and fixed key accesses, distinguish capacity eviction from TTL expiration.
- Exact LRU is the reference, not Redis's actual hash-plus-linked-list implementation.
- Redis samples keys and merges sampled idle scores into bounded persistent candidate pool; retained pool entries affect later rounds.
- Pool stores idle scores at sampling time; choosing a retained entry checks key existence, not a fresh current-recency recomputation. Either freeze intervening accesses or label saved scores accurately.
- The oldest available candidate need not be the globally oldest key. A larger sample is a CPU/approximation tradeoff, not every-workload benefit guarantee.
- Actual pool size16 and default sampling5 may be simplified only with visible teaching-model disclosure. Stale/deleted keys can leave ghosts that are skipped.
- A seeded sample path is a teaching model. Standard server results do not expose exact internal samples/pool; runtime experiment scope must be distinct.
- LFU, volatile scope/noeviction and clock granularity belong mainly in article; do not crowd the main mechanism.

Read saved `evict.c`:30–110,134–223,570–657 and `key-eviction.md`:199–248.

## Cross-topic acceptance

- One concrete promise, source-backed causal chain, same example, visible condition changes, verbal chapter bridges and explicit reset for alternative cases.
- Novice can identify each actor and explain why the next step occurs without filling gaps using prior expertise. Terms follow demonstrated relationships.
- References keep exact real titles and institution/author credit; continuous source quotes support the adjacent claim. Research-only facts must not silently replace missing video causality.
- Approval is per exact script/article/research SHA. Voice is permitted only after root accepts independent editorial verdict. Dynamic, encoded-media, site and online validation are later independent gates, not implied by this review.
