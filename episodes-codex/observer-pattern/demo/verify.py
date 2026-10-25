"""Run independent behavior cases and retain the actual execution receipt."""

import hashlib
import json
import platform
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from observer import Order, ChangeLog, Summary


def run():
    results = []

    # One event, two different reactions; cancel before the next event.
    order = Order("17")
    summary, stats = Summary(), ChangeLog()
    cancel_summary = order.subscribe(summary.receive)
    order.subscribe(stats.receive)
    order.change_status("已付款")
    assert summary.status == "已付款" and stats.change_count == 1
    first = {"order": order.status, "summary": summary.status,
             "changeRecordCount": stats.change_count,
             "changeRecords": [[event.order_id, event.status] for event in stats.events],
             "recipients": ["摘要", "变化记录"]}
    cancel_summary()
    cancel_summary()  # cleanup can be repeated, without affecting statistics.
    order.change_status("已发货")
    assert summary.status == "已付款" and len(summary.events) == 1
    assert stats.change_count == 2 and stats.events[-1].status == "已发货"
    results.append({"case": "video-story", "first": first,
                    "second": {"order": order.status, "summary": summary.status,
                               "summarySubscribed": False,
                               "changeRecordCount": stats.change_count,
                               "changeRecords": [[event.order_id, event.status] for event in stats.events],
                               "recipients": ["变化记录"]}})

    # A source with no observers still changes its own state.
    empty = Order("O-empty")
    empty.change_status("已付款")
    assert empty.status == "已付款" and empty._observers == []
    results.append({"case": "zero-observers", "state": empty.status,
                    "notifications": 0})

    # This example has no replay and does not notify repeated same state.
    late = ChangeLog()
    empty.subscribe(late.receive)
    assert late.change_count == 0
    empty.change_status("已付款")
    assert late.change_count == 0
    empty.change_status("已发货")
    assert late.change_count == 1
    results.append({"case": "no-replay-and-no-change", "notifications": 1})

    # Synchronous means completion happens before change_status returns.
    sequence = []
    synchronous = Order("O-sync")
    synchronous.subscribe(lambda event: sequence.append("摘要完成"))
    synchronous.subscribe(lambda event: sequence.append("变化记录完成"))
    sequence.append("开始修改")
    synchronous.change_status("已付款")
    sequence.append("修改返回")
    assert sequence == ["开始修改", "摘要完成", "变化记录完成", "修改返回"]
    results.append({"case": "synchronous-insertion-order", "trace": sequence})

    # Unsubscription during a notification affects the next event, not snapshot.
    snapshot = Order("O-snapshot")
    trace = []
    def remove_second(event):
        trace.append(["摘要", event.status])
        cancel_second()
    snapshot.subscribe(remove_second)
    cancel_second = snapshot.subscribe(lambda event: trace.append(["变化记录", event.status]))
    snapshot.change_status("已付款")
    snapshot.change_status("已发货")
    assert trace == [["摘要", "已付款"], ["变化记录", "已付款"], ["摘要", "已发货"]]
    results.append({"case": "snapshot-unsubscribe-during-event", "trace": trace})

    # A listener error stops this implementation's later notifications.
    failing = Order("O-error")
    error_trace = []
    def broken(event):
        error_trace.append("摘要失败")
        raise ValueError("示例接收者故障")
    failing.subscribe(broken)
    failing.subscribe(lambda event: error_trace.append("变化记录收到"))
    try:
        failing.change_status("已付款")
    except ValueError as error:
        error_trace.append(str(error))
    else:
        raise AssertionError("expected the original listener error")
    assert failing.status == "已付款" and error_trace == ["摘要失败", "示例接收者故障"]
    assert failing._notifying is False
    results.append({"case": "listener-error-propagates", "trace": error_trace,
                    "orderRemains": failing.status, "laterListenerCalled": False,
                    "rollback": False, "retry": False})

    # This scoped implementation forbids changing the source inside a listener.
    nested = Order("O-reentrant")
    nested.subscribe(lambda event: nested.change_status("已发货"))
    try:
        nested.change_status("已付款")
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected explicit reentrancy rejection")
    assert nested.status == "已付款" and nested._notifying is False
    results.append({"case": "reentrant-change-rejected", "orderRemains": nested.status})

    return results


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    report = {"checkedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
              "runtime": platform.python_version(), "language": "Python",
              "implementationSha256": hashlib.sha256((here / "observer.py").read_bytes()).hexdigest(),
              "scope": "Educational single-process, single-thread example; policies are not pattern-wide guarantees.",
              "cases": run(), "passed": True}
    (here / "verified-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "cases": len(report["cases"])}, ensure_ascii=False))
