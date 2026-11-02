#!/usr/bin/env python3
"""Finite teaching model; no Kafka/PostgreSQL process is executed here."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

D = Path(__file__).resolve().parent
record = dict(eventId="E01", orderId=7042, accountId=17, delta=10,
              topic="orders", partition=0, offset=0)
states = []
by_id = {}
checks = []


def check(condition, description):
    if not condition:
        raise AssertionError(description)
    checks.append(description)


def save(s, state_id, label, action, parent=None, branch=None, reset=None):
    s = deepcopy(s)
    s.update(id=state_id, label=label, action=action, parentId=parent,
             branch=branch or s.get("branch", "replay"), resetFrom=reset)
    states.append(s)
    by_id[state_id] = s
    return s


base = dict(
    log=dict(records=[record], producerSendCount=1, appendCount=1,
             retainedInExample=True, logStartOffset=0, logEndOffset=1),
    consumer=dict(owner=None, active=False, position=None,
                  committedLoaded=None, fetchOffset=None, returned=[]),
    group=dict(id="points", committed={"P0": 0}, initialValueExplicitlyCommitted=True),
    db=dict(accountId=17, points=0, processedKeys=[], transaction="idle",
            pendingPoints=None, pendingKeys=[], effect="none",
            businessAttemptCount=0, effectCount=0),
    application=dict(knownProcessingOutcome="not-started", lostEffectRisk=False),
)
s = save(base, "one-appended", "唯一E01已保存，尚未首次读取", "initial-explicit-commit0")
s = deepcopy(s);s["consumer"].update(owner="A", active=True, committedLoaded=0, position=0)
s = save(s, "a-position-installed", "A从已提交0安装本地读取位置0", "install-position", "one-appended")
s = deepcopy(s);s["consumer"]["fetchOffset"] = 0
s = save(s, "a-fetch-sent", "A请求从0读取", "fetch-request", "a-position-installed")
s = deepcopy(s);s["consumer"].update(position=1, returned=[record])
s = save(s, "a-polled", "A取得原E01@0，内存position1，持久committed0", "poll-return", "a-fetch-sent")


def db_begin(s, state_id, points, keys, branch=None):
    t = deepcopy(s);t["db"]["businessAttemptCount"] += 1
    t["db"].update(transaction="open", pendingPoints=points, pendingKeys=keys, effect="none")
    return save(t, state_id, "业务事务暂存，外部已提交积分尚未变化", "database-begin", s["id"], branch)


def db_commit(s, state_id, label):
    t = deepcopy(s)
    old_points = t["db"]["points"]
    t["db"].update(points=t["db"]["pendingPoints"], processedKeys=t["db"]["pendingKeys"],
                   transaction="committed", pendingPoints=None, pendingKeys=[], effect="applied")
    if t["db"]["points"] != old_points:
        t["db"]["effectCount"] += 1
    t["application"]["knownProcessingOutcome"] = "database-committed"
    return save(t, state_id, label, "database-commit", s["id"])


def halt(s, state_id):
    t = deepcopy(s)
    t["consumer"].update(owner=None, active=False, position=None, committedLoaded=None,
                          fetchOffset=None, returned=[])
    t["application"]["knownProcessingOutcome"] = "process-exited"
    return save(t, state_id, "A退出，内存位置消失；日志、组恢复值和DB保留", "process-halt", s["id"])


def restore(s, prefix, empty=False):
    t = deepcopy(s);t["consumer"].update(owner="B", active=True)
    t = save(t, prefix+"-offset-requested", "B无内存position，查询同组持久恢复值", "offset-fetch-request", s["id"])
    t = deepcopy(t);t["consumer"]["committedLoaded"] = t["group"]["committed"]["P0"]
    t = save(t, prefix+"-committed-loaded", "B收到组恢复值，但尚未安装position", "offset-fetch-response", t["id"])
    t = deepcopy(t);t["consumer"]["position"] = t["consumer"]["committedLoaded"]
    t = save(t, prefix+"-position-installed", "客户端把恢复值安装成B的本地position", "install-position", t["id"])
    t = deepcopy(t);t["consumer"]["fetchOffset"] = t["consumer"]["position"]
    t = save(t, prefix+"-fetch-sent", "Fetch参数来自刚安装的本地position", "fetch-request", t["id"])
    t = deepcopy(t)
    t["consumer"]["returned"] = [r for r in t["log"]["records"] if r["offset"] >= t["consumer"]["fetchOffset"]]
    if t["consumer"]["returned"]:
        t["consumer"]["position"] = t["consumer"]["returned"][-1]["offset"] + 1
    t["application"]["knownProcessingOutcome"] = "not-started"
    t["application"]["lostEffectRisk"] = empty
    return save(t, prefix+("-poll-empty" if empty else "-polled-same"),
                "B未读到零号记录" if empty else "B再次取得同一E01和同一offset0，position推进1",
                "poll-return", t["id"])


def commit_source(s, prefix):
    t = save(s, prefix+"-commit-requested", "应用显式提交P0下一位置1，尚未收到成功", "offset-commit-request", s["id"])
    t = deepcopy(t);t["group"]["committed"]["P0"] = 1
    return save(t, prefix+"-committed", "Kafka确认保存本组P0恢复位置1", "offset-commit-success", t["id"])


s = db_begin(by_id["a-polled"], "first-db-pending", 10, [])
s = db_commit(s, "db-committed", "第一次DB已提交10分，Kafka仍0")
s = halt(s, "a-halted")
s = restore(s, "b")
s = db_begin(s, "unguarded-db-pending", 20, [])
s = db_commit(s, "unguarded-twenty", "无业务防护，第二次DB提交变20分")

s = save(by_id["a-polled"], "early-reset", "完整回到首次业务前：DB0/无key/组0/日志仍1条",
         "scenario-reset", "unguarded-twenty", "early-commit", "a-polled")
s = commit_source(s, "early")
s = halt(s, "early-a-halted")
s = restore(s, "early-b", empty=True)

s = save(by_id["a-polled"], "guard-reset", "完整回到首次业务前，改用同事务业务键",
         "scenario-reset", "early-b-poll-empty", "guarded", "a-polled")
s = db_begin(s, "guard-first-db-pending", 10, ["points:E01"])
s = db_commit(s, "guard-db-committed", "同一DB事务提交业务键与10分，Kafka仍0")
s = halt(s, "guard-a-halted")
s = restore(s, "guard-b")
s = deepcopy(s);s["db"]["businessAttemptCount"] += 1
check("points:E01" in s["db"]["processedKeys"], "第二次业务尝试查询已提交的同一逻辑业务键")
s["db"].update(transaction="idle", effect="skipped")
s["application"]["knownProcessingOutcome"] = "already-committed-business-key"
s = save(s, "guard-duplicate-skipped", "第二次业务尝试跳过加分，仍10分", "business-key-skip", "guard-b-polled-same")
s = commit_source(s, "guard")
s = save(s, "guard-final", "日志1条、业务尝试2次、业务效果1次", "recap", s["id"])

# Assertions test the mechanism and reset premises; they do not emulate a Broker.
for s in states:
    check(s["log"] == base["log"], s["id"]+":单条原始日志/生产一次全程不变")
    check(s["consumer"]["owner"] in [None, "A", "B"], s["id"]+":只有一位当前分区拥有者")
    if not s["consumer"]["active"]:
        check(s["consumer"]["position"] is None, s["id"]+":退出不保留客户端内存position")
    if s["db"]["transaction"] == "open":
        check(s["db"]["pendingPoints"] is not None, s["id"]+":未提交暂存与已提交积分分开")
    if s["action"] == "fetch-request":
        check(s["consumer"]["fetchOffset"] == s["consumer"]["position"], s["id"]+":Fetch参数来自当前position")
    if s["resetFrom"]:
        expected = by_id[s["resetFrom"]]
        check(all(s[k] == expected[k] for k in ["log", "consumer", "group", "db", "application"]), s["id"]+":reset完整恢复共同前提")
check(by_id["a-polled"]["consumer"]["position"] == 1 and by_id["a-polled"]["group"]["committed"]["P0"] == 0, "poll推进position不自动提交组恢复值")
check(by_id["b-committed-loaded"]["consumer"]["position"] is None, "收到committed和安装position是分开的步骤")
check(by_id["b-polled-same"]["consumer"]["returned"] == [record], "B再次读到完全相同的E01/offset0而非新生产记录")
check(by_id["unguarded-twenty"]["db"]["points"] == 20, "无防护对同记录产生两次业务效果")
check(by_id["early-b-poll-empty"]["consumer"]["fetchOffset"] == 1 and not by_id["early-b-poll-empty"]["consumer"]["returned"] and by_id["early-b-poll-empty"]["db"]["points"] == 0, "先Kafka提交可能跳过尚未执行的DB效果，日志原记录仍保留")
check(by_id["guard-db-committed"]["db"]["points"] == 10 and by_id["guard-db-committed"]["db"]["processedKeys"] == ["points:E01"], "第一次key和积分在一个DB事务提交")
check(s["db"]["points"] == 10 and s["db"]["businessAttemptCount"] == 2 and s["db"]["effectCount"] == 1, "正确结尾是一条日志/两次业务尝试/一次效果")
check(s["group"]["committed"]["P0"] == 1, "跳过重复后仍显式提交Kafka下一恢复位置1")
model = dict(schemaVersion=1, kind="finite-teaching-model-not-kafka-or-database-runtime",
             fixedInput=dict(kafkaVersion="4.4.0", commit="1156b2752aaa28eafc0b4c4d387e63356793268d",
                             groupProtocol="classic", enableAutoCommit=False, maxPollRecords=1,
                             initialCommittedOffsetEstablishedBy="explicit commitSync({P0:0})",
                             businessKey="points:E01", retained=True), snapshots=states)
b = (json.dumps(model, ensure_ascii=False, indent=2)+"\n").encode()
(D/"model.json").write_bytes(b)
(D/"model-verification.json").write_text(json.dumps(dict(status="passed", kind=model["kind"], modelSHA256=sha256(b).hexdigest(),
    checks=len(checks), snapshots=len(states), assertions=checks,
    notClaimed=["No Broker/database process is executed by this generator.", "No producer resend, reappend, partition-owner overlap or cross-resource atomicity."]), ensure_ascii=False, indent=2)+"\n")
print(f"PASS {len(checks)} checks / {len(states)} snapshots / model {sha256(b).hexdigest()}")
