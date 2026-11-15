"""Deterministic Kahn BFS trace for LC.207 visuals.

Events carry full state snapshots so the animation never reconstructs state:
edge (b->a mapped), count (indegree tallied), enqueue, learn, release
(indegree decrement of one target), blocked (queue empty, courses remain),
result.
"""


def trace(numCourses, prerequisites):
    targets = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    events = []
    for course, pre in prerequisites:
        targets[pre].append(course)
        indegree[course] += 1
        events.append({'kind': 'edge', 'from': pre, 'to': course,
                       'indegrees': list(indegree)})
    events.append({'kind': 'count', 'indegrees': list(indegree),
                   'queue': [], 'done': []})
    queue = []
    done = []
    for c in range(numCourses):
        if indegree[c] == 0:
            queue.append(c)
            events.append({'kind': 'enqueue', 'node': c,
                           'indegrees': list(indegree), 'queue': list(queue),
                           'done': list(done)})
    head = 0
    while head < len(queue):
        pre = queue[head]
        head += 1
        done.append(pre)
        events.append({'kind': 'learn', 'node': pre,
                       'indegrees': list(indegree), 'queue': list(queue[head:]),
                       'done': list(done)})
        for course in targets[pre]:
            indegree[course] -= 1
            entered = indegree[course] == 0
            if entered:
                queue.append(course)
            events.append({'kind': 'release', 'from': pre, 'to': course,
                           'indegrees': list(indegree),
                           'queue': list(queue[head:]), 'done': list(done),
                           'entered': entered})
    remaining = [c for c in range(numCourses) if c not in done]
    if remaining:
        events.append({'kind': 'blocked', 'remaining': remaining,
                       'indegrees': list(indegree), 'queue': [],
                       'done': list(done)})
    result = not remaining
    events.append({'kind': 'result', 'value': result,
                   'indegrees': list(indegree), 'queue': [],
                   'done': list(done), 'remaining': remaining})
    return {'numCourses': numCourses,
            'prerequisites': [list(p) for p in prerequisites],
            'result': result, 'events': events}
