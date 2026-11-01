import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.channels.OverlappingFileLockException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Properties;

/** Application policy, not a Kafka retry API. Requires Java 17+. */
public final class Mq08Core {
    public static final int MAX_STARTED = 3;
    public enum Phase { READY, BACKOFF, IN_FLIGHT, BUSINESS_DONE, DLQ_PENDING, DLQ_CONFIRMED, COMMITTED }
    public enum Outcome { TEMPORARY, PERMANENT, SUCCESS }
    public record Identity(String topic, int partition, long offset, String eventId,
                           String payloadHash, String logicalHandler, String group, String dlq) { }
    public record Policy(long backoffMs, String outcomes, long handlerDelayMs) {
        public Policy {
            if (backoffMs < 0 || backoffMs > 60_000 || handlerDelayMs < 0 || handlerDelayMs > 10_000)
                throw new IllegalArgumentException("fixture timing outside finite limits");
        }
    }
    public record State(Identity identity, Policy policy, String valueBase64, String keyBase64,
                        Phase phase, int totalStarted, long readyAtMs, String reason,
                        String dlqTopic, int dlqPartition, long dlqOffset) {
        State next(Phase phase, int started, long readyAt, String reason) {
            return new State(identity, policy, valueBase64, keyBase64, phase, started,
                    readyAt, reason, dlqTopic, dlqPartition, dlqOffset);
        }
    }
    public static String sha256(byte[] value) {
        try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value)); }
        catch (NoSuchAlgorithmException impossible) { throw new AssertionError(impossible); }
    }
    static String encode(byte[] value) {
        return value == null ? "NULL" : Base64.getEncoder().encodeToString(value);
    }
    public static final class Journal implements AutoCloseable {
        private final Path directory;
        private final Path journal;
        private final FileChannel lockChannel;
        private final FileLock processLock;
        private State state;

        public Journal(Path path) throws IOException {
            Files.createDirectories(path);
            directory = path.toRealPath();
            journal = directory.resolve("journal.properties");
            lockChannel = FileChannel.open(directory.resolve("worker.lock"),
                    StandardOpenOption.CREATE, StandardOpenOption.WRITE);
            FileLock acquired;
            try { acquired = lockChannel.tryLock(); }
            catch (OverlappingFileLockException busy) { acquired = null; }
            if (acquired == null) {
                lockChannel.close();
                throw new IOException("state directory already locked: " + directory);
            }
            processLock = acquired;
            try {
                if (Files.exists(journal)) {
                    Properties p = new Properties();
                    try (var input = Files.newInputStream(journal)) { p.load(input); }
                    state = decode(p);
                }
            } catch (IOException | RuntimeException failure) {
                processLock.close(); lockChannel.close(); throw failure;
            }
        }
        public State state() { return state; }
        public Path path() { return journal; }
        public void verifyConfiguration(String topic, String group, String dlq, Policy policy) {
            if (state != null && (!state.identity.topic.equals(topic) ||
                    !state.identity.group.equals(group) || !state.identity.dlq.equals(dlq) ||
                    state.identity.partition != 0 || !state.identity.eventId.equals("E01") ||
                    !state.identity.logicalHandler.equals("notify") || !state.policy.equals(policy)))
                throw new IllegalArgumentException("journal configuration mismatch; do not mix runs/events");
        }
        public void bind(Identity identity, Policy policy, byte[] value, byte[] key) throws IOException {
            if (state == null) {
                if (identity.partition != 0 || !identity.eventId.equals("E01") ||
                        !identity.logicalHandler.equals("notify") ||
                        !identity.payloadHash.equals(sha256(value)))
                    throw new IllegalArgumentException("unexpected fixture identity");
                persist(new State(identity, policy, encode(value), encode(key), Phase.READY,
                        0, 0, "ready", "", -1, -1));
            } else if (!state.identity.equals(identity) || !state.policy.equals(policy) ||
                    !state.valueBase64.equals(encode(value)) || !state.keyBase64.equals(encode(key))) {
                throw new IllegalArgumentException("journal identity mismatch: topic/P0/offset/event/hash/handler/key");
            }
        }
        /** A durable reservation precedes every handler invocation. Fail closed if persistence fails. */
        public void begin(long nowMs) throws IOException {
            require(Phase.READY, Phase.BACKOFF);
            if (state.totalStarted >= MAX_STARTED || nowMs < state.readyAtMs)
                throw new IllegalStateException("no attempt budget or backoff not due");
            persist(state.next(Phase.IN_FLIGHT, state.totalStarted + 1, 0, "attempt_reserved"));
        }
        public void classify(Outcome outcome, long nowMs) throws IOException {
            require(Phase.IN_FLIGHT);
            switch (outcome) {
                case SUCCESS -> persist(state.next(Phase.BUSINESS_DONE, state.totalStarted, 0, "success"));
                case PERMANENT -> persist(state.next(Phase.DLQ_PENDING, state.totalStarted, 0, "permanent_rejection"));
                case TEMPORARY -> {
                    boolean exhausted = state.totalStarted == MAX_STARTED;
                    persist(state.next(exhausted ? Phase.DLQ_PENDING : Phase.BACKOFF,
                            state.totalStarted, exhausted ? 0 : Math.addExact(nowMs, state.policy.backoffMs),
                            exhausted ? "temporary_budget_exhausted" : "temporary_failure"));
                }
            }
        }
        /** An unfinished reservation remains consumed, even if the process died before invocation. */
        public void recoverInFlight(long nowMs) throws IOException {
            if (state.phase != Phase.IN_FLIGHT) return;
            boolean exhausted = state.totalStarted == MAX_STARTED;
            persist(state.next(exhausted ? Phase.DLQ_PENDING : Phase.BACKOFF,
                    state.totalStarted, exhausted ? 0 : Math.addExact(nowMs, state.policy.backoffMs),
                    exhausted ? "unknown_outcome_budget_exhausted" : "unknown_outcome_after_crash"));
        }
        public void confirmDlq(String topic, int partition, long offset) throws IOException {
            require(Phase.DLQ_PENDING);
            if (!topic.equals(state.identity.dlq) || partition < 0 || offset < 0)
                throw new IllegalArgumentException("invalid acknowledged DLQ metadata");
            persist(new State(state.identity, state.policy, state.valueBase64, state.keyBase64,
                    Phase.DLQ_CONFIRMED, state.totalStarted, 0, state.reason, topic, partition, offset));
        }
        public void markCommitted() throws IOException {
            require(Phase.BUSINESS_DONE, Phase.DLQ_CONFIRMED);
            persist(state.next(Phase.COMMITTED, state.totalStarted, 0, state.reason));
        }
        private void require(Phase... expected) {
            if (state != null) for (Phase phase : expected) if (state.phase == phase) return;
            throw new IllegalStateException("unexpected state: " + (state == null ? "unbound" : state.phase));
        }
        private void persist(State candidate) throws IOException {
            Properties p = new Properties();
            p.setProperty("version", "1");
            p.setProperty("topic", candidate.identity.topic);
            p.setProperty("partition", Integer.toString(candidate.identity.partition));
            p.setProperty("offset", Long.toString(candidate.identity.offset));
            p.setProperty("eventId", candidate.identity.eventId);
            p.setProperty("payloadHash", candidate.identity.payloadHash);
            p.setProperty("logicalHandler", candidate.identity.logicalHandler);
            p.setProperty("group", candidate.identity.group);
            p.setProperty("dlq", candidate.identity.dlq);
            p.setProperty("backoffMs", Long.toString(candidate.policy.backoffMs));
            p.setProperty("handlerOutcomes", candidate.policy.outcomes);
            p.setProperty("handlerDelayMs", Long.toString(candidate.policy.handlerDelayMs));
            p.setProperty("maxStarted", Integer.toString(MAX_STARTED));
            p.setProperty("originalValueBase64", candidate.valueBase64);
            p.setProperty("originalKeyBase64", candidate.keyBase64);
            p.setProperty("phase", candidate.phase.name());
            p.setProperty("totalStarted", Integer.toString(candidate.totalStarted));
            p.setProperty("readyAtMs", Long.toString(candidate.readyAtMs));
            p.setProperty("reason", candidate.reason);
            p.setProperty("dlqTopic", candidate.dlqTopic);
            p.setProperty("dlqPartition", Integer.toString(candidate.dlqPartition));
            p.setProperty("dlqOffset", Long.toString(candidate.dlqOffset));
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            p.store(output, "MQ08 local single-process journal; not a distributed transaction");
            Path temporary = directory.resolve("journal.properties.tmp");
            try (FileChannel file = FileChannel.open(temporary, StandardOpenOption.CREATE,
                    StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.WRITE)) {
                ByteBuffer bytes = ByteBuffer.wrap(output.toByteArray());
                while (bytes.hasRemaining()) file.write(bytes);
                file.force(true);
            }
            // Do not fall back to a non-atomic move: this example requires a local Linux filesystem.
            Files.move(temporary, journal, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            try (FileChannel parent = FileChannel.open(directory, StandardOpenOption.READ)) { parent.force(true); }
            state = candidate; // Only report success after all persistence steps succeeded.
        }
        private static String field(Properties p, String key) {
            String value = p.getProperty(key);
            if (value == null) throw new IllegalArgumentException("missing journal field: " + key);
            return value;
        }
        private static State decode(Properties p) {
            if (!field(p, "version").equals("1") || Integer.parseInt(field(p, "maxStarted")) != MAX_STARTED)
                throw new IllegalArgumentException("unsupported journal version/budget");
            Identity identity = new Identity(field(p, "topic"), Integer.parseInt(field(p, "partition")),
                    Long.parseLong(field(p, "offset")), field(p, "eventId"), field(p, "payloadHash"),
                    field(p, "logicalHandler"), field(p, "group"), field(p, "dlq"));
            Policy policy = new Policy(Long.parseLong(field(p, "backoffMs")), field(p, "handlerOutcomes"),
                    Long.parseLong(field(p, "handlerDelayMs")));
            State state = new State(identity, policy, field(p, "originalValueBase64"),
                    field(p, "originalKeyBase64"), Phase.valueOf(field(p, "phase")),
                    Integer.parseInt(field(p, "totalStarted")), Long.parseLong(field(p, "readyAtMs")),
                    field(p, "reason"), field(p, "dlqTopic"), Integer.parseInt(field(p, "dlqPartition")),
                    Long.parseLong(field(p, "dlqOffset")));
            if (identity.offset < 0 || identity.partition != 0 || state.totalStarted < 0 ||
                    state.totalStarted > MAX_STARTED || !identity.eventId.equals("E01") ||
                    !identity.logicalHandler.equals("notify") ||
                    !sha256(Base64.getDecoder().decode(state.valueBase64)).equals(identity.payloadHash))
                throw new IllegalArgumentException("invalid journal identity/budget/payload");
            if ((state.phase == Phase.IN_FLIGHT || state.phase == Phase.BACKOFF) && state.totalStarted == 0)
                throw new IllegalArgumentException("invalid zero-start phase");
            if (state.phase == Phase.READY && state.totalStarted != 0)
                throw new IllegalArgumentException("invalid ready budget");
            if (state.phase == Phase.DLQ_CONFIRMED && (!state.dlqTopic.equals(identity.dlq) ||
                    state.dlqPartition < 0 || state.dlqOffset < 0))
                throw new IllegalArgumentException("invalid DLQ confirmation");
            return state;
        }
        @Override public void close() throws IOException { processLock.close(); lockChannel.close(); }
    }
}
