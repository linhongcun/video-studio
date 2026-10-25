class Solution:
    def trap(self, height: list[int]) -> int:
        n = len(height)
        left = [0] * n
        right = [0] * n
        highest = 0
        for i in range(n):
            highest = max(highest, height[i])
            left[i] = highest
        highest = 0
        for i in range(n - 1, -1, -1):
            highest = max(highest, height[i])
            right[i] = highest
        total = 0
        for i in range(n):
            level = min(left[i], right[i])
            depth = level - height[i]
            total += depth
        return total
