"""Single-rule pricing example for D01. Amounts are integer cents.

Teaching rules, not a production promotion engine: percentages round down to
one cent, one rule is selected, and no discounts are stacked.
"""

from collections.abc import Callable, Mapping

Pricing = Callable[[int], int]


def validate_total(total_cents: int) -> None:
    if type(total_cents) is not int or total_cents < 0:
        raise ValueError("total_cents must be a non-negative integer")


def ordinary(total_cents: int) -> int:
    return total_cents


def member(total_cents: int) -> int:
    return total_cents * 90 // 100


def campaign(total_cents: int) -> int:
    return total_cents * 80 // 100


def campaign_v2(total_cents: int) -> int:
    return total_cents * 75 // 100


def newcomer(total_cents: int) -> int:
    return max(0, total_cents - 1_000)


def before_checkout(total_cents: int, kind: str) -> int:
    """Original implementation: the checkout contains the concrete rules."""
    validate_total(total_cents)
    if kind == "ordinary":
        return total_cents
    if kind == "member":
        return total_cents * 90 // 100
    if kind == "campaign":
        return total_cents * 80 // 100
    raise ValueError("unknown pricing rule")


def checkout(total_cents: int, pricing: Pricing) -> int:
    """The stable context: validate, delegate, validate the result, return."""
    validate_total(total_cents)
    payable = pricing(total_cents)
    if type(payable) is not int or not 0 <= payable <= total_cents:
        raise ValueError("pricing must return integer cents within [0, total]")
    return payable


RULES_V1: Mapping[str, Pricing] = {
    "ordinary": ordinary,
    "member": member,
    "campaign": campaign,
}
RULES_V2: Mapping[str, Pricing] = {
    **RULES_V1,
    "campaign": campaign_v2,
}
RULES_EXTENDED: Mapping[str, Pricing] = {
    **RULES_V2,
    "newcomer": newcomer,
}


def select_rule(kind: str, rules: Mapping[str, Pricing]) -> Pricing:
    """The caller selects a rule. Selection has not disappeared."""
    if not isinstance(kind, str) or kind not in rules:
        raise ValueError("unknown pricing rule")
    return rules[kind]


if __name__ == "__main__":
    for name in RULES_V1:
        print(name, before_checkout(10_000, name),
              checkout(10_000, select_rule(name, RULES_V1)))
    print("campaign after update:",
          checkout(10_000, select_rule("campaign", RULES_V2)))
    print("newcomer:",
          checkout(10_000, select_rule("newcomer", RULES_EXTENDED)))
