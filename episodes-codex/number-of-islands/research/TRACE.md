# Actual solver trace

`python research/generate_demo_trace.py` produces the single authoritative
`research/demo-trace.json` from the official second example. The generator reads
the pinned `solution.py`, compiles it unchanged, and compiles a second AST with
observer expression statements inserted. Removing only those tagged callbacks
must recover the complete original AST exactly. It does not implement another
DFS solver or change a condition, loop, assignment, neighbor order, or stack.

`python research/verify_algorithm.py` executes both versions, checks input deep
snapshots, compares independent union-find partitions, and regenerates the same
demonstration trace. Detailed snapshots are restricted to the 4×5 example;
summary observers never copy the whole seen set or stack per event.

The top level contains `grid` (the original string matrix), `events`, integer
`result`, `componentMap` (0 means water; positive values are discovery-order
island IDs), `solutionSHA256`, and `summary`. Generator/source identities are
also recorded. The grid is never overwritten.

Every event has `index`, `action`, `row`, `col`, `cell`, `from`, `reason`,
`islandId`, `count`, `active`, `stack`, `seen`, and `expanded`. Coordinates are
zero-based. Stack arrays run **bottom to top**; the final entry is popped next.
Set snapshots are sorted row-major and detached from the live program state.

All snapshots describe the state after the named action:

- `scan`: outer row-major scan reaches this cell. No component is active.
- `skip`: the actual outer condition skips water or an already discovered cell.
- `seed`: the answer has incremented, but the seed is not yet marked or pushed.
- `mark`: `seen.add` has run. This is discovery/assignment, before the push.
- `push`: the seed-stack assignment or neighbor append has run.
- `pop`: the LIFO removal has run; this cell is now active, not yet expanded.
- `neighbor_check`: one actual right/down/left/up check decides `boundary`,
  `water`, `seen`, or `fresh`. Boundary is checked before any grid indexing.
- `expanded`: all four neighbors of the active cell have been checked. The cell
  enters `expanded` and `active` clears.
- `component_done`: the actual while loop has ended with an empty stack.

`seen` means **already discovered and assigned**, not already expanded. In the
first component, (0,0) marks/pushes (0,1), then (1,0). LIFO pops (1,0), then
(1,1), and only later (0,1). That waiting cell is already seen and belongs to
the same island throughout. During `mark`, a new seen cell has not been pushed
yet, so do not treat every intermediate snapshot as `seen = stack ∪ expanded`.

For `scan`/`skip`, `islandId` is the known owner of that cell or null; it is not
the previous component ID. `count` is always the current accumulated answer.
For component actions, `islandId` is the current component. Boundary candidates
may have coordinates outside the grid; they must not be rendered as grid cells.

The oracle initializes one disjoint set per land cell and merges only right/down
orthogonal edges. Every implementation component must correspond bijectively
to one oracle root. This checks full partitions, not just equal total counts.
The implementation's existing connectivity argument and complexity analysis
remain separate from these finite execution checks.
