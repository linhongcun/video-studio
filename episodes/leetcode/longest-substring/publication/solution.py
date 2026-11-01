class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        seen = set()
        left = 0
        best = 0

        for right, ch in enumerate(s):
            while ch in seen:
                seen.remove(s[left])
                left += 1
            seen.add(ch)
            best = max(best, right - left + 1)

        return best
