"""Observe the actual submitted solver; inserted callbacks never change its AST logic."""
from __future__ import annotations

import ast
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
EXPECTED_SOLUTION_SHA256 = "844388d14016202d9c62e4d9c4b63e159365b7c03250e6555472dea3cec59cb6"
DEMO_GRID = [list(row) for row in ["11000", "11000", "00100", "00011"]]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def callback(action, cell="None", origin="None", reason="None"):
    node = ast.parse(
        f"_observer({action!r}, locals(), {cell}, {origin}, {reason})"
    ).body[0]
    node._audit_inserted = True
    return node


class InsertObserver(ast.NodeTransformer):
    """These source-line anchors are guarded by the complete pinned source SHA."""

    def __init__(self):
        self.insertions = Counter()

    def event(self, name, cell="None", origin="None", reason="None"):
        self.insertions[name] += 1
        return callback(name, cell, origin, reason)

    def visit_For(self, node):
        self.generic_visit(node)
        if node.lineno == 9:  # Each actual outer row-major cell visit.
            node.body.insert(0, self.event("scan", "(row, col)"))
        if node.lineno == 17:  # All four directions of the popped cell are done.
            return [node, self.event("expanded", "(r, c)")]
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if node.lineno == 10:
            node.body.insert(0, self.event(
                "skip", "(row, col)", reason='"water" if grid[row][col] == "0" else "seen"'
            ))
        elif node.lineno == 19:
            node.body.insert(0, self.event(
                "neighbor_check", "(nr, nc)", "(r, c)", '"boundary"'
            ))
        elif node.lineno == 21:
            node.body.insert(0, self.event(
                "neighbor_check", "(nr, nc)", "(r, c)",
                '"water" if grid[nr][nc] == "0" else "seen"'
            ))
            return [node, self.event(
                "neighbor_check", "(nr, nc)", "(r, c)", '"fresh"'
            )]
        return node

    def visit_AugAssign(self, node):
        if node.lineno == 12:
            return [node, self.event("seed", "(row, col)")]
        return node

    def visit_Expr(self, node):
        if node.lineno == 13:
            return [node, self.event("mark", "(row, col)", reason='"seed"')]
        if node.lineno == 23:
            return [node, self.event("mark", "(nr, nc)", "(r, c)", '"neighbor"')]
        if node.lineno == 24:
            return [node, self.event("push", "(nr, nc)", "(r, c)", '"neighbor"')]
        return node

    def visit_Assign(self, node):
        if node.lineno == 14:
            return [node, self.event("push", "(row, col)", reason='"seed"')]
        if node.lineno == 16:
            return [node, self.event("pop", "(r, c)")]
        return node

    def visit_While(self, node):
        self.generic_visit(node)
        return [node, self.event("component_done")]


class RemoveObserver(ast.NodeTransformer):
    def visit_Expr(self, node):
        if getattr(node, "_audit_inserted", False):
            return None
        return node


class Observer:
    """Summary mode is O(land); only the small demonstration copies whole states."""

    def __init__(self, grid, detailed=False):
        self.grid = grid
        self.rows, self.cols = len(grid), len(grid[0])
        self.land = {(r, c) for r, row in enumerate(grid)
                     for c, value in enumerate(row) if value == "1"}
        self.detailed = detailed
        self.events = []
        self.counts = Counter()
        self.discovered = {}
        self.pushed, self.popped = set(), set()
        self.expanded = set()
        self.seeds = []
        self.done = []
        self.active = None
        self.max_stack = 0
        self.neighbor_checks = Counter()
        self.pending_neighbor = None
        self.last_index = 0

    def __call__(self, action, state, cell=None, origin=None, reason=None):
        cell = tuple(cell) if cell is not None else None
        origin = tuple(origin) if origin is not None else None
        seen, stack = state["seen"], state.get("stack", [])
        count = state["islands"]
        self.last_index += 1
        self.counts[action] += 1
        if action == "scan":
            assert self.active is None and not stack
            assert self.counts[action] == cell[0] * self.cols + cell[1] + 1
        elif action == "skip":
            assert (reason == "water" and cell not in self.land) or (
                reason == "seen" and cell in self.discovered
            )
        elif action == "seed":
            assert count == len(self.seeds) + 1 and cell in self.land and cell not in seen
            self.seeds.append(cell)
        elif action == "mark":
            assert cell in self.land and cell in seen and cell not in self.discovered
            if reason == "neighbor":
                assert self.pending_neighbor == cell and origin == self.active
                self.pending_neighbor = None
            else:
                assert cell == self.seeds[-1]
            self.discovered[cell] = count
        elif action == "push":
            assert cell in self.discovered and cell not in self.pushed and stack[-1] == cell
            self.pushed.add(cell)
        elif action == "pop":
            assert cell in self.pushed and cell not in self.popped and self.active is None
            self.popped.add(cell)
            self.active = cell
        elif action == "neighbor_check":
            assert origin == self.active and origin not in self.expanded
            assert abs(cell[0] - origin[0]) + abs(cell[1] - origin[1]) == 1
            number = self.neighbor_checks[origin]
            dr, dc = [(0, 1), (1, 0), (0, -1), (-1, 0)][number]
            assert cell == (origin[0] + dr, origin[1] + dc)
            self.neighbor_checks[origin] += 1
            inside = 0 <= cell[0] < self.rows and 0 <= cell[1] < self.cols
            expected = ("boundary" if not inside else "water" if cell not in self.land
                        else "seen" if cell in self.discovered else "fresh")
            assert reason == expected and self.pending_neighbor is None
            if reason == "fresh":
                self.pending_neighbor = cell
        elif action == "expanded":
            assert cell == self.active and self.neighbor_checks[cell] == 4
            assert cell not in self.expanded and self.pending_neighbor is None
            self.expanded.add(cell)
            self.active = None
        elif action == "component_done":
            assert not stack and self.active is None and count == len(self.done) + 1
            self.done.append(count)
        else:
            raise AssertionError(action)
        assert len(seen) == len(self.discovered)
        self.max_stack = max(self.max_stack, len(stack))
        if self.detailed:
            owner = (self.discovered.get(cell) if action in {"scan", "skip"} else count)
            self.events.append(dict(
                index=self.last_index, action=action,
                row=cell[0] if cell is not None else None,
                col=cell[1] if cell is not None else None,
                cell=list(cell) if cell is not None else None,
                **{"from": list(origin) if origin is not None else None},
                reason=reason, islandId=owner, count=count,
                active=list(self.active) if self.active is not None else None,
                stack=[list(x) for x in stack],
                seen=[list(x) for x in sorted(seen)],
                expanded=[list(x) for x in sorted(self.expanded)],
            ))

    def finish(self, result):
        assert set(self.discovered) == self.land == self.pushed == self.popped == self.expanded
        assert self.counts["scan"] == self.rows * self.cols
        assert self.counts["seed"] == self.counts["component_done"] == result
        assert self.counts["skip"] == self.rows * self.cols - result
        assert self.counts["mark"] == self.counts["push"] == self.counts["pop"] == len(self.land)
        assert self.counts["neighbor_check"] == 4 * len(self.land)
        return dict(
            landCells=len(self.land), islands=result, events=self.last_index,
            actionCounts=dict(sorted(self.counts.items())),
            componentSizes=dict(sorted(Counter(self.discovered.values()).items())),
            seeds=[list(x) for x in self.seeds], maxStackDepth=self.max_stack,
            everyLandDiscoveredPushedPoppedExpandedExactlyOnce=True,
            waterNeverDiscovered=True, neighborOrder="right, down, left, up",
            seenMeaning="discovered and assigned; not necessarily expanded",
        )


class Runners:
    def __init__(self):
        self.source_bytes = (EP / "solution.py").read_bytes()
        self.source_sha = sha(self.source_bytes)
        assert self.source_sha == EXPECTED_SOLUTION_SHA256, "Re-audit changed solver before tracing"
        display = json.loads((EP / "solution.json").read_text())
        assert display["lines"] == self.source_bytes.decode().splitlines()
        original = ast.parse(self.source_bytes, filename=str(EP / "solution.py"))
        transform = InsertObserver()
        observed = transform.visit(copy.deepcopy(original))
        expected_counts = dict(scan=1, skip=1, seed=1, mark=2, push=2, pop=1,
                               neighbor_check=3, expanded=1, component_done=1)
        assert dict(transform.insertions) == expected_counts
        stripped = RemoveObserver().visit(copy.deepcopy(observed))
        self.original_ast = ast.dump(original, include_attributes=False)
        assert ast.dump(stripped, include_attributes=False) == self.original_ast
        self.insertions = dict(transform.insertions)
        plain_ns, self.observed_ns = {}, {}
        exec(compile(original, str(EP / "solution.py"), "exec"), plain_ns)
        exec(compile(ast.fix_missing_locations(observed), str(EP / "solution.py"), "exec"),
             self.observed_ns)
        self.plain = plain_ns["Solution"]().numIslands
        self.observed = self.observed_ns["Solution"]().numIslands

    def run(self, grid, detailed=False):
        before = tuple(tuple(row) for row in grid)
        plain_result = self.plain(grid)
        assert tuple(tuple(row) for row in grid) == before, "Unmodified solver mutated input"
        observer = Observer(grid, detailed=detailed)
        self.observed_ns["_observer"] = observer
        result = self.observed(grid)
        assert tuple(tuple(row) for row in grid) == before, "Observed solver mutated input"
        assert type(result) is int and result == plain_result
        summary = observer.finish(result)
        return result, observer, summary

    def check_source_unchanged(self):
        assert (EP / "solution.py").read_bytes() == self.source_bytes
        assert json.loads((EP / "solution.json").read_text())["lines"] == self.source_bytes.decode().splitlines()


def generate_demo(runners=None):
    runners = runners or Runners()
    grid = copy.deepcopy(DEMO_GRID)
    result, observer, summary = runners.run(grid, detailed=True)
    assert result == 3 and summary["landCells"] == 7
    assert observer.seeds == [(0, 0), (2, 2), (3, 3)]
    pops = [tuple(event["cell"]) for event in observer.events if event["action"] == "pop"]
    assert pops == [(0, 0), (1, 0), (1, 1), (0, 1), (2, 2), (3, 3), (3, 4)]
    first_marks = [tuple(event["cell"]) for event in observer.events if event["action"] == "mark"]
    assert first_marks[:3] == [(0, 0), (0, 1), (1, 0)]
    component_map = [[observer.discovered.get((r, c), 0) for c in range(len(grid[0]))]
                     for r in range(len(grid))]
    runners.check_source_unchanged()
    return dict(
        schemaVersion=1, grid=grid, events=observer.events, result=result,
        componentMap=component_map, solutionSHA256=runners.source_sha,
        generatorSHA256=sha(Path(__file__).read_bytes()),
        generatedFrom="Unmodified solver AST plus removable observer expression callbacks",
        originalASTPreservedAfterRemovingCallbacks=True,
        stackOrder="bottom to top; the last element is popped next",
        stateSemantics="Every event snapshots after its named operation; mark is discovery before push; expanded follows all four neighbor checks.",
        summary=summary,
    )


if __name__ == "__main__":
    trace = generate_demo()
    destination = EP / "research/demo-trace.json"
    destination.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(dict(status="passed", result=trace["result"],
                          events=len(trace["events"]), traceSHA256=sha(destination.read_bytes()))))
