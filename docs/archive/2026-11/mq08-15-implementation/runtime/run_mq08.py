#!/usr/bin/env python3
"""Run the author's finite application against a real isolated Kafka broker."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, signal, socket, subprocess, time, traceback, uuid

A = Path(__file__).resolve().parent
ROOT = A.parents[4]
HOME_KAFKA = Path('/tmp/mq08-15-runtime/kafka_2.13-4.4.0')
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
Q = A / 'runs' / ('mq08-' + STAMP)
T = Path('/tmp/mq08-15-runtime') / ('mq08-' + STAMP)
Q.mkdir(parents=True)
T.mkdir(parents=True)
CP_LIBS = os.pathsep.join(str(p) for p in sorted((HOME_KAFKA / 'libs').glob('*.jar')))
CLASSES = Q / 'classes'
CLASSES.mkdir()
CP = str(CLASSES) + os.pathsep + CP_LIBS
JVM = ['java', '-Xmx128m', '-Dlog4j.configurationFile=' + str(A / 'client-log4j2.yaml'), '-cp', CP]
assertions = []
commands = []
broker = None
broker_out = None
report = {'kind': 'real-Kafka-4.4.0-application-policy-runtime', 'startedAtUTC': STAMP,
          'runDirectory': str(Q), 'temporaryDataDirectory': str(T), 'pass': False,
          'cases': [], 'assertions': assertions, 'commands': commands,
          'scope': 'Real Kafka storage/group offsets and child-JVM crash/restart around an explicitly simulated handler. No real notification endpoint or distributed exactly-once journal claim.'}

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def check(name, result, detail=None):
    item = {'name': name, 'pass': bool(result), 'detail': detail}
    assertions.append(item)
    print(json.dumps({'assert': name, 'pass': bool(result)}, ensure_ascii=False), flush=True)
    if not result:
        raise AssertionError(item)

def run(cmd, name, timeout=45, accepted=(0,), env=None):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as failure:
        (Q / (name + '.stdout')).write_bytes(failure.stdout or b'')
        (Q / (name + '.stderr')).write_bytes(failure.stderr or b'')
        commands.append({'name': name, 'command': cmd, 'startedAtUTC': started,
                         'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                         'exit': 'timeout', 'timeoutSeconds': timeout,
                         'stdout': name + '.stdout', 'stderr': name + '.stderr'})
        (Q / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        raise
    (Q / (name + '.stdout')).write_bytes(result.stdout)
    (Q / (name + '.stderr')).write_bytes(result.stderr)
    commands.append({'name': name, 'command': cmd, 'startedAtUTC': started,
                     'finishedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     'exit': result.returncode, 'stdout': name + '.stdout', 'stderr': name + '.stderr'})
    (Q / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if result.returncode not in accepted:
        raise AssertionError({'command': name, 'exit': result.returncode,
                              'stderrTail': result.stderr.decode(errors='replace')[-1500:]})
    return result

def obj(stdout):
    return json.loads([line for line in stdout.decode().splitlines() if line.startswith('{')][-1])

def probe(mode, name, topic='', dlq='', group='', *extra):
    args = [mode, report['bootstrap']]
    if topic:
        args += [topic, dlq, group] + list(extra)
    return obj(run(JVM + ['Mq08RuntimeProbe'] + args, name).stdout)

def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def new_case(label, outcomes, dlq_exists=True):
    ident = f'mq08-{label}-{uuid.uuid4().hex[:8]}'
    case = {'name': label, 'topic': ident, 'dlq': ident + '-dlq', 'group': ident + '-group',
            'outcomes': outcomes, 'stateDir': str(T / ident), 'processes': [], 'snapshots': []}
    seed = probe('seed', label + '-seed', case['topic'], case['dlq'], case['group'], str(dlq_exists).lower())
    check(label + ':seed-two-records', [x['offset'] for x in seed['sent']] == [0, 1], seed)
    report['cases'].append(case)
    inspect(case, 'initial', 0, 0 if dlq_exists else None)
    return case

def inspect(case, tag, committed, dlq_count):
    value = probe('inspect', case['name'] + '-' + tag, case['topic'], case['dlq'], case['group'])
    case['snapshots'].append({'tag': tag, 'value': value})
    check(case['name'] + ':' + tag + ':committed', value['committed'] == committed, value['committed'])
    check(case['name'] + ':' + tag + ':original-log-retained', value['logs'][case['topic']]['endOffset'] == 2)
    if dlq_count is None:
        check(case['name'] + ':' + tag + ':dlq-missing', not value['dlqExists'])
    else:
        check(case['name'] + ':' + tag + ':dlq-count', value['logs'][case['dlq']]['endOffset'] == dlq_count)
    return value

def worker(case, hook='none', exit_code=0):
    index = len(case['processes']) + 1
    name = f'{case["name"]}-worker-{index}'
    args = ['--bootstrap', report['bootstrap'], '--topic', case['topic'], '--dlq', case['dlq'],
            '--group', case['group'], '--state-dir', case['stateDir'],
            '--handler-outcomes', case['outcomes'], '--handler-delay-ms', '700',
            '--backoff-ms', '500', '--crash-at', hook, '--max-runtime-ms', '25000']
    result = run(JVM + ['Mq08Worker'] + args, name, timeout=35, accepted=(exit_code,))
    events = [json.loads(line) for line in result.stdout.decode().splitlines() if line.startswith('{')]
    process = {'index': index, 'hook': hook, 'expectedExit': exit_code, 'actualExit': result.returncode,
               'events': events, 'output': name + '.stdout'}
    case['processes'].append(process)
    state = Path(case['stateDir']) / 'journal.properties'
    journal_dest = Q / f'{case["name"]}-journal-after-{index}.properties'
    shutil.copyfile(state, journal_dest)
    process['journalSnapshot'] = journal_dest.name
    process['journalSHA256'] = sha(journal_dest)
    held = [x for x in events if x['event'] == 'record_held']
    check(name + ':only-E01-held', not held or all(x['offset'] == 0 and x['eventId'] == 'E01' for x in held))
    check(name + ':consumer-owner-main', all(x['thread'] == 'main' for x in events if x['event'] in ['poll', 'record_held', 'original_commit', 'original_commit_start']))
    starts = [x['totalStarted'] for x in events if x['event'] == 'attempt_start']
    check(name + ':budget-cap', all(1 <= n <= 3 for n in starts), starts)
    if exit_code == 86:
        check(name + ':actual-halt-hook', any(x['event'] == 'crash_hook' and x['hook'] == hook for x in events))
        probe('wait-empty', name + '-wait-old-member-expiration', case['topic'], case['dlq'], case['group'])
    return events

def evs(case, event):
    return [x for p in case['processes'] for x in p['events'] if x['event'] == event]

def starts(case):
    return [x['totalStarted'] for x in evs(case, 'attempt_start')]

try:
    source = ROOT / 'episodes/message-queue/kafka-retry-dead-letter/production/examples'
    snap = Q / 'source'
    snap.mkdir()
    source_hashes = {}
    for name in ['Mq08Core.java', 'Mq08Worker.java', 'Mq08CoreTest.java', 'README.md', 'run.sh']:
        p = source / name
        source_hashes[name] = sha(p)
        shutil.copyfile(p, snap / name)
    shutil.copyfile(A / 'Mq08RuntimeProbe.java', snap / 'Mq08RuntimeProbe.java')
    check('source-copy-exact', all(sha(source / n) == h == sha(snap / n) for n, h in source_hashes.items()))
    report['authorSourceIdentity'] = source_hashes
    report['runtimeProbeSHA256'] = sha(snap / 'Mq08RuntimeProbe.java')
    compiler = ['java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-proc:none',
                '-source', '17', '-target', '17', '-cp', CP_LIBS, '-d', str(CLASSES)]
    run(compiler + [str(p) for p in sorted(snap.glob('*.java'))], 'compile')
    broker_port, controller_port = port(), port()
    report['bootstrap'] = f'127.0.0.1:{broker_port}'
    report['controllerPort'] = controller_port
    config = Q / 'broker.properties'
    properties = {'process.roles': 'broker,controller', 'node.id': '1',
                  'listeners': f'PLAINTEXT://127.0.0.1:{broker_port},CONTROLLER://127.0.0.1:{controller_port}',
                  'advertised.listeners': f'PLAINTEXT://127.0.0.1:{broker_port}',
                  'controller.listener.names': 'CONTROLLER',
                  'listener.security.protocol.map': 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT',
                  'inter.broker.listener.name': 'PLAINTEXT',
                  'controller.quorum.bootstrap.servers': f'127.0.0.1:{controller_port}',
                  'log.dirs': str(T / 'broker-data'), 'num.partitions': '1',
                  'default.replication.factor': '1', 'min.insync.replicas': '1',
                  'offsets.topic.replication.factor': '1', 'offsets.topic.num.partitions': '1',
                  'transaction.state.log.replication.factor': '1', 'transaction.state.log.min.isr': '1',
                  'auto.create.topics.enable': 'false', 'group.initial.rebalance.delay.ms': '0',
                  'group.min.session.timeout.ms': '1000', 'unclean.leader.election.enable': 'false',
                  'num.network.threads': '2', 'num.io.threads': '2', 'log.cleaner.threads': '1'}
    config.write_text(''.join(k + '=' + v + '\n' for k, v in properties.items()))
    env = dict(os.environ, KAFKA_HEAP_OPTS='-Xms192m -Xmx384m',
               KAFKA_LOG4J_OPTS='-Dlog4j.configurationFile=' + str(A / 'broker-log4j2.yaml'),
               LOG_DIR=str(T / 'tool-logs'))
    cluster = run([str(HOME_KAFKA / 'bin/kafka-storage.sh'), 'random-uuid'], 'cluster-id', env=env).stdout.decode().strip().splitlines()[-1]
    run([str(HOME_KAFKA / 'bin/kafka-storage.sh'), 'format', '-t', cluster, '-c', str(config),
         '--standalone', '--feature', 'eligible.leader.replicas.version=0'], 'format', env=env)
    broker_out = (Q / 'broker.log').open('wb')
    broker = subprocess.Popen([str(HOME_KAFKA / 'bin/kafka-server-start.sh'), str(config)],
                              stdout=broker_out, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    report['brokerPid'] = broker.pid
    deadline = time.monotonic() + 45
    attempt = 0
    while True:
        attempt += 1
        result = run(JVM + ['Mq08RuntimeProbe', 'ready', report['bootstrap']], f'ready-{attempt}', timeout=10, accepted=(0, 1))
        if result.returncode == 0:
            report['brokerActualIdentity'] = obj(result.stdout)
            break
        if time.monotonic() > deadline or broker.poll() is not None:
            raise AssertionError('Broker not ready; preserve startup evidence')
        time.sleep(.2)
    check('actual-Kafka-version', report['brokerActualIdentity']['version'] == '4.4.0')
    check('actual-Kafka-commit', report['brokerActualIdentity']['commit'] == '1156b2752aaa28ea')

    c = new_case('temporary-recovery', 'temporary,temporary,success')
    events = worker(c)
    inspect(c, 'final', 1, 0)
    check('temporary-recovery:three-reservations', starts(c) == [1, 2, 3])
    check('temporary-recovery:no-dlq-send', not evs(c, 'dlq_application_send'))
    check('temporary-recovery:poll-during-backoff', sum(x['event'] == 'poll' and x['paused'] and x['journalPhase'] == 'BACKOFF' for x in events) >= 4)
    check('temporary-recovery:poll-during-handler', sum(x['event'] == 'poll' and x['paused'] and x['journalPhase'] == 'IN_FLIGHT' for x in events) >= 4)
    waiting = None
    for event in events:
        if event['event'] == 'journal_persist' and event['phase'] == 'BACKOFF':
            waiting = event['readyAtMs']
        if event['event'] == 'attempt_start' and waiting is not None:
            actual_ms = datetime.datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')).timestamp() * 1000
            check('temporary-recovery:backoff-due-before-next-start', actual_ms >= waiting, {'readyAtMs': waiting, 'actualStartMs': actual_ms})
            waiting = None

    c = new_case('permanent', 'permanent')
    worker(c)
    inspect(c, 'final', 1, 1)
    check('permanent:one-attempt', starts(c) == [1])
    ordered = [x['event'] for p in c['processes'] for x in p['events']]
    check('permanent:dlq-confirm-before-original-commit', ordered.index('dlq_future_confirm') < ordered.index('original_commit_start') < ordered.index('original_commit'))

    c = new_case('budget-exhausted', 'temporary,temporary,temporary')
    worker(c)
    inspect(c, 'final', 1, 1)
    check('budget-exhausted:exactly-three', starts(c) == [1, 2, 3])
    check('budget-exhausted:reason', evs(c, 'dlq_application_send')[0]['reason'] == 'temporary_budget_exhausted')

    c = new_case('dlq-unavailable', 'permanent', False)
    worker(c, exit_code=1)
    inspect(c, 'failed-dlq', 0, None)
    check('dlq-unavailable:actual-future-failure', len(evs(c, 'dlq_future_failure')) == 1)
    check('dlq-unavailable:no-original-commit', not evs(c, 'original_commit_start'))
    probe('create-dlq', c['name'] + '-repair-create-topic', c['topic'], c['dlq'], c['group'])
    second = worker(c)
    inspect(c, 'after-repair-same-journal', 1, 1)
    check('dlq-unavailable:no-business-retry-after-repair', not any(x['event'] == 'handler_invoked' for x in second))

    c = new_case('restart-budget', 'success')
    for reservation in [1, 2, 3]:
        worker(c, 'after-begin', 86)
        inspect(c, 'after-halt-' + str(reservation), 0, 0)
    fourth = worker(c)
    inspect(c, 'final', 1, 1)
    check('restart-budget:preserved-1-2-3', starts(c) == [1, 2, 3])
    check('restart-budget:no-handler-before-or-after-exhaustion', not evs(c, 'handler_invoked'))
    check('restart-budget:unknown-outcome-reason', evs(c, 'dlq_application_send')[0]['reason'] == 'unknown_outcome_budget_exhausted')

    c = new_case('success-before-journal', 'success')
    worker(c, 'after-handler-success-before-journal', 86)
    inspect(c, 'after-halt', 0, 0)
    worker(c)
    inspect(c, 'final', 1, 0)
    check('success-before-journal:remaining-budget-and-repeat-invocation', starts(c) == [1, 2] and len(evs(c, 'handler_invoked')) == 2)

    c = new_case('dlq-ack-before-journal', 'permanent')
    worker(c, 'after-dlq-ack-before-journal', 86)
    inspect(c, 'after-halt', 0, 1)
    second = worker(c)
    final = inspect(c, 'final', 1, 2)
    records = final['logs'][c['dlq']]['records']
    check('dlq-ack-before-journal:actual-duplicate-content', records[0]['value'] == records[1]['value'])
    check('dlq-ack-before-journal:no-extra-handler', not any(x['event'] == 'handler_invoked' for x in second))

    c = new_case('dlq-journal-before-commit', 'permanent')
    worker(c, 'after-dlq-journal-before-commit', 86)
    inspect(c, 'after-halt', 0, 1)
    second = worker(c)
    inspect(c, 'final', 1, 1)
    check('dlq-journal-before-commit:no-send-or-handler-on-replay', not any(x['event'] in ['dlq_application_send', 'handler_invoked'] for x in second))
    report['pass'] = True
except BaseException as exc:
    report['failure'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    raise
finally:
    cleanup = {'brokerStopped': broker is None, 'temporaryDataRemoved': False}
    if broker is not None:
        try:
            os.killpg(broker.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            broker.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(broker.pid, signal.SIGKILL)
            broker.wait(timeout=10)
        cleanup.update(brokerStopped=broker.poll() is not None, brokerExit=broker.returncode)
    if broker_out is not None:
        broker_out.close()
    if T.exists():
        shutil.rmtree(T)
    cleanup['temporaryDataRemoved'] = not T.exists()
    report['cleanup'] = cleanup
    report['finishedAtUTC'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (Q / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    files = {str(p.relative_to(Q)): sha(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.name != 'files-sha256.json'}
    (Q / 'files-sha256.json').write_text(json.dumps(files, indent=2) + '\n')
print(json.dumps({'pass': report['pass'], 'run': str(Q), 'cases': len(report['cases']), 'assertions': len(assertions), 'cleanup': cleanup}))
