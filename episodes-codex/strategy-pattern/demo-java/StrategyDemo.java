import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/** Teaching example: one pricing strategy per calculation; amounts are yuan. */
public final class StrategyDemo {
    // CARD_BEGIN
    interface PricingStrategy { BigDecimal price(BigDecimal original); }
    static final class MemberPricing implements PricingStrategy {
        public BigDecimal price(BigDecimal n) { return discounted(n, "0.90"); }
    }
    static final class CampaignPricing implements PricingStrategy {
        public BigDecimal price(BigDecimal n) { return discounted(n, "0.80"); }
    }

    static final class Checkout {
        private final PricingStrategy strategy;
        Checkout(PricingStrategy strategy) { this.strategy = Objects.requireNonNull(strategy); }
        BigDecimal total(BigDecimal original) { return strategy.price(original); }
    }

    public static void main(String[] args) {
        BigDecimal original = new BigDecimal("100.00");
        Checkout checkout = new Checkout(new MemberPricing());
        System.out.println(checkout.total(original)); // 90.00
        checkout = new Checkout(new CampaignPricing());
        System.out.println(checkout.total(original)); // 80.00
    }
    // CARD_END

    // Shared amount validation/calculation is omitted from the short video card.
    // This example rounds down to one cent, matching the earlier Python example.
    private static BigDecimal discounted(BigDecimal original, String factor) {
        Objects.requireNonNull(original, "original amount");
        if (original.signum() < 0 || original.scale() > 2) {
            throw new IllegalArgumentException("non-negative yuan amount, at most two decimals");
        }
        return original.multiply(new BigDecimal(factor)).setScale(2, RoundingMode.DOWN);
    }
}
