import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from merge_trace import merge_with_trace
from solution import Solution


def component_oracle(intervals):
    visited = set()
    components = []

    for root in range(len(intervals)):
        if root in visited:
            continue

        visited.add(root)
        pending = [root]
        members = []
        while pending:
            current = pending.pop()
            members.append(current)
            left_start, left_end = intervals[current]
            for candidate, (right_start, right_end) in enumerate(intervals):
                if candidate in visited:
                    continue
                if left_start <= right_end and right_start <= left_end:
                    visited.add(candidate)
                    pending.append(candidate)

        components.append([
            min(intervals[index][0] for index in members),
            max(intervals[index][1] for index in members),
        ])

    return sorted(components)


class MergeIntervalsTests(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def assert_trace_matches_oracle(self, intervals):
        result, events = merge_with_trace(intervals)
        self.assertEqual(result, self.solution.merge(intervals))

        if intervals:
            order = sorted(range(len(intervals)), key=lambda i: (intervals[i][0], i))
            self.assertEqual(events[0]["order"], order)
        else:
            order = []
            self.assertEqual(events[0]["kind"], "empty")

        for event in events:
            processed = event["processedIds"]
            self.assertEqual(processed, order[:len(processed)])
            prefix = [intervals[index] for index in processed]
            expected = component_oracle(prefix)
            state = event["completed"][:]
            if event["current"] is not None:
                state.append(event["current"])
            self.assertEqual(state, expected, msg=f"event={event}")

    def test_official_examples(self):
        cases = [
            (
                [[1, 3], [2, 6], [8, 10], [15, 18]],
                [[1, 6], [8, 10], [15, 18]],
            ),
            ([[1, 4], [4, 5]], [[1, 5]]),
            ([[4, 7], [1, 4]], [[1, 7]]),
        ]
        for intervals, expected in cases:
            with self.subTest(intervals=intervals):
                self.assertEqual(self.solution.merge(intervals), expected)
                self.assert_trace_matches_oracle(intervals)

    def test_review_sample_event_order_and_states(self):
        intervals = [[8, 10], [1, 4], [2, 3], [3, 5], [5, 6], [12, 14]]
        result, events = merge_with_trace(intervals)
        self.assertEqual(result, [[1, 6], [8, 10], [12, 14]])
        self.assertEqual(events[0]["order"], [1, 2, 3, 4, 0, 5])
        self.assertEqual(
            [(event["kind"], event.get("relation")) for event in events],
            [
                ("begin", None),
                ("merge", "nested"),
                ("merge", "overlap"),
                ("merge", "touching"),
                ("separate", None),
                ("separate", None),
                ("finish", None),
            ],
        )
        self.assertEqual(events[1]["current"], [1, 4])
        self.assertEqual(events[2]["current"], [1, 5])
        self.assertEqual(events[3]["current"], [1, 6])
        self.assert_trace_matches_oracle(intervals)

    def test_duplicate_nested_disjoint_single_zero_and_empty(self):
        cases = [
            [[1, 10], [2, 3], [4, 5]],
            [[1, 2], [1, 2]],
            [[4, 4]],
            [[1, 3], [5, 5]],
            [],
        ]
        for intervals in cases:
            with self.subTest(intervals=intervals):
                self.assertEqual(self.solution.merge(intervals), component_oracle(intervals))
                self.assert_trace_matches_oracle(intervals)

    def test_input_is_not_mutated(self):
        intervals = [[8, 10], [1, 4], [2, 3], [3, 5], [5, 6], [12, 14]]
        original = [interval[:] for interval in intervals]
        self.solution.merge(intervals)
        self.assertEqual(intervals, original)

    def test_exhaustive_small_interval_lists(self):
        values = [(start, end) for start in range(4) for end in range(start, 4)]
        for size in range(5):
            for items in itertools.product(values, repeat=size):
                intervals = [list(item) for item in items]
                expected = component_oracle(intervals)
                self.assertEqual(self.solution.merge(intervals), expected)
                self.assert_trace_matches_oracle(intervals)

    def test_seeded_random_cases(self):
        rng = random.Random(56059)
        for _ in range(500):
            intervals = []
            for _ in range(rng.randrange(11)):
                start = rng.randrange(10)
                end = rng.randrange(start, 10)
                intervals.append([start, end])
            expected = component_oracle(intervals)
            self.assertEqual(self.solution.merge(intervals), expected)
            self.assert_trace_matches_oracle(intervals)


if __name__ == "__main__":
    unittest.main()
