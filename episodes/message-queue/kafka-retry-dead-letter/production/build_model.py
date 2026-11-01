#!/usr/bin/env python3
"""Finite application teaching model; not Kafka, filesystem, or network emulation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
EVENT = {'eventId': 'E01', 'orderId': 7042, 'topic': 'orders', 'partition': 0, 'offset': 0}
SOURCE_LOG = [EVENT, {'eventId': 'E02', 'orderId': 7043, 'topic': 'orders', 'partition': 0, 'offset': 1}]
MAX = 3
BACKOFF = 400
timeline = []
checks = []


def check(condition, why):
    assert condition, why
    checks.append(why)


def initial():
    return {
        'journal': {'key': {'logicalHandler': 'notify', 'eventId': 'E01'},
                    'phase': 'READY', 'totalStarted': 0, 'maxStarted': MAX,
                    'readyAtMs': 0, 'reason': 'ready', 'dlqMetadata': None,
                    'storage': 'same-machine-retained-state-directory', 'persisted': True},
        'consumer': {'process': 'A', 'active': True, 'paused': True, 'heldEventId': 'E01',
                     'position': 1, 'committedNextOffset': 0, 'pollCount': 1,
                     'sourceCommitState': 'not-requested', 'nextEventReleased': False},
        'source': {'records': deepcopy(SOURCE_LOG), 'retainedInExample': True},
        'clock': {'nowMs': 0},
        'business': {'invocations': 0, 'lastResult': 'not-called', 'knownComplete': False,
                     'earlierOutcomeUnknown': False},
        'dlq': {'records': [], 'applicationSends': 0, 'futureState': 'none',
                'senderObservedResult': 'none', 'metadata': None},
    }


def snapshot(id, s, label, scenario='main', reset_from=None):
    row = {'id': id, 'label': label, 'scenario': scenario, **deepcopy(s)}
    if reset_from:
        row['resetFrom'] = reset_from
    timeline.append(row)
    return row


def reserve(s):
    j = s['journal']
    if j['phase'] not in ('READY', 'BACKOFF') or j['totalStarted'] >= MAX or s['clock']['nowMs'] < j['readyAtMs']:
        raise ValueError('no budget or not due')
    j.update(phase='IN_FLIGHT', totalStarted=j['totalStarted']+1, readyAtMs=0, reason='attempt_reserved')


def invoke(s):
    if s['journal']['phase'] != 'IN_FLIGHT' or not s['journal']['persisted']:
        raise ValueError('reserve durably before invoke')
    s['business']['invocations'] += 1
    s['business']['lastResult'] = 'in-flight'


def classify(s, outcome):
    j = s['journal']
    if j['phase'] != 'IN_FLIGHT':
        raise ValueError('no active reservation')
    s['business']['lastResult'] = outcome
    if outcome == 'success':
        s['business']['knownComplete'] = True
        j.update(phase='BUSINESS_DONE', readyAtMs=0, reason='success')
    elif outcome == 'permanent':
        j.update(phase='DLQ_PENDING', readyAtMs=0, reason='permanent_rejection')
    elif outcome == 'temporary':
        full = j['totalStarted'] >= MAX
        j.update(phase='DLQ_PENDING' if full else 'BACKOFF',
                 readyAtMs=0 if full else s['clock']['nowMs']+BACKOFF,
                 reason='temporary_budget_exhausted' if full else 'temporary_failure')
    else:
        raise ValueError(outcome)


def poll(s, now):
    if not s['consumer']['active'] or now < s['clock']['nowMs']:
        raise ValueError('invalid poll')
    s['clock']['nowMs'] = now
    s['consumer']['pollCount'] += 1


def crash(s):
    s['consumer'].update(active=False, heldEventId=None, position=None)


def restore(s, now):
    s['consumer'].update(process=chr(ord(s['consumer']['process'])+1), active=True, heldEventId=None, position=None, paused=False)
    # Producer Future/current observations belong to the dead process, not the journal.
    s['dlq'].update(futureState='none', senderObservedResult='none', metadata=None)
    s['clock']['nowMs'] = now
    if s['journal']['phase'] == 'IN_FLIGHT':
        s['business'].update(lastResult='unknown-after-crash', earlierOutcomeUnknown=True)


def reacquire(s):
    if s['consumer']['committedNextOffset'] != 0:
        raise ValueError('source event already passed')
    s['consumer'].update(heldEventId='E01', position=1, paused=True)
    s['consumer']['pollCount'] += 1
    # Match Worker.accept: read/verify the original record before recovering its journal.
    j = s['journal']
    if j['phase'] == 'IN_FLIGHT':
        full = j['totalStarted'] >= MAX
        j.update(phase='DLQ_PENDING' if full else 'BACKOFF',
                 readyAtMs=0 if full else s['clock']['nowMs']+BACKOFF,
                 reason='unknown_outcome_budget_exhausted' if full else 'unknown_outcome_after_crash')


def publish(s):
    if s['journal']['phase'] != 'DLQ_PENDING':
        raise ValueError('not pending disposal')
    q = s['dlq']
    q.update(applicationSends=q['applicationSends']+1, futureState='pending',
             senderObservedResult='pending', metadata=None)


def append_dlq(s):
    q = s['dlq']
    if q['futureState'] != 'pending':
        raise ValueError('no send')
    q['records'].append({'eventId': 'E01', 'orderId': 7042, 'partition': 0,
                         'offset': len(q['records']), 'logicalHandler': 'notify',
                         'source': deepcopy(EVENT), 'totalStarted': s['journal']['totalStarted'],
                         'reason': s['journal']['reason'], 'applicationSend': q['applicationSends']})


def ack_dlq(s):
    q = s['dlq']
    r = q['records'][-1]
    q.update(futureState='success', senderObservedResult='confirmed',
             metadata={'topic': 'orders-dlq', 'partition': 0, 'offset': r['offset']})


def remember_dlq(s):
    if s['dlq']['futureState'] != 'success':
        raise ValueError('no successful DLQ result')
    s['journal'].update(phase='DLQ_CONFIRMED', dlqMetadata=deepcopy(s['dlq']['metadata']))


def start_source_commit(s):
    if s['journal']['phase'] not in ('BUSINESS_DONE', 'DLQ_CONFIRMED'):
        raise ValueError('not terminally handled')
    s['consumer']['sourceCommitState'] = 'pending-callback'


def finish_source_commit(s):
    if s['consumer']['sourceCommitState'] != 'pending-callback':
        raise ValueError('no commit request')
    s['consumer'].update(committedNextOffset=1, sourceCommitState='success', paused=False,
                         nextEventReleased=True)
    s['journal']['phase'] = 'COMMITTED'


def must_reject(call, reason):
    try:
        call()
    except ValueError:
        check(True, reason)
    else:
        raise AssertionError(reason)


s = initial()
snapshot('held-ready', s, '应用持有E01，P0暂停，原进度0')
reserve(s); snapshot('first-reserved', s, '第一次预留已保存；此刻尚未调用')
invoke(s); snapshot('first-in-flight', s, '第一次调用进行中')
poll(s, 20); classify(s, 'temporary'); snapshot('first-backoff', s, '临时失败，下次时间420ms')
poll(s, 200); snapshot('before-deadline', s, '未到420ms，仍poll，不调用')
must_reject(lambda: reserve(s), 'deadline前不能预留')
poll(s, 420); snapshot('second-ready', s, '到期且剩余预算2')
reserve(s); snapshot('second-reserved', s, '第二个名额先保存')
invoke(s); snapshot('second-in-flight', s, '第二次业务正在调用')
crash(s); snapshot('crashed-in-flight', s, '进程退出，已占2，业务结果未知')
restore(s, 500); snapshot('restored-two', s, '新进程读回2/IN_FLIGHT，尚待重读核验E01')
reacquire(s); snapshot('reacquired-two', s, '重读核验原E01后按未知恢复/暂停，期限900ms')
poll(s, 800); snapshot('third-before-deadline', s, '还剩1个名额，未到下一时间')
poll(s, 900); common = deepcopy(s)
snapshot('third-ready-common', s, '共同起点：2个名额已用，第三次尚未开始')
reserve(s); snapshot('third-reserved', s, '最后一个名额已保存')
invoke(s); snapshot('third-in-flight', s, '调用原E01，不向源日志重发')
classify(s, 'success'); snapshot('third-success', s, '业务返回成功，原进度仍0')
start_source_commit(s); snapshot('success-source-commit-pending', s, '显式提交P0下一位置1，尚等回调')
finish_source_commit(s); snapshot('success-committed', s, '原提交成功，才resume放行E02')

s = deepcopy(common)
snapshot('exhaust-reset-two', s, '重置共同起点，只改变第三次结果', 'exhausted', 'third-ready-common')
reserve(s); invoke(s); snapshot('exhaust-third-in-flight', s, '最后名额进行中', 'exhausted')
classify(s, 'temporary'); snapshot('budget-exhausted', s, '3已用，不允许第四次调用', 'exhausted')
must_reject(lambda: reserve(s), '3个名额耗尽后不能预留第4次')
exhausted = deepcopy(s)

s = initial(); snapshot('permanent-reset', s, '重新从0个名额开始', 'permanent', 'held-ready')
reserve(s); invoke(s); snapshot('permanent-in-flight', s, '第一次调用', 'permanent')
classify(s, 'permanent'); snapshot('permanent-pending', s, '永久拒绝，直接待处置，未耗满预算', 'permanent')
check(s['journal']['totalStarted'] == 1, '永久拒绝只耗首次名额')

s = deepcopy(exhausted)
snapshot('dlq-envelope', s, '回到耗尽路径，整理身份/原位置/次数/原因', 'dlq', 'budget-exhausted')
publish(s); snapshot('dlq-send-pending', s, '一次应用send，Future尚未完成', 'dlq')
must_reject(lambda: start_source_commit(s), '仅send返回不能提交原进度')
append_dlq(s); snapshot('dlq-appended-unconfirmed', s, 'DLQ已追加，但客户端尚未取得确认', 'dlq')
ack_dlq(s); snapshot('dlq-ack-before-journal', s, '成功metadata已到，本机尚未记住', 'dlq')
remember_dlq(s); snapshot('dlq-confirmed', s, 'DLQ_CONFIRMED已保存，原进度仍0', 'dlq')
confirmed = deepcopy(s)
start_source_commit(s); snapshot('dlq-source-commit-pending', s, '另一独立请求，等待提交成功回调', 'dlq')
finish_source_commit(s); snapshot('dlq-source-committed', s, '原提交成功，E02可交付；不等于业务成功', 'dlq')
check(not s['business']['knownComplete'], '转存+原commit不冒充业务成功')

s = deepcopy(exhausted); snapshot('dlq-fail-reset', s, '只改变目标可用性', 'dlq-failure', 'budget-exhausted')
publish(s); s['dlq'].update(futureState='failed', senderObservedResult='terminal-error')
snapshot('dlq-final-failure', s, '本例目标缺失最终失败，保持pending/原0', 'dlq-failure')
must_reject(lambda: start_source_commit(s), 'DLQ终态失败不能越过原事件')
u = deepcopy(exhausted); publish(u); append_dlq(u)
u['dlq'].update(futureState='failed', senderObservedResult='terminal-error-result-unknown')
snapshot('dlq-error-may-have-record', u, '反例：报错也可能已追加，不据异常断言空日志', 'bounded-counterexample')
check(len(u['dlq']['records']) == 1 and u['consumer']['committedNextOffset'] == 0, '发送错误与服务端有记录可以同时成立')

s = deepcopy(exhausted); snapshot('duplicate-reset', s, '重置发送前，展示确认到本机保存的空隙', 'duplicate-window', 'budget-exhausted')
publish(s); append_dlq(s); ack_dlq(s)
snapshot('duplicate-first-ack', s, 'DLQ@0成功，但journal仍pending', 'duplicate-window')
crash(s); snapshot('duplicate-crashed', s, '未记确认就退出，原commit仍0', 'duplicate-window')
restore(s, 1000); reacquire(s); snapshot('duplicate-restored', s, '同目录pending、重读原E01', 'duplicate-window')
publish(s); snapshot('duplicate-second-send', s, '新进程又一次应用send，同一事件编号', 'duplicate-window')
append_dlq(s); ack_dlq(s); remember_dlq(s)
snapshot('duplicate-second-confirmed', s, 'DLQ同E01两个位置0/1，各自确认', 'duplicate-window')
start_source_commit(s); finish_source_commit(s)
snapshot('duplicate-source-committed', s, '另commit原1，重复窗口没有被幂等producer消除', 'duplicate-window')
check([r['offset'] for r in s['dlq']['records']] == [0, 1], '新应用send允许相同eventId产生两个DLQ offset')
check(s['journal']['totalStarted'] == 3, 'DLQ应用重发没有再调用业务/增加业务预算')
r = next(x for x in timeline if x['id']=='duplicate-restored')
check(r['consumer']['process']=='C' and r['dlq']['futureState']=='none' and r['dlq']['senderObservedResult']=='none' and r['dlq']['metadata'] is None, '重启新session不继承旧producer Future或观察结果')
check(len(r['dlq']['records'])==1 and r['journal']['phase']=='DLQ_PENDING', '新进程不知道旧ACK但物理DLQ和持久pending均保留')

# More constrained local recovery can skip a known acknowledged DLQ send.
t = deepcopy(confirmed); crash(t); restore(t, 1000); reacquire(t)
check(t['journal']['phase'] == 'DLQ_CONFIRMED', 'confirmed已落盘时恢复保留阶段')
start_source_commit(t); finish_source_commit(t)
check(t['dlq']['applicationSends'] == 1, '同目录confirmed恢复只补原commit，不重复send')
q = initial(); reserve(q); crash(q); restore(q, 100)
check(q['business']['invocations'] == 0 and q['journal']['totalStarted'] == 1,
      '保存后未实际调用就崩溃仍消耗一次名额')
must_reject(lambda: invoke(initial()), '未持久预留不能调用业务')
bad = initial(); bad['journal']['persisted'] = False; reserve(bad)
must_reject(lambda: invoke(bad), '状态保存失败时调用门关闭')
for row in timeline:
    check(row['source']['records'] == SOURCE_LOG, f"{row['id']}保留同一源日志两条记录")
    check(0 <= row['journal']['totalStarted'] <= 3, f"{row['id']}预算在0到3内")
    if row['consumer']['committedNextOffset'] == 1:
        check(row['journal']['phase'] == 'COMMITTED', f"{row['id']}原提交后才完成")
    if row['journal']['phase'] == 'DLQ_CONFIRMED':
        check(row['dlq']['futureState'] == 'success', f"{row['id']}本地确认有成功发送依据")
check(next(x for x in timeline if x['id']=='before-deadline')['business']['invocations'] == 1,
      '退避中的持续poll不触发业务重试')
check(next(x for x in timeline if x['id']=='restored-two')['journal']['totalStarted'] == 2,
      '重启不能重新领三个名额')
out = {'schemaVersion': 1, 'kind': 'finite-application-teaching-model-not-broker-experiment',
       'fixedInput': {'event': EVENT, 'sourceLog': SOURCE_LOG, 'logicalHandler': 'notify',
                      'maxReservedStarts': MAX, 'backoffMs': BACKOFF},
       'scope': 'Virtual milliseconds, retained same-machine directory, one record held by one consumer; no real Kafka/filesystem durability assertion.',
       'timeline': timeline}
serialized = json.dumps(out, ensure_ascii=False, indent=2)+'\n'
(D/'model.json').write_text(serialized)
(D/'model-verification.json').write_text(json.dumps({'status':'passed','kind':out['kind'],
    'modelSHA256':hashlib.sha256(serialized.encode()).hexdigest(), 'checks':len(checks),
    'snapshots':len(timeline),'assertions':checks,
    'notClaimed':['Broker execution','filesystem crash durability','real notifications','exactly-once','learning effect']},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'snapshots':len(timeline),'status':'passed'}))
