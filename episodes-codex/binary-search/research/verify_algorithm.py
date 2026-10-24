"""Finite verification of the actual solution, display source and teaching trace.

Run from any directory. The oracle enumerates the original array; it does not
perform binary search. Runtime tracing observes the actual submitted function.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re
import sys

EP = Path(__file__).resolve().parents[1]


def oracle(nums, target):
    return next((i for i, value in enumerate(nums) if value == target), -1)


def observe(solve, nums, target):
    """Observe before midpoint assignment using Python's line tracing API."""
    rows = []
    midpoint_line = solve.__code__.co_firstlineno + next(
        i for i, line in enumerate(
            (EP / 'solution.py').read_text().splitlines()[solve.__code__.co_firstlineno - 1:]
        ) if line.strip().startswith('mid =')
    )

    def tracer(frame, event, arg):
        if frame.f_code is solve.__code__ and event == 'line' and frame.f_lineno == midpoint_line:
            left = frame.f_locals['left']
            right = frame.f_locals['right']
            rows.append(dict(left=left, right=right,
                             mid=left + (right - left) // 2))
        return tracer

    previous_trace = sys.gettrace()
    sys.settrace(tracer)
    try:
        result = solve(nums, target)
    finally:
        sys.settrace(previous_trace)

    expected = oracle(nums, target)
    assert result == expected, (nums, target, result, expected)
    previous_count = None
    for row in rows:
        left, right, mid = row['left'], row['right'], row['mid']
        assert 0 <= left <= mid <= right < len(nums), row
        if expected >= 0:
            assert left <= expected <= right, (nums, target, row)
        count = right - left + 1
        if previous_count is not None:
            assert count <= previous_count // 2, (previous_count, count)
        row['value'] = nums[mid]
        row['candidateCount'] = count
        row['relation'] = '=' if nums[mid] == target else '<' if nums[mid] < target else '>'
        previous_count = count
    return result, rows


def main():
    code = (EP / 'solution.py').read_text()
    namespace = {}
    exec(compile(code, str(EP / 'solution.py'), 'exec'), namespace)
    solve = namespace['Solution']().search

    display = json.loads((EP / 'solution.json').read_text())
    assert '\n'.join(display['lines']) + '\n' == code, 'Display source differs'
    article = (EP / 'article.mdx').read_text()
    python_blocks = re.findall(r'```python\n(.*?)\n```', article, re.S)
    assert len(python_blocks) == 1 and python_blocks[0] + '\n' == code, 'Article code differs'

    # Every ascending unique array over this finite universe, all nearby targets.
    exhaustive = 0
    universe = range(-4, 5)
    for length in range(1, len(universe) + 1):
        for values in itertools.combinations(universe, length):
            nums = list(values)
            before = nums.copy()
            for target in range(-5, 6):
                observe(solve, nums, target)
                assert nums == before, 'Input array was modified'
                exhaustive += 1

    cases = [
        ([-1, 0, 3, 5, 9, 12], 9, 4),
        ([-1, 0, 3, 5, 9, 12], 2, -1),
        ([1, 3, 5, 7, 9, 11, 13, 15], 13, 6),
        ([1, 3, 5, 7, 9, 11, 13, 15], 8, -1),
        ([5], 5, 0), ([5], 4, -1), ([5], 6, -1),
        ([1, 3], 1, 0), ([1, 3], 3, 1), ([1, 3], 2, -1),
        ([1, 3], 0, -1), ([1, 3], 4, -1),
        ([-9999, 0, 9999], -9999, 0),
        ([-9999, 0, 9999], 9999, 2),
        (list(range(-5000, 5000)), 4999, 9999),
        (list(range(-5000, 5000)), 5000, -1),
    ]
    for nums, target, expected in cases:
        assert observe(solve, nums, target)[0] == expected

    # Empty arrays are outside the official n >= 1 constraint.
    for target in [-1, 0, 1]:
        result, rows = observe(solve, [], target)
        assert result == -1 and not rows

    teaching = []
    for target in [13, 8]:
        nums = [1, 3, 5, 7, 9, 11, 13, 15]
        answer, rows = observe(solve, nums, target)
        expected_mids = [3, 5, 6] if target == 13 else [3, 5, 4]
        assert [r['mid'] for r in rows] == expected_mids
        assert len(rows) == 3
        final_left = rows[-1]['left']
        final_right = rows[-1]['right']
        if answer == -1:
            final_right = rows[-1]['mid'] - 1
            assert (final_left, final_right) == (4, 3)
        teaching.append(dict(target=target, returned=answer, rounds=rows,
                             finalLeft=final_left, finalRight=final_right))

    report = dict(
        status='passed',
        solutionSha256=hashlib.sha256(code.encode()).hexdigest(),
        method='Run the actual submitted function; compare to independent sequential enumeration; observe real execution via line tracing.',
        exhaustiveUniverse=list(universe), exhaustiveTargets=list(range(-5, 6)),
        exhaustiveUniqueSortedNonemptyArrays=2 ** len(universe) - 1,
        exhaustiveCases=exhaustive, explicitCases=len(cases),
        outsideOfficialEmptyArrayCases=3,
        invariantChecks=['Target index remains in every nonempty candidate interval when present.',
                         'Midpoint is within the current closed interval.',
                         'After each nonterminal step, candidate count is at most floor(previous count / 2).',
                         'Input array remains unchanged.'],
        displayCodeExact=True, articleCodeExact=True,
        teachingTrace=teaching,
        limits='Finite cases check this implementation and trace, not the general proof, animation pixels, speech or learning outcomes.',
    )
    report_path = EP / 'research/algorithm-verification.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    main()
