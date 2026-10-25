import java.util.ArrayList;
import java.util.List;

/** SDK-owned request shapes differ; the business expectation is independent. */
public final class VerifyAdapterUpgrade {
    private static final String RECIPIENT = "buyer17@shop.example";
    private static final String TEXT = "订单17已发货";
    private static final List<String> passed = new ArrayList<>();

    @FunctionalInterface
    interface CheckedAction { void run() throws Exception; }

    static final class V1Probe implements AdapterDemo.VendorSdk {
        final List<AdapterDemo.Payload> requests = new ArrayList<>();
        public AdapterDemo.RawReceipt deliver(AdapterDemo.Payload request) {
            requests.add(request);
            return new AdapterDemo.RawReceipt("QUEUED", "Q17");
        }
    }

    static final class V2Probe implements AdapterUpgradeDemo.VendorSdkV2 {
        final List<AdapterUpgradeDemo.Envelope> requests = new ArrayList<>();
        AdapterUpgradeDemo.ReplyV2 reply;
        AdapterUpgradeDemo.VendorFailureV2 failure;
        boolean recordAcceptanceBeforeFailure;
        int recordedAcceptances;

        V2Probe(AdapterUpgradeDemo.ReplyV2 reply) { this.reply = reply; }

        public AdapterUpgradeDemo.ReplyV2 submit(AdapterUpgradeDemo.Envelope request)
                throws AdapterUpgradeDemo.VendorFailureV2 {
            requests.add(request);
            if (recordAcceptanceBeforeFailure) recordedAcceptances++;
            if (failure != null) throw failure;
            return reply;
        }
    }

    static AdapterUpgradeDemo.ReplyV2 reply(String state, String reference) {
        return new AdapterUpgradeDemo.ReplyV2(new AdapterUpgradeDemo.ReceiptV2(state, reference));
    }

    static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    static <T extends Throwable> T expect(Class<T> type, CheckedAction action) throws Exception {
        try {
            action.run();
        } catch (Throwable error) {
            if (type.isInstance(error)) return type.cast(error);
            throw new AssertionError("Expected " + type.getSimpleName() + ", got " + error, error);
        }
        throw new AssertionError("Expected " + type.getSimpleName());
    }

    static AdapterDemo.Submission submit(V2Probe sdk) throws AdapterDemo.SendFailure {
        return AdapterUpgradeDemo.useBusiness(new AdapterUpgradeDemo.NotificationAdapterV2(sdk));
    }

    static void sameBusinessWithDifferentSdks() throws Exception {
        V1Probe v1 = new V1Probe();
        V2Probe v2 = new V2Probe(reply("ENQUEUED", "Q17"));
        AdapterDemo.Submission first = AdapterUpgradeDemo.useBusiness(new AdapterDemo.NotificationAdapter(v1));
        AdapterDemo.Submission second = submit(v2);
        AdapterDemo.Submission expected = new AdapterDemo.Submission(AdapterDemo.Status.ACCEPTED, "Q17");
        check(first.equals(expected) && second.equals(expected), "both meet the same business result");
        check(v1.requests.equals(List.of(new AdapterDemo.Payload(RECIPIENT, TEXT))), "V1 target/body exact once");
        check(v2.requests.equals(List.of(new AdapterUpgradeDemo.Envelope(RECIPIENT, TEXT))), "V2 destination/content exact once");
        passed.add("same unchanged business call receives ACCEPTED/Q17 from both independently invoked SDK versions");
    }

    static void explicitDecline() throws Exception {
        V2Probe sdk = new V2Probe(reply("DECLINED", "vendor-trace"));
        AdapterDemo.Submission result = submit(sdk);
        check(result.equals(new AdapterDemo.Submission(AdapterDemo.Status.REJECTED, "")), "decline remains business rejection");
        check(sdk.requests.size() == 1, "one rejected V2 call");
        passed.add("V2 DECLINED maps to the same REJECTED and empty business reference");
    }

    static void invalidInputs() throws Exception {
        V2Probe sdk = new V2Probe(reply("ENQUEUED", "Q17"));
        AdapterDemo.Notifier notifier = new AdapterUpgradeDemo.NotificationAdapterV2(sdk);
        for (String invalid : new String[] { null, "", " \t\n" }) {
            expect(IllegalArgumentException.class, () -> notifier.send(invalid, TEXT));
            expect(IllegalArgumentException.class, () -> notifier.send(RECIPIENT, invalid));
        }
        check(sdk.requests.isEmpty(), "six invalid inputs fail before V2 call");
        passed.add("six invalid V2 business inputs fail before delegation");
    }

    static void missingReplyOrState() throws Exception {
        List<AdapterUpgradeDemo.ReplyV2> malformed = new ArrayList<>();
        malformed.add(null);
        malformed.add(new AdapterUpgradeDemo.ReplyV2(null));
        malformed.add(reply(null, "Q17"));
        malformed.add(reply("", "Q17"));
        malformed.add(reply(" \t", "Q17"));
        for (AdapterUpgradeDemo.ReplyV2 raw : malformed) {
            V2Probe sdk = new V2Probe(raw);
            expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(sdk.requests.size() == 1, "malformed nested reply does not cause retry");
        }
        passed.add("null V2 wrapper, nested receipt and missing states are unconfirmed");
    }

    static void unknownStates() throws Exception {
        for (String state : List.of("QUEUED", "DELIVERED", "enqueued")) {
            V2Probe sdk = new V2Probe(reply(state, "Q17"));
            expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(sdk.requests.size() == 1, "unknown V2 semantics are not guessed or retried");
        }
        passed.add("unknown V2 state, including V1 QUEUED, cannot silently imply acceptance");
    }

    static void missingReference() throws Exception {
        for (String reference : new String[] { null, "", " \t" }) {
            V2Probe sdk = new V2Probe(reply("ENQUEUED", reference));
            expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(sdk.requests.size() == 1, "no fabricated reference or retry");
        }
        passed.add("V2 ENQUEUED needs a nonblank original reference");
    }

    static void communicationFailures() throws Exception {
        for (boolean acceptedBeforeFailure : new boolean[] { false, true }) {
            V2Probe sdk = new V2Probe(null);
            sdk.recordAcceptanceBeforeFailure = acceptedBeforeFailure;
            sdk.failure = new AdapterUpgradeDemo.VendorFailureV2("reply unavailable");
            AdapterDemo.SendFailure failure = expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(failure.getCause() == sdk.failure, "V2 cause preserved");
            check(sdk.requests.size() == 1, "V2 failure does not retry");
            check(sdk.recordedAcceptances == (acceptedBeforeFailure ? 1 : 0), "fake records what caller cannot infer");
        }
        passed.add("V2 failures before and after simulated acceptance preserve unknown outcome and cause without retry");
    }

    static void exactAndIndependentRequests() throws Exception {
        V2Probe sdk = new V2Probe(reply("ENQUEUED", " Q17 "));
        AdapterDemo.Notifier notifier = new AdapterUpgradeDemo.NotificationAdapterV2(sdk);
        String recipient = " buyer17@shop.example ";
        String text = " 订单17已发货！📦\n ";
        AdapterDemo.Submission first = notifier.send(recipient, text);
        sdk.reply = reply("DECLINED", null);
        AdapterDemo.Submission second = notifier.send("buyer18@shop.example", "订单18已发货");
        check(first.equals(new AdapterDemo.Submission(AdapterDemo.Status.ACCEPTED, " Q17 ")), "reference not normalized");
        check(second.equals(new AdapterDemo.Submission(AdapterDemo.Status.REJECTED, "")), "no stale accepted result");
        check(sdk.requests.equals(List.of(new AdapterUpgradeDemo.Envelope(recipient, text),
                new AdapterUpgradeDemo.Envelope("buyer18@shop.example", "订单18已发货"))), "two exact independent requests");
        passed.add("V2 Unicode fields and reference stay exact; consecutive calls have independent results");
    }

    public static void main(String[] args) throws Exception {
        sameBusinessWithDifferentSdks(); explicitDecline(); invalidInputs(); missingReplyOrState();
        unknownStates(); missingReference(); communicationFailures(); exactAndIndependentRequests();
        check(passed.size() == 8, "eight SDK-upgrade behavior cases");
        System.out.println("{\"passed\":true,\"behaviorCases\":8,\"bothVersionsResult\":\"ACCEPTED/Q17\","
                + "\"independentVersionRequests\":true,\"automaticRetry\":false,\"realExternalSend\":false}");
        for (int i = 0; i < passed.size(); i++) System.err.println((i + 1) + ". " + passed.get(i));
    }
}
