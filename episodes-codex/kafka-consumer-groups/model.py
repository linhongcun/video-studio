#!/usr/bin/env python3
"""Executable teaching model; not a Kafka broker/client experiment.

Every scenario starts at offset 0 on the same retained log. Assignments below
are one legal stable assignment, not a prediction of a particular assignor.
"""
from __future__ import annotations
import json
from pathlib import Path

D = Path(__file__).resolve().parent
PARTITIONS = [
    {"id": "P0", "records": [
        {"eventId": "E01", "orderId": "7042", "offset": 0},
        {"eventId": "E03", "orderId": "7044", "offset": 1}]},
    {"id": "P1", "records": [
        {"eventId": "E02", "orderId": "7043", "offset": 0},
        {"eventId": "E04", "orderId": "7045", "offset": 1}]}]


def member(member_id, role, partitions):
    return {"id": member_id, "role": role, "partitions": partitions}


def make_scenario(scenario_id, groups):
    groups = json.loads(json.dumps(groups))
    for group in groups:
        for instance in group["members"]:
            # Partition order is display order only; no cross-partition ordering claim.
            instance["received"] = [dict(record, partition=p["id"])
                for p in PARTITIONS if p["id"] in instance["partitions"]
                for record in p["records"]]
        group["receivedEventIds"] = sorted({r["eventId"] for m in group["members"]
                                           for r in m["received"]})
    return {"id": scenario_id, "resetBefore": True,
            "startOffsets": {p["id"]: 0 for p in PARTITIONS}, "groups": groups}


def build():
    return {
        "schemaVersion": 1, "episode": "kafka-consumer-groups",
        "kind": "deterministic-teaching-model-not-broker-measurement",
        "topic": "orders", "partitions": PARTITIONS,
        "conditions": {
            "kafkaVersion": "4.4.0", "client": "Java KafkaConsumer 4.4.0 semantics",
            "group.protocol": "classic", "subscription": "all members subscribe orders",
            "assignment": "legal stable assignments chosen explicitly for illustration",
            "enable.auto.commit": False,
            "initialPosition": "fresh groups without committed offsets; auto.offset.reset=earliest; retained beginning offset is 0",
            "retention": "cleanup.policy=delete, retention.ms=604800000, retention.bytes=-1; all four records remain for entire example",
            "producerPartitioning": "explicit P0/P1 assignment; not a key-hash claim",
            "businessOutcome": "received records only; no claim of side-effect success or exactly-once business processing",
            "crossPartitionOrder": "none"
        },
        "scenarios": [
            make_scenario("wrong-shared", [
                {"id": "shop", "members": [member("N1", "通知", ["P0"]), member("S1", "积分", ["P1"])]}]),
            make_scenario("separate-groups", [
                {"id": "notify", "members": [member("N1", "通知", ["P0", "P1"])]},
                {"id": "points", "members": [member("S1", "积分", ["P0", "P1"])]}]),
            make_scenario("scale-notify", [
                {"id": "notify", "members": [member("N1", "通知", ["P0"]), member("N2", "通知", ["P1"])]},
                {"id": "points", "members": [member("S1", "积分", ["P0", "P1"])]}])]
    }


def verify(model):
    checks=[]
    def check(name, condition):
        assert condition, name
        checks.append({"name":name,"pass":True})
    all_ids={r["eventId"] for p in model["partitions"] for r in p["records"]}
    check("four unique event identities",len(all_ids)==4)
    for p in model["partitions"]:
        check(f"{p['id']} offsets are 0,1",[r["offset"] for r in p["records"]]==[0,1])
    for scenario in model["scenarios"]:
        check(scenario["id"]+" reset uses same start positions",scenario["resetBefore"] and scenario["startOffsets"]=={"P0":0,"P1":0})
        for g in scenario["groups"]:
            assigned=[p for m in g["members"] for p in m["partitions"]]
            check(scenario["id"]+"/"+g["id"]+" exactly one owner per partition",sorted(assigned)==["P0","P1"])
            ids=[r["eventId"] for m in g["members"] for r in m["received"]]
            check(scenario["id"]+"/"+g["id"]+" full group set exactly once",set(ids)==all_ids and len(ids)==4)
            for m in g["members"]:
                check(scenario["id"]+"/"+m["id"]+" only assigned partitions",all(r["partition"] in m["partitions"] for r in m["received"]))
                for pid in m["partitions"]:
                    offsets=[r["offset"] for r in m["received"] if r["partition"]==pid]
                    check(scenario["id"]+"/"+m["id"]+"/"+pid+" ordered reads",offsets==[0,1])
    wrong,separate,scale=model["scenarios"]
    check("wrong: each service misses required events",all(set(r["eventId"] for r in m["received"])!=all_ids for m in wrong["groups"][0]["members"]))
    check("separate: both services receive all events",all(set(r["eventId"] for r in g["members"][0]["received"])==all_ids for g in separate["groups"]))
    check("scale: notify has 2+2 records not 4+4",[len(m["received"]) for m in scale["groups"][0]["members"]]==[2,2])
    check("scale: points subscription unaffected",scale["groups"][1]==separate["groups"][1])
    # Deliberately invalid assignment shows verifier's uniqueness rule is effective.
    duplicate_owner=["P0","P0","P1"]
    check("invalid shared ownership rejected by invariant",sorted(duplicate_owner)!=["P0","P1"])
    return {"schemaVersion":1,"status":"pass","kind":"teaching-model-verification-not-Kafka-runtime-test","checks":checks,"checkCount":len(checks),"limitations":["No real Kafka broker, client, rebalance timing or fault injection was run.","One legal stable assignment per scenario; not an assignor implementation.","received is not business success; all scenario counts apply only to this finite retained input."]}


if __name__ == "__main__":
    model=build()
    (D/"model.json").write_text(json.dumps(model,ensure_ascii=False,indent=2)+"\n")
    result=verify(model)
    (D/"model-verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(f"PASS {result['checkCount']} teaching-model checks")
