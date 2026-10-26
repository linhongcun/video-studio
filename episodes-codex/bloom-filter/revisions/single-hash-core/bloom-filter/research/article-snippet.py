from hashlib import sha256


def position(key, seed=22):
    digest = sha256(f"{seed}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % 8


def add(bits, key):
    bits[position(key)] = 1


def maybe_contains(bits, key):
    return bits[position(key)] == 1


bits = [0] * 8
for key in ("A", "B"):
    add(bits, key)

for key in ("A", "B", "C", "D"):
    print(key, position(key), maybe_contains(bits, key))

assert bits == [0, 0, 0, 1, 0, 0, 0, 0]
assert not maybe_contains(bits, "D")  # 7号是0，可以排除
assert maybe_contains(bits, "C")  # C未加入，但3号是1，发生假阳性

# 错误操作反例：假设只移除A，B仍在，不能直接清零共享位。
wrong = bits.copy()
wrong[position("A")] = 0
assert not maybe_contains(wrong, "B")  # B被错误排除

# 另从全0重建两位置对照，仍然只加入A和B。
two = [0] * 8
for key in ("A", "B"):
    for seed in (22, 0):
        two[position(key, seed)] = 1
assert two == [0, 1, 1, 1, 0, 0, 0, 0]
assert not all(two[position("C", seed)] for seed in (22, 0))
