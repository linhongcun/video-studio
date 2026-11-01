import java.util.ArrayList;
import java.util.List;

/** Independent observable expectations, with SDK doubles owned by the checker. */
public final class VerifyAdapter {
    private static final String RECIPIENT = "buyer17@shop.example";
    private static final String TEXT = "订单17已发货";
    private static final List<String> passed = new ArrayList<>();

    @FunctionalInterface
    interface CheckedAction { void run() throws Exception; }

    static final class ProbeSdk implements AdapterDemo.VendorSdk {
        final List<AdapterDemo.Payload> requests = new ArrayList<>();
        AdapterDemo.RawReceipt receipt;
        AdapterDemo.VendorFailure failure;
        boolean recordAcceptanceBeforeFailure;
        int recordedAcceptances;

        ProbeSdk(AdapterDemo.RawReceipt receipt) { this.receipt = receipt; }

        public AdapterDemo.RawReceipt deliver(AdapterDemo.Payload payload)
                throws AdapterDemo.VendorFailure {
            requests.add(payload);
            if (recordAcceptanceBeforeFailure) recordedAcceptances++;
            if (failure != null) throw failure;
            return receipt;
        }
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

    static AdapterDemo.Submission submit(ProbeSdk sdk) throws AdapterDemo.SendFailure {
        return new AdapterDemo.NotificationAdapter(sdk).send(RECIPIENT, TEXT);
    }

    static void accepted() throws Exception {
        ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt("QUEUED", "Q17"));
        AdapterDemo.Submission result = submit(sdk);
        check(result.status() == AdapterDemo.Status.ACCEPTED, "queued means accepted");
        check(result.reference().equals("Q17"), "preserve original ticket");
        check(sdk.requests.equals(List.of(new AdapterDemo.Payload(RECIPIENT, TEXT))), "one exact request");
        passed.add("QUEUED/Q17 maps to ACCEPTED/Q17, with one request");
    }

    static void rejected() throws Exception {
        ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt("REJECTED", "vendor-trace"));
        AdapterDemo.Submission result = submit(sdk);
        check(result.status() == AdapterDemo.Status.REJECTED, "explicit rejection stays rejection");
        check(result.reference().isEmpty(), "no invented acceptance reference");
        check(sdk.requests.size() == 1, "one rejected request");
        passed.add("explicit REJECTED maps to REJECTED with empty reference");
    }

    static void vendorFailure() throws Exception {
        ProbeSdk sdk = new ProbeSdk(null);
        sdk.failure = new AdapterDemo.VendorFailure("connection unavailable");
        AdapterDemo.SendFailure failure = expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
        check(failure.getCause() == sdk.failure, "preserve exact vendor cause");
        check(sdk.requests.size() == 1, "no retry on communication failure");
        passed.add("declared SDK failure becomes unknown SendFailure with original cause");
    }

    static void acceptedThenLostReply() throws Exception {
        ProbeSdk sdk = new ProbeSdk(null);
        sdk.recordAcceptanceBeforeFailure = true;
        sdk.failure = new AdapterDemo.VendorFailure("reply lost after acceptance");
        AdapterDemo.SendFailure failure = expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
        check(sdk.recordedAcceptances == 1, "SDK may have accepted before error");
        check(sdk.requests.size() == 1 && failure.getCause() == sdk.failure, "unknown, no second call");
        passed.add("acceptance before lost reply remains unknown and does not trigger retry");
    }

    static void nullReceipt() throws Exception {
        ProbeSdk sdk = new ProbeSdk(null);
        expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
        check(sdk.requests.size() == 1, "null receipt follows exactly one call");
        passed.add("null receipt cannot imply acceptance or rejection");
    }

    static void missingStatus() throws Exception {
        for (String status : new String[] { null, "", " \t\n" }) {
            ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt(status, "Q17"));
            expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(sdk.requests.size() == 1, "no retry after missing status");
        }
        passed.add("null and blank receipt statuses are unconfirmed");
    }

    static void unknownStatus() throws Exception {
        for (String status : List.of("DELIVERED", "PENDING_V2", "queued")) {
            ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt(status, "Q17"));
            expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(sdk.requests.size() == 1, "no guessed mapping or retry");
        }
        passed.add("reachable unknown String statuses are unconfirmed, including DELIVERED");
    }

    static void missingTicket() throws Exception {
        for (String ticket : new String[] { null, "", " \t" }) {
            ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt("QUEUED", ticket));
            expect(AdapterDemo.SendFailure.class, () -> submit(sdk));
            check(sdk.requests.size() == 1, "no fabricated ticket or retry");
        }
        passed.add("QUEUED requires a nonblank original ticket");
    }

    static void invalidInputs() throws Exception {
        ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt("QUEUED", "Q17"));
        AdapterDemo.Notifier notifier = new AdapterDemo.NotificationAdapter(sdk);
        for (String invalid : new String[] { null, "", " \t\n" }) {
            expect(IllegalArgumentException.class, () -> notifier.send(invalid, TEXT));
            expect(IllegalArgumentException.class, () -> notifier.send(RECIPIENT, invalid));
        }
        check(sdk.requests.isEmpty(), "reject invalid input before SDK call");
        passed.add("six invalid input cases fail before any SDK invocation");
    }

    static void exactMapping() throws Exception {
        String recipient = " buyer17@shop.example ";
        String text = " 订单17已发货：请查收！📦\n ";
        ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt("QUEUED", " Q17 "));
        AdapterDemo.Submission result = new AdapterDemo.NotificationAdapter(sdk).send(recipient, text);
        check(sdk.requests.equals(List.of(new AdapterDemo.Payload(recipient, text))), "no trim, swap, truncation");
        check(result.reference().equals(" Q17 "), "preserve ticket without normalization");
        passed.add("recipient/body Unicode and ticket map exactly without hidden normalization");
    }

    static void repeatedCalls() throws Exception {
        ProbeSdk sdk = new ProbeSdk(new AdapterDemo.RawReceipt("QUEUED", "Q17"));
        AdapterDemo.Notifier notifier = new AdapterDemo.NotificationAdapter(sdk);
        AdapterDemo.Submission first = notifier.send(RECIPIENT, TEXT);
        sdk.receipt = new AdapterDemo.RawReceipt("REJECTED", null);
        AdapterDemo.Submission second = notifier.send("buyer18@shop.example", "订单18已发货");
        check(first.status() == AdapterDemo.Status.ACCEPTED && first.reference().equals("Q17"), "first stable");
        check(second.status() == AdapterDemo.Status.REJECTED && second.reference().isEmpty(), "second independent");
        check(sdk.requests.equals(List.of(new AdapterDemo.Payload(RECIPIENT, TEXT),
                new AdapterDemo.Payload("buyer18@shop.example", "订单18已发货"))), "two exact calls");
        passed.add("two submissions delegate independently without cached result or silent deduplication");
    }

    static void clientUsesTarget() throws Exception {
        List<String> requests = new ArrayList<>();
        AdapterDemo.Submission expected = new AdapterDemo.Submission(AdapterDemo.Status.REJECTED, "");
        AdapterDemo.Notifier target = (recipient, text) -> {
            requests.add(recipient);
            requests.add(text);
            return expected;
        };
        AdapterDemo.Submission result = new AdapterDemo.ShipmentReminder(target).send(RECIPIENT);
        check(result == expected && requests.equals(List.of(RECIPIENT, TEXT)), "client accepts target double");
        AdapterDemo.SendFailure original = new AdapterDemo.SendFailure("unconfirmed");
        AdapterDemo.Notifier failingTarget = (recipient, text) -> { throw original; };
        AdapterDemo.SendFailure actual = expect(AdapterDemo.SendFailure.class,
                () -> new AdapterDemo.ShipmentReminder(failingTarget).send(RECIPIENT));
        check(actual == original, "client neither swallows unknown nor retries");
        passed.add("client works with independent Notifier doubles and preserves unknown failure");
    }

    public static void main(String[] args) throws Exception {
        accepted(); rejected(); vendorFailure(); acceptedThenLostReply();
        nullReceipt(); missingStatus(); unknownStatus(); missingTicket();
        invalidInputs(); exactMapping(); repeatedCalls(); clientUsesTarget();
        check(passed.size() == 12, "twelve behavior cases");
        System.out.println("{\"passed\":true,\"behaviorCases\":12,\"recipient\":\"" + RECIPIENT
                + "\",\"acceptedReference\":\"Q17\",\"automaticRetry\":false,\"realExternalSend\":false}");
        for (int i = 0; i < passed.size(); i++) {
            System.err.println((i + 1) + ". " + passed.get(i));
        }
    }
}
