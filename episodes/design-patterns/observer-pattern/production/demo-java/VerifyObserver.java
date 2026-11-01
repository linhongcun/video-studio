import java.util.ArrayList;
import java.util.List;

/** Behavioral checks are specific to ObserverDemo's synchronous policy. */
public final class VerifyObserver {
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }

    private static void rejects(Runnable action) {
        try { action.run(); } catch (IllegalStateException expected) { return; }
        throw new AssertionError("expected IllegalStateException");
    }

    public static void main(String[] args) {
        var order = new ObserverDemo.Order("17");
        var summary = new ObserverDemo.SummaryObserver();
        var log = new ObserverDemo.ChangeLogObserver();
        order.subscribe(summary); order.subscribe(log);
        order.changeStatus("已付款");
        check(order.status.equals("已付款") && summary.lastStatus.equals("已付款"), "first state");
        check(summary.received.size() == 1 && log.received.size() == 1, "both notified");
        order.unsubscribe(summary); order.unsubscribe(summary);
        order.changeStatus("已发货");
        check(order.status.equals("已发货") && summary.lastStatus.equals("已付款"), "stopped history");
        check(summary.received.size() == 1 && log.received.size() == 2, "only remaining notified");
        check(log.received.equals(List.of(new ObserverDemo.OrderChange("17", "已付款"),
                new ObserverDemo.OrderChange("17", "已发货"))), "facts preserve order");

        var empty = new ObserverDemo.Order("zero");
        empty.changeStatus("已付款"); check(empty.status.equals("已付款"), "zero observers");

        var noReplay = new ObserverDemo.Order("no-replay");
        var late = new ObserverDemo.SummaryObserver();
        noReplay.changeStatus("已付款"); noReplay.subscribe(late);
        noReplay.changeStatus("已付款"); check(late.received.isEmpty(), "no replay/no change");
        noReplay.changeStatus("已发货"); check(late.received.size() == 1, "new change");

        var sequential = new ObserverDemo.Order("sequence");
        var trace = new ArrayList<String>();
        sequential.subscribe(change -> {check(sequential.status.equals(change.status()), "mutate first"); trace.add("摘要");});
        sequential.subscribe(change -> trace.add("记录"));
        trace.add("开始"); sequential.changeStatus("已付款"); trace.add("返回");
        check(trace.equals(List.of("开始", "摘要", "记录", "返回")), "sync order");

        var snapshot = new ObserverDemo.Order("snapshot");
        var snapshotTrace = new ArrayList<String>();
        ObserverDemo.OrderObserver second = change -> snapshotTrace.add("记录:" + change.status());
        snapshot.subscribe(change -> {snapshotTrace.add("摘要:" + change.status()); snapshot.unsubscribe(second);});
        snapshot.subscribe(second); snapshot.changeStatus("已付款"); snapshot.changeStatus("已发货");
        check(snapshotTrace.equals(List.of("摘要:已付款", "记录:已付款", "摘要:已发货")), "snapshot cancellation");

        var failure = new ObserverDemo.Order("failure");
        var untouched = new ObserverDemo.ChangeLogObserver();
        failure.subscribe(change -> {throw new IllegalStateException("receiver failed");});
        failure.subscribe(untouched); rejects(() -> failure.changeStatus("已付款"));
        check(failure.status.equals("已付款") && untouched.received.isEmpty(), "no rollback/retry/continued delivery");

        var reentrant = new ObserverDemo.Order("reentrant");
        reentrant.subscribe(change -> reentrant.changeStatus("已发货"));
        rejects(() -> reentrant.changeStatus("已付款"));
        check(reentrant.status.equals("已付款"), "reentrant rejected before mutation");

        boolean duplicateRejected = false;
        try { order.subscribe(log); } catch (IllegalArgumentException expected) { duplicateRejected = true; }
        check(duplicateRejected, "duplicate subscription");
        System.out.println("{\"passed\":true,\"behaviorCases\":8,\"orderId\":\"17\","
                + "\"source\":\"已发货\",\"summaryLastReceived\":\"已付款\","
                + "\"summaryNotificationCount\":1,\"changeLog\":[\"已付款\",\"已发货\"],"
                + "\"synchronous\":true,\"snapshot\":true,\"errorsPropagate\":true,\"retry\":false,\"rollback\":false}");
    }
}
