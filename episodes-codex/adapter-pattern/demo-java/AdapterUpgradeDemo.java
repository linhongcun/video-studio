import java.util.Objects;

/** Independent V1/V2 teaching requests, with no network or real external send. */
public final class AdapterUpgradeDemo {
    record Envelope(String destination, String content) {}
    record ReceiptV2(String state, String reference) {}
    record ReplyV2(ReceiptV2 receipt) {}
    interface VendorSdkV2 {
        ReplyV2 submit(Envelope request) throws VendorFailureV2;
    }
    static final class VendorFailureV2 extends Exception {
        VendorFailureV2(String message) { super(message); }
    }

    // CARD_ROLE_BEGIN
    // 类内节选：完整构造、校验与异常处理见源码
    static final class NotificationAdapterV2 implements AdapterDemo.Notifier {
        private final VendorSdkV2 sdk;
    // CARD_ROLE_END

        NotificationAdapterV2(VendorSdkV2 sdk) {
            this.sdk = Objects.requireNonNull(sdk);
        }

        public AdapterDemo.Submission send(String recipient, String text) throws AdapterDemo.SendFailure {
            requireInputs(recipient, text);
            try {
                // CARD_SEND_BEGIN
                // send方法内：转换格式，委托持有的SDK
                ReplyV2 raw = sdk.submit(new Envelope(recipient, text));
                return toSubmission(raw);
                // CARD_SEND_END
            } catch (VendorFailureV2 ex) {
                throw new AdapterDemo.SendFailure("受理结果未确认：V2通信异常", ex);
            }
        }
    }

    private static void requireInputs(String recipient, String text) {
        if (recipient == null || recipient.isBlank() || text == null || text.isBlank()) {
            throw new IllegalArgumentException("接收者和正文不能为空");
        }
    }

    private static AdapterDemo.Submission toSubmission(ReplyV2 raw) throws AdapterDemo.SendFailure {
        if (raw == null || raw.receipt() == null || raw.receipt().state() == null
                || raw.receipt().state().isBlank()) {
            throw new AdapterDemo.SendFailure("受理结果未确认：V2回执或状态缺失");
        }
        ReceiptV2 receipt = raw.receipt();
        return switch (receipt.state()) {
            case "ENQUEUED" -> {
                if (receipt.reference() == null || receipt.reference().isBlank()) {
                    throw new AdapterDemo.SendFailure("受理结果未确认：V2受理凭据缺失");
                }
                yield new AdapterDemo.Submission(AdapterDemo.Status.ACCEPTED, receipt.reference());
            }
            case "DECLINED" -> new AdapterDemo.Submission(AdapterDemo.Status.REJECTED, "");
            default -> throw new AdapterDemo.SendFailure("受理结果未确认：V2未知状态");
        };
    }

    // This substitute only returns a local reply; it never sends a notification.
    static final class FakeVendorSdkV2 implements VendorSdkV2 {
        public ReplyV2 submit(Envelope request) {
            Objects.requireNonNull(request);
            return new ReplyV2(new ReceiptV2("ENQUEUED", "Q17"));
        }
    }

    static AdapterDemo.Submission useBusiness(AdapterDemo.Notifier notifier) throws AdapterDemo.SendFailure {
        // CARD_BUSINESS_BEGIN
        // 同一业务使用者的调用：不出现V1/V2的SDK类型
        return new AdapterDemo.ShipmentReminder(notifier).send("buyer17@shop.example");
        // CARD_BUSINESS_END
    }

    public static void main(String[] args) throws AdapterDemo.SendFailure {
        // CARD_WIRE_BEGIN
        // 外部接线：两版本各自独立验证，不是页面的第二次提交
        AdapterDemo.Notifier v1 =
            new AdapterDemo.NotificationAdapter(new AdapterDemo.FakeVendorSdk());
        AdapterDemo.Notifier v2 = new NotificationAdapterV2(new FakeVendorSdkV2());
        // CARD_WIRE_END
        AdapterDemo.Submission first = useBusiness(v1);
        AdapterDemo.Submission second = useBusiness(v2);
        if (!first.equals(second)) throw new AssertionError("同一业务约定的结果不一致");
        System.out.println("教学模拟，不会外发；V1/V2是两次独立验证");
        System.out.println("V1=" + first.status() + "/" + first.reference());
        System.out.println("V2=" + second.status() + "/" + second.reference());
        System.out.println("业务调用相同；ACCEPTED仅表示受理，未确认送达");
    }
}
