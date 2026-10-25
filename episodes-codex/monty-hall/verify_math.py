#!/usr/bin/env python3
"""Exact Fraction verification of informed-host Monty Hall and a blind variant.

This is an independent QA program, not production animation or a video code card.
No external code is downloaded or executed. All probabilities remain rational.
"""

import argparse
from collections import defaultdict
from datetime import datetime
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from zoneinfo import ZoneInfo


DOORS = (1, 2, 3)
ONE_THIRD = Fraction(1, 3)
ONE_HALF = Fraction(1, 2)
ZERO = Fraction(0)


def enumerate_paths(informed):
    """Choose pick/prize independently and uniformly, then apply the host law."""
    paths = []
    for pick, prize in product(DOORS, repeat=2):
        choices = tuple(door for door in DOORS if door != pick and (not informed or door != prize))
        host_probability = Fraction(1, len(choices))
        for opened in choices:
            switched_to = next(door for door in DOORS if door != pick and door != opened)
            paths.append({
                "pick": pick,
                "prize": prize,
                "opened": opened,
                "switchTo": switched_to,
                "hostProbability": host_probability,
                "jointProbability": ONE_THIRD * ONE_THIRD * host_probability,
                "probabilityGivenPick": ONE_THIRD * host_probability,
                "openedEmpty": opened != prize,
                "stayWins": pick == prize,
                "switchWins": switched_to == prize,
            })
    return paths


def independently_count_equal_seed_tickets(informed):
    """Eighteen equal tickets: pick x prize x a fair two-valued host seed.

    Wrong initial picks force the informed opening, so two different seeds merge
    into the same observable path. This implementation does not use host choices
    or probabilities returned by enumerate_paths().
    """
    unchosen = {1: (2, 3), 2: (1, 3), 3: (1, 2)}
    counts = defaultdict(int)
    for pick, prize, seed in product(DOORS, DOORS, (0, 1)):
        if informed and prize != pick:
            opened = 6 - pick - prize
        else:
            opened = unchosen[pick][seed]
        counts[(pick, prize, opened)] += 1
    assert sum(counts.values()) == 18
    return {key: Fraction(count, 18) for key, count in counts.items()}


def mass(paths, predicate):
    return sum((path["jointProbability"] for path in paths if predicate(path)), ZERO)


def conditional(paths, outcome, given):
    denominator = mass(paths, given)
    if denominator == 0:
        raise ValueError("conditioning event has probability zero")
    return mass(paths, lambda path: given(path) and outcome(path)) / denominator


def records(paths):
    return [
        {key: str(value) if isinstance(value, Fraction) else value for key, value in path.items()}
        for path in paths
    ]


def outcomes_under(paths, given):
    return {
        "stayWinProbability": str(conditional(paths, lambda path: path["stayWins"], given)),
        "switchWinProbability": str(conditional(paths, lambda path: path["switchWins"], given)),
    }


def posterior_prize(paths, given):
    return {str(door): str(conditional(paths, lambda path, door=door: path["prize"] == door, given)) for door in DOORS}


def grouped_fixed_pick_scenarios(paths, pick):
    scenarios = []
    pick_mass = mass(paths, lambda path: path["pick"] == pick)
    for prize in DOORS:
        selected = [path for path in paths if path["pick"] == pick and path["prize"] == prize]
        scenario_probability = sum((path["jointProbability"] for path in selected), ZERO) / pick_mass
        assert scenario_probability == ONE_THIRD
        assert len({path["stayWins"] for path in selected}) == 1
        assert len({path["switchWins"] for path in selected}) == 1
        scenarios.append({
            "prizeDoor": prize,
            "probabilityGivenPick": str(scenario_probability),
            "initialPickCorrect": prize == pick,
            "stayWins": selected[0]["stayWins"],
            "switchWins": selected[0]["switchWins"],
            "hostBranches": records(selected),
        })
    return scenarios


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write exact auditable JSON report")
    args = parser.parse_args()
    informed = enumerate_paths(True)
    blind = enumerate_paths(False)

    assert len(informed) == 12 and len(blind) == 18
    for is_informed, paths in ((True, informed), (False, blind)):
        assert mass(paths, lambda path: True) == 1
        actual_weights = {(path["pick"], path["prize"], path["opened"]): path["jointProbability"] for path in paths}
        assert actual_weights == independently_count_equal_seed_tickets(is_informed)
        for path in paths:
            assert path["opened"] != path["pick"]
            assert path["switchTo"] not in (path["pick"], path["opened"])
            assert path["switchTo"] in DOORS
            if path["openedEmpty"]:
                assert path["stayWins"] != path["switchWins"]
            else:
                assert not is_informed and not path["stayWins"] and not path["switchWins"]
        for pick, prize in product(DOORS, repeat=2):
            choices = [path for path in paths if path["pick"] == pick and path["prize"] == prize]
            assert sum((path["hostProbability"] for path in choices), ZERO) == 1
        for pick in DOORS:
            assert mass(paths, lambda path, pick=pick: path["pick"] == pick) == ONE_THIRD

    # Direct event calculation, independent of opening-path enumeration.
    initially_correct = ONE_THIRD
    direct_stay = initially_correct
    direct_switch = 1 - initially_correct
    direct_blind_empty = initially_correct + (1 - initially_correct) * ONE_HALF
    direct_blind_stay_given_empty = initially_correct / direct_blind_empty
    direct_blind_switch_given_empty = (1 - initially_correct) * ONE_HALF / direct_blind_empty
    assert direct_stay == ONE_THIRD and direct_switch == Fraction(2, 3)
    assert direct_blind_empty == Fraction(2, 3)
    assert direct_blind_stay_given_empty == direct_blind_switch_given_empty == ONE_HALF
    assert all(path["openedEmpty"] for path in informed)
    assert mass(informed, lambda path: path["stayWins"]) == direct_stay
    assert mass(informed, lambda path: path["switchWins"]) == direct_switch

    for pick in DOORS:
        given_pick = lambda path, pick=pick: path["pick"] == pick
        assert conditional(informed, lambda path: path["stayWins"], given_pick) == ONE_THIRD
        assert conditional(informed, lambda path: path["switchWins"], given_pick) == Fraction(2, 3)
        for opened in DOORS:
            if opened == pick:
                continue
            given_open = lambda path, pick=pick, opened=opened: path["pick"] == pick and path["opened"] == opened
            assert conditional(informed, lambda path: path["stayWins"], given_open) == ONE_THIRD
            assert conditional(informed, lambda path: path["switchWins"], given_open) == Fraction(2, 3)

    pick_one = lambda path: path["pick"] == 1
    pick_one_open_three = lambda path: path["pick"] == 1 and path["opened"] == 3
    scenarios = grouped_fixed_pick_scenarios(informed, 1)
    assert [len(scenario["hostBranches"]) for scenario in scenarios] == [2, 1, 1]
    fixed_paths = [path for path in informed if path["pick"] == 1]
    assert [path["probabilityGivenPick"] for path in fixed_paths] == [Fraction(1, 6), Fraction(1, 6), ONE_THIRD, ONE_THIRD]
    assert posterior_prize(informed, pick_one_open_three) == {"1": "1/3", "2": "2/3", "3": "0"}

    blind_empty = lambda path: path["openedEmpty"]
    blind_pick_one_empty = lambda path: path["pick"] == 1 and path["openedEmpty"]
    blind_pick_one_open_three_empty = lambda path: path["pick"] == 1 and path["opened"] == 3 and path["openedEmpty"]
    assert mass(blind, blind_empty) == direct_blind_empty
    assert mass(blind, lambda path: not path["openedEmpty"]) == ONE_THIRD
    assert conditional(blind, lambda path: path["stayWins"], blind_empty) == ONE_HALF
    assert conditional(blind, lambda path: path["switchWins"], blind_empty) == ONE_HALF
    assert conditional(blind, lambda path: path["stayWins"], blind_pick_one_empty) == ONE_HALF
    assert conditional(blind, lambda path: path["switchWins"], blind_pick_one_empty) == ONE_HALF
    assert posterior_prize(blind, blind_pick_one_open_three_empty) == {"1": "1/2", "2": "1/2", "3": "0"}

    result = {
        "status": "passed",
        "executedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "executor": "/root/puzzle_batch_a",
        "verifierSha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "probabilityEncoding": "all probabilities are exact reduced Fraction strings; no floating point or simulation",
        "mainModel": {
            "doors": list(DOORS),
            "prizeUniformAndIndependentOfInitialPick": True,
            "playerInitialPickForTeaching": 1,
            "allThreeInitialPicksChecked": True,
            "hostKnowsPrizeLocation": True,
            "hostAlwaysOpensAnUnpickedEmptyDoor": True,
            "hostAlwaysOffersSwitch": True,
            "hostChoosesUniformlyWhenTwoEmptyDoorsAreAvailable": True,
            "globalEnumerationPickPrior": "1/3",
            "globalEnumerationPrizePrior": "1/3",
        },
        "informedHost": {
            "globalPathCount": len(informed),
            "globalPathsJointMass": "1",
            "globalPaths": records(informed),
            "stayWinProbability": str(direct_stay),
            "switchWinProbability": str(direct_switch),
            "fixedPick1": {
                "paths": records(fixed_paths),
                "pathsGivenPickSum": "1",
                "threeEqualPriorPrizeScenarios": scenarios,
                "threeScenarioProbabilities": ["1/3", "1/3", "1/3"],
                "correctInitialPickTwoBranchesCombinedProbability": "1/3",
                "specificHostOpensDoor3": {
                    "probabilityGivenPick1": str(conditional(informed, lambda path: path["opened"] == 3, pick_one)),
                    "posteriorPrizeByDoor": posterior_prize(informed, pick_one_open_three),
                    **outcomes_under(informed, pick_one_open_three),
                },
            },
        },
        "differentBlindHostModel": {
            "description": "host does not know the prize and uniformly opens either unpicked door; an empty opening is observed/conditioned, not guaranteed",
            "globalPathCount": len(blind),
            "globalPathsJointMass": "1",
            "globalPaths": records(blind),
            "probabilityHostOpensEmpty": str(direct_blind_empty),
            "probabilityHostRevealsPrize": "1/3",
            "givenHostOpensEmpty": outcomes_under(blind, blind_empty),
            "fixedPick1": {
                "paths": records([path for path in blind if path["pick"] == 1]),
                "givenHostOpensEmpty": outcomes_under(blind, blind_pick_one_empty),
                "specificHostOpensDoor3AndItIsEmpty": {
                    "probabilityGivenPick1": str(conditional(blind, lambda path: path["opened"] == 3 and path["openedEmpty"], pick_one)),
                    "posteriorPrizeByDoor": posterior_prize(blind, blind_pick_one_open_three_empty),
                    **outcomes_under(blind, blind_pick_one_open_three_empty),
                },
            },
        },
        "independentChecks": {
            "all9PickPrizePairsCheckedInEachModel": True,
            "hostChoiceProbabilitiesSumToOneForEachPair": True,
            "equalSeedTicketsPerModel": 18,
            "independentSeedImplementationMatchesAllObservablePathWeights": True,
            "directInitialCorrectIncorrectEventMethodMatches": True,
            "specificEmptyDoorConditionalsCheckedForEveryPickAndUnpickedDoor": True,
            "fixedPick1FourPathWeights": ["1/6", "1/6", "1/3", "1/3"],
        },
        "scopeLimits": [
            "Main results compare always-stay and always-switch under the complete informed-host protocol.",
            "Three initial prize positions have equal prior weight; the four host-opening paths do not.",
            "Uniform tie-breaking is fixed for specific opened-door posteriors; it is not necessary for the unconditional 2/3 always-switch identity.",
            "Blind-host half/half is conditional on the host having opened an empty door; it is a different protocol.",
            "Exact finite enumeration is not a claim that every three played games yield two switch wins.",
            "Does not execute external code or inspect animation, voice, encoded media, web pages or audience understanding.",
        ],
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
        print(json.dumps({"status": "passed", "output": str(args.output), "informedPaths": 12, "blindPaths": 18, "stay": "1/3", "switch": "2/3", "blindGivenEmptyStay": "1/2", "blindGivenEmptySwitch": "1/2", "verifierSha256": result["verifierSha256"]}, ensure_ascii=False))
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
