import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** One process/thread; own observer contract, no persistence/retry guarantees. */
public final class ObserverDemo {
    // CARD_CONTRACT_BEGIN
    record OrderChange(String orderId, String status) {}
    interface OrderObserver { void onChange(OrderChange change); }
    // CARD_CONTRACT_END

    static final class Order {
        final String id;
        String status = "待付款";
        private final List<OrderObserver> observers = new ArrayList<>();
        private boolean notifying;

        Order(String id) { this.id = Objects.requireNonNull(id); }

        void subscribe(OrderObserver observer) {
            Objects.requireNonNull(observer);
            if (observers.contains(observer)) throw new IllegalArgumentException("duplicate observer");
            observers.add(observer);
        }

        void unsubscribe(OrderObserver observer) { observers.remove(observer); }

        void changeStatus(String next) {
            Objects.requireNonNull(next);
            if (notifying) throw new IllegalStateException("reentrant change is outside this example");
            if (status.equals(next)) return;
            // CARD_NOTIFY_BEGIN
            // Order内：先改状态，再通知当前名单快照
            status = next;
            OrderChange change = new OrderChange(id, next);
            // CARD_NOTIFY_SPLIT
            notifying = true;
            try {
                // CARD_LOOP_BEGIN
                for (OrderObserver observer : List.copyOf(observers)) {
                    observer.onChange(change);
                }
                // CARD_LOOP_END
            } finally {
                notifying = false;
            }
        }
    }

    static final class SummaryObserver implements OrderObserver {
        String lastStatus = "待付款";
        final List<OrderChange> received = new ArrayList<>();
        public void onChange(OrderChange change) {
            lastStatus = change.status();
            received.add(change);
        }
    }

    static final class ChangeLogObserver implements OrderObserver {
        final List<OrderChange> received = new ArrayList<>();
        public void onChange(OrderChange change) { received.add(change); }
    }

    public static void main(String[] args) {
        // CARD_USAGE_BEGIN
        // main内：摘要显示，变化记录追加，各自响应
        Order order = new Order("17");
        SummaryObserver summary = new SummaryObserver();
        ChangeLogObserver log = new ChangeLogObserver();
        order.subscribe(summary);
        order.subscribe(log);
        order.changeStatus("已付款");
        order.unsubscribe(summary);
        order.changeStatus("已发货");
        // 摘要最后收到已付款，记录保留已付款、已发货
        // CARD_USAGE_END
        System.out.println("订单=" + order.status + "; 摘要最后收到=" + summary.lastStatus
                + "; 变化记录=" + log.received);
    }
}
