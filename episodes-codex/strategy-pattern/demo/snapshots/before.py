"""Minimal independently runnable snapshot of the campaign rule."""

from collections.abc import Callable

Pricing = Callable[[int], int]


def ordinary(total_cents: int) -> int:
    return total_cents


def member(total_cents: int) -> int:
    return total_cents * 90 // 100


def campaign(total_cents: int) -> int:
    return total_cents * 80 // 100


def checkout(total_cents: int, pricing: Pricing) -> int:
    if type(total_cents) is not int or total_cents < 0:
        raise ValueError("total_cents must be a non-negative integer")
    payable = pricing(total_cents)
    if type(payable) is not int or not 0 <= payable <= total_cents:
        raise ValueError("pricing must return integer cents within [0, total]")
    return payable


RULES = {"ordinary": ordinary, "member": member, "campaign": campaign}


def select_rule(kind: str) -> Pricing:
    if not isinstance(kind, str) or kind not in RULES:
        raise ValueError("unknown pricing rule")
    return RULES[kind]


if __name__ == "__main__":
    for name in RULES:
        print(name, checkout(10_000, select_rule(name)))
