class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        targets = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, pre in prerequisites:
            targets[pre].append(course)
            indegree[course] += 1
        queue = [c for c in range(numCourses) if indegree[c] == 0]
        done = 0
        head = 0
        while head < len(queue):
            pre = queue[head]
            head += 1
            done += 1
            for course in targets[pre]:
                indegree[course] -= 1
                if indegree[course] == 0:
                    queue.append(course)
        return done == numCourses
