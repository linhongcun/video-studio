import java.math.BigDecimal;

/** Independent integer-cent reference checks for the teaching implementation. */
public final class VerifyStrategy {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void rejects(Runnable action, Class<? extends Throwable> type) {
        try {
            action.run();
        } catch (Throwable failure) {
            check(type.isInstance(failure), "unexpected failure: " + failure);
            return;
        }
        throw new AssertionError("expected " + type.getSimpleName());
    }

    public static void main(String[] args) {
        var member = new StrategyDemo.Checkout(new StrategyDemo.MemberPricing());
        var campaign = new StrategyDemo.Checkout(new StrategyDemo.CampaignPricing());
        BigDecimal original = new BigDecimal("100.00");
        check(member.total(original).equals(new BigDecimal("90.00")), "member100");
        check(campaign.total(original).equals(new BigDecimal("80.00")), "campaign100");
        check(original.equals(new BigDecimal("100.00")), "original must stay100");
        check(campaign.total(original).compareTo(new BigDecimal("72.00")) != 0, "not stacked");

        int referenceChecks = 0;
        for (int cents = 0; cents <= 20_000; cents++) {
            BigDecimal amount = BigDecimal.valueOf(cents, 2);
            check(member.total(amount).equals(BigDecimal.valueOf(cents * 90L / 100L, 2)), "member cents" + cents);
            check(campaign.total(amount).equals(BigDecimal.valueOf(cents * 80L / 100L, 2)), "campaign cents" + cents);
            referenceChecks += 2;
        }
        check(member.total(new BigDecimal("99.99")).equals(new BigDecimal("89.99")), "cent rounding");
        check(member.total(new BigDecimal("0.01")).equals(new BigDecimal("0.00")), "low amount");
        rejects(() -> member.total(new BigDecimal("-0.01")), IllegalArgumentException.class);
        rejects(() -> member.total(new BigDecimal("1.001")), IllegalArgumentException.class);
        rejects(() -> member.total(null), NullPointerException.class);
        rejects(() -> new StrategyDemo.Checkout(null), NullPointerException.class);
        System.out.println("{\"passed\":true,\"referenceChecks\":" + referenceChecks
                + ",\"member100\":\"90.00\",\"campaign100\":\"80.00\",\"original\":\"100.00\","
                + "\"discountsStacked\":false,\"amountPolicy\":\"nonnegative yuan; at most2decimals; round down to cents\","
                + "\"invalidInputsRejected\":4}");
    }
}
