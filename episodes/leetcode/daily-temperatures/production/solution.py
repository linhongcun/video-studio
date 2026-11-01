class Solution:
    def dailyTemperatures(
        self, temperatures: list[int]
    ) -> list[int]:
        answer = [0] * len(temperatures)
        pending = []
        for today, temperature in enumerate(temperatures):
            while pending and temperature > temperatures[pending[-1]]:
                previous = pending.pop()
                answer[previous] = today - previous
            pending.append(today)
        return answer
