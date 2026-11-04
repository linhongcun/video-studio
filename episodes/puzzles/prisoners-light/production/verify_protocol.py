#!/usr/bin/env python3
"""Build and independently rerun P10's finite protocol model and teaching trace.

The operational state is one shared lamp plus each sender's private sent flag
and the counter's private integer. Pending identity, receipts and visit history
are proof instrumentation: no prisoner can read them. Finite state exploration
does not replace the separate arbitrary-population fairness argument.
"""
from collections import deque
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform


D = Path(__file__).resolve().parent
MAIN_VISITS = [1, 2, 1, 0, 1, 2, 3, 0, 0, 3, 3, 0]


@dataclass(frozen=True)
class State:
    light: bool = False
    sent: int = 0
    count: int = 0
    visited: int = 0
    pending: int | None = None
    received: int = 0
    declared: bool = False
    phantom_receipts: int = 0


def ids(mask):
    return [i for i in range(mask.bit_length()) if mask & (1 << i)]


def packed(s):
    return [s.light, s.sent, s.count, s.visited, s.pending, s.received,
            s.declared, s.phantom_receipts]


def view(s, total):
    return {
        'light': s.light,
        'lightState': 'on' if s.light else 'off',
        'sentIds': ids(s.sent),
        'count': s.count,
        'targetCount': total - 1,
        'declared': s.declared,
        'pendingSenderForAudit': s.pending,
        'receivedIdsForAudit': ids(s.received),
        'visitedIdsForAudit': ids(s.visited),
        'allPeopleActuallyVisitedForAudit': s.visited == (1 << total) - 1,
        'phantomReceiptsForAudit': s.phantom_receipts,
    }


def observation(s, actor):
    if actor == 0:
        return {'actorId': 0, 'role': 'counter', 'observedLight': s.light,
                'privateCountBefore': s.count}
    return {'actorId': actor, 'role': 'sender', 'observedLight': s.light,
            'privateSentOnceBefore': bool(s.sent & (1 << actor))}


def transition(s, actor, total):
    """One actual visit; only the actor's permitted local knowledge is used."""
    assert 0 <= actor < total and total >= 2
    t = replace(s, visited=s.visited | (1 << actor))
    if actor == 0:
        if s.light:
            t = replace(t, light=False, count=s.count + 1, pending=None,
                        received=s.received | ((1 << s.pending) if s.pending is not None else 0),
                        phantom_receipts=s.phantom_receipts + (s.pending is None),
                        declared=s.declared or s.count + 1 == total - 1)
            return t, 'receive_and_increment'
        return t, 'counter_off_noop'
    if s.sent & (1 << actor):
        return t, 'already_sent_noop'
    if s.light:
        return t, 'wait_light_on_keep_eligibility'
    return replace(t, light=True, sent=s.sent | (1 << actor), pending=actor), 'send_once'


def invariants(s, total):
    all_people = (1 << total) - 1
    senders = all_people ^ 1
    pending_mask = (1 << s.pending) if s.pending is not None else 0
    checks = {
        'allIdsWithinPopulation': not ((s.sent | s.visited | s.received | pending_mask) & ~all_people),
        'onlyNonCounterContributes': not ((s.sent | s.received | pending_mask) & 1),
        'lampOnExactlyOnePendingSender': s.light == (s.pending is not None),
        'pendingNotAlreadyReceived': not (pending_mask & s.received),
        'eachSuccessfulSignalEitherReceivedOrPending': s.sent == s.received | pending_mask,
        'successfulSenderActuallyVisited': not (s.sent & ~s.visited),
        'countEqualsDistinctReceivedSenders': s.count == s.received.bit_count(),
        'noPhantomInitialSignal': s.phantom_receipts == 0,
        'countWithinTarget': 0 <= s.count <= total - 1,
        'declarationExactlyAtTarget': s.declared == (s.count == total - 1),
        'declarationRequiresAllSenderSignals': not s.declared or s.sent == senders,
        'declarationRequiresEveryPersonVisited': not s.declared or s.visited == all_people,
    }
    return checks


def assert_valid(s, total):
    failed = [name for name, passed in invariants(s, total).items() if not passed]
    assert not failed, (total, packed(s), failed)


def rank(s):
    return s.visited.bit_count() + s.sent.bit_count() + s.count + s.received.bit_count()


def explore(total):
    """Explore all operational choices and audit visit histories for small N."""
    initial = State()
    seen = {initial}
    queue = deque([initial])
    edges = self_loops = terminal_states = nonterminal_states = 0
    least_missing_actor_count = total
    maximum_count = 0
    digest = hashlib.sha256()
    invariant_checks = 0
    while queue:
        s = queue.popleft()
        assert_valid(s, total)
        invariant_checks += len(invariants(s, total))
        maximum_count = max(maximum_count, s.count)
        self_loop_actors = []
        for actor in range(total):
            t, action = transition(s, actor, total)
            assert_valid(t, total)
            invariant_checks += len(invariants(t, total))
            edges += 1
            # These properties check the state change, independently of the
            # arithmetic audit invariant used to establish distinct receipts.
            assert (t.sent | s.sent) == t.sent
            assert (t.received | s.received) == t.received
            assert (t.visited | s.visited) == t.visited
            assert t.count >= s.count
            if t != s:
                assert rank(t) > rank(s)
            else:
                self_loops += 1
                self_loop_actors.append(actor)
            digest.update((json.dumps([packed(s), actor, action, packed(t)],
                                      separators=(',', ':')) + '\n').encode())
            if t not in seen:
                seen.add(t)
                queue.append(t)
        if s.declared:
            terminal_states += 1
            assert len(self_loop_actors) == total
        else:
            nonterminal_states += 1
            # Every nonterminal state lacks at least one actor-labelled
            # self-loop. Monotone rank excludes multi-state directed cycles;
            # therefore no nonterminal infinite path can visit all actors
            # infinitely often. This is a finite-graph check for this N only.
            missing = total - len(self_loop_actors)
            assert missing >= 1
            least_missing_actor_count = min(least_missing_actor_count, missing)
    assert terminal_states == 1 and maximum_count == total - 1
    return {
        'totalPeople': total,
        'senderCount': total - 1,
        'reachableStates': len(seen),
        'transitions': edges,
        'selfLoopTransitions': self_loops,
        'checkedInvariantInstances': invariant_checks,
        'terminalStates': terminal_states,
        'nonterminalStates': nonterminal_states,
        'maximumCounterValue': maximum_count,
        'everyChangedEdgeStrictlyIncreasesRank': True,
        'allNonterminalStatesLackAFairActorSelfLoop': True,
        'minimumMissingSelfLoopActorCount': least_missing_actor_count,
        'transitionDigestSHA256': digest.hexdigest(),
        'passed': True,
    }


def trace(total, visits, name):
    s = State()
    rows = []
    for number, actor in enumerate(visits, 1):
        assert_valid(s, total)
        t, action = transition(s, actor, total)
        assert_valid(t, total)
        rows.append({
            'id': f'e{number:02d}',
            'visitNumber': number,
            'actorId': actor,
            'actorDisplayName': '计数员' if actor == 0 else f'{actor}号',
            'before': view(s, total),
            'actorLocalObservation': observation(s, actor),
            'action': action,
            'after': view(t, total),
            'newlySent': action == 'send_once',
            'newlyCounted': action == 'receive_and_increment',
            'newlyDeclared': t.declared and not s.declared,
            'countDelta': t.count - s.count,
            'invariantsPassed': True,
        })
        s = t
    return {'id': name, 'totalPeople': total, 'counterId': 0,
            'senderIds': list(range(1, total)), 'targetCount': total - 1,
            'initial': view(State(), total), 'visits': visits, 'steps': rows,
            'final': view(s, total),
            'scope': 'One deterministic finite teaching prefix, not an infinite fair schedule or an optimal-time claim.'}


def bad_first_visit():
    """Wrong rule: spend the only chance at the first visit, even if ON."""
    total = 4
    visits = [1, 2, 0, 2, 3, 0] + [0, 1, 2, 3] * 3
    lamp, count, pending = False, 0, None
    first_visit_spent, sent, visited, receipts = set(), set(), set(), []
    rows = []
    for actor in visits:
        visited.add(actor)
        action = 'noop'
        if actor == 0 and lamp:
            lamp, count = False, count + 1
            receipts.append(pending)
            pending, action = None, 'receive'
        elif actor and actor not in first_visit_spent:
            first_visit_spent.add(actor)
            if not lamp:
                lamp, pending, action = True, actor, 'send'
                sent.add(actor)
            else:
                action = 'wrongly_spend_eligibility_without_sending'
        rows.append({'actorId': actor, 'action': action, 'lightAfter': lamp,
                     'countAfter': count, 'firstVisitSpentIds': sorted(first_visit_spent),
                     'actuallySentIds': sorted(sent)})
    assert visited == set(range(total)) and count == 2
    assert first_visit_spent == {1, 2, 3} and sent == {1, 3} and not lamp
    # The last full repeated round leaves every operational field unchanged;
    # repeating that same round forever visits everybody infinitely often but
    # cannot create the lost 2号 signal.
    assert rows[-1] == rows[-5]
    return {'variant': 'wrong-first-entry-only', 'visits': visits,
            'steps': rows, 'finalCount': count, 'target': total - 1,
            'lostSenderId': 2, 'receipts': receipts,
            'fairInfiniteExtension': {'repeatForever': [0, 1, 2, 3],
                                      'alreadyFixedOperationalState': True},
            'failure': 'First entrance while ON consumes eligibility without sending; all people have visited, but the count stays 2 forever.'}


def bad_repeated_sending():
    lamp = False
    pending = None
    count = 0
    visited, receipts = set(), []
    visits = [1, 0, 1, 0, 1, 0]
    for actor in visits:
        visited.add(actor)
        if actor == 0 and lamp:
            lamp, count = False, count + 1
            receipts.append(pending)
            pending = None
        elif actor and not lamp:
            lamp, pending = True, actor
    assert count == 3 and visited == {0, 1} and receipts == [1, 1, 1]
    return {'variant': 'wrong-resend-after-every-reset', 'totalPeople': 4,
            'visits': visits, 'receipts': receipts, 'finalCount': count,
            'declaresAtTarget': True, 'actuallyVisitedIds': sorted(visited),
            'allPeopleActuallyVisited': False,
            'failure': 'One sender is counted three times, so the declaration is unsafe.'}


def unknown_initial_on():
    # Deliberately violate the specified initial-OFF precondition. This is not
    # a supported correct-protocol start state or an unknown-initial solution.
    s = State(light=True)
    visits = [0, 1, 0, 2, 0]
    rows = []
    for actor in visits:
        s, action = transition(s, actor, 4)
        rows.append({'actorId': actor, 'action': action, 'after': view(s, 4)})
    assert s.declared and s.count == 3 and s.visited == 0b0111
    assert s.phantom_receipts == 1
    assert not invariants(s, 4)['countEqualsDistinctReceivedSenders']
    return {'variant': 'unsupported-initially-on', 'totalPeople': 4,
            'visits': visits, 'steps': rows, 'phantomReceipts': 1,
            'declaredWithoutPerson3Visiting': True,
            'failure': 'The initial ON is mistaken for a contributed signal; the known-OFF assumption is necessary for this exact protocol.'}


def delay_families():
    rows = []
    for length in [0, 1, 17, 1000]:
        s = State()
        for _ in range(length):
            s, _ = transition(s, 0, 4)
            assert_valid(s, 4)
        assert s.count == 0 and not s.declared and not s.light
        after_prefix = view(s, 4)
        for actor in [1, 0, 2, 0, 3, 0]:
            s, _ = transition(s, actor, 4)
            assert_valid(s, 4)
        assert s.declared
        rows.append({'counterOnlyPrefixLength': length,
                     'stateAfterPrefix': after_prefix,
                     'completionSuffix': [1, 0, 2, 0, 3, 0],
                     'declaredAfterSuffix': True,
                     'fairInfiniteTail': {'repeatForever': [0, 1, 2, 3]}})
    return {
        'executedFiniteFixtures': rows,
        'generalArgument': 'For every proposed finite visit bound B, visit counter 0 at least B times first while the lamp is OFF. No signal is collected. Append the finite completion suffix and then repeat all people forever. This is a fair infinite schedule, yet it has not completed by visit B. The quantified argument, not four fixtures alone, rules out a uniform visit bound.',
        'noRandomArrivalOrClockAssumption': True,
    }


def build():
    main = trace(4, MAIN_VISITS, 'main-four-person')
    assert main['final']['declared'] and main['final']['count'] == 3
    assert [s['id'] for s in main['steps'] if s['newlySent']] == ['e01', 'e06', 'e10']
    assert [s['id'] for s in main['steps'] if s['newlyCounted']] == ['e04', 'e08', 'e12']
    assert main['steps'][1]['after']['sentIds'] == [1]
    assert main['steps'][5]['actorLocalObservation']['privateSentOnceBefore'] is False
    hundred_visits = [actor for sender in range(1, 100) for actor in [sender, 0]]
    hundred = trace(100, hundred_visits, 'hundred-person-existence-fixture')
    assert hundred['final']['count'] == 99 and hundred['final']['declared']
    graphs = [explore(total) for total in range(2, 9)]
    negatives = {
        'firstVisitInsteadOfFirstSuccess': bad_first_visit(),
        'repeatedSignalsFromSamePerson': bad_repeated_sending(),
        'unknownInitialLampUnsupported': unknown_initial_on(),
    }
    data = {
        'schemaVersion': 1,
        'episode': 57,
        'episodePart': '趣味推理 P10',
        'slug': 'prisoners-light',
        'rules': {
            'totalPeople': 100, 'counterId': 0, 'senderIds': list(range(1, 100)),
            'initialLamp': 'off', 'oneVisitorAtATime': True,
            'sharedCommunication': ['one persistent binary lamp'],
            'allowedPrivateMemory': {'sender': 'has successfully switched OFF to ON once',
                                     'counter': 'number of ON to OFF receptions'},
            'noOtherMarksOrCommunication': True,
            'targetCount': 99,
            'declarationMoment': 'Immediately after the 99th ON-to-OFF reception by the unique counter.',
            'fairness': 'Every person is selected infinitely often in an infinitely continued schedule.',
            'uniformRandomArrivalRequired': False, 'sharedClockRequired': False,
            'fixedCompletionDeadlineClaimed': False,
        },
        'protocol': {
            'sender': [
                {'if': 'private sentOnce is true', 'then': 'leave the lamp unchanged'},
                {'if': 'private sentOnce is false and observed lamp is ON',
                 'then': 'leave ON and keep sentOnce false'},
                {'if': 'private sentOnce is false and observed lamp is OFF',
                 'then': 'switch ON and set own sentOnce true'},
            ],
            'counter': [
                {'if': 'observed lamp is OFF', 'then': 'leave OFF and do not increment'},
                {'if': 'observed lamp is ON', 'then': 'switch OFF, increment own count by one; declare when count reaches 99'},
            ],
        },
        'actionLabels': {
            'send_once': '首次成功发信：灭→亮，本人的发信资格用完',
            'wait_light_on_keep_eligibility': '灯已亮：不动，仍可在以后成功发信',
            'already_sent_noop': '已经发过：无论灯亮灭都不再开灯',
            'receive_and_increment': '计数员见亮：亮→灭，累计加一',
            'counter_off_noop': '计数员见灭：不动，不加一',
        },
        'visibilityContract': {
            'prisonerCanRead': ['lamp state during own visit', 'own private memory'],
            'teachingAndAuditOnly': ['other people sentIds', 'pendingSenderForAudit',
                                     'receivedIdsForAudit', 'visitedIdsForAudit',
                                     'allPeopleActuallyVisitedForAudit'],
            'notPublicRecords': 'Global arrays and pending attribution are instrumentation for explaining and checking the model; they are not extra marks, communication or information available to the counter.',
            'pendingAttribution': 'The viewer can follow whose successful switch created a pending ON. The counter only sees ON and learns one more distinct sender has contributed, not that sender identity.',
            'sentVsCounted': 'A sender becomes sent immediately on switching ON, while the global count changes only when the counter later switches OFF.',
        },
        'mainExample': main,
        'hundredPersonFixture': hundred,
        'proof': {
            'safetyInvariant': 'Let S be distinct successful senders, R distinct received senders, and P either empty or the unique pending sender. S is the disjoint union of R and P. Lamp ON iff P is nonempty. The counter value is |R|. Every sender can enter S only once; only the counter removes P by switching OFF.',
            'safetyConclusion': 'After count n−1, all n−1 non-counters have successfully signalled and therefore visited. The counter is currently visiting too. Declaring then is safe for every visit prefix consistent with the specified initial state.',
            'inductiveCases': [
                'Initially lamp OFF, S=R=P=empty and count 0.',
                'An unsent person observing OFF adds only self to S and P, switches ON and permanently marks own successful send.',
                'Any non-counter seeing ON, or any already-sent non-counter, changes neither the signal nor count.',
                'The unique counter seeing ON moves the unique P into R, switches OFF and increments exactly once; seeing OFF changes nothing.',
            ],
            'livenessUnderFairness': [
                'If a signal is pending, no sender can erase it, and the counter eventually visits under fairness, receives it and resets OFF.',
                'If OFF while some sender has not sent, such a sender eventually visits under fairness. Either that visit sends, or an earlier unsent visitor has already made the lamp ON and a signal is pending.',
                'Thus while count is below n−1, another distinct reception occurs at a finite later visit. Repeating finitely many times yields n−1 receptions. No common bound on the gaps follows from fairness.',
            ],
            'fairnessScope': 'This is an argument for arbitrary finite n and every schedule satisfying each-person-infinitely-often fairness. Finite fixtures are examples and finite graph checks are limited to their enumerated populations.',
            'noUniformBound': 'An arbitrary finite prefix of counter-only visits while OFF can precede a completion suffix and an infinitely repeated all-person tail; therefore fairness gives eventual completion but no uniform finite visit bound.',
            'noOptimalityClaim': 'The one-signal-per-non-counter protocol is a correct construction. No expected-time or optimal strategy claim is made.',
            'knownInitialOffEssentialForThisProtocol': True,
        },
        'negativeControls': negatives,
        'delayFamilies': delay_families(),
    }
    verification = {
        'passed': True,
        'finiteGraphExplorations': graphs,
        'totalReachableStates': sum(g['reachableStates'] for g in graphs),
        'totalTransitions': sum(g['transitions'] for g in graphs),
        'totalInvariantInstances': sum(g['checkedInvariantInstances'] for g in graphs),
        'mainExampleVisits': len(MAIN_VISITS),
        'mainExampleSuccessfulSignals': 3,
        'mainExampleReceptions': 3,
        'hundredPersonFixtureVisits': len(hundred_visits),
        'hundredPersonFixtureReceptions': 99,
        'negativeControlsDetected': list(negatives),
        'delayFixturePrefixLengths': [0, 1, 17, 1000],
        'scope': 'Complete finite-state reachability and fairness-cycle checks only for total populations 2..8; one explicit 100-person schedule; three deliberately invalid variants and four delay prefixes. Arbitrary-population safety, fairness liveness and unbounded delay are separately stated inductive/quantified arguments, not inferred from random trials.',
    }
    return data, verification


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Create new model and verification files; refuse replacement.')
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    data, result = build()
    payload = canonical(data)
    report = {
        'startedAtUTC': started,
        'endedAtUTC': datetime.now(timezone.utc).isoformat(),
        'engine': platform.python_implementation() + ' ' + platform.python_version(),
        'scriptSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'modelDataSHA256': hashlib.sha256(payload).hexdigest(),
        **result,
    }
    if args.write:
        for name in ['model-data.json', 'model-verification.json']:
            assert not (D / name).exists(), f'Preserve existing evidence: {name}'
        (D / 'model-data.json').write_bytes(payload)
        (D / 'model-verification.json').write_bytes(canonical(report))
    else:
        assert (D / 'model-data.json').read_bytes() == payload, 'Stored model data differs from the actually recomputed model.'
        original = json.loads((D / 'model-verification.json').read_text())
        for key in ['scriptSHA256', 'modelDataSHA256', *result]:
            assert original[key] == report[key], f'Stored verification differs: {key}'
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
