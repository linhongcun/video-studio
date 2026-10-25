"""Finite cross-check of the actual published solution against enumeration.

Run from any directory. This verifies implementation and the selected teaching
trace; it is not a substitute for the correctness argument in article.mdx.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re

EP = Path(__file__).resolve().parents[1]


def brute(s):
    """Enumerate contiguous intervals; do not use a moving-window algorithm."""
    return max((end - start for start in range(len(s) + 1)
                for end in range(start, len(s) + 1)
                if len(set(s[start:end])) == end - start), default=0)


def expected_earliest_left(s, right):
    return next(left for left in range(right + 1)
                if len(set(s[left:right + 1])) == right - left + 1)


def teaching_trace(s):
    """Instrument the same rule only to inspect states, against brute invariants."""
    members, left, best = set(), 0, 0
    rows = []
    for right, ch in enumerate(s):
        removed = []
        while ch in members:
            removed.append([left, s[left]])
            members.remove(s[left])
            left += 1
        members.add(ch)
        best = max(best, right - left + 1)
        window = s[left:right + 1]
        assert len(set(window)) == len(window)
        assert members == set(window)
        assert left == expected_earliest_left(s, right)
        assert best == brute(s[:right + 1])
        rows.append(dict(right=right, candidate=ch, removed=removed, left=left,
                         window=window, current=len(window), best=best))
    return rows


def main():
    code = (EP / 'solution.py').read_text()
    namespace = {}
    exec(compile(code, str(EP / 'solution.py'), 'exec'), namespace)
    solve = namespace['Solution']().lengthOfLongestSubstring

    display = json.loads((EP / 'solution.json').read_text())
    assert '\n'.join(display['lines']) + '\n' == code

    explicit = {
        '': 0, 'a': 1, 'aaaa': 1, 'abcabcbb': 3, 'bbbbb': 1,
        'pwwkew': 3, 'abba': 2, 'abcbadea': 5, ' ': 1,
        '  ': 1, 'a a': 2, 'a# a': 3, '\t \t': 2,
        '你好你': 2, '🙂a🙂b': 3, 'aA': 2,
    }
    for value, expected in explicit.items():
        assert solve(value) == expected == brute(value), (repr(value), expected)

    count = 0
    for length in range(8):
        for chars in itertools.product('ab #', repeat=length):
            value = ''.join(chars)
            assert solve(value) == brute(value), repr(value)
            count += 1

    trace = teaching_trace('abcbadea')
    assert trace[3]['removed'] == [[0, 'a'], [1, 'b']]
    assert trace[3]['window'] == 'cb' and trace[3]['best'] == 3
    assert trace[6]['window'] == 'cbade' and trace[6]['best'] == 5
    assert trace[7]['removed'] == [[2, 'c'], [3, 'b'], [4, 'a']]
    assert trace[7]['window'] == 'dea' and trace[7]['best'] == 5

    article = (EP / 'article.mdx').read_text()
    python_blocks = re.findall(r'```python\n(.*?)\n```', article, re.S)
    article_match = any(block + '\n' == code for block in python_blocks)
    result = dict(status='passed' if article_match else 'program-passed-article-pending',
                  method='Actual solution execution against independently enumerated contiguous intervals.',
                  solutionSha256=hashlib.sha256(code.encode()).hexdigest(),
                  exhaustiveAlphabet='ab #', exhaustiveMaxLength=7,
                  exhaustiveCases=count, explicitCases=len(explicit),
                  displayCodeExact=True, articleCodeExact=article_match,
                  teachingTrace=trace,
                  limits='Finite cases verify this implementation, not the general proof or video pixels/audio.')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    main()
