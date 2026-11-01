import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.concurrent.TimeUnit;

/** Pure-JDK tests: no broker, no pretend Kafka execution. Run with run.sh test-core. */
public final class Mq08CoreTest {
    private static final byte[] VALUE = "{\"eventId\":\"E01\",\"orderId\":7042}".getBytes(StandardCharsets.UTF_8);
    private static final Mq08Core.Policy POLICY = new Mq08Core.Policy(400, "temporary,temporary,success", 250);
    private static final Mq08Core.Identity ID = new Mq08Core.Identity("orders", 0, 0,
            "E01", Mq08Core.sha256(VALUE), "notify", "mq08-test", "orders-dlq");
    private static int checks;
    public static void main(String[] args) throws Exception {
        if (args.length > 0) { child(args); return; }
        Path root = Files.createTempDirectory("mq08-core-test-");
        try {
            budgetAndBackoff(root.resolve("budget"));
            successAndPermanent(root.resolve("success"), root.resolve("permanent"));
            crashRecovery(root.resolve("crash"));
            processLock(root.resolve("lock"));
            identityAndConfiguration(root.resolve("identity"));
            persistenceFailure(root.resolve("failed-write"));
            System.out.println("PASS Mq08CoreTest checks=" + checks + " (pure core; not Kafka runtime)");
        } finally {
            try (var paths = Files.walk(root)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) Files.delete(path);
            }
        }
    }
    private static void budgetAndBackoff(Path path) throws Exception {
        try (var journal = create(path)) {
            journal.begin(1000);
            journal.classify(Mq08Core.Outcome.TEMPORARY, 1100);
            check(journal.state().readyAtMs() == 1500, "fixed backoff scheduled from classification");
            expect(IllegalStateException.class, () -> journal.begin(1499));
        }
        try (var journal = new Mq08Core.Journal(path)) {
            check(journal.state().totalStarted() == 1, "reopen preserves first reservation");
            journal.begin(1500); journal.classify(Mq08Core.Outcome.TEMPORARY, 1600);
            journal.begin(2000); journal.classify(Mq08Core.Outcome.TEMPORARY, 2100);
            check(journal.state().totalStarted() == 3, "exactly three reservations");
            check(journal.state().phase() == Mq08Core.Phase.DLQ_PENDING, "third temporary goes to DLQ");
            expect(IllegalStateException.class, () -> journal.begin(100000));
            expect(IllegalStateException.class, journal::markCommitted);
            journal.confirmDlq("orders-dlq", 0, 7);
        }
        try (var journal = new Mq08Core.Journal(path)) {
            check(journal.state().phase() == Mq08Core.Phase.DLQ_CONFIRMED, "confirmed DLQ survives reopen");
            check(journal.state().dlqOffset() == 7, "confirmed metadata retained");
            journal.markCommitted();
        }
        try (var journal = new Mq08Core.Journal(path)) {
            check(journal.state().phase() == Mq08Core.Phase.COMMITTED, "commit marker survives reopen");
        }
    }
    private static void successAndPermanent(Path success, Path permanent) throws Exception {
        try (var journal = create(success)) {
            journal.begin(0); journal.classify(Mq08Core.Outcome.SUCCESS, 1);
            check(journal.state().phase() == Mq08Core.Phase.BUSINESS_DONE, "success must precede commit");
            journal.markCommitted();
            expect(IllegalStateException.class, () -> journal.confirmDlq("orders-dlq", 0, 0));
        }
        try (var journal = create(permanent)) {
            journal.begin(0); journal.classify(Mq08Core.Outcome.PERMANENT, 1);
            check(journal.state().phase() == Mq08Core.Phase.DLQ_PENDING, "permanent refusal bypasses retry");
            check(journal.state().totalStarted() == 1, "permanent refusal does not consume remaining budget");
        }
    }
    private static void crashRecovery(Path path) throws Exception {
        for (int started = 1; started <= 3; started++) {
            int code = process("reserve-and-halt", path).waitFor();
            check(code == 86, "child performed abrupt process halt");
            try (var journal = new Mq08Core.Journal(path)) {
                check(journal.state().phase() == Mq08Core.Phase.IN_FLIGHT, "reservation persisted before process death");
                check(journal.state().totalStarted() == started, "new process cannot reset consumed budget");
                journal.recoverInFlight(1000);
                check(journal.state().phase() == (started < 3 ? Mq08Core.Phase.BACKOFF : Mq08Core.Phase.DLQ_PENDING),
                        "unknown outcome consumes reservation and respects budget");
                if (started < 3) {
                    check(journal.state().readyAtMs() == 1400, "unknown outcome waits a new backoff");
                    expect(IllegalStateException.class, () -> journal.begin(1399));
                }
            }
        }
    }
    private static void processLock(Path path) throws Exception {
        try (var journal = create(path)) {
            check(journal.state().totalStarted() == 0, "lock owner remains idle");
            Process other = process("try-lock", path);
            check(other.waitFor(5, TimeUnit.SECONDS), "competing child terminates promptly");
            check(other.exitValue() == 17, "second process cannot enter same state directory");
        }
        try (var journal = new Mq08Core.Journal(path)) { check(journal.state() != null, "lock released on close"); }
    }
    private static void identityAndConfiguration(Path path) throws Exception {
        try (var journal = create(path)) {
            var wrongOffset = new Mq08Core.Identity("orders", 0, 1, "E01", Mq08Core.sha256(VALUE),
                    "notify", "mq08-test", "orders-dlq");
            expect(IllegalArgumentException.class, () -> journal.bind(wrongOffset, POLICY, VALUE, null));
            expect(IllegalArgumentException.class, () -> journal.bind(ID, POLICY, new byte[] { 1 }, null));
            expect(IllegalArgumentException.class, () -> journal.bind(ID, POLICY, VALUE, new byte[] { 1 }));
            expect(IllegalArgumentException.class, () -> journal.verifyConfiguration("orders", "new-group", "orders-dlq", POLICY));
            expect(IllegalArgumentException.class, () -> journal.verifyConfiguration("orders", "mq08-test", "new-dlq", POLICY));
            expect(IllegalArgumentException.class, () -> journal.verifyConfiguration("orders", "mq08-test", "orders-dlq",
                    new Mq08Core.Policy(401, POLICY.outcomes(), 250)));
            check(journal.state().totalStarted() == 0, "mismatch never consumes budget");
        }
    }
    private static void persistenceFailure(Path path) throws Exception {
        try (var journal = create(path)) {
            Files.delete(journal.path());
            Files.createDirectory(journal.path()); // Force ATOMIC_MOVE replacement failure on local Linux.
            int[] calls = { 0 };
            try { journal.begin(0); calls[0]++; throw new AssertionError("expected forced persistence failure"); }
            catch (IOException expected) { checks++; }
            check(calls[0] == 0, "handler cannot be reached after failed begin persistence");
            check(journal.state().phase() == Mq08Core.Phase.READY && journal.state().totalStarted() == 0,
                    "failed begin never publishes an in-memory reservation");
        }
    }
    private static Mq08Core.Journal create(Path path) throws Exception {
        var journal = new Mq08Core.Journal(path);
        journal.bind(ID, POLICY, VALUE, null);
        return journal;
    }
    private static Process process(String mode, Path path) throws IOException {
        return new ProcessBuilder(Path.of(System.getProperty("java.home"), "bin", "java").toString(),
                "-cp", System.getProperty("java.class.path"), "Mq08CoreTest", mode, path.toString())
                .inheritIO().start();
    }
    private static void child(String[] args) throws Exception {
        Path path = Path.of(args[1]);
        if (args[0].equals("try-lock")) {
            try (var journal = new Mq08Core.Journal(path)) { System.exit(18); }
            catch (IOException busy) { System.exit(17); }
        }
        if (args[0].equals("reserve-and-halt")) {
            try (var journal = create(path)) {
                journal.begin(10000);
                Runtime.getRuntime().halt(86); // Deliberately no handler invocation and no close.
            }
        }
        throw new IllegalArgumentException("unknown child test mode");
    }
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
        checks++;
    }
    private interface Checked { void run() throws Exception; }
    private static void expect(Class<? extends Throwable> expected, Checked operation) throws Exception {
        try { operation.run(); }
        catch (Throwable failure) {
            if (expected.isInstance(failure)) { checks++; return; }
            throw failure;
        }
        throw new AssertionError("expected " + expected.getSimpleName());
    }
}
