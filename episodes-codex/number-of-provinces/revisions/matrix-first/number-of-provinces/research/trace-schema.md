# Observed execution schema

`trace.json` pins the sole `solution.py` SHA. `cases` contains `main`, `extraCycle`, and program-QA-only `compressionCheck`. Each case supplies `inputMatrix`, original `edges`, `cityLabels`, `actual`, `expected`, and `events`.

Every event: `id`, `type`, `sourceLine`, `a`, `b`, `pair`, copied `parent`, copied `size`, `count`, `groupRoots`, and `groups`. `pair` is null outside an actual matrix candidate. `inspect` also has `connected` and covers every upper-triangle cell, including zeros.

`find-start/find-check/compress/find-root` also provide actual `city`, `findSide`, `path`; `find-root` provides actual returned `root`. `compress` supplies `parentBefore`, `changed`, and `effectLine`. A halving operation can leave an already shallow parent unchanged; do not animate an invented shortcut when `changed` is false. The path is the actual loop's successive city values, not a claim that every intermediate grandparent was stepped through.

`roots/size-compare/link/resize/decrement/already-connected` provide the actual current `roots`. `size-compare` adds `rootSizes`; `link` adds `parentBefore/mergedRoots`. The `size` of nonroot slots may be historical; group size is read from a current root.

Python line events occur before their `sourceLine` executes. Link, resize, decrement and compress are observed after the preceding assignment; `effectLine` identifies that completed assignment. Already-connected is recorded only on the actually entered `continue` line, after the real equality branch.

Main event IDs: init0; AB roots8/link10/decrement12(count5); BC roots26(roots0/2)/link28/decrement30(count4); DE roots44/link46/decrement48(count3); finish51. ExtraCycle: AB decrement12(count5); AC decrement24(count4); BC roots39/already-connected40(count4); DE decrement58(count3); finish61.

The input relation graph is drawn from `edges`. Parent records belong to a separately labeled implementation view. Never draw parent[C]=A as if it created an input relation AC.
