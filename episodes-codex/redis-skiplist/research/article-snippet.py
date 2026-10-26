forward = [
    {"HEAD": 10, 10: 20, 20: 30, 30: 40, 40: 50,
     50: 60, 60: 70, 70: 80, 80: None},
    {"HEAD": 40, 40: 70, 70: None},
]
target = 55
cursor = "HEAD"
predecessors = {}
checks = []

for level in (1, 0):
    next_node = forward[level][cursor]
    while next_node is not None:
        checks.append(next_node)
        if next_node >= target:
            break
        cursor = next_node
        next_node = forward[level][cursor]
    predecessors[level] = cursor

assert checks == [40, 70, 50, 60]
assert predecessors == {1: 40, 0: 50}

# 本次固定为两层，每层都先接原后继，再改前驱。
for level in (0, 1):
    previous = predecessors[level]
    forward[level][target] = forward[level][previous]
    forward[level][previous] = target


def order(level):
    result = []
    node = forward[level]["HEAD"]
    while node is not None:
        result.append(node)
        node = forward[level][node]
    return result


assert order(0) == [10, 20, 30, 40, 50, 55, 60, 70, 80]
assert order(1) == [40, 55, 70]
print("底层：", order(0))
print("上层：", order(1))
