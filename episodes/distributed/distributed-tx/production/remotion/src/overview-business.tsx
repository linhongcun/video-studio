import React from 'react';
import {Shot} from './data';
import {C} from './theme';
import {
  Txt, Ledger, Chip, Line, MovingChip, RuleLine, SmallLabel, ease,
} from './overview-primitives';

const at = (s: Shot, sentence: number, part: number) => {
  const starts = s.cueFrames?.sentences ?? [0, s.durationInFrames * .5];
  const a = Number(starts[sentence] ?? 0);
  const next = Number(starts[sentence + 1] ?? s.durationInFrames - 15);
  return a + (Math.max(a + 1, next) - a) * part;
};
const phase = (s: Shot, f: number, sentence: number, start = .1, end = .7) =>
  ease(f, at(s, sentence, start), Math.max(1, at(s, sentence, end) - at(s, sentence, start)));
const cue = (s: Shot, name: string) => Number(s.cueFrames?.labels?.[name] ?? 1);

/** These are three states of the same four units, not three copies of stock. */
const Inventory: React.FC<{
  available: number; reserved: number; sold?: number; alpha?: number;
  emphasis?: 'available' | 'reserved' | 'sold'; state?: string;
}> = ({available, reserved, sold = 0, alpha = 1, emphasis = 'reserved', state}) => <>
  <Txt x={960} y={292} center size={25} color={C.muted} alpha={alpha}>
    商品7042 · 同一份库存
  </Txt>
  <Ledger x={570} y={355} width={290} label="可用" value={available}
    state={emphasis === 'available' ? '可继续分配' : '未被占用'}
    color={C.text} alpha={alpha}/>
  <Ledger x={960} y={355} width={290} label="本单预留" value={reserved}
    state={reserved ? '已为8124占好' : '没有预留'}
    color={reserved ? C.gold : C.muted} alpha={alpha}/>
  <Ledger x={1350} y={355} width={290} label="本单正式扣减" value={sold}
    state={sold ? '已经确认' : '尚未正式扣减'}
    color={sold ? C.teal : C.muted} alpha={alpha}/>
  {state && <SmallLabel y={700} color={C.gold} alpha={alpha}>{state}</SmallLabel>}
</>;

const Branch: React.FC<{children: React.ReactNode; color?: string; alpha?: number}> =
  ({children, color = C.gold, alpha = 1}) => <Txt x={130} y={260} size={24}
    color={color} alpha={alpha}>{children}</Txt>;

const PaymentHistory: React.FC<{
  balance: number; refund?: 'none' | 'pending' | 'complete' | 'failed';
  x?: number; alpha?: number;
}> = ({balance, refund = 'none', x = 650, alpha = 1}) => <>
  <Ledger x={x} y={335} label="付款账户 · 余额" value={balance}
    state={refund === 'complete' ? '退款已本地提交' : '扣款已本地提交'}
    color={refund === 'complete' ? C.teal : C.text} alpha={alpha}/>
  <Txt x={x} y={590} center size={27} color={C.muted} alpha={alpha} mono>
    原扣款记录 −200 · 保留
  </Txt>
  {refund !== 'none' && <Chip x={x} y={645} width={440}
    color={refund === 'complete' ? C.teal : refund === 'failed' ? C.red : C.gold}
    alpha={alpha}>
    {refund === 'complete' ? '新增退款记录 +200 · 已提交'
      : refund === 'failed' ? '退款未完成 · 进度仍保留'
        : '新增退款 +200 · 尚未提交'}
  </Chip>}
</>;

export const BusinessScene: React.FC<{shot: Shot; f: number}> = ({shot: s, f}) => {
  const t = s.visualType as string;
  const s1 = at(s, 1, 0);

  if (t === 'tcc-intro') {
    const term = f >= cue(s, 'TCC');
    const enter = phase(s, f, 1, .1, .65);
    return <>
      <Txt>{term ? 'TCC：先预留，再确认或取消' : '先把资源留住'}</Txt>
      <Branch>另一种方案 · 重新演示 · 可用4，预留0</Branch>
      <Inventory available={4} reserved={0}/>
      <Line x1={360} y1={656} x2={860} y2={656} p={enter} color={C.gold}/>
      <MovingChip x1={360} y1={624} x2={800} y2={624} p={enter}
        width={250} alpha={enter} color={C.gold}>尝试：预留1件</MovingChip>
      <RuleLine alpha={phase(s, f, 1, .65, .8)}>业务实现三个操作：尝试 → 确认 / 取消</RuleLine>
    </>;
  }

  if (t === 'tcc-try') {
    const move = phase(s, f, 0, .1, .65);
    const moved = move >= 1;
    const commit = f >= at(s, 1, .3);
    return <>
      <Txt>尝试：把一件可用库存转为预留</Txt>
      <Inventory available={moved ? 3 : 4} reserved={moved ? 1 : 0}
        state={commit ? '尝试已在本地提交 · 尚未正式成交' : '正在记录本单预留'}/>
      <Line x1={570} y1={666} x2={960} y2={666} p={move} color={C.gold}/>
      <MovingChip x1={570} y1={632} x2={960} y2={632} p={move} width={160}
        alpha={1 - phase(s, f, 0, .7, .9)}>1件</MovingChip>
      <Chip x={960} y={633} width={470} color={commit ? C.teal : C.gold}
        alpha={phase(s, f, 1, .05, .2)}>{commit ? '预留记录 · 本地已提交' : '本地提交预留记录'}</Chip>
      <RuleLine alpha={phase(s, f, 1, .55, .75)}>预留先占住资源；正式扣减仍是0</RuleLine>
    </>;
  }

  if (t === 'tcc-confirm') {
    const ready = phase(s, f, 0, .1, .55);
    const move = phase(s, f, 1, .1, .6);
    const done = move >= 1;
    return <>
      <Txt>确认：把预留变为正式扣减</Txt>
      <Branch color={C.teal}>各方尝试都成功 → 执行确认</Branch>
      <Inventory available={3} reserved={done ? 0 : 1} sold={done ? 1 : 0}
        emphasis="sold"/>
      <Chip x={960} y={630} width={410} color={C.teal}
        alpha={f < s1 ? ready : 0}>各方准备完成</Chip>
      <Line x1={960} y1={665} x2={1350} y2={665} p={move} color={C.teal}/>
      <MovingChip x1={960} y1={632} x2={1350} y2={632} p={move} width={180}
        color={C.teal} alpha={phase(s, f, 1, 0, .08) * (1 - phase(s, f, 1, .65, .8))}>确认1件</MovingChip>
      <RuleLine alpha={phase(s, f, 1, .6, .8)} color={C.teal}>可用仍是3；不会再从3扣成2</RuleLine>
    </>;
  }

  if (t === 'tcc-cancel') {
    const move = phase(s, f, 0, .35, .7);
    const done = move >= 1;
    return <>
      <Txt>取消：把已经预留的资源释放</Txt>
      <Branch color={C.red}>另一种结果 · 某方尝试失败</Branch>
      <Inventory available={done ? 4 : 3} reserved={done ? 0 : 1} sold={0}
        emphasis="available"/>
      <Line x1={960} y1={666} x2={570} y2={666} p={move} color={C.gold}/>
      <MovingChip x1={960} y1={632} x2={570} y2={632} p={move} width={200}
        alpha={1 - phase(s, f, 0, .75, .95)}>释放预留1件</MovingChip>
      <RuleLine alpha={phase(s, f, 1, .3, .5)} color={C.teal}>可用3→4；预留1→0；本单没有成交</RuleLine>
    </>;
  }

  if (t === 'tcc-limit') {
    // Both duplicate handling and late Try belong to sentence one. Sentence two
    // can then hold the interface-cost conclusion without starting a new demo.
    const switchAt = at(s, 0, .48);
    const second = f >= switchAt;
    const attempt = phase(s, f, 0, .05, .3);
    const late = phase(s, f, 0, .52, .8);
    return <>
      <Txt>边界：幂等与异常控制，由业务实现</Txt>
      {!second ? <>
        <Branch>回看确认成功分支 · 重复确认</Branch>
        <Inventory available={3} reserved={0} sold={1} emphasis="sold"/>
        <Line x1={350} y1={665} x2={910} y2={665} p={attempt} color={C.blue}/>
        <MovingChip x1={350} y1={632} x2={825} y2={632} p={attempt}
          color={C.blue} width={230}>重复确认</MovingChip>
        <Chip x={1320} y={632} width={300} color={C.teal} alpha={phase(s, f, 0, .3, .38)}>
          返回原结果 · 不再扣
        </Chip>
      </> : <>
        <Branch>再看另一分支 · 已取消，尝试却迟到</Branch>
        <Ledger x={620} y={350} label="本次业务事务" value="已取消" valueSize={66}
          mono={false} state="结束状态已经保存" color={C.teal}/>
        <Ledger x={1370} y={350} label="库存" value={4} state="不再接受本次预留" color={C.text}/>
        <Line x1={620} y1={665} x2={1180} y2={665} p={late} color={C.red}/>
        <MovingChip x1={620} y1={632} x2={1020} y2={632} p={late}
          width={230} color={C.gold}>迟到的尝试</MovingChip>
        <Chip x={1370} y={632} width={300} color={C.red} alpha={phase(s, f, 0, .8, .9)}>
          校验状态 → 拒绝
        </Chip>
      </>}
      <RuleLine>适合可预留资源；业务需实现尝试、确认、取消</RuleLine>
    </>;
  }

  if (t === 'saga-intro') {
    const term = f >= cue(s, 'Saga');
    const payAt = at(s, 0, .65);
    const payDone = f >= payAt;
    const stockAt = at(s, 1, .6);
    const stockDone = f >= stockAt;
    return <>
      <Txt>{term ? 'Saga：一笔笔本地事务，逐步提交' : '把长流程分成可追踪的步骤'}</Txt>
      <Branch>另一种方案 · 重新演示 · 初始库存4</Branch>
      <Line x1={490} y1={610} x2={1380} y2={610}
        p={ease(f, at(s, 0, .15), Math.max(1, stockAt - at(s, 0, .15)))}/>
      <Ledger x={530} y={345} label="付款服务 · 账户余额" value={payDone ? 800 : 1000}
        state={payDone ? '付款200 · 本地已提交' : '待付款200'} color={payDone ? C.teal : C.gold}/>
      <Ledger x={1370} y={345} label="库存服务" value={stockDone ? 3 : 4}
        state={stockDone ? '扣减1件 · 本地已提交' : '等待上一笔完成'}
        color={stockDone ? C.teal : C.gold}/>
      <Chip x={530} y={630} width={300} color={payDone ? C.teal : C.gold}>本地事务①</Chip>
      <Chip x={1370} y={630} width={300} color={stockDone ? C.teal : C.muted}>本地事务②</Chip>
      <RuleLine alpha={phase(s, f, 1, .6, .8)} color={C.teal}>每步各自提交；全部完成，业务才走完</RuleLine>
    </>;
  }

  if (t === 'saga-failure') {
    const paid = f >= at(s, 1, .25);
    const fail = phase(s, f, 1, .45, .7);
    return <>
      <Txt>付款已提交，后面的库存却不足</Txt>
      <Branch color={C.red}>换个失败例 · 初始库存0</Branch>
      {paid ? <PaymentHistory balance={800} x={580}/> :
        <Ledger x={580} y={335} label="付款账户 · 余额" value={1000}
          state="将支付200" color={C.gold}/>}
      <Ledger x={1380} y={335} label="本例库存" value={0}
        state={fail >= 1 ? '本单缺货 · 操作失败' : '库存不足'} color={C.red}/>
      <Line x1={820} y1={565} x2={1150} y2={565} p={phase(s, f, 1, .3, .5)} color={C.red}/>
      <Txt x={1020} y={595} center size={38} color={C.red} alpha={fail}>×</Txt>
      <RuleLine alpha={phase(s, f, 1, .7, .85)} color={C.gold}>扣款已经提交，不能把历史当作没有发生</RuleLine>
    </>;
  }

  if (t === 'saga-compensate') {
    const travel = phase(s, f, 0, .1, .6);
    const commitAt = at(s, 0, .7);
    const done = f >= commitAt;
    return <>
      <Txt>补偿：新增一笔退款，不抹掉原扣款</Txt>
      <PaymentHistory balance={done ? 1000 : 800}
        refund={done ? 'complete' : 'pending'} x={660}/>
      <Line x1={1440} y1={460} x2={920} y2={460} p={travel} color={C.teal}/>
      <MovingChip x1={1440} y1={426} x2={1060} y2={426} p={travel}
        width={300} color={C.teal} alpha={1 - phase(s, f, 0, .75, .95)}>
        新的退款请求 +200
      </MovingChip>
      <Txt x={1390} y={585} center width={460} size={29} color={C.muted}
        alpha={phase(s, f, 1, .1, .3)}>{'新的本地事务\n不是原扣款事务回滚'}</Txt>
      <RuleLine alpha={phase(s, f, 1, .25, .5)}>原扣款−200与新退款+200，两条业务记录都保留</RuleLine>
    </>;
  }

  if (t === 'saga-risk') {
    const fail = phase(s, f, 0, .08, .35);
    const read = phase(s, f, 1, .1, .55);
    const reveal = phase(s, f, 1, .55, .7);
    return <>
      <Txt>补偿也会失败，中间状态也可能被读到</Txt>
      <Branch color={C.red}>另一失败结果 · 扣款已提交，退款尚未完成</Branch>
      <PaymentHistory balance={800} refund="failed" x={570}/>
      <Line x1={1040} y1={433} x2={1430} y2={433} p={fail} color={C.red}/>
      <Chip x={1370} y={397} width={410} color={C.red} alpha={fail}>
        持久进度：待补偿
      </Chip>
      <Txt x={1370} y={488} center size={27} color={C.gold} alpha={fail}>
        重试 / 告警 / 人工处理
      </Txt>
      <Line x1={1450} y1={635} x2={950} y2={635} p={read} color={C.blue}/>
      <MovingChip x1={1450} y1={602} x2={1000} y2={602} p={read}
        width={310} color={C.blue} alpha={phase(s, f, 1, 0, .08) * (1 - reveal)}>
        另一笔事务：查询
      </MovingChip>
      <Chip x={1370} y={605} width={410} color={C.blue} alpha={reveal}>
        可读到：已扣款 / 待退款
      </Chip>
      <RuleLine color={C.gold}>没有覆盖全流程的全局隔离；补偿失败仍需收尾</RuleLine>
    </>;
  }

  if (t === 'saga-limit') {
    const move = phase(s, f, 0, .1, .65);
    const blocked = phase(s, f, 1, .1, .45);
    return <>
      <Txt>适合长流程，也要先定义业务补偿</Txt>
      <Line x1={350} y1={490} x2={1540} y2={490} p={move} color={C.teal}/>
      <Chip x={420} y={455} width={320} color={C.teal}>本地业务提交</Chip>
      <MovingChip x1={760} y1={455} x2={1220} y2={455} p={move}
        width={340} color={C.teal}>可定义的补偿操作</MovingChip>
      <Txt x={560} y={613} center size={29} color={C.muted} alpha={blocked}>
        不能接受中间状态
      </Txt>
      <Txt x={560} y={672} center size={29} color={C.red} alpha={blocked}>
        需要别的设计
      </Txt>
      <Txt x={1350} y={613} center size={29} color={C.muted} alpha={blocked}>
        不可逆、无法补偿
      </Txt>
      <Txt x={1350} y={672} center size={29} color={C.red} alpha={blocked}>
        提前安排边界与人工处置
      </Txt>
      <RuleLine alpha={phase(s, f, 1, .55, .75)}>业务补偿是明确的新动作，不是恢复数据库快照</RuleLine>
    </>;
  }

  return null;
};
