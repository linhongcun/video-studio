import java.util.Objects;

/** A local teaching example. No network calls and no real notifications. */
public final class AdapterDemo {
    enum Status { ACCEPTED, REJECTED }

    record Submission(Status status, String reference) {
        Submission {
            Objects.requireNonNull(status, "status");
            Objects.requireNonNull(reference, "reference");
        }
    }

    static final class SendFailure extends Exception {
        SendFailure(String message) { super(message); }
        SendFailure(String message, Throwable cause) { super(message, cause); }
    }

    // The existing, fictional vendor contract; it does not implement Notifier.
    record Payload(String target, String body) {}
    record RawReceipt(String status, String ticket) {}
    interface VendorSdk {
        RawReceipt deliver(Payload payload) throws VendorFailure;
    }
    static final class VendorFailure extends Exception {
        VendorFailure(String message) { super(message); }
    }

    // CARD_CORE_BEGIN
    interface Notifier { Submission send(String recipient, String text) throws SendFailure; }
    static final class NotificationAdapter implements Notifier {
        private final VendorSdk sdk;
        NotificationAdapter(VendorSdk sdk) { this.sdk = Objects.requireNonNull(sdk); }
        public Submission send(String recipient, String text) throws SendFailure {
            requireInputs(recipient, text);
            try {
                RawReceipt raw = requireReceipt(sdk.deliver(new Payload(recipient, text)));
                return switch (raw.status()) {
                    case "QUEUED" -> new Submission(Status.ACCEPTED, raw.ticket());
                    case "REJECTED" -> new Submission(Status.REJECTED, "");
                    default -> throw new SendFailure("受理结果未确认：未知回执状态");
                };
            } catch (VendorFailure ex) {
                throw new SendFailure("受理结果未确认：SDK通信异常", ex);
            }
        }
    }
    // CARD_CORE_END

    private static void requireInputs(String recipient, String text) {
        if (recipient == null || recipient.isBlank() || text == null || text.isBlank()) {
            throw new IllegalArgumentException("接收者和正文不能为空");
        }
    }

    private static RawReceipt requireReceipt(RawReceipt raw) throws SendFailure {
        if (raw == null || raw.status() == null || raw.status().isBlank()) {
            throw new SendFailure("受理结果未确认：回执或状态缺失");
        }
        if ("QUEUED".equals(raw.status()) && (raw.ticket() == null || raw.ticket().isBlank())) {
            throw new SendFailure("受理结果未确认：受理凭据缺失");
        }
        return raw;
    }

    // Client: it depends only on the business target, not on vendor DTOs or states.
    static final class ShipmentReminder {
        private final Notifier notifier;

        ShipmentReminder(Notifier notifier) {
            this.notifier = Objects.requireNonNull(notifier);
        }

        Submission send(String recipient) throws SendFailure {
            return notifier.send(recipient, "订单17已发货");
        }
    }

    // Teaching substitute only. It queues nothing outside this process.
    static final class FakeVendorSdk implements VendorSdk {
        public RawReceipt deliver(Payload payload) {
            Objects.requireNonNull(payload);
            return new RawReceipt("QUEUED", "Q17");
        }
    }

    public static void main(String[] args) throws SendFailure {
        // CARD_USE_BEGIN
        // main内：SDK为教学模拟，不外发
        Notifier notifier = new NotificationAdapter(new FakeVendorSdk());
        Submission result = new ShipmentReminder(notifier).send("buyer17@shop.example");
        // CARD_USE_END
        System.out.println("教学模拟，不会外发");
        System.out.println("订单17发货提醒：" + result.status() + "/" + result.reference());
        System.out.println("已受理，等待送达回执；并非已送达");
    }
}
