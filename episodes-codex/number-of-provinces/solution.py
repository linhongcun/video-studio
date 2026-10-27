class Solution:
    def findCircleNum(self, isConnected: list[list[int]]) -> int:
        n = len(isConnected)
        parent = list(range(n))
        size = [1] * n
        count = n
        def find(city):
            while parent[city] != city:
                parent[city] = parent[parent[city]]
                city = parent[city]
            return city
        for a in range(n):
            for b in range(a + 1, n):
                if isConnected[a][b] == 0:
                    continue
                ra, rb = find(a), find(b)
                if ra == rb:
                    continue
                if size[ra] < size[rb]:
                    ra, rb = rb, ra
                parent[rb] = ra
                size[ra] += size[rb]
                count -= 1
        return count
