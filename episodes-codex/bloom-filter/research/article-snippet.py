from hashlib import sha256


def positions(key):
    return [
        int.from_bytes(sha256(f"{seed}:{key}".encode("utf-8")).digest()[:8], "big") % 16
        for seed in range(3)
    ]


bits = [0] * 16


def add(key):
    for index in positions(key):
        bits[index] = 1


def maybe_contains(key):
    for index in positions(key):
        if bits[index] == 0:
            return False
    return True


catalog = {"sku101", "sku205"}
for key in ["sku101", "sku205"]:
    add(key)

for key in ["sku101", "sku205", "sku001", "sku067"]:
    print(key, positions(key), maybe_contains(key), key in catalog)

assert not maybe_contains("sku001")  # 遇到2号位的0，可排除
assert maybe_contains("sku067") and "sku067" not in catalog  # 假阳性

# 错误删除反例：不能把某个编号的位直接清零。
saved_bits = bits.copy()
catalog.remove("sku101")
for index in positions("sku101"):
    bits[index] = 0
assert "sku205" in catalog and not maybe_contains("sku205")  # 误清共享位

# 恢复原状态，演示另一个维护场景：新增真实记录后也要更新摘要。
bits[:] = saved_bits
catalog = {"sku101", "sku205", "sku001"}
assert "sku001" in catalog and not maybe_contains("sku001")  # 尚未同步，不能信任排除
add("sku001")
assert maybe_contains("sku001")  # 现在可以继续去真实目录确认
