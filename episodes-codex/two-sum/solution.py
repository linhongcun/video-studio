class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}

        for i, x in enumerate(nums):
            need = target - x

            if need in seen:
                return [seen[need], i]

            seen[x] = i

        return []
