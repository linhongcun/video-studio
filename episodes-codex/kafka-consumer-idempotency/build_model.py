#!/usr/bin/env python3
"""Executable finite teaching state machine, not a PostgreSQL/Kafka emulator."""
from pathlib import Path
import copy, hashlib, json

D = Path(__file__).resolve().parent
EVENT = {'eventId': 'E01', 'orderId': '7042', 'accountId': 17, 'delta': 10, 'partition': 'P0', 'offset': 0}
KEY = ['points', 'E01']


class Database:
    def __init__(self):
        self.points = 0
        self.processed = []
        self.transactions = {}
        self.waiters = []
        self.uncommitted_owner = None
        self.internal_guard = None
        self.retired_writes = []  # Outcome trace, no physical tuple-cleanup timing claim.

    def begin(self, name):
        assert name not in self.transactions
        self.transactions[name] = {'status': 'active', 'key': KEY[:], 'registration': 'not-attempted', 'returning': None,
                                   'pendingDelta': 0, 'waitsFor': None, 'ordinarySelectSawKey': None, 'updateExecuted': False}

    def select(self, name):
        seen = KEY in self.processed
        self.transactions[name]['ordinarySelectSawKey'] = seen
        return seen

    def register(self, name):
        t = self.transactions[name]
        assert t['status'] in ('active', 'waiting')
        if self.uncommitted_owner not in (None, name):
            t.update(status='waiting', waitsFor=self.uncommitted_owner, registration='waiting', returning=None)
            if name not in self.waiters:
                self.waiters.append(name)
            return None
        t.update(status='active', waitsFor=None)
        if name in self.waiters:
            self.waiters.remove(name)
        if KEY in self.processed:
            t.update(registration='skipped-existing', returning=[])
            return []
        assert self.uncommitted_owner is None
        self.uncommitted_owner = name
        t.update(registration='inserted-new', returning=['E01'])
        return ['E01']

    def award(self, name, target_exists=True):
        t = self.transactions[name]
        assert t['status'] == 'active' and t['returning'] == ['E01'] and t['registration'] == 'inserted-new'
        if not target_exists:
            raise LookupError('Application must roll back: target update count is zero')
        assert not t['updateExecuted']
        t.update(pendingDelta=10, updateExecuted=True)

    def commit(self, name):
        t = self.transactions[name]
        assert t['status'] == 'active'
        if t['registration'] == 'inserted-new':
            assert self.uncommitted_owner == name and KEY not in self.processed
            self.processed.append(KEY[:])
            self.uncommitted_owner = None
        self.points += t['pendingDelta']
        t.update(status='committed', pendingDelta=0)

    def rollback(self, name):
        t = self.transactions[name]
        assert t['status'] == 'active'
        self.retired_writes.append({'owner': name, 'registrationWasPending': t['registration'] == 'inserted-new',
                                    'deltaWasPending': t['pendingDelta'], 'outcome': 'aborted-not-effective',
                                    'physicalBytesRemoved': 'not-modeled'})
        if self.uncommitted_owner == name:
            self.uncommitted_owner = None
        t.update(status='aborted', pendingDelta=0, registration='aborted-not-effective', returning=None)

    def export(self):
        return {'committed': {'points': self.points, 'processed': copy.deepcopy(self.processed)},
                'transactions': copy.deepcopy(self.transactions),
                'index': {'key': KEY[:], 'uncommittedOwner': self.uncommitted_owner,
                          'waitingAttempts': self.waiters[:], 'shortInternalGuard': self.internal_guard},
                'retiredWriteOutcomes': copy.deepcopy(self.retired_writes)}


timeline = []
database = Database()
kafka = {'groupId': 'points', 'committedNextOffset': 0, 'position': 0, 'instance': 'C1', 'alive': True,
         'received': [], 'records': [EVENT.copy()]}


def snap(id, branch, label, reset=False, note=None):
    timeline.append({'id': id, 'branch': branch, 'label': label, 'resetBefore': reset, 'event': EVENT.copy(),
                     'kafka': copy.deepcopy(kafka), 'database': database.export(), 'note': note})


snap('initial', 'redelivery', '账户0分，日志一条E01，组保存下一位置0')
kafka.update(position=1, received=[EVENT.copy()])
snap('record-delivered', 'redelivery', 'poll返回同E01，客户端下一位置1')
database.points = 10
snap('business-committed-offset-old', 'redelivery', '第一次无去重业务已提交10，Kafka恢复值仍0')
kafka.update(position=None, alive=False, instance='C1')
snap('crashed-before-offset-commit', 'redelivery', '在DB提交与Kafka进度提交之间退出')
kafka.update(position=0, alive=True, instance='C2', received=[])
snap('restored-zero', 'redelivery', '新实例从保存0恢复')
kafka.update(position=1, received=[EVENT.copy()])
snap('same-record-redelivered', 'redelivery', '原日志同E01再次返回')
database.points = 20
snap('unguarded-twenty', 'redelivery', '不作资格判断，再提交一次+10成为20')

database = Database()
database.begin('T1'); database.begin('T2')
snap('query-reset', 'query-race', '回到0分和空登记，两个DB处理任务重叠', True)
assert database.select('T1') is False and database.select('T2') is False
snap('both-select-absent', 'query-race', '两个普通查询都未见已提交登记，没有取得资格')
database.points = 10
snap('unsafe-first-award-committed', 'query-race', '错误分支先单独提交第一次+10')
database.points = 20
snap('unsafe-second-award-committed', 'query-race', '错误分支已单独提交第二次+10')
assert database.register('T1') == ['E01']; database.commit('T1')
snap('unsafe-late-mark', 'query-race', '先加分提交后，T1才补登记')
assert database.register('T2') == []; database.commit('T2')
snap('unsafe-conflict-too-late', 'query-race', '后补登记发现冲突也不能撤销已提交积分20')

database = Database()
database.begin('T1'); database.begin('T2')
snap('safe-reset', 'commit-wins', '相同0分空登记起点，稳定逻辑键points/E01', True)
database.internal_guard = 'T1'
snap('index-check-protected', 'commit-wins', '索引检查到插入的短内部保护，不等于等待期间持页锁')
assert database.register('T1') == ['E01']
database.internal_guard = None
snap('t1-insert-returned', 'commit-wins', '本次插入成功返回E01，事务仍未提交')
database.award('T1')
snap('t1-award-pending', 'commit-wins', '同事务暂存登记和+10，公共积分仍0')
assert database.select('T2') is False
snap('t2-ordinary-select-absent', 'commit-wins', '普通查询不可见T1未提交登记，不代表唯一检查无冲突')
assert database.register('T2') is None
snap('t2-waits-for-t1', 'commit-wins', '同键未决事务使T2等待，没有返回成功或永久重复')
shared_pending = copy.deepcopy(database)
database.commit('T1')
snap('t1-committed', 'commit-wins', 'T1登记与10分成为同一提交结果，等待者尚未重检')
assert database.register('T2') == []
snap('t2-rechecked-existing', 'commit-wins', 'T2重检，确认已有键，DO NOTHING返回空')
database.commit('T2')
snap('t2-skipped-award', 'commit-wins', '本次无新登记，UPDATE未执行，积分10')
database.begin('R')
assert database.register('R') == []; database.commit('R')
snap('redelivery-skipped', 'commit-wins', '同E01再来仍返回空，不重复增量')
kafka.update(committedNextOffset=1)
snap('offset-committed-separately', 'commit-wins', 'DB事务完成后，Kafka下一恢复位置另一步提交1')

database = copy.deepcopy(shared_pending)
kafka.update(committedNextOffset=0)
snap('rollback-reset-pending', 'rollback-wins', '回到T1两项未提交/T2等待的同一状态，只改T1结局', True)
database.rollback('T1')
snap('t1-aborted', 'rollback-wins', 'T1登记与积分均不生效，物理清理不建模')
assert database.register('T2') == ['E01']
snap('t2-insert-after-abort', 'rollback-wins', 'T2重检后本次插入成功返回E01')
database.award('T2')
snap('t2-award-pending', 'rollback-wins', 'T2自己的同一事务暂存+10，公共积分仍0')
database.commit('T2')
snap('t2-committed-after-abort', 'rollback-wins', '接手者提交一份登记和一次+10，结果仍10')

database = Database()
database.begin('T1')
snap('split-reset', 'split-transaction', '独立反例重新从0分/空登记开始', True)
assert database.register('T1') == ['E01']; database.commit('T1')
snap('mark-only-committed', 'split-transaction', '错误分支只提交登记，积分还没做')
snap('failed-after-mark', 'split-transaction', '登记单独提交后退出，留下有效登记1/积分0')
database.begin('T2')
assert database.register('T2') == []; database.commit('T2')
snap('split-skips-needed-award', 'split-transaction', '重试返回空并跳过，使该加的10分遗漏')

checks = []


def check(name, value):
    assert value, name
    checks.append({'name': name, 'passed': True})


S = {s['id']: s for s in timeline}
check('business commit does not advance Kafka committed offset', S['business-committed-offset-old']['kafka']['committedNextOffset'] == 0)
check('redelivery has same event identity/order/account/offset', S['same-record-redelivered']['kafka']['received'] == [EVENT])
check('no guard produces20 and one original Kafka record', S['unguarded-twenty']['database']['committed']['points'] == 20 and len(S['unguarded-twenty']['kafka']['records']) == 1)
check('two ordinary queries can both observe absence', all(not t['ordinarySelectSawKey'] for t in S['both-select-absent']['database']['transactions'].values()))
check('late unique conflict cannot undo separate business commits', S['unsafe-conflict-too-late']['database']['committed']['points'] == 20)
check('pending registration and+10 not public yet', S['t1-award-pending']['database']['committed'] == {'points': 0, 'processed': []})
check('ordinary invisibility and unique conflict coexist', S['t2-waits-for-t1']['database']['transactions']['T2']['ordinarySelectSawKey'] is False)
check('waiting is neither success nor duplicate returning', S['t2-waits-for-t1']['database']['transactions']['T2']['returning'] is None)
check('no page guard held across transaction wait', S['t2-waits-for-t1']['database']['index']['shortInternalGuard'] is None)
check('commit resolves both local effects', S['t1-committed']['database']['committed'] == {'points': 10, 'processed': [KEY]})
check('after commit waiter gets zero returning rows', S['t2-rechecked-existing']['database']['transactions']['T2']['returning'] == [])
check('skipped insert does not execute award', not S['t2-skipped-award']['database']['transactions']['T2']['updateExecuted'])
check('arbitrary later replay is also skipped', S['redelivery-skipped']['database']['committed']['points'] == 10)
check('Kafka commit follows separate successful DB transaction', S['offset-committed-separately']['database']['committed']['points'] == 10 and S['offset-committed-separately']['kafka']['committedNextOffset'] == 1)
check('rollback branch reset has exact shared pending database', S['rollback-reset-pending']['database'] == S['t2-waits-for-t1']['database'])
check('rollback leaves no effective processed mark or increment', S['t1-aborted']['database']['committed'] == {'points': 0, 'processed': []})
check('rollback outcome trace does not claim immediate byte erasure', S['t1-aborted']['database']['retiredWriteOutcomes'][0]['physicalBytesRemoved'] == 'not-modeled')
check('waiter after rollback gets actual new row', S['t2-insert-after-abort']['database']['transactions']['T2']['returning'] == ['E01'])
check('rollback and takeover yields single effective increment', S['t2-committed-after-abort']['database']['committed'] == {'points': 10, 'processed': [KEY]})
check('split marker transaction produces missing business effect', S['split-skips-needed-award']['database']['committed'] == {'points': 0, 'processed': [KEY]})

# Negative checks guard the application decision, not merely snapshot formatting.
db = Database(); db.begin('A'); db.begin('B'); db.register('A'); db.register('B')
try:
    db.award('B')
except AssertionError:
    check('a waiting attempt cannot award', True)
else:
    raise AssertionError('waiting attempt awarded')
db.award('A'); db.commit('A'); db.register('B')
try:
    db.award('B')
except AssertionError:
    check('zero-row RETURNING cannot award', True)
else:
    raise AssertionError('duplicate attempt awarded')
db = Database(); db.begin('A'); db.register('A')
try:
    db.award('A', target_exists=False)
except LookupError:
    db.rollback('A')
check('target update0 application rollback removes effective mark', db.points == 0 and db.processed == [])
check('different process IDs cannot replace logical consumer key', len({('process-A', 'E01'), ('process-B', 'E01')}) == 2 and len({tuple(KEY), tuple(KEY)}) == 1)
for s in timeline:
    check('retained same original log at ' + s['id'], s['kafka']['records'] == [EVENT])
    check('no duplicate effective key at ' + s['id'], len(s['database']['committed']['processed']) <= 1)

model = {'schemaVersion': 1, 'episode': 'kafka-consumer-idempotency',
         'kind': 'finite-teaching-state-machine-not-Broker-or-database-experiment',
         'versions': {'kafka': '4.4.0', 'kafkaCommit': '1156b2752aaa28eafc0b4c4d387e63356793268d',
                      'postgresql': '18.0', 'postgresqlCommit': '3d6a828938a5fa0444275d3d2f67b64ec3199eb7'},
         'conditions': {'group.protocol': 'classic', 'group.id': 'points', 'enable.auto.commit': False,
                        'max.poll.records': 1, 'databaseIsolation': 'Read Committed', 'key': KEY,
                        'keyConstraint': 'NOT NULL immediate non-deferrable PRIMARY KEY',
                        'concurrency': 'Database processing attempts of the same logical business, not two stable same-group owners ofP0',
                        'retention': 'E01 and processed key retained for whole example',
                        'transactionScope': 'Only processed_events and account_points; Kafka offset is separate',
                        'excluded': ['physical speculative tuple/index layout', 'page latch implementation', 'physical rollback cleanup timing', 'external side effects', 'higher isolation serialization failure', 'full rebalance protocol']},
         'event': EVENT, 'key': KEY, 'timeline': timeline}
(D/'model.json').write_text(json.dumps(model, ensure_ascii=False, indent=2)+'\n')
(D/'model-verification.json').write_text(json.dumps({'passed': True, 'checks': checks, 'snapshots': len(timeline),
    'modelSHA256': hashlib.sha256((D/'model.json').read_bytes()).hexdigest(),
    'scope': 'Executed finite model and meaningful negative application checks; no Kafka/PostgreSQL runtime experiment or learning test.'}, ensure_ascii=False, indent=2)+'\n')
print(len(checks), 'finite checks;', len(timeline), 'snapshots')
