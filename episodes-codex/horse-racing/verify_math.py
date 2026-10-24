#!/usr/bin/env python3
"""Independent finite checks for the seven-race construction and lower-bound lemma.

No claim of enumerating 25! full speed orders or all adaptive six-race policies.
The universal proof is in research-math.md, not inferred from random samples.
"""

from collections import Counter
from itertools import combinations, permutations
import json
from random import Random


def seven_races(speed_order):
    """Rank is supplied only by the oracle; the schedule sees race orders only."""
    rank = {horse: place for place, horse in enumerate(speed_order)}
    races = []

    def race(entrants):
        assert 1 <= len(entrants) <= 5
        assert len(set(entrants)) == len(entrants)
        result = tuple(sorted(entrants, key=rank.__getitem__))
        races.append(result)
        return result

    heats = [race(tuple(range(start, start + 5))) for start in range(0, 25, 5)]
    by_winner = {heat[0]: heat for heat in heats}
    winner_order = race(tuple(by_winner))
    groups = [by_winner[winner] for winner in winner_order]
    a, b, c, _, _ = groups
    finalists = race(a[1:3] + b[:2] + c[:1])
    answer = (a[0], finalists[0], finalists[1])
    assert len(races) == 7
    return answer, races


def check_normalized_partial_order():
    groups = [[f"{group}{i}" for i in range(1, 6)] for group in "ABCDE"]
    horses = [horse for group in groups for horse in group]
    slower = {horse: set() for horse in horses}
    results = groups + [[group[0] for group in groups]]
    for result in results:
        for i, fast in enumerate(result):
            slower[fast].update(result[i + 1 :])
    for mid in horses:
        for fast in horses:
            if mid in slower[fast]:
                slower[fast].update(slower[mid])
    faster = {horse: {fast for fast in horses if horse in slower[fast]} for horse in horses}
    viable = {horse for horse in horses if len(faster[horse]) < 3}
    expected = {"A1", "A2", "A3", "B1", "B2", "C1"}
    assert viable == expected, (viable, expected)
    assert slower["A1"] == set(horses) - {"A1"}

    witness_sets = {
        "A4": {"A1", "A2", "A3"},
        "A5": {"A1", "A2", "A3"},
        **{f"B{i}": {"A1", "B1", "B2"} for i in (3, 4, 5)},
        **{f"C{i}": {"A1", "B1", "C1"} for i in (2, 3, 4, 5)},
        **{f"{group}{i}": {"A1", "B1", "C1"} for group in "DE" for i in range(1, 6)},
    }
    assert set(witness_sets) == set(horses) - viable
    for horse, witnesses in witness_sets.items():
        assert witnesses <= faster[horse], (horse, witnesses, faster[horse])

    finalists = ("A2", "A3", "B1", "B2", "C1")
    compatible_orders = []
    for order in permutations(finalists):
        position = {horse: i for i, horse in enumerate(order)}
        if all(
            position[fast] < position[slow]
            for fast in finalists
            for slow in finalists
            if slow in slower[fast]
        ):
            compatible_orders.append(order)
    answer_counts = Counter(order[:2] for order in compatible_orders)
    assert len(compatible_orders) == 20
    assert set(answer_counts) == {
        ("A2", "A3"), ("A2", "B1"),
        ("B1", "A2"), ("B1", "B2"), ("B1", "C1"),
    }
    return {
        "known_six_race_results": results,
        "horses_still_eligible_for_top_three": sorted(viable),
        "excluded_horses_with_three_faster_witnesses": len(witness_sets),
        "finalist_permutations_checked": 120,
        "compatible_finalist_orders": len(compatible_orders),
        "distinct_ordered_second_third_results": len(answer_counts),
    }


def check_constructive_oracle():
    horses = tuple(range(25))
    placements_checked = 0
    for top_three in permutations(horses, 3):
        top_set = set(top_three)
        order = top_three + tuple(horse for horse in horses if horse not in top_set)
        answer, _ = seven_races(order)
        assert answer == top_three, (order, answer)
        placements_checked += 1
    assert placements_checked == 25 * 24 * 23 == 13800
    rng = Random(20261025)
    for _ in range(1000):
        order = list(horses)
        rng.shuffle(order)
        answer, _ = seven_races(order)
        assert answer == tuple(order[:3]), (order, answer)
    return {
        "ordered_top_three_placements_checked": placements_checked,
        "remaining_horses_order_in_those_cases": "ascending identifier; not all 22! orders",
        "additional_random_complete_orders": 1000,
        "random_seed": 20261025,
        "full_25_factorial_enumeration": False,
    }


def check_adjacent_swap_lemma():
    # Fixed order X > Y > Z > all others. The first race contains X and Z,
    # but not Y. Choosing this input after seeing a deterministic algorithm's
    # initial lineup is valid: it is fixed before any race outcome is supplied.
    x, y, z = 0, 1, 2
    horses = tuple(range(25))
    first_race = (x, z, 3, 4, 5)
    original_rank = {horse: horse for horse in horses}
    swapped_order = (x, z, y) + tuple(range(3, 25))
    swapped_rank = {horse: i for i, horse in enumerate(swapped_order)}
    assert tuple(sorted(first_race, key=original_rank.__getitem__)) == first_race
    assert tuple(sorted(first_race, key=swapped_rank.__getitem__)) == first_race
    first_losers = set(first_race[1:])
    assert z in first_losers

    total = invariant = distinguishes_pair = 0
    for size in range(1, 6):
        for entrants in combinations(horses, size):
            original = tuple(sorted(entrants, key=original_rank.__getitem__))
            swapped = tuple(sorted(entrants, key=swapped_rank.__getitem__))
            total += 1
            if y in entrants and z in entrants:
                assert original != swapped
                assert z in original[1:]
                assert z in first_losers
                distinguishes_pair += 1
            else:
                assert original == swapped
                invariant += 1
    assert (total, invariant, distinguishes_pair) == (68405, 66357, 2048)

    # One concrete six-race transcript that determines the winner and saturates
    # the loss budget; it still cannot distinguish the ordered runners-up.
    unseen = [horse for horse in horses if horse not in first_race]
    transcript = [first_race]
    for offset in range(0, len(unseen), 4):
        transcript.append(tuple(sorted((x, *unseen[offset : offset + 4]), key=original_rank.__getitem__)))
    loss_counts = Counter(horse for result in transcript for horse in result[1:])
    assert len(transcript) == 6
    assert set(loss_counts) == set(horses) - {x}
    assert all(count == 1 for count in loss_counts.values())
    assert all(not ({y, z} <= set(result)) for result in transcript)
    assert all(tuple(sorted(result, key=swapped_rank.__getitem__)) == result for result in transcript)
    assert horses[:3] != swapped_order[:3]
    return {
        "first_race": first_race,
        "all_possible_single_race_subsets_sizes_one_through_five": total,
        "unchanged_race_subsets_not_containing_both_y_and_z": invariant,
        "distinguishing_subsets_that_would_give_z_a_second_loss": distinguishes_pair,
        "example_six_race_transcript": transcript,
        "every_nonwinner_loses_exactly_once_in_example": True,
        "example_transcript_preserved_by_y_z_swap": True,
        "all_adaptive_schedules_enumerated": False,
    }


def main():
    result = {
        "status": "passed",
        "scope": "ordered first, second and third; exact local lemmas plus finite construction checks",
        "normalized_partial_order": check_normalized_partial_order(),
        "constructive_oracle": check_constructive_oracle(),
        "lower_bound_adjacent_swap_lemma": check_adjacent_swap_lemma(),
        "universal_proof": "research-math.md; finite checks do not substitute for the proof",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
