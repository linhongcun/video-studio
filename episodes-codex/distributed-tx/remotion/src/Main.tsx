import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {C, FONT, MONO} from './theme';
import {Shot, VIDEO, shots} from './data';
import {Chip, Ledger, Line, LocalBoundary, MovingChip, RuleLine, SmallLabel,
  StageDots, Txt, ease, lerp, clamp} from './overview-primitives';
import {BusinessScene} from './overview-business';
declare const __HAS_VOICE_AUDIO__: boolean;

const cue = (s: Shot, label: string) => Number(s.cueFrames?.labels?.[label] ?? 1);
const at = (s: Shot, sentence: number, part: number) => {
  const ss = s.cueFrames?.sentences ?? [9, s.durationInFrames / 2];
  const a = Number(ss[sentence] ?? 0);
  const b = Number(ss[sentence + 1] ?? s.durationInFrames - 15);
  return Math.round(a + (b - a) * part);
};
const phase = (s: Shot, f: number, sentence: number, a = .08, b = .66) =>
  ease(f, at(s, sentence, a), at(s, sentence, b) - at(s, sentence, a));
const reset = (text = '另一种方案 · 重新演示') =>
  <Txt x={130} y={152} size={22} color={C.muted}>{text}</Txt>;
const title = (text: string, color: string = C.text, alpha = 1) =>
  <Txt x={130} y={197} size={44} color={color} alpha={alpha}>{text}</Txt>;
const term = (s: Shot, f: number, key: string, text: string, color = C.teal) =>
  title(text, color, f >= cue(s, key) ? 1 : 0);
const coordinator = (state: string, color = C.gold, alpha = 1) => <>
  <Txt x={960} y={293} center size={23} color={C.muted} alpha={alpha}>协调者 · 持久记录</Txt>
  <Chip x={960} y={335} width={360} color={color} alpha={alpha}>{state}</Chip>
</>;
const stock = (value: React.ReactNode, state: string, color: string = C.text,
  detail?: string, x = 1430, y = 425, alpha = 1) =>
  <Ledger label="库存库 · 商品7042" value={value} state={state} detail={detail}
    x={x} y={y} color={color} alpha={alpha}/>;
const order = (state: string, color = C.gold, detail?: string, x = 490, y = 425, alpha = 1) =>
  <Ledger label="订单库 · 本单记录" value="8124" state={state} detail={detail}
    x={x} y={y} color={color} valueSize={82} alpha={alpha}/>;
const globalPending = (text = '全局仍待定', alpha = 1) =>
  <Chip x={960} y={689} color={C.gold} width={360} alpha={alpha} size={25}>{text}</Chip>;

const IntroScene: React.FC<{shot: Shot; f: number}> = ({shot: s, f}) => {
  const type = s.visualType;
  if (type === 'hook') {
    const p = phase(s, f, 0, .02, .35), failed = f >= at(s, 0, .62);
    return <>
      {title('库存扣了，支付却失败？')}
      <Txt x={130} y={267} size={25} color={C.gold}>订单8124 · 整单仍待确认</Txt>
      {stock(p === 1 ? 3 : 4, p === 1 ? '本次已扣 1 件' : '准备扣 1 件', C.teal, undefined, 520, 368)}
      <Line x1={790} y1={526} x2={1120} y2={526} p={phase(s, f, 0, .3, .6)} color={failed ? C.red : C.gold}/>
      <Ledger label="支付服务" value="200" state={failed ? '支付失败' : '付款请求'}
        detail="两个系统，各自处理" x={1410} y={368} color={failed ? C.red : C.gold}/>
      {f >= cue(s, '分布式事务') && <RuleLine color={C.teal}>分布式事务：跨系统协作，要选哪条路线？</RuleLine>}
    </>;
  }
  if (type === 'local-boundary') {
    const localDone = f >= at(s, 0, .55), outside = phase(s, f, 1, .02, .27);
    return <>
      {title('本地事务，有自己的边界')}
      <LocalBoundary x={180} y={335} w={830} h={400} p={phase(s, f, 0)} color={localDone ? C.teal : C.gold}/>
      {order(localDone ? '订单已提交' : '订单待提交', localDone ? C.teal : C.gold, undefined, 465, 382)}
      <Chip x={792} y={489} width={290} color={localDone ? C.teal : C.gold}>操作流水 {localDone ? '已提交' : '待提交'}</Chip>
      {stock(4, '独立的事务', C.text, '这笔事务不会自动覆盖它', 1435, 382, outside)}
      <Line x1={1040} y1={530} x2={1170} y2={530} color={C.red} p={outside}/>
      <RuleLine alpha={outside}>同库的共同提交，不能直接扩展成跨系统共同提交</RuleLine>
    </>;
  }
  const a = phase(s, f, 0, .05, .35), b = phase(s, f, 0, .38, .68), c = phase(s, f, 1, .03, .35);
  return <>
    {title('逐章看五条常见工程路线')}
    <Txt x={290} y={375} size={108} mono color={C.teal}>01—05</Txt>
    <Txt x={300} y={548} size={28} color={C.muted}>不同层次的机制，放进同一张工程地图</Txt>
    <Chip x={1270} y={349} width={500} alpha={a}>先看：怎么执行</Chip>
    <Chip x={1270} y={467} width={500} alpha={b}>再看：失败怎么办</Chip>
    <Chip x={1270} y={585} width={500} alpha={c}>最后：适用条件和代价</Chip>
    <RuleLine alpha={c}>每章都回答同样的问题，再比较边界</RuleLine>
  </>;
};

const XaScene: React.FC<{shot: Shot; f: number}> = ({shot: s, f}) => {
  const type = s.visualType;
  if (type === 'xa-intro') {
    const p = phase(s, f, 0, .25, .82);
    return <>
      {reset()}{term(s, f, '两阶段提交', '2PC · 两阶段提交：先准备，再决定')}
      <Line x1={960} y1={397} x2={490} y2={440} p={p}/>
      <Line x1={960} y1={397} x2={1430} y2={440} p={clamp(p * 1.6 - .6)}/>
      {coordinator('询问：能否提交？')}{order('本次新示例 · 待修改')}{stock(4, '本次新示例 · 未扣减')}
      <RuleLine color={C.teal} alpha={f >= cue(s, 'XA') ? 1 : 0}>XA 是资源协作接口；2PC 是先准备、再决定的过程</RuleLine>
    </>;
  }
  if (type === 'xa-prepare') {
    const o = f >= at(s, 0, .25), k = f >= at(s, 0, .57), held = phase(s, f, 1, .03, .35);
    return <>
      {title('准备好了，仍然尚未提交')}
      {coordinator(k ? '已收到：可提交' : '正在收集准备响应')}
      <Line x1={500} y1={421} x2={830} y2={405} p={o ? 1 : 0} color={C.gold}/>
      <Line x1={1420} y1={421} x2={1090} y2={405} p={k ? 1 : 0} color={C.gold}/>
      {order(o ? '准备成功 · 待决定' : '待执行修改', C.gold)}
      {stock(4, '已确认值仍是 4', C.text, k ? '待提交修改：3' : undefined)}
      <Chip x={490} y={728} width={350} alpha={held}>数据库资源仍占用</Chip>
      <Chip x={1430} y={728} width={350} alpha={held}>数据库资源仍占用</Chip>
      <RuleLine>准备成功 ≠ 已提交；不能把待定修改画成最终结果</RuleLine>
    </>;
  }
  if (type === 'xa-commit') {
    const decided = f >= at(s, 0, .62), p1 = phase(s, f, 1, .03, .34), p2 = phase(s, f, 1, .32, .7);
    const od = p1 === 1, sd = p2 === 1;
    return <>
      {title('唯一决定，分别送达')}
      <Line x1={900} y1={402} x2={490} y2={426} p={p1} color={C.teal}/>
      <Line x1={1020} y1={402} x2={1430} y2={426} p={p2} color={C.teal}/>
      {coordinator(decided ? '提交决定 · 已持久化' : '准备响应已收齐', decided ? C.teal : C.gold)}
      {order(od ? '订单已提交' : '已准备 · 等待决定', od ? C.teal : C.gold)}
      {stock(sd ? 3 : 4, sd ? '库存已提交' : '已准备 · 等待决定', sd ? C.teal : C.gold,
        sd ? '本次扣减 1 件' : '待提交修改：3')}
      <RuleLine color={sd ? C.teal : C.muted}>遵循同一终局决定，执行与回复可以先后完成</RuleLine>
    </>;
  }
  if (type === 'xa-abort') {
    const refused = f >= at(s, 0, .28), decision = f >= at(s, 0, .65), undone = f >= at(s, 1, .45);
    return <>
      {reset('另一种结果 · 准备失败例')}{title('一方准备失败，决定回滚')}
      {coordinator(decision ? '回滚决定 · 已记录' : '尚未作提交决定', decision ? C.red : C.gold)}
      {order(undone ? '待提交修改已撤销' : '已准备 · 待提交', undone ? C.text : C.gold)}
      {stock(4, refused ? '拒绝准备' : '检查资源', refused ? C.red : C.gold, '已确认库存始终没有改变')}
      <Line x1={1430} y1={420} x2={1100} y2={405} p={refused ? 1 : 0} color={C.red}/>
      <RuleLine color={undone ? C.teal : C.muted}>撤销尚未提交的修改，保留原确认结果</RuleLine>
    </>;
  }
  const disconnected = phase(s, f, 0, .07, .4), points = phase(s, f, 1, .02, .45);
  return <>
    {reset('故障分支 · 已准备，终局决定未知')}{title('准备之后失联，不能自行猜结果')}
    <Line x1={960} y1={402} x2={490} y2={425} color={C.red} alpha={1 - disconnected}/>
    <Line x1={960} y1={402} x2={1430} y2={425} color={C.red} alpha={1 - disconnected}/>
    {coordinator('连接中断 · 待恢复决定', C.red)}
    {order('已准备 · 仍在等待', C.gold, '资源仍占用')}
    {stock(4, '已准备 · 仍在等待', C.gold, '待提交3；资源仍占用')}
    <RuleLine alpha={points}>支持 XA 的资源 · 事务宜短 · 等待与持锁是代价</RuleLine>
  </>;
};

const AtScene: React.FC<{shot: Shot; f: number}> = ({shot: s, f}) => {
  const type = s.visualType;
  if (type === 'at-intro') {
    const p = phase(s, f, 1, .05, .6);
    return <>
      {reset()}{term(s, f, 'AT', 'AT 模式 · 框架代理数据库操作')}
      <LocalBoundary x={360} y={347} w={1200} h={395} p={p}/>
      {stock(4, '将产生本次修改', C.text, undefined, 690, 407)}
      <Chip x={1250} y={469} width={400} alpha={p}>撤销记录：4 → 3</Chip>
      <SmallLabel x={1250} y={566} alpha={p}>本章以 Seata AT 机制为例</SmallLabel>
      <RuleLine alpha={p}>业务修改 + 撤销记录，放进同一笔本地事务</RuleLine>
    </>;
  }
  if (type === 'at-success') {
    const committed = f >= at(s, 0, .27), complete = f >= at(s, 1, .6), clear = phase(s, f, 1, .62, .85);
    return <>
      {title('本地先提交，全局后结束')}
      {stock(committed ? 3 : 4, committed ? '本地已提交' : '本地待提交', committed ? C.teal : C.gold, undefined, 650, 363)}
      <Chip x={1270} y={418} width={430} alpha={1 - clear} color={committed ? C.teal : C.gold}>撤销记录：4 → 3</Chip>
      <Chip x={1270} y={531} width={430} color={complete ? C.teal : C.gold}>{complete ? '全局成功 · 释放写锁' : '全局待定 · 写冲突受控'}</Chip>
      <SmallLabel x={650} y={664} color={C.teal} alpha={committed ? 1 : 0}>本地锁已释放</SmallLabel>
      <RuleLine color={complete ? C.teal : C.muted}>提前释放本地锁，不等于全局事务已经完成</RuleLine>
    </>;
  }
  if (type === 'at-failure') {
    const fail = phase(s, f, 0, .05, .5), checked = f >= at(s, 1, .28), restored = f >= at(s, 1, .62);
    return <>
      {reset('另一种结果 · 全局失败例')}{title('已本地提交，再校验并恢复')}
      {stock(restored ? 4 : 3, restored ? '恢复操作已完成' : '本地已经提交', restored ? C.teal : C.gold,
        restored ? '根据撤销记录恢复' : '这不是未提交的修改', 610, 358)}
      <Chip x={1280} y={362} width={470} color={C.red} alpha={fail}>另一项操作失败</Chip>
      <Chip x={1280} y={470} width={470} color={checked ? C.teal : C.gold}>{restored ? '校验通过 · 已恢复 3 → 4' : '校验：当前值 3 / 记录 4 → 3'}</Chip>
      <Line x1={1110} y1={602} x2={845} y2={602} p={phase(s, f, 1, .28, .62)} color={C.teal}/>
      <SmallLabel x={1280} y={599} color={checked ? C.teal : C.muted}>{checked ? '校验通过，按记录恢复' : '先校验，不能盲目覆盖'}</SmallLabel>
      <RuleLine>已提交的数据通过受控恢复操作改回；外部副作用不在这里自动撤销</RuleLine>
    </>;
  }
  if (type === 'at-isolation') {
    const read = phase(s, f, 0, .08, .61), received = read === 1;
    return <>
      {reset('回看本地已提交、全局尚未结束的期间')}{title('普通读，可能看到中间值')}
      {stock(3, '本地已提交', C.teal, '全局仍待定', 610, 355)}
      <Line x1={1110} y1={519} x2={880} y2={519} p={read} color={C.blue}/>
      <Ledger label="另一个普通查询" value={received ? '3' : '?'} state={received ? '已经读到中间值' : '发起读取'}
        x={1370} y={355} color={C.blue}/>
      <Chip x={610} y={683} width={400}>本地提交 ≠ 全局完成</Chip>
      <RuleLine alpha={phase(s, f, 1, .05, .45)}>更强读隔离，需要满足框架的代理与接入要求</RuleLine>
    </>;
  }
  const external = phase(s, f, 1, .03, .55);
  return <>
    {title('自动撤销，有明确的操作范围')}
    <LocalBoundary x={220} y={350} w={800} h={385} p={1} label="框架支持、受代理的数据操作" color={C.teal}/>
    {stock(3, '支持的数据库 / SQL', C.teal, '业务修改和撤销记录', 620, 412)}
    <Ledger label="边界之外" value="外部调用" state="必须另行设计恢复方式" x={1440} y={412}
      mono={false} valueSize={57} color={C.red} alpha={external}/>
    <RuleLine alpha={external}>一条数据库撤销记录，不能自动撤销任意外部动作</RuleLine>
  </>;
};

const MessageScene: React.FC<{shot: Shot; f: number}> = ({shot: s, f}) => {
  const type = s.visualType;
  if (type === 'message-intro') {
    const done = f >= at(s, 0, .4), progress = phase(s, f, 1, .06, .65);
    return <>
      {reset()}{term(s, f, '可靠消息', '可靠消息 · 允许异步推进')}
      {order(done ? '本地已记录' : '本地待提交', done ? C.teal : C.gold, '整单仍待确认', 490, 367)}
      {stock(4, '下游还未处理', C.gold, undefined, 1430, 367)}
      <Line x1={520} y1={695} x2={1420} y2={695} color={C.edge}/>
      <div style={{position: 'absolute', left: lerp(520, 960, progress) - 8, top: 687,
        width: 16, height: 16, borderRadius: 8, background: C.gold}}/>
      <SmallLabel x={520} y={730}>先完成本地事务</SmallLabel><SmallLabel x={1420} y={730}>再处理下游</SmallLabel>
      <RuleLine alpha={progress}>允许暂时没对上，同时保留能恢复、能追踪的处理进度</RuleLine>
    </>;
  }
  if (type === 'outbox-record') {
    const event = phase(s, f, 0, .25, .7), done = f >= at(s, 1, .6);
    return <>
      {term(s, f, 'Outbox', 'Outbox · 订单和待发事件共同落盘')}
      <LocalBoundary x={190} y={343} w={1040} h={410} p={phase(s, f, 0, .02, .38)} color={done ? C.teal : C.gold}/>
      {order(done ? '订单已提交' : '订单待提交', done ? C.teal : C.gold, undefined, 470, 400)}
      <Chip x={965} y={476} width={380} alpha={event} color={done ? C.teal : C.gold}>E8124 · {done ? '待发事件已提交' : '待发事件待提交'}</Chip>
      {stock(4, '边界外 · 尚未处理', C.muted, undefined, 1575, 400, .62)}
      <RuleLine color={done ? C.teal : C.muted}>原子范围：订单 + 同库待发记录；不包含库存库</RuleLine>
    </>;
  }
  if (type === 'outbox-send') {
    const first = phase(s, f, 0, .12, .7), fail = phase(s, f, 1, .02, .18), retry = phase(s, f, 1, .3, .8);
    return <>
      {title('发送可以失败，持久待办继续保留')}
      <Chip x={440} y={388} width={500} color={C.teal}>订单库 · 已保存 E8124</Chip>
      <Txt x={440} y={503} center size={26} color={C.muted}>发送实例由这份待办读出</Txt>
      <Ledger label="消息队列" value="E8124" state={retry === 1 ? '再次发送后到达' : '等待接收'}
        x={1460} y={345} valueSize={66} color={retry === 1 ? C.teal : C.text}/>
      <Line x1={725} y1={624} x2={1230} y2={624} p={first} color={fail ? C.red : C.blue}/>
      <MovingChip x1={725} y1={588} x2={1040} y2={588} p={first}
        alpha={1 - fail} color={C.gold} width={300}>E8124 · 首次发送</MovingChip>
      <MovingChip x1={725} y1={675} x2={1230} y2={675} p={retry}
        alpha={ease(f, at(s, 1, .3), 15)} color={C.blue} width={300}>E8124 · 重试</MovingChip>
      <RuleLine>重试仍使用同一事件标识，不提前删掉唯一的可恢复待办</RuleLine>
    </>;
  }
  if (type === 'outbox-consume') {
    const p = phase(s, f, 0, .1, .6), done = p === 1, repeat = phase(s, f, 1, .02, .48);
    return <>
      {title('消费端：库存和处理标记共同提交')}
      <LocalBoundary x={650} y={335} w={1030} h={420} color={done ? C.teal : C.gold}/>
      {stock(done ? 3 : 4, done ? '库存扣减已提交' : '待扣减 1 件', done ? C.teal : C.gold, undefined, 1170, 367)}
      <Chip x={1170} y={669} width={500} color={done ? C.teal : C.gold}>
        {done ? '已处理 E8124 · 同时提交' : '处理标记 E8124 · 待提交'}
      </Chip>
      <MovingChip x1={300} y1={447} x2={480} y2={447} p={repeat}
        alpha={phase(s, f, 1, 0, .08) * (1 - phase(s, f, 1, .6, .8))} color={C.blue} width={300}>
        E8124 · 重复到达
      </MovingChip>
      <SmallLabel x={350} y={574} color={C.teal} alpha={repeat}>查到已处理，返回原结果</SmallLabel>
      <RuleLine color={done ? C.teal : C.muted}>唯一处理键 + 库存修改，同一本地事务；重复后仍为 3</RuleLine>
    </>;
  }
  if (type === 'outbox-limit') {
    const arrived = phase(s, f, 0, .03, .4), handling = phase(s, f, 1, .03, .6);
    return <>
      {reset('另一种结果 · 缺货失败例，库存重置为 0')}{title('送到了，不等于业务已经成功')}
      <Chip x={500} y={397} width={500} color={C.teal} alpha={arrived}>E8124 · 消息已送达</Chip>
      {stock(0, '库存不足 · 不能扣减', C.red, '整单仍需失败处理', 1400, 350)}
      <Chip x={500} y={531} width={500} color={C.gold} alpha={handling}>取消 / 补偿 / 告警 / 人工</Chip>
      <RuleLine alpha={handling}>永久失败和业务拒绝，需要明确收尾；等待不会自动增加库存</RuleLine>
    </>;
  }
  if (type === 'tx-message-intro') {
    const saved = f >= at(s, 0, .4), local = phase(s, f, 1, .08, .67);
    return <>
      {reset('另一种发布机制 · 此处没有 Outbox 表')}
      {term(s, f, 'RocketMQ事务消息', 'RocketMQ事务消息 · 先存半消息')}
      <Ledger label="消息系统中的持久记录" value="E8124" valueSize={76}
        state={saved ? '半消息 · 暂不可消费' : '准备保存消息'} color={C.gold} x={560} y={345}/>
      <Ledger label="生产者 · 订单数据库" value="8124" valueSize={80}
        state={local === 1 ? '本地事务已提交' : '随后执行本地事务'}
        color={local === 1 ? C.teal : C.muted} x={1400} y={345} alpha={saved ? 1 : .35}/>
      <Line x1={840} y1={635} x2={1120} y2={635} p={local} color={C.blue}/>
      <RuleLine>先存半消息，再执行本地事务；此时不向消费端投递</RuleLine>
    </>;
  }
  if (type === 'tx-message-check') {
    const check = phase(s, f, 1, .24, .68), checked = check === 1;
    const success = phase(s, f, 0, .02, .24), failure = phase(s, f, 0, .4, .68), unknown = phase(s, f, 1, .02, .24);
    return <>
      {title('是否可投递，按本地事务结果决定')}
      <Chip x={460} y={352} width={480} color={C.teal} alpha={success}>本地成功 → 开放消息</Chip>
      <Chip x={460} y={465} width={480} color={C.red} alpha={failure}>本地失败 → 丢弃消息</Chip>
      <Chip x={460} y={578} width={480} color={C.gold} alpha={unknown}>结果未知 → 发起回查</Chip>
      <Line x1={760} y1={615} x2={1110} y2={615} p={check} color={C.blue}/>
      <Ledger label="回查生产者的持久业务状态" value={checked ? '已提交' : '?'} mono={false} valueSize={65}
        state={checked ? '据此报告本地结果' : '不是重新执行业务操作'}
        x={1390} y={378} color={checked ? C.teal : C.blue} alpha={unknown}/>
      <RuleLine alpha={ease(f, at(s, 1, .05), 25)}>回查的是生产端本地结果，不是下游库存有没有扣完</RuleLine>
    </>;
  }
  const consumed = phase(s, f, 1, .15, .55);
  return <>
    {title('生产端的保证，不会自动扩成跨库提交')}
    <LocalBoundary x={150} y={335} w={730} h={405} label="生产端本地事务" color={C.teal}/>
    {order('本地提交结果', C.teal, undefined, 500, 383)}
    <Line x1={910} y1={507} x2={1070} y2={507} p={phase(s, f, 0)} color={C.blue}/>
    <Txt x={990} y={568} center size={22} color={C.muted}>消息可投递</Txt>
    <LocalBoundary x={1110} y={335} w={660} h={405} label="消费端独立本地事务" color={consumed === 1 ? C.teal : C.gold}/>
    {stock(consumed === 1 ? 3 : 4, consumed === 1 ? '扣减 + 已处理标记' : '独立处理，可能失败或重复',
      consumed === 1 ? C.teal : C.gold, undefined, 1440, 383)}
    <RuleLine>两个独立事务：消费端仍要重试、幂等与业务失败处理</RuleLine>
  </>;
};

const CompareScene: React.FC<{shot: Shot; f: number}> = ({shot: s, f}) => {
  const type = s.visualType;
  if (type === 'compare-questions') {
    const a = phase(s, f, 0, .05, .6), b = phase(s, f, 1, .03, .35), c = phase(s, f, 1, .4, .7);
    return <>
      {title('先写业务约束，再选机制')}
      <Chip x={960} y={357} width={1050} alpha={a} color={C.text}>等待：能接受多久的协调与资源占用？</Chip>
      <Chip x={960} y={482} width={1050} alpha={b} color={C.text}>中间状态：能否被其他业务看见？</Chip>
      <Chip x={960} y={607} width={1050} alpha={c} color={C.text}>失败：预留、撤销、补偿或异步处理？</Chip>
      <RuleLine alpha={c}>相同问题，逐章对照；方案名称本身不是选型依据</RuleLine>
    </>;
  }
  const rows: Record<string, {name: string; intent: string; boundary: string; cost: string; kind: number}> = {
    'compare-xa': {name: '2PC / XA', intent: '先准备，再遵循同一决定', boundary: '参与资源支持 XA · 较短事务', cost: '等待、资源占用；不自动产生跨库一致快照', kind: 1},
    'compare-at': {name: 'AT', intent: '本地先提交，框架记录并恢复', boundary: '受支持的数据库 / SQL / 接入路径', cost: '普通读可能见中间状态，全局锁和日志仍有代价', kind: 2},
    'compare-tcc': {name: 'TCC', intent: '先业务预留，再确认或释放', boundary: '资源能预留 · 业务提供三个操作', cost: '幂等、乱序、超时与异常控制都要设计', kind: 3},
    'compare-saga': {name: 'Saga', intent: '逐步本地提交，失败做业务补偿', boundary: '较长流程 · 能接受中间状态', cost: '补偿不是数据库回滚，补偿失败仍要收尾', kind: 4},
    'compare-message': {name: '可靠消息', intent: '一边先提交，另一边异步处理', boundary: '允许异步推进 · 有可靠进度', cost: '独立提交；消费幂等、重试与业务失败处理', kind: 5},
  };
  if (type === 'recap') {
    const items = [
      ['2PC / XA', '准备后决定'], ['AT', '记录并恢复'], ['TCC', '业务先预留'],
      ['Saga', '提交后补偿'], ['可靠消息', '异步推进'],
    ];
    const final = phase(s, f, 1, .6, .94);
    return <>
      {title('别只记名字，要记住边界')}
      {items.map(([name, meaning], i) => {
        const p = ease(f, at(s, 0, .04 + i * .13), 20) * (1 - final);
        return <React.Fragment key={name}>
          <Txt x={380} y={317 + i * 81} size={32} color={C.teal} alpha={p}>{name}</Txt>
          <Txt x={950} y={317 + i * 81} size={31} color={C.text} alpha={p}>{meaning}</Txt>
        </React.Fragment>;
      })}
      <Txt x={960} y={462} center size={62} alpha={final}>按业务约束选择</Txt>
      <Txt x={960} y={568} center size={32} color={C.muted} alpha={final}>IT小村 · 原创</Txt>
      <RuleLine>资源 · 隔离 · 时长 · 失败后的处理，没有一种方案能消除所有代价</RuleLine>
    </>;
  }
  const row = rows[type];
  if (!row) return null;
  const a = phase(s, f, 0, .03, .4), b = phase(s, f, 1, .03, .5);
  return <>
    {title('逐项比较 · 当前只看一种路线')}
    <Txt x={190} y={350} size={66} color={C.teal}>{row.name}</Txt>
    <Txt x={190} y={478} size={30} width={560} color={C.muted}>核心动作</Txt>
    <Txt x={190} y={535} size={37} width={580}>{row.intent}</Txt>
    <div style={{position: 'absolute', left: 828, top: 337, height: 365, width: 2, background: C.edge}}/>
    <Txt x={930} y={346} size={26} color={C.muted} alpha={a}>适用前提</Txt>
    <Txt x={930} y={408} size={33} width={780} alpha={a}>{row.boundary}</Txt>
    <Txt x={930} y={538} size={26} color={C.muted} alpha={b}>仍需承担的代价</Txt>
    <Txt x={930} y={597} size={31} width={790} color={C.gold} alpha={b}>{row.cost}</Txt>
    <RuleLine alpha={b}>把机制、前提和失败处理一起比较</RuleLine>
  </>;
};

const chapterInfo = (s: Shot) => {
  const id = s.chapterId;
  const map: Record<string, [number, string]> = {
    xa: [1, '先准备，再决定'], at: [2, '本地先提交，记录后恢复'],
    tcc: [3, '业务先预留'], saga: [4, '提交后业务补偿'],
    message: [5, '允许异步推进'],
  };
  return map[id] ?? [0, id === 'compare' ? '按相同问题比较边界' : '先弄清楚跨系统的问题'];
};
const Scene: React.FC<{shot: Shot; f: number}> = ({shot, f}) => {
  if (shot.chapterId === 'problem') return <IntroScene shot={shot} f={f}/>;
  if (shot.chapterId === 'xa') return <XaScene shot={shot} f={f}/>;
  if (shot.chapterId === 'at') return <AtScene shot={shot} f={f}/>;
  if (shot.chapterId === 'tcc' || shot.chapterId === 'saga') return <BusinessScene shot={shot} f={f}/>;
  if (shot.chapterId === 'message') return <MessageScene shot={shot} f={f}/>;
  return <CompareScene shot={shot} f={f}/>;
};

export type MainProps = {showSubtitles?: boolean; hideSubtitles?: boolean};
const ShotView: React.FC<{shot: Shot; captions: boolean}> = ({shot, captions}) => {
  const f = useCurrentFrame(), [chapter, intent] = chapterInfo(shot);
  const sub = shot.subtitles?.find(v => f >= v.from && f <= (v.to ?? v.from + (v.duration ?? 1) - 1));
  return <AbsoluteFill style={{background: C.bg, color: C.text, fontFamily: FONT, overflow: 'hidden'}}>
    <div style={{position: 'absolute', inset: 0,
      background: 'radial-gradient(ellipse at 85% 5%, #173B5555, transparent 62%)'}}/>
    <Txt x={100} y={54} size={24} color={C.muted}>分布式 · EP.21</Txt>
    <Txt x={100} y={94} size={20} color={chapter ? C.teal : C.muted}>
      {chapter ? `${String(chapter).padStart(2, '0')} / 05 · ${intent}` : intent}
    </Txt>
    <StageDots current={chapter}/>
    <Txt x={1700} y={54} size={25}>IT小村</Txt>
    <Txt x={1650} y={101} center width={480} size={18} color={C.muted}>示例数据 · 不同方案分别演示</Txt>
    <Scene shot={shot} f={f}/>
    {captions && sub && <div data-subtitle style={{position: 'absolute', left: 130, right: 130,
      top: 925, minHeight: 100, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 40, fontWeight: 500, lineHeight: 1.4, textAlign: 'center',
      background: `${C.bg}F8`, borderRadius: 12, padding: '7px 15px', boxSizing: 'border-box'}}>{sub.text}</div>}
  </AbsoluteFill>;
};
export const Main: React.FC<MainProps> = ({showSubtitles = true, hideSubtitles = false}) =>
  <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
    {typeof __HAS_VOICE_AUDIO__ !== 'undefined' && __HAS_VOICE_AUDIO__ && <Audio src={staticFile('audio/voice.wav')}/>}
    {shots.map(s => <Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}>
      <ShotView shot={s} captions={showSubtitles && !hideSubtitles}/>
    </Sequence>)}
  </AbsoluteFill>;
