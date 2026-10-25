#!/usr/bin/env python3
"""Replay a fixed Responses tool-call item against a real loopback HTTP service.

The model side is a fixture; this program makes no model API request.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import http.client
import json
import platform
import re
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = {"order_id": "8124", "signed_days": 3, "usage": None}


def load_json(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class Session:
    # This trusted application context is never supplied by the model.
    user_id: str
    can_read_orders: bool


@contextmanager
def order_service():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            user_id = self.headers.get("X-Demo-User")
            if user_id != "demo-user-a":
                status, result = 403, {"error": "permission_denied"}
            elif self.path != "/orders/8124":
                status, result = 404, {"error": "order_not_found"}
            else:
                status, result = 200, copy.deepcopy(ORDER)
            requests.append({"method": "GET", "path": self.path, "status": status})
            data = json_text(result).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield server.server_port, requests
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


def dispatch(call, session, port, trace):
    # A fixed dispatch table: a model cannot choose an arbitrary URL or code.
    if call.get("type") != "function_call" or call.get("name") != "get_order":
        trace.append({"actor": "application", "event": "unknown_tool_rejected"})
        return {"ok": False, "error": "unknown_tool", "application_status": 400}
    try:
        args = json.loads(call["arguments"])
        if not isinstance(args, dict) or set(args) != {"order_id"}:
            raise ValueError("unexpected keys")
        if not isinstance(args["order_id"], str) or not re.fullmatch(r"[0-9]{4}", args["order_id"]):
            raise ValueError("invalid order_id")
    except (KeyError, TypeError, ValueError):
        trace.append({"actor": "application", "event": "arguments_rejected"})
        return {"ok": False, "error": "invalid_arguments", "application_status": 400}
    trace.append({"actor": "application", "event": "arguments_validated", "arguments": args})
    if not session.can_read_orders:
        trace.append({"actor": "application", "event": "permission_denied", "executor_called": False})
        # This 403 is an application status, not an HTTP response from the service.
        return {"ok": False, "error": "permission_denied", "application_status": 403}
    trace.append({"actor": "application", "event": "permission_granted"})
    trace.append({"actor": "application", "event": "http_request_sent", "method": "GET", "path": f"/orders/{args['order_id']}"})
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        # Teaching-only identity header; real services need authenticated identity.
        conn.request("GET", f"/orders/{args['order_id']}", headers={"X-Demo-User": session.user_id})
        response = conn.getresponse()
        result = json.loads(response.read())
        trace.append({"actor": "order_service", "event": "http_response_received", "http_status": response.status, "data": result})
        return {"ok": response.status == 200, **({"data": result} if response.status == 200 else result)}
    finally:
        conn.close()


def fixture_answer(output):
    """A deterministic formatter replacing the second model response, not an LLM."""
    result = json.loads(output["output"])
    if not result["ok"]:
        return "没有读取权限，未查询订单。"
    order = result["data"]
    return f"订单{order['order_id']}已签收{order['signed_days']}天。"


def run_case(name, can_read_orders):
    call = load_json("model-call.fixture.json")
    user_id = "demo-user-a" if can_read_orders else "demo-user-b"
    if not can_read_orders:
        call["call_id"] = "call_demo_02"
    trace = [{"actor": "application", "event": "tools_offered", "tools": [load_json("tool-definition.json")]}]
    with order_service() as (port, requests):
        trace.append({"actor": "model_fixture", "event": "tool_call_received", "item": call, "http_requests_so_far": len(requests)})
        assert len(requests) == 0, "A proposed call must not execute itself"
        result = dispatch(call, Session(user_id, can_read_orders), port, trace)
        output = {"type": "function_call_output", "call_id": call["call_id"], "output": json_text(result)}
        trace.append({"actor": "application", "event": "tool_output_prepared", "item": output})
        answer = fixture_answer(output)
        trace.append({"actor": "model_fixture", "event": "fixture_continued", "text": answer})
        assert output["call_id"] == call["call_id"]
        assert len(requests) == (1 if can_read_orders else 0)
        if can_read_orders:
            assert result == {"ok": True, "data": ORDER}
            assert requests == [{"method": "GET", "path": "/orders/8124", "status": 200}]
        else:
            assert result == {"ok": False, "error": "permission_denied", "application_status": 403}
            assert not any(x["event"] == "http_request_sent" for x in trace)
        return {"case": name, "independent_run": True, "session_user_id": user_id, "session_can_read_orders": can_read_orders,
                "model_inference_performed": False, "tool_call": call, "tool_output": output,
                "http_requests": copy.deepcopy(requests), "http_request_count": len(requests),
                "fixture_answer": answer, "trace": trace, "assertions": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Write verification evidence JSON")
    args = parser.parse_args()
    inputs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), HERE / "model-call.fixture.json", HERE / "tool-definition.json", HERE / "protocol-lock.json"]}
    report = {"checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "python": platform.python_version(), "source_sha256": inputs,
              "protocol_lock": load_json("protocol-lock.json"),
              "scope": "Actual local HTTP and application dispatch; fixed model output, no model API or real orders",
              "cases": [run_case("allowed_query", True), run_case("reset_permission_denied", False)],
              "status": "passed"}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
