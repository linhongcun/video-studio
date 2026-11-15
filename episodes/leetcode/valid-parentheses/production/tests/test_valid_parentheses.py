import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paren_trace import PAIRS, validate_with_trace
from solution import Solution

OPEN = "([{"
CLOSE = ")]}"


def reduction_oracle(s: str) -> bool:
    text = s
    while True:
        reduced = text.replace("()", "").replace("[]", "").replace("{}", "")
        if reduced == text:
            return text == ""
        text = reduced


class ValidParenthesesTests(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def assert_trace_matches(self, s):
        valid, events = validate_with_trace(s)
        self.assertEqual(valid, self.solution.isValid(s))
        self.assertEqual(valid, reduction_oracle(s))
        stack = []
        for event in events:
            kind = event["kind"]
            if kind == "push":
                stack.append(event["char"])
            elif kind == "pop":
                self.assertEqual(stack.pop(), PAIRS[event["char"]])
            elif kind == "mismatch":
                self.assertNotEqual(stack[-1], PAIRS[event["char"]])
            elif kind == "empty":
                self.assertEqual(stack, [])
            elif kind == "leftover":
                self.assertTrue(stack)
            elif kind == "finish":
                self.assertEqual(stack, [])
            if kind in {"push", "pop"}:
                self.assertEqual(event["stack"], stack)
        self.assertIn(events[-1]["kind"], {"finish", "leftover", "mismatch", "empty"})
        self.assertEqual(valid, events[-1]["kind"] == "finish")

    def test_official_examples(self):
        for s, expected in [("()", True), ("()[]{}", True), ("(]", False), ("([])", True), ("([)]", False)]:
            self.assertEqual(self.solution.isValid(s), expected, s)
            self.assert_trace_matches(s)

    def test_teaching_examples(self):
        self.assertTrue(self.solution.isValid("{[()]}()"))
        self.assertFalse(self.solution.isValid("())"))
        self.assertFalse(self.solution.isValid("(()"))
        self.assertFalse(self.solution.isValid(")"))
        self.assertFalse(self.solution.isValid("(("))
        self.assertTrue(self.solution.isValid(""))
        for s in ["{[()]}()", "())", "(()", ")", "((", ""]:
            self.assert_trace_matches(s)

    def test_main_trace_shape(self):
        valid, events = validate_with_trace("{[()]}()")
        self.assertTrue(valid)
        self.assertEqual([e["kind"] for e in events], ["push"] * 3 + ["pop"] * 3 + ["push", "pop", "finish"])
        self.assertEqual(events[2]["stack"], ["{", "[", "("])
        self.assertEqual(events[5]["stack"], [])

    def test_exhaustive_short_strings(self):
        for length in range(0, 7):
            for chars in itertools.product(OPEN + CLOSE, repeat=length):
                self.assert_trace_matches("".join(chars))

    def test_random_strings(self):
        rng = random.Random(20)
        for _ in range(300):
            s = "".join(rng.choice(OPEN + CLOSE) for _ in range(rng.randint(1, 16)))
            self.assert_trace_matches(s)


if __name__ == "__main__":
    unittest.main()
