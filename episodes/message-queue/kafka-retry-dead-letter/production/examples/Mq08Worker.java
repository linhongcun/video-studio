import java.nio.ByteBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRebalanceListener;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.ByteArrayDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.utils.internals.AppInfoParser;

/** Real Kafka I/O around a finite, explicitly simulated business handler. */
public final class Mq08Worker {
    private static final Duration POLL = Duration.ofMillis(50);
    private static final Pattern EVENT = Pattern.compile(
            "\\s*\\{\\s*\"eventId\"\\s*:\\s*\"E01\"\\s*,\\s*\"orderId\"\\s*:\\s*(?:7042|\"7042\")\\s*}\\s*");
    private final Config config;
    private final Mq08Core.Policy policy;
    private final TopicPartition partition;
    private final Mq08Core.Outcome[] outcomes;
    private final ExecutorService handlerExecutor = Executors.newSingleThreadExecutor(task -> {
        Thread thread = new Thread(task, "mq08-fixture-handler"); thread.setDaemon(true); return thread;
    });
    private final ExecutorService dlqExecutor = Executors.newSingleThreadExecutor(task -> {
        Thread thread = new Thread(task, "mq08-dlq-send"); thread.setDaemon(true); return thread;
    });
    private final long processStartedNanos = System.nanoTime();
    private Mq08Core.Journal journal;
    private KafkaConsumer<byte[], byte[]> consumer;
    private KafkaProducer<String, String> producer;
    private ConsumerRecord<byte[], byte[]> held;
    private Future<Mq08Core.Outcome> handler;
    private Future<Future<RecordMetadata>> sendInvocation;
    private Future<RecordMetadata> delivery;
    private boolean committing;
    private boolean commitSucceeded;
    private Exception commitFailure;
    private boolean finished;
    private boolean closing;

    private Mq08Worker(Config config) {
        this.config = config;
        policy = new Mq08Core.Policy(config.backoffMs, config.handlerOutcomes, config.handlerDelayMs);
        outcomes = Arrays.stream(config.handlerOutcomes.split(",", -1))
                .map(value -> Mq08Core.Outcome.valueOf(value.toUpperCase(java.util.Locale.ROOT)))
                .toArray(Mq08Core.Outcome[]::new);
        if (outcomes.length < 1 || outcomes.length > Mq08Core.MAX_STARTED)
            throw new IllegalArgumentException("use 1..3 fixture outcomes");
        partition = new TopicPartition(config.topic, 0);
    }
    public static void main(String[] args) {
        try { new Mq08Worker(Config.parse(args)).run(); }
        catch (Exception failure) {
            log("fatal", "exception", failure.getClass().getName(), "message", failure.getMessage());
            failure.printStackTrace(System.err);
            System.exit(1);
        }
    }
    private void run() throws Exception {
        if (!AppInfoParser.getVersion().equals("4.4.0"))
            throw new IllegalStateException("Kafka client must be exactly 4.4.0; got " + AppInfoParser.getVersion());
        try (Mq08Core.Journal ownedJournal = new Mq08Core.Journal(config.stateDir)) {
            journal = ownedJournal;
            log("journal_lock_acquired", "path", journal.path().toString());
            journal.verifyConfiguration(config.topic, config.group, config.dlq, policy);
            log("config", "kafkaVersion", AppInfoParser.getVersion(), "group", config.group,
                    "topic", config.topic, "partition", 0, "dlq", config.dlq,
                    "group.protocol", "classic", "enable.auto.commit", false,
                    "max.poll.records", 1, "allow.auto.create.topics", false,
                    "pollMs", 50, "maxStarted", 3, "backoffMs", config.backoffMs,
                    "handlerOutcomes", config.handlerOutcomes, "handlerDelayMs", config.handlerDelayMs,
                    "acks", "all", "enable.idempotence", true, "max.block.ms", 2000,
                    "delivery.timeout.ms", 3000, "request.timeout.ms", 1000, "linger.ms", 0);
            try (KafkaConsumer<byte[], byte[]> ownedConsumer = new KafkaConsumer<>(consumerProperties());
                 KafkaProducer<String, String> ownedProducer = new KafkaProducer<>(producerProperties())) {
                consumer = ownedConsumer;
                producer = ownedProducer;
                var metadata = consumer.partitionsFor(config.topic, Duration.ofSeconds(2));
                if (metadata.size() != 1 || metadata.get(0).partition() != 0)
                    throw new IllegalArgumentException("input topic must contain exactly partition P0");
                OffsetAndMetadata committed = consumer.committed(Set.of(partition), Duration.ofSeconds(2)).get(partition);
                long position = committed == null ? -1 : committed.offset();
                log("startup_committed", "offset", position, "journalPhase", phase());
                if (reconcileCommitted(position)) return;
                consumer.subscribe(List.of(config.topic), new ConsumerRebalanceListener() {
                    @Override public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
                        if (!closing && held != null && !finished && partitions.contains(partition))
                            throw new IllegalStateException("partition revoked while E01 held; stop without commit");
                    }
                    @Override public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
                        if (!partitions.equals(Set.of(partition)) &&
                                !(partitions.size() == 1 && partitions.contains(partition)))
                            throw new IllegalStateException("expected exclusive P0 assignment: " + partitions);
                        if (journal.state() != null) consumer.seek(partition, journal.state().identity().offset());
                        log("partition_assigned", "partition", 0, "recoverySeek",
                                journal.state() == null ? null : journal.state().identity().offset());
                    }
                });
                try {
                    while (!finished) {
                        if (elapsedMs() >= config.maxRuntimeMs)
                            throw new IllegalStateException("max runtime reached; preserve journal and do not commit");
                        long pollStart = elapsedMs();
                        var records = consumer.poll(POLL); // All consumer methods remain on this owner thread.
                        log("poll", "startedMs", pollStart, "returned", records.count(),
                                "paused", held != null, "journalPhase", phase(), "elapsedMs", elapsedMs());
                        for (ConsumerRecord<byte[], byte[]> record : records) accept(record);
                        advance();
                    }
                } finally { closing = true; }
            } finally {
                handlerExecutor.shutdownNow();
                dlqExecutor.shutdownNow();
                handlerExecutor.awaitTermination(1, TimeUnit.SECONDS);
                dlqExecutor.awaitTermination(1, TimeUnit.SECONDS);
            }
        }
    }
    private boolean reconcileCommitted(long committed) throws Exception {
        Mq08Core.State state = journal.state();
        if (state == null) return false;
        long next = Math.addExact(state.identity().offset(), 1);
        boolean terminal = state.phase() == Mq08Core.Phase.BUSINESS_DONE ||
                state.phase() == Mq08Core.Phase.DLQ_CONFIRMED || state.phase() == Mq08Core.Phase.COMMITTED;
        if (committed >= next) {
            if (!terminal) throw new IllegalStateException("Kafka progress advanced without local terminal result");
            if (state.phase() != Mq08Core.Phase.COMMITTED) {
                journal.markCommitted(); persisted("startup_reconcile");
            }
            log("already_committed", "offset", committed, "nextOffset", next, "noPollNeeded", true);
            return true;
        }
        if (state.phase() == Mq08Core.Phase.COMMITTED)
            throw new IllegalStateException("Kafka offset reset behind COMMITTED journal; use a separate experiment directory/group");
        return false;
    }
    private void accept(ConsumerRecord<byte[], byte[]> record) throws Exception {
        if (held != null || record.partition() != 0 || !record.topic().equals(config.topic))
            throw new IllegalStateException("unexpected record while E01 held");
        if (record.value() == null) throw new IllegalArgumentException("expected non-null E01 JSON fixture");
        String value = StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
                .decode(ByteBuffer.wrap(record.value())).toString();
        if (!EVENT.matcher(value).matches())
            throw new IllegalArgumentException("expected only E01/order7042 fixture, received offset " + record.offset());
        consumer.pause(Set.of(partition));
        held = record; // Application retention is independent of Kafka's internal fetch buffer.
        Mq08Core.Identity identity = new Mq08Core.Identity(record.topic(), record.partition(), record.offset(),
                "E01", Mq08Core.sha256(record.value()), "notify", config.group, config.dlq);
        journal.bind(identity, policy, record.value(), record.key()); persisted("bind_or_verify");
        log("record_held", "eventId", "E01", "orderId", 7042, "offset", record.offset(),
                "logicalHandler", "notify", "idempotencyKey", "notify:E01");
        if (journal.state().phase() == Mq08Core.Phase.IN_FLIGHT) {
            journal.recoverInFlight(System.currentTimeMillis()); persisted("recover_unknown_outcome");
        }
    }
    private void advance() throws Exception {
        if (held == null) return;
        if (commitFailure != null) throw new IllegalStateException("original commit failed; keep durable terminal state", commitFailure);
        if (commitSucceeded) {
            journal.markCommitted(); persisted("original_commit_acknowledged");
            consumer.resume(Set.of(partition));
            log("partition_resumed", "partition", 0, "nextOffset", held.offset() + 1,
                    "stopBeforeNextPoll", true);
            finished = true;
            return;
        }
        Mq08Core.State state = journal.state();
        switch (state.phase()) {
            case READY, BACKOFF -> {
                if (System.currentTimeMillis() < state.readyAtMs()) return;
                journal.begin(System.currentTimeMillis()); persisted("begin");
                int started = journal.state().totalStarted();
                log("attempt_start", "eventId", "E01", "totalStarted", started, "maxStarted", 3,
                        "idempotencyKey", "notify:E01");
                crash("after-begin");
                Mq08Core.Outcome outcome = outcomes[Math.min(started - 1, outcomes.length - 1)];
                handler = handlerExecutor.submit(() -> {
                    log("handler_invoked", "totalStarted", started, "logicalHandler", "notify",
                            "fixtureOnly", true, "idempotencyKey", "notify:E01");
                    Thread.sleep(config.handlerDelayMs); // Bounded controlled fixture, no real notification.
                    return outcome;
                });
            }
            case IN_FLIGHT -> {
                if (handler == null) throw new IllegalStateException("missing handler for current reservation");
                if (!handler.isDone()) return;
                Mq08Core.Outcome outcome = handler.get();
                handler = null;
                log("classification", "totalStarted", state.totalStarted(), "outcome", outcome.name().toLowerCase(java.util.Locale.ROOT));
                if (outcome == Mq08Core.Outcome.SUCCESS) crash("after-handler-success-before-journal");
                journal.classify(outcome, System.currentTimeMillis()); persisted("classify");
            }
            case DLQ_PENDING -> {
                if (sendInvocation == null) {
                    String payload = dlqPayload(state);
                    log("dlq_application_send", "applicationSendOrdinalThisProcess", 1,
                            "totalStarted", state.totalStarted(), "reason", state.reason(), "topic", config.dlq);
                    // send() can block on metadata up to max.block.ms; keep it off the consumer owner.
                    sendInvocation = dlqExecutor.submit(() -> producer.send(
                            new ProducerRecord<>(config.dlq, "notify:E01", payload)));
                }
                if (delivery == null) {
                    if (!sendInvocation.isDone()) return;
                    try { delivery = sendInvocation.get(); }
                    catch (Exception failure) { dlqFailed(failure); }
                }
                if (!delivery.isDone()) return;
                RecordMetadata metadata;
                try { metadata = delivery.get(); } // No timeout: isDone established a terminal future first.
                catch (Exception failure) { dlqFailed(failure); return; }
                log("dlq_future_confirm", "topic", metadata.topic(), "partition", metadata.partition(),
                        "offset", metadata.offset(), "totalStarted", state.totalStarted());
                crash("after-dlq-ack-before-journal");
                journal.confirmDlq(metadata.topic(), metadata.partition(), metadata.offset()); persisted("dlq_confirmed");
                crash("after-dlq-journal-before-commit");
            }
            case BUSINESS_DONE, DLQ_CONFIRMED -> {
                if (committing) return;
                committing = true;
                long nextOffset = Math.addExact(held.offset(), 1);
                log("original_commit_start", "offset", held.offset(), "nextOffset", nextOffset, "journalPhase", phase());
                consumer.commitAsync(Map.of(partition, new OffsetAndMetadata(nextOffset)), (offsets, failure) -> {
                    if (failure != null) {
                        commitFailure = failure;
                        log("original_commit_failure", "nextOffset", nextOffset, "message", failure.toString());
                    } else {
                        commitSucceeded = true;
                        log("original_commit", "nextOffset", nextOffset, "success", true);
                    }
                });
            }
            case COMMITTED -> throw new IllegalStateException("COMMITTED journal should have reconciled before poll");
        }
    }
    private void dlqFailed(Exception failure) {
        log("dlq_future_failure", "journalPhase", phase(), "originalCommitPerformed", false,
                "message", failure.toString());
        throw new IllegalStateException("single application DLQ send failed; keep DLQ_PENDING, exit, no original commit", failure);
    }
    private static String dlqPayload(Mq08Core.State state) {
        var id = state.identity();
        return "{\"eventId\":\"E01\",\"orderId\":7042,\"logicalHandler\":\"notify\"," +
                "\"idempotencyKey\":\"notify:E01\",\"originalTopic\":" + quote(id.topic()) +
                ",\"originalPartition\":0,\"originalOffset\":" + id.offset() +
                ",\"totalStarted\":" + state.totalStarted() + ",\"reason\":" + quote(state.reason()) +
                ",\"originalValueBase64\":" + quote(state.valueBase64()) +
                ",\"originalKeyBase64\":" + quote(state.keyBase64()) + "}";
    }
    private Properties consumerProperties() {
        Properties p = new Properties();
        p.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, config.bootstrap);
        p.put(ConsumerConfig.GROUP_ID_CONFIG, config.group);
        p.put("group.protocol", "classic");
        p.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
        p.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "1");
        p.put(ConsumerConfig.ALLOW_AUTO_CREATE_TOPICS_CONFIG, "false");
        p.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        p.put(ConsumerConfig.DEFAULT_API_TIMEOUT_MS_CONFIG, "2000");
        p.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, "6000");
        p.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, "1000");
        p.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer.class);
        p.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer.class);
        p.put(ConsumerConfig.CLIENT_ID_CONFIG, "mq08-owner");
        return p;
    }
    private Properties producerProperties() {
        Properties p = new Properties();
        p.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, config.bootstrap);
        p.put(ProducerConfig.ACKS_CONFIG, "all");
        p.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
        p.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, "2000");
        p.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, "3000");
        p.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, "1000");
        p.put(ProducerConfig.LINGER_MS_CONFIG, "0");
        p.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        p.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        p.put(ProducerConfig.CLIENT_ID_CONFIG, "mq08-dlq");
        return p;
    }
    private void persisted(String action) {
        var state = journal.state();
        log("journal_persist", "action", action, "phase", state.phase().name(),
                "totalStarted", state.totalStarted(), "readyAtMs", state.readyAtMs(), "reason", state.reason());
    }
    private String phase() { return journal.state() == null ? "UNBOUND" : journal.state().phase().name(); }
    private long elapsedMs() { return (System.nanoTime() - processStartedNanos) / 1_000_000; }
    private void crash(String hook) {
        if (config.crashAt.equals(hook)) {
            log("crash_hook", "hook", hook, "haltCode", 86, "journalPhase", phase(),
                    "totalStarted", journal.state().totalStarted());
            System.out.flush(); System.err.flush(); Runtime.getRuntime().halt(86);
        }
    }
    private static synchronized void log(String event, Object... pairs) {
        StringBuilder line = new StringBuilder("{\"timestamp\":").append(quote(Instant.now().toString()))
                .append(",\"pid\":").append(ProcessHandle.current().pid())
                .append(",\"thread\":").append(quote(Thread.currentThread().getName()))
                .append(",\"event\":").append(quote(event));
        for (int i = 0; i < pairs.length; i += 2) {
            line.append(',').append(quote(pairs[i].toString())).append(':');
            Object value = pairs[i + 1];
            if (value == null) line.append("null");
            else if (value instanceof Number || value instanceof Boolean) line.append(value);
            else line.append(quote(value.toString()));
        }
        System.out.println(line.append('}')); System.out.flush();
    }
    private static String quote(String value) {
        if (value == null) return "null";
        StringBuilder out = new StringBuilder("\"");
        for (char character : value.toCharArray()) {
            switch (character) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                default -> { if (character < 32) out.append(String.format("\\u%04x", (int) character)); else out.append(character); }
            }
        }
        return out.append('"').toString();
    }
    private record Config(String bootstrap, String topic, String dlq, String group, Path stateDir,
                          String handlerOutcomes, long backoffMs, long handlerDelayMs,
                          String crashAt, long maxRuntimeMs) {
        static Config parse(String[] args) {
            Set<String> allowed = Set.of("bootstrap", "topic", "dlq", "group", "state-dir", "handler-outcomes",
                    "backoff-ms", "handler-delay-ms", "crash-at", "max-runtime-ms");
            Map<String, String> values = new HashMap<>();
            for (int i = 0; i < args.length; i += 2) {
                if (!args[i].startsWith("--") || i + 1 == args.length)
                    throw new IllegalArgumentException("expected --option value");
                String key = args[i].substring(2);
                if (!allowed.contains(key) || values.putIfAbsent(key, args[i + 1]) != null)
                    throw new IllegalArgumentException("unknown or duplicate option: " + key);
            }
            for (String key : List.of("bootstrap", "topic", "dlq", "group", "state-dir"))
                if (!values.containsKey(key) || values.get(key).isBlank())
                    throw new IllegalArgumentException("required --" + key);
            String crash = values.getOrDefault("crash-at", "none");
            if (!Set.of("none", "after-begin", "after-handler-success-before-journal",
                    "after-dlq-ack-before-journal", "after-dlq-journal-before-commit").contains(crash))
                throw new IllegalArgumentException("unsupported crash hook");
            long runtime = Long.parseLong(values.getOrDefault("max-runtime-ms", "60000"));
            if (runtime < 1 || runtime > 600000) throw new IllegalArgumentException("max runtime must be 1..600000 ms");
            if (values.get("topic").equals(values.get("dlq")))
                throw new IllegalArgumentException("input and DLQ topics must differ");
            return new Config(values.get("bootstrap"), values.get("topic"), values.get("dlq"),
                    values.get("group"), Path.of(values.get("state-dir")),
                    values.getOrDefault("handler-outcomes", "temporary,temporary,success"),
                    Long.parseLong(values.getOrDefault("backoff-ms", "400")),
                    Long.parseLong(values.getOrDefault("handler-delay-ms", "250")), crash, runtime);
        }
    }
}
