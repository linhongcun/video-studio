import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {C, FONT, MONO} from './theme';
import {Shot, shots} from './data';
import source from '../../model.json';
import {createMiddlewareIdentity} from '../../../_shared/middleware-identity';

declare const __HAS_VOICE_AUDIO__: boolean;
const KafkaMark = createMiddlewareIdentity(React);
const M = source as any;
const state = (id: string) => {
  const s = M.timeline.find((v: any) => v.id === id);
  if (!s) throw new Error(`Missing model snapshot: ${id}`);
  return s;
};
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const tween = (f: number, a: number, b: number) => {
  const t = clamp((f - a) / Math.max(1, b - a));
  return t * t * (3 - 2 * t);
};

const Text: React.FC<{x: number; y: number; w: number; size?: number; color?: string; alpha?: number; align?: 'left' | 'center' | 'right'; mono?: boolean; children: React.ReactNode}> = ({x, y, w, size = 28, color = C.text, alpha = 1, align = 'left', mono = false, children}) => {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (el && alpha > .1 && el.scrollWidth > el.clientWidth + 2) console.error('COPYFIT', el.textContent, el.scrollWidth, el.clientWidth);
  });
  return <div ref={ref} data-text data-copyfit style={{position: 'absolute', left: x, top: y, width: w, fontSize: size, fontWeight: 600, lineHeight: 1.4, fontFamily: mono ? MONO : FONT, whiteSpace: 'nowrap', color, opacity: alpha, textAlign: align}}>{children}</div>;
};
const Box: React.FC<{x: number; y: number; w: number; h: number; color?: string; owner?: string; alpha?: number}> = ({x, y, w, h, color = C.edge, owner, alpha = 1}) => <div data-panel={owner} style={{position: 'absolute', left: x, top: y, width: w, height: h, border: `2px solid ${color}`, background: C.surface, borderRadius: 16, boxSizing: 'border-box', opacity: alpha}} />;
const Foot: React.FC<{children: React.ReactNode; alpha?: number; color?: string}> = ({children, alpha = 1, color = C.orange}) => <Text x={100} y={842} w={1720} size={28} alpha={alpha} color={color} align="center">{children}</Text>;
const Header: React.FC<{title: string; phase?: number; tag?: string; ending?: boolean}> = ({title, phase = 0, tag = 'E01 · 订单7042 · 账户17 · 本次应加10分', ending = false}) => <>
  <Text x={100} y={45} w={540} size={25} color={C.orange}>Kafka · MQ05 · 消费幂等</Text>
  {['为什么重来', '取得资格', '等后重查', '同一事务'].map((s, i) => <Text key={s} x={750 + 190 * i} y={46} w={170} size={23} color={phase === i ? C.orange : C.muted} align="center">{s}</Text>)}
  <Text x={1540} y={45} w={280} size={25} align="right">{ending ? 'IT小村 · 原创' : 'IT小村'}</Text>
  <Text x={100} y={135} w={1720} size={46}>{title}</Text>
  <Text x={100} y={216} w={1720} size={23} color={C.muted}>{tag}</Text>
</>;
const FrameModel: React.FC<{id: string; mode?: string; children: (s: any) => React.ReactNode}> = ({id, mode = 'current', children}) => {
  const s = state(id), db = s.database;
  return <div data-model-state={id} data-view-mode={mode} data-committed-points={db.committed.points} data-effective-marks={db.committed.processed.length} data-attempts={JSON.stringify(db.transactions)} data-index-owner={db.index.uncommittedOwner ?? 'none'} data-index-guard={db.index.shortInternalGuard ?? 'none'} data-kafka-committed={s.kafka.committedNextOffset} data-position={s.kafka.position ?? 'none'} data-log-records={JSON.stringify(s.kafka.records)}>{children(s)}</div>;
};
const Flight: React.FC<{p: number; from: number; to: number; y: number; color?: string; name: string}> = ({p, from, to, y, color = C.orange, name}) => {
  if (p <= 0) return null;
  const d = to > from ? 1 : -1;
  return <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
    <path d={`M${from} ${y}H${to}`} fill="none" stroke={color} strokeWidth={3} strokeOpacity={.7} />
    <polyline points={`${to - 11 * d},${y - 8} ${to},${y} ${to - 11 * d},${y + 8}`} fill="none" stroke={color} strokeWidth={3} />
    {p < 1 && <circle data-moving-body={name} cx={from + (to - from) * p} cy={y} r={9} fill={color} stroke={C.bg} strokeWidth={3} />}
  </svg>;
};
const Reset: React.FC<{children: React.ReactNode}> = ({children}) => <div data-branch-reset>
  <Box x={300} y={420} w={1320} h={255} color={C.blue} />
  <Text x={335} y={453} w={1250} size={35} color={C.blue} align="center">回到共同状态，再改变条件</Text>
  <Text x={335} y={541} w={1250} size={29} align="center">{children}</Text>
</div>;

const Attempt: React.FC<{s: any; name: 'T1' | 'T2'; x: number; query?: boolean}> = ({s, name, x, query = false}) => {
  const t = s.database.transactions[name];
  if (!t) return <div data-attempt={name} data-attempt-status="not-created"><Box x={x} y={341} w={430} h={429} owner={name} /><Text x={x+25} y={363} w={380} size={29} color={C.muted}>T2 · 后续应用重试</Text><Text x={x+25} y={530} w={380} size={32} color={C.muted} align="center">尚未开始</Text></div>;
  const col = name === 'T1' ? C.orange : C.blue;
  const predecessor = t.waitsFor && s.database.transactions[t.waitsFor];
  const status: Record<string, string> = {active: '当前事务尚未提交', waiting: '等待同键事务的结局', committed: '本次事务已经提交', aborted: '本次事务已经回滚'};
  const returning = t.returning === null ? (t.status === 'aborted' ? '已回滚 · 未生效' : '尚未取得结果') : t.returning.length ? 'E01 · 本次新行' : '[ ] · 没有新行';
  const delta = t.status === 'aborted' ? '登记与增量均未生效' : t.pendingDelta ? '本事务暂存 +10' : t.registration === 'skipped-existing' ? (t.status === 'committed' ? '已跳过积分增量' : '应跳过积分增量') : t.updateExecuted ? '已随本事务提交 +10' : t.status === 'committed' && t.registration === 'inserted-new' ? '只提交登记 · 尚未加分' : '尚未执行加分';
  const waiting = s.branch === 'split-transaction' ? (name === 'T1' ? (t.status === 'committed' ? '错误：登记已经单独提交' : '此分支把两个本地事务拆开') : '重试看见旧登记便跳过') : predecessor && predecessor.status !== 'active' ? '前者已结束，等待重新检查' : t.status === 'waiting' ? '等待期间不占索引页锁' : '资格与业务留在同一事务内';
  return <div data-attempt={name} data-attempt-status={t.status} data-returning={JSON.stringify(t.returning)} data-pending-delta={t.pendingDelta}>
    <Box x={x} y={341} w={430} h={429} color={t.status === 'aborted' ? C.muted : col} owner={name} />
    <Text x={x + 25} y={363} w={380} size={29} color={col}>{name} · {name === 'T1' ? '第一' : '第二'}处理尝试</Text>
    <Text x={x + 25} y={420} w={380} size={23} color={C.muted}>{status[t.status]}</Text>
    <Text x={x + 25} y={482} w={380} size={23} color={C.muted}>{query ? '普通查询：处理过E01吗？' : '本次 INSERT 的 RETURNING'}</Text>
    <Text x={x + 25} y={530} w={380} size={query ? 36 : 28} color={t.returning?.length ? col : C.text} align="center">{query ? (t.ordinarySelectSawKey === null ? '查询尚未返回' : t.ordinarySelectSawKey ? '已登记' : '未查到') : returning}</Text>
    <Text x={x + 25} y={625} w={380} size={26} color={t.status === 'aborted' ? C.muted : t.pendingDelta ? col : C.text} align="center">{delta}</Text>
    <Text x={x + 25} y={709} w={380} size={20} color={C.muted} align="center">{query ? '没有查到 ≠ 已认领处理资格' : waiting}</Text>
  </div>;
};
const Database: React.FC<{s: any; showKafka?: boolean}> = ({s, showKafka = false}) => {
  const db = s.database, committed = db.committed;
  return <div data-db-result data-committed-points={committed.points} data-effective-marks={committed.processed.length}>
    <Box x={650} y={341} w={620} h={429} color={C.edge} owner="database-committed" />
    <Text x={677} y={363} w={566} size={29} align="center">PostgreSQL · 公共已提交结果</Text>
    <Text x={679} y={440} w={250} size={25} color={C.orange} align="center">账户17 · 积分</Text>
    <Text x={679} y={492} w={250} size={72} color={C.orange} align="center">{committed.points}</Text>
    <Text x={958} y={440} w={280} size={25} color={C.blue} align="center">有效处理登记</Text>
    <Text x={958} y={492} w={280} size={72} color={C.blue} align="center">{committed.processed.length}</Text>
    <Text x={677} y={610} w={566} size={25} color={committed.processed.length ? C.text : C.muted} align="center">{committed.processed.length ? "键：('points', 'E01')" : '尚无已提交的事件登记'}</Text>
    <Text x={677} y={709} w={566} size={21} color={showKafka ? C.orange : C.muted} align="center">{showKafka ? `Kafka另一步保存恢复位置：${s.kafka.committedNextOffset}` : db.index.shortInternalGuard ? `索引页短写锁：${db.index.shortInternalGuard}` : db.index.uncommittedOwner ? `另有 ${db.index.uncommittedOwner} 的未提交登记，尚未计入` : '未提交修改不计入这里'}</Text>
  </div>;
};
const World: React.FC<{s: any; alpha?: number; query?: boolean; showKafka?: boolean}> = ({s, alpha = 1, query = false, showKafka = false}) => <div style={{opacity: alpha}}>
  <Text x={100} y={289} w={430} size={25}>同一逻辑业务 · 积分</Text>
  <Text x={650} y={289} w={620} size={25} align="center">{query ? 'E01的处理登记' : '同一去重键 · points / E01'}</Text>
  <Text x={1390} y={289} w={430} size={25} align="right">{s.branch === 'split-transaction' ? '前一进程退出后的应用重试' : '重叠的数据库处理尝试'}</Text>
  <Attempt s={s} name="T1" x={100} query={query} /><Database s={s} showKafka={showKafka} /><Attempt s={s} name="T2" x={1390} query={query} />
</div>;
const Ledger: React.FC<{s: any; y?: number}> = ({s, y = 410}) => <>
  <Box x={270} y={y} w={1380} h={300} color={C.orange} />
  <Text x={315} y={y + 25} w={1290} size={30} color={C.orange}>订单积分 · 教学页面</Text>
  <Text x={315} y={y + 93} w={900} size={33}>订单7042　E01　账户17　应加10分</Text>
  <Text x={315} y={y + 175} w={700} size={27} color={C.muted}>当前已提交积分</Text>
  <Text x={1030} y={y + 135} w={530} size={92} color={s.database.committed.points === 20 ? C.danger : C.orange} align="center">{s.database.committed.points}</Text>
</>;

const Scene: React.FC<{shot: Shot}> = ({shot}) => {
  const f = useCurrentFrame(), n = Number(String(shot.id).slice(0, 2)), d = shot.durationInFrames;
  const a = shot.voice?.[0]?.localStart ?? 10, b = shot.voice?.[0]?.localEnd ?? 140;
  const c = shot.voice?.[1]?.localStart ?? 160, e = shot.voice?.[1]?.localEnd ?? d - 25;
  const at = (p: number) => a + (b - a) * p, after = (p: number) => c + (e - c) * p;
  const late = tween(f, c + 8, c + 35);
  if (n === 1) {
    const id = f < at(.68) ? 'business-committed-offset-old' : 'unguarded-twenty';
    return <FrameModel id={id}>{s => <><Header title="已加过10分，重启后为什么成了20？" tag="观察同一E01的两次业务处理，日志里保留一条原记录" /><Ledger s={s} /><Foot alpha={late}>事件可以再来一次；积分能不能再加一次，要由业务判断</Foot></>}</FrameModel>;
  }
  if (n === 2) {
    const committed = at(.55), crashed = c + 15, restored = after(.48), received = e - 15;
    const id = f < committed ? 'record-delivered' : f < crashed ? 'business-committed-offset-old' : f < restored ? 'crashed-before-offset-commit' : f < received ? 'restored-zero' : 'same-record-redelivered';
    return <FrameModel id={id}>{s => <>
      <Header title="数据库成功与Kafka进度，是两个提交" tag="classic · 手动提交 · 单次poll一条 · 初始恢复值0 · 原日志在示例期间保留" />
      <Text x={100} y={289} w={520} size={27}><span style={{display: 'inline-flex', alignItems: 'center', gap: 12}}><KafkaMark kind="kafka" size={32} />Kafka · 保留日志</span></Text>
      <Box x={100} y={341} w={520} h={429} /><Text x={130} y={365} w={460} size={28}>orders / P0 / offset 0</Text><Text x={130} y={448} w={460} size={52} color={C.blue} align="center">E01</Text><Text x={130} y={535} w={460} size={27} align="center">原记录始终只有这一条</Text><Text x={130} y={650} w={460} size={27} color={f >= crashed && f < restored ? C.danger : C.muted} align="center">{f < crashed ? 'C1取得本条，下一读取位置1' : f < restored ? 'C1已退出' : f < received ? 'C2从保存的0恢复' : 'C2再次读到同一E01'}</Text>
      <Box x={700} y={341} w={520} h={429} color={C.orange} /><Text x={730} y={365} w={460} size={30} color={C.orange} align="center">数据库 · 积分提交</Text><Text x={730} y={466} w={460} size={90} color={C.orange} align="center">{s.database.committed.points}</Text><Text x={730} y={650} w={460} size={27} align="center">{f >= committed ? 'DB COMMIT已经成功' : '积分尚未提交'}</Text>
      <Box x={1300} y={341} w={520} h={429} color={C.blue} /><Text x={1330} y={365} w={460} size={30} color={C.blue} align="center">Kafka · 已提交恢复位置</Text><Text x={1330} y={466} w={460} size={90} color={C.blue} align="center">{s.kafka.committedNextOffset}</Text><Text x={1330} y={650} w={460} size={27} align="center">提交下一位置1尚未发生</Text>
      <Flight p={tween(f, a + 8, committed)} from={635} to={685} y={500} name="E01-business-call" />
      <Foot alpha={late}>{f < crashed ? '先提交积分，不会自动替Kafka保存消费进度' : '退出空隙：数据库已是10分，Kafka仍保存旧的0'}</Foot>
    </>}</FrameModel>;
  }
  if (n === 3) {
    const done = at(.62), id = f < done ? 'same-record-redelivered' : 'unguarded-twenty';
    return <FrameModel id={id}>{s => <><Header title={f < done ? '同一E01再次进入积分处理' : '没有资格判断，又提交了一次加分'} /><Ledger s={s} y={345} /><Box x={270} y={682} w={1380} h={110} color={C.blue} /><Text x={305} y={712} w={1310} size={32} align="center">{f < done ? '第一次E01@0：已提交 +10　　第二次E01@0：准备再加分' : '第一次E01@0：已提交 +10　＋　第二次E01@0：已提交 +10'}</Text><Foot alpha={late}>同一条日志记录，被提交了两次业务增量</Foot></>}</FrameModel>;
  }
  if (n === 4) {
    const resetEnd = at(.53), queried = after(.36), id = f < queried ? 'query-reset' : 'both-select-absent';
    return <FrameModel id={id}>{s => <><Header title="先查询，没有查到就能认领吗？" phase={1} tag="独立对照 · 同一业务的两个数据库处理尝试发生重叠" /><World s={s} query alpha={f < resetEnd ? .15 : 1} />{f < resetEnd && <Reset>积分0 · 没有登记 · 两次尝试都处理同一E01</Reset>}<Flight p={f >= c ? tween(f, c + 5, queried) : 0} from={545} to={635} y={510} name="T1-ordinary-query" /><Flight p={f >= c ? tween(f, c + 5, queried) : 0} from={1375} to={1285} y={510} color={C.blue} name="T2-ordinary-query" /><Foot alpha={late}>{f < queried ? "查询仍在进行，尚未取得处理资格" : "查询空结果只是一项观察，没有取得排他处理资格"}</Foot></>}</FrameModel>;
  }
  if (n === 5) {
    const one = at(.25), two = at(.68), mark = after(.3), conflict = after(.68);
    const id = f < one ? 'both-select-absent' : f < two ? 'unsafe-first-award-committed' : f < mark ? 'unsafe-second-award-committed' : f < conflict ? 'unsafe-late-mark' : 'unsafe-conflict-too-late';
    return <FrameModel id={id}>{s => <><Header title="加分先各自提交，补登记已经太迟" phase={1} tag="错误顺序：查询 → 单独提交积分 → 再补处理标记" /><Box x={100} y={341} w={520} h={429} color={C.orange} /><Text x={130} y={365} w={460} size={31} color={C.orange}>T1 · 第一次处理</Text><Text x={130} y={475} w={460} size={34}>{f >= one ? '+10已单独提交' : '准备单独提交+10'}</Text><Text x={130} y={630} w={460} size={27}>{f >= mark ? '后来才补上处理登记' : '处理登记尚未提交'}</Text><Box x={700} y={341} w={520} h={429} /><Text x={730} y={365} w={460} size={31} align="center">公共已提交积分</Text><Text x={730} y={467} w={460} size={95} color={s.database.committed.points === 20 ? C.danger : C.orange} align="center">{s.database.committed.points}</Text><Text x={730} y={650} w={460} size={26} align="center">有效处理登记：{s.database.committed.processed.length}</Text><Box x={1300} y={341} w={520} h={429} color={C.blue} /><Text x={1330} y={365} w={460} size={31} color={C.blue}>T2 · 第二次处理</Text><Text x={1330} y={475} w={460} size={34}>{f >= two ? '+10也已单独提交' : '也准备单独提交+10'}</Text><Text x={1330} y={630} w={460} size={27} color={f >= conflict ? C.danger : C.text}>{f >= conflict ? '补登记冲突，不能倒退旧提交' : '处理登记尚未完成'}</Text><Foot alpha={late}>后来的冲突，不能撤销以前另一个事务已经提交的加分</Foot></>}</FrameModel>;
  }
  if (n === 6) {
    const resetEnd = at(.45), revealed = c + 12;
    return <FrameModel id="safe-reset">{s => <><Header title="同一逻辑业务，同一事件，使用同一键" phase={1} tag="重新从积分0/登记空开始 · 主键两个字段均NOT NULL，立即且不可延迟" /><div style={{opacity: f < resetEnd ? .15 : 1}}><Box x={100} y={374} w={420} h={338} color={C.orange} /><Text x={130} y={410} w={360} size={38} color={C.orange} align="center">T1</Text><Text x={130} y={528} w={360} size={28} align="center">第一处理进程</Text><Box x={640} y={374} w={640} h={338} color={C.blue} /><Text x={670} y={402} w={580} size={30} color={C.blue} align="center">登记表 · 共同唯一键</Text><Text x={675} y={489} w={270} size={25} color={C.muted} align="center">逻辑业务身份</Text><Text x={980} y={489} w={270} size={25} color={C.muted} align="center">事件编号</Text><Text x={675} y={540} w={270} size={42} mono align="center">points</Text><Text x={980} y={540} w={270} size={42} mono align="center">E01</Text><Text x={670} y={638} w={580} size={24} color={C.muted} align="center">进程名称不进入这个键</Text><Box x={1400} y={374} w={420} h={338} color={C.blue} /><Text x={1430} y={410} w={360} size={38} color={C.blue} align="center">T2</Text><Text x={1430} y={528} w={360} size={28} align="center">另一个处理进程</Text></div>{f < resetEnd && <Reset>积分0 · 登记空 · 改用同一个逻辑消费身份</Reset>}<Flight p={f >= revealed ? tween(f, revealed, revealed + 35) : 0} from={540} to={620} y={578} name="T1-same-key" /><Flight p={f >= revealed ? tween(f, revealed, revealed + 35) : 0} from={1380} to={1300} y={578} color={C.blue} name="T2-same-key" /><Foot alpha={late}>换进程或重启，不会给同一个业务事件换一个去重键</Foot></>}</FrameModel>;
  }
  if (n === 7) {
    const guarded = at(.12), inserted = at(.48), awarded = at(.86);
    const id = f < guarded ? 'safe-reset' : f < inserted ? 'index-check-protected' : f < awarded ? 't1-insert-returned' : 't1-award-pending';
    return <FrameModel id={id}>{s => <><Header title="本次插入成功，才放行这次加分" phase={1} tag="T1把登记与积分放在同一本地事务；尚未COMMIT，不计入公共结果" /><World s={s} /><Flight p={tween(f, guarded, inserted)} from={545} to={635} y={540} name="T1-register-key" /><Foot alpha={late}>本事务暂存登记与+10，外部已提交结果仍是0分</Foot></>}</FrameModel>;
  }
  if (n === 8) {
    const locked = at(.12), written = at(.68), back = c, looked = c + 22, waiting = c + 54;
    if (f < back) {
      const id = f < locked ? 'safe-reset' : f < written ? 'index-check-protected' : 't1-insert-returned';
      return <FrameModel id={id} mode="historical-replay">{s => <><Header title="回看刚才T1：检查到写入持续受保护" phase={2} tag="回看已发生的索引短步骤 · 候选索引页短写锁，不是整个业务事务都串行" /><Box x={100} y={360} w={490} h={385} color={C.orange} /><Text x={130} y={397} w={430} size={34} color={C.orange} align="center">同一个键</Text><Text x={130} y={505} w={430} size={39} mono align="center">points / E01</Text><Text x={130} y={642} w={430} size={26} align="center">真正准备写入这个索引</Text><Box x={710} y={360} w={1110} h={385} color={f >= locked && f < written ? C.orange : C.blue} /><Text x={750} y={393} w={1030} size={31} align="center">同键候选页 · 同一把短页写锁</Text><Text x={750} y={485} w={1030} size={44} color={f < written ? C.orange : C.success} align="center">{f < locked ? '准备取得写锁' : f < written ? 'T1持锁：检查 → 写入' : 'T1写入完成，短写锁已释放'}</Text><Text x={750} y={625} w={1030} size={26} color={C.muted} align="center">检查到写入先后进行，后来的同键写入不能跳过检查</Text><Flight p={tween(f, locked, written)} from={610} to={690} y={545} name="historical-index-insert" /><Foot>回看结束后，回到当前仍未提交的T1与准备登记的T2</Foot></>}</FrameModel>;
    }
    const id = f < looked ? 't1-award-pending' : f < waiting ? 't2-ordinary-select-absent' : 't2-waits-for-t1';
    return <FrameModel id={id}>{s => <><Header title="回到当前：同键未决，先等结局再重查" phase={2} tag={f < waiting ? "当前T1尚未提交 · T2准备按同一个键执行冲突检查" : "T1登记与+10尚未提交 · T2在ON CONFLICT预查遇到同键未决事务"} /><World s={s} /><Flight p={f >= looked ? tween(f, looked, waiting) : 0} from={1375} to={1285} y={540} color={C.blue} name="T2-conflict-check" /><Foot alpha={late}>{f < waiting ? "当前T1尚未提交，T2准备按同一个键检查" : "当前等待的是T1的事务结局；T2没有占着索引页写锁"}</Foot></>}</FrameModel>;
  }
  if (n === 9) {
    const committed = at(.45), rechecked = after(.36), id = f < committed ? 't2-waits-for-t1' : f < rechecked ? 't1-committed' : 't2-rechecked-existing';
    return <FrameModel id={id}>{s => <><Header title={f < committed ? '先等T1结束，尚不能决定T2的结果' : 'T1提交后，T2重新检查同一个键'} phase={2} tag="登记与积分同一事务结局；DO NOTHING不会把已有行作为本次新行返回" /><World s={s} /><Flight p={f >= committed ? tween(f, committed + 5, rechecked) : 0} from={1285} to={1375} y={673} color={C.blue} name="T2-wakeup-to-recheck" /><Foot alpha={late}>{f < rechecked ? 'T1已经提交，等待者还要重新检查' : '本次RETURNING为空：没有新登记行，不能无条件加分'}</Foot></>}</FrameModel>;
  }
  if (n === 10) {
    const skipped = at(.42), replayed = after(.24), offset = after(.82);
    const id = f < skipped ? 't2-rechecked-existing' : f < replayed ? 't2-skipped-award' : f < offset ? 'redelivery-skipped' : 'offset-committed-separately';
    return <FrameModel id={id}>{s => <><Header title="返回空就跳过；Kafka进度另一步保存" phase={2} tag="INSERT成功执行，不等于本次插入新行；只按RETURNING结果决定积分增量" /><World s={s} showKafka />{f >= replayed && <div data-redelivery-result={JSON.stringify(s.database.transactions.R.returning)}><Text x={200} y={792} w={1520} size={25} color={C.blue} align="center">同E01再次处理：本次新登记 {s.database.transactions.R.returning.length} 行 → 跳过加分</Text></div>}<Foot alpha={late}>{f < offset ? '同E01重读仍会检查共同键，重复尝试不再增加积分' : '数据库事务先完成，再独立提交Kafka下一恢复位置1'}</Foot></>}</FrameModel>;
  }
  if (n === 11) {
    const resetEnd = at(.7), aborted = after(.3), id = f < aborted ? 'rollback-reset-pending' : 't1-aborted';
    return <FrameModel id={id}>{s => <><Header title="只改T1结局：如果它失败并回滚" phase={3} tag="独立条件对照 · 回到T1两项未提交、T2正在等待、公共积分0的共同状态" /><World s={s} alpha={f < resetEnd ? .15 : 1} />{f < resetEnd && <Reset>T1暂存登记与+10 · T2等待 · 已提交积分0</Reset>}<Foot alpha={late}>{f < aborted ? '这次只改变T1的结局，原先暂存修改还没有成为公共结果' : 'T1两项新结果均未生效，公共结果保持0分'}</Foot></>}</FrameModel>;
  }
  if (n === 12) {
    const inserted = at(.26), awarded = at(.62), committed = c + 18;
    const id = f < inserted ? 't1-aborted' : f < awarded ? 't2-insert-after-abort' : f < committed ? 't2-award-pending' : 't2-committed-after-abort';
    return <FrameModel id={id}>{s => <><Header title={f < committed ? 'T2再检查，取得资格后才加分' : '接手者提交，仍然只有一次有效增量'} phase={3} tag="前一事务已回滚 · 等待者重检 · T2的RETURNING新行才放行T2的+10" /><World s={s} /><Flight p={tween(f, a + 8, inserted)} from={1375} to={1285} y={540} color={C.blue} name="T2-recheck-after-abort" /><Foot alpha={late}>{f < committed ? "接手者正在同一事务暂存登记与+10，公共积分仍0" : "回滚者的修改未生效；接手者同事务提交一份登记和10分"}</Foot></>}</FrameModel>;
  }
  if (n === 13) {
    const resetEnd = at(.4), marked = at(.8), failed = c + 15, skipped = after(.58);
    const id = f < marked ? 'split-reset' : f < failed ? 'mark-only-committed' : f < skipped ? 'failed-after-mark' : 'split-skips-needed-award';
    return <FrameModel id={id}>{s => <><Header title="登记先单独提交，也会把积分漏掉" phase={3} tag="另一个错误顺序 · 从0分/空登记重置 · 先COMMIT登记，之后才准备积分" /><World s={s} alpha={f < resetEnd ? .15 : 1} />{f < resetEnd && <Reset>重新从积分0、没有登记开始；这次拆开两个本地提交</Reset>}<Foot alpha={late} color={C.danger}>{f < failed ? '先提交登记，积分尚未更新' : f < skipped ? '登记已提交后进程退出，留下标记1 / 积分0' : '重试跳过已有登记，原本该加的10分反而漏掉'}</Foot></>}</FrameModel>;
  }
  return <div data-conceptual-recap><Header title="允许事件再来，约束本地业务结果" phase={3} ending tag="回顾正确方案，不把上一错误分支悄悄改成成功现场" />
    <Box x={100} y={359} w={1720} h={419} color={C.blue} />
    <Text x={145} y={382} w={1630} size={30} color={C.blue} align="center">同一个本地数据库事务 · 登记与积分共享结局</Text>
    {[{x: 155, t: '本次新登记成功', b: 'RETURNING有新行', c: C.orange}, {x: 735, t: '才执行积分增量', b: '暂存+10，尚未生效', c: C.blue}, {x: 1315, t: '共同提交或回滚', b: '一起生效 / 都不生效', c: C.success}].map((q, i) => <React.Fragment key={q.x}><Box x={q.x} y={473} w={450} h={223} color={q.c} /><Text x={q.x + 22} y={505} w={406} size={31} color={q.c} align="center">{q.t}</Text><Text x={q.x + 22} y={597} w={406} size={26} align="center">{q.b}</Text>{i < 2 && <svg width={80} height={30} style={{position: 'absolute', left: q.x + 475, top: 565}}><path d="M0 15H70M58 5L70 15L58 25" fill="none" stroke={C.orange} strokeWidth={3} /></svg>}</React.Fragment>)}
    <Foot alpha={late}>同一本地事务约束积分结果，Kafka恢复进度另一步保存</Foot>
  </div>;
};

const View: React.FC<{shot: Shot; captions: boolean}> = ({shot, captions}) => {
  const f = useCurrentFrame();
  const sub = shot.subtitles?.find(s => f >= s.from && f <= (s.to ?? s.from + (s.duration ?? 1) - 1));
  return <AbsoluteFill style={{background: C.bg, color: C.text, fontFamily: FONT, overflow: 'hidden'}}><Scene shot={shot} />{captions && sub && <div data-subtitle style={{position: 'absolute', left: 110, right: 110, top: 925, height: 110, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 37, fontWeight: 600, lineHeight: 1.4, textAlign: 'center', padding: '0 18px', boxSizing: 'border-box', background: `${C.bg}F5`, borderRadius: 14}}>{sub.text}</div>}</AbsoluteFill>;
};
export type MainProps = {showSubtitles?: boolean; hideSubtitles?: boolean};
export const Main: React.FC<MainProps> = ({showSubtitles = true, hideSubtitles = false}) => <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
  {typeof __HAS_VOICE_AUDIO__ !== 'undefined' && __HAS_VOICE_AUDIO__ && <Audio src={staticFile('audio/voice.wav')} />}
  {shots.map(s => <Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><View shot={s} captions={showSubtitles && !hideSubtitles} /></Sequence>)}
</AbsoluteFill>;
