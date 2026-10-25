#!/usr/bin/env python3
"""Re-fetch pinned official source files and review citation identity separately.

The semantic notes below record the reviewer's reading of the listed sections;
hash/title/quotation checks establish source identity, not automatic truth.
"""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
ROOT = D.parents[1]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_official(source: dict) -> dict:
    response = subprocess.run(
        ["gh", "api", source["retrievedAPI"], "--method", "GET"],
        check=True, capture_output=True, timeout=60,
    )
    payload = json.loads(response.stdout)
    assert payload["encoding"] == "base64", source["id"]
    remote = base64.b64decode(payload["content"])
    path = (ROOT / source["evidence"]).resolve()
    assert path.is_relative_to(ROOT)
    local = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(remote)).encode("ascii") + b"\0" + remote).hexdigest()
    assert remote == local, (source["id"], "retrieved/local byte mismatch")
    assert sha(remote) == source["sha256"], (source["id"], "SHA-256")
    assert blob == source["gitBlobSHA1"] == payload["sha"], (source["id"], "Git blob")
    assert source["commit"] in source["sourceURL"]
    return {
        "id": source["id"], "repository": source["repository"],
        "commit": source["commit"], "retrievedAPI": source["retrievedAPI"],
        "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "method": "Independent GitHub Contents API GET via configured gh; decoded original bytes compared against repository candidate evidence.",
        "status": "passed", "bytes": len(remote), "sha256": sha(remote),
        "gitBlobSHA1": blob, "apiResponseSHA256": sha(response.stdout),
        "evidence": source["evidence"],
    }


def main() -> None:
    source_manifest = json.loads((D / "research/source-verification.json").read_text())
    references = json.loads((D / "references.json").read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        retrieved = list(pool.map(read_official, source_manifest["sources"]))
    records = {source["id"]: source for source in source_manifest["sources"]}
    citations = []
    for reference in references["sources"]:
        record = records[reference["id"]]
        source = (ROOT / reference["titleEvidence"]["evidence"]).read_text()
        if reference["id"] == "R1":
            actual_title = re.search(r"^title:\s*(.+)$", source, re.MULTILINE).group(1)
        else:
            actual_title = source.splitlines()[0].removeprefix("= ")
        assert reference["title"] == actual_title == record["originalTitle"]
        quotation = reference["quotation"]["text"]
        assert quotation in source, (reference["id"], "quotation is not a continuous exact substring")
        assert reference["url"] == record["sourceURL"]
        assert reference["verification"]["sha256"] == record["sha256"]
        offset = source.index(quotation)
        line = source[:offset].count("\n") + 1
        endline = line + quotation.count("\n")
        citations.append({
            "id": reference["id"], "status": "passed", "originalTitle": actual_title,
            "titleExactlyMatches": True, "quotationExactlyContinuous": True,
            "quotationCharacters": len(quotation), "actualQuotationLineRange": [line, endline],
            "declaredLocator": reference["quotation"]["locator"], "sourceURL": reference["url"],
        })
    notes = [
        {
            "claim": "A zero at any fixed probe position safely rejects a correctly maintained membership summary; all one bits mean only possible presence.",
            "sources": ["R1 Overview paragraph 3 first sentence", "R2 opening section", "R3 Strategy.mightContain contract and strategy loops"],
            "review": "Supported. The code sets selected bits and returns false on its first unset probe; code and Javadoc use the same mapping for insertion/query.",
        },
        {
            "claim": "More space can reduce false-positive risk for a chosen capacity; bounded teaching fixtures do not determine a production error rate.",
            "sources": ["R1 Total size of a Bloom filter", "R2 opening RAM/accuracy section", "R3 expectedFpp and capacity documentation"],
            "review": "Supported as a configuration tradeoff. No product defaults, memory multiples, or the document's simplified positive-answer denominator are adopted.",
        },
        {
            "claim": "Wrong bit clearing can create false negatives; an unsynchronized external catalog cannot be safely gated by stale marks.",
            "sources": ["Independent model counterexamples", "R3 stable Strategy and funnel requirements"],
            "review": "These are explicit deductions/witnesses from the set-bit model, not claims that an official source specifies this episode's maintenance protocol.",
        },
        {
            "claim": "The episode's 16-bit SHA-256 teaching mapping is distinct from product implementations.",
            "sources": ["R3-strategy MURMUR128_MITZ_32 and MURMUR128_MITZ_64"],
            "review": "Correctly separated. Guava derives probes from Murmur hashes; the teaching SHA mapping does not purport to reproduce Guava or Redis internals.",
        },
    ]
    report = {
        "status": "passed", "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "reviewer": "Independent model/source-review agent",
        "scope": "Official pinned-source re-fetch, evidence identity, original titles, continuous quotations and listed semantic claims.",
        "inputs": {name: sha((D / name).read_bytes()) for name in
                   ["references.json", "research/source-verification.json", "research.md", "script.md"]},
        "checkerSHA256": sha(Path(__file__).read_bytes()),
        "independentRetrievals": retrieved, "citations": citations, "semanticReview": notes,
        "readingScope": [
            "Redis Overview, reserving/capacity/size and scaling distinctions; selected first-sentence quotation.",
            "Full Cassandra Bloom Filters page, including RAM tradeoff and product-specific defaults/change lifecycle boundaries.",
            "Guava class/Strategy Javadoc, put/mightContain and expectedFpp sections; 32/64 strategy set/get loops and stable funnel/mapping contract.",
        ],
        "limitations": [
            "The four independent GETs target immutable official GitHub files; canonical website pages were not re-requested in this audit.",
            "No Redis, Guava or Cassandra build/runtime, production measurement, full-library audit, audio, animation or final media check was performed.",
            "Source identity and exact quotations do not substitute for the separately recorded editorial/semantic review.",
        ],
    }
    (D / "qa-source-independent.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (D / "qa-source-independent.md").write_text(
        "# 布隆过滤器独立来源复核\n\n"
        "状态：通过。独立重新GET四份固定commit的官方GitHub原文，base64还原字节与本期证据一致，Git blob SHA-1及SHA-256均吻合。"
        "片尾两项原始题名逐字匹配；两段原文均为连续精确摘录，真实行号与声明定位一致。\n\n"
        "实际审读支持任一0排除、全1仍可能误判，以及空间/容量/准确性的取舍。Guava实际置位与遇0短路查询为结构佐证，教学SHA映射与产品实现已分开。"
        "共享位误清与目录漏同步的风险由独立模型反例支撑，不冒称来源给出了本片维护协议。\n\n"
        "Redis概述中关于阳性答案错误比例的简化表述未采用；Cassandra产品默认参数与内存倍数未推广为通用规律。"
        "本次只重新获取官方仓库原文，没有重新访问官网正文，未运行产品或检查配音、动画、正式媒体。详见JSON中的实际阅读范围与完整摘要。\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "independentRetrievalCount": len(retrieved),
                      "citationCount": len(citations), "quoteLineRanges": [c["actualQuotationLineRange"] for c in citations]}))


if __name__ == "__main__":
    main()
