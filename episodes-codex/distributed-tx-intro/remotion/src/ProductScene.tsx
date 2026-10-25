import React from 'react';
import {createDatabaseIdentity} from '../../../_shared/database-identity';
import {C, FONT, MONO} from './theme';
import {ease, lerp, Line, MovingChip, Chip} from './primitives';
import {Stock} from './objects';

const DatabaseMark = createDatabaseIdentity(React);

export type ProductSceneProps = {
  mode: 'opening' | 'mapping' | 'return';
  /** Local shot frame; for return, zero is the start of the return overlay. */
  frame: number;
};

/** Sampling anchors, not new narration or shot timing. */
export const productSceneEvents = {
  opening: {click: 42, orderOpened: 64, backstageStart: 62, backstageVisible: 86},
  mapping: {start: 24, end: 92, targetStart: 112, targetVisible: 162},
} as const;

const Text = ({children, x, y, width, size = 30, color = C.text, center = false,
  mono = false, opacity = 1}: {
  children: React.ReactNode; x: number; y: number; width?: number;
  size?: number; color?: string; center?: boolean; mono?: boolean; opacity?: number;
}) => <div style={{position: 'absolute', left: x, top: y, width, color, opacity,
  fontFamily: mono ? MONO : FONT, fontSize: size, fontWeight: 600, lineHeight: 1.35,
  textAlign: center ? 'center' : 'left', whiteSpace: 'pre-line',
  transform: center ? 'translateX(-50%)' : undefined}}>{children}</div>;

/** One persistent order identity: opening the page never creates this record. */
const OrderIdentity = ({mapping}: {mapping: number}) => <div data-order-id="8124">
  <Text x={520} y={lerp(426, 405, mapping)} center size={26} color={C.muted}>
    {mapping < .5 ? '订单编号' : '订单记录'}
  </Text>
  <Text x={520} y={lerp(461, 440, mapping)} width={470} center mono
    size={lerp(80, 94, mapping)} color={C.text}>8124</Text>
  <div style={{position: 'absolute', left: 305, top: lerp(578, 575, mapping),
    width: 430, height: 2, background: C.blue, opacity: .65}}/>
  <Text x={520} y={lerp(599, 597, mapping)} center size={31}
    color={mapping > .5 ? C.teal : C.gold}>
    {mapping > .5 ? '目标：订单确认' : '尚未完成下单确认'}
  </Text>
</div>;

const ProductUi = ({frame, mapping, opened}: {
  frame: number; mapping: number; opened: boolean;
}) => {
  const click = productSceneEvents.opening.click;
  const ready = productSceneEvents.opening.orderOpened;
  const pressing = !opened && frame >= click && frame < click + 10;
  const loading = !opened && frame >= click && frame < ready;
  const chrome = 1 - mapping;
  const feedback = opened ? 1 : ease(frame, ready, 12);
  const pulse = !opened && frame >= click && frame < click + 20 ? (frame - click) / 20 : -1;
  return <>
    <div data-product-page={opened ? 'orders' : 'submission-result'} style={{
      position: 'absolute', left: 130, top: 278, width: 1030, height: 504,
      border: `1.5px solid ${C.edge}`, borderRadius: 20,
      background: C.surface, opacity: chrome,
    }}/>
    <div style={{opacity: chrome}}>
      <Text x={168} y={300} size={25} color={C.muted}>{opened ? '‹ 订单详情' : '教学购物 · 提交结果'}</Text>
      <Text x={1052} y={299} center size={25} color={C.blue}>
        {opened ? '我的订单' : '已收到下单请求'}
      </Text>
      <div style={{position: 'absolute', left: 164, top: 344, width: 962, height: 58,
        borderBottom: `1px solid ${C.edge}`}}>
        <Text x={7} y={0} size={31}>笔记本 · 商品 7042</Text>
        <Text x={842} y={0} center width={220} size={30}>购买 1 件</Text>
      </div>
      <div style={{position: 'absolute', left: 864, top: 449, padding: '8px 18px',
        border: `1px solid ${C.blue}`, borderRadius: 24, color: C.blue,
        fontSize: 24, background: C.bg}}>已记录</div>
      <div data-product-action="view-order" style={{position: 'absolute', left: 170,
        top: 676, width: 390, height: 66, display: 'flex', alignItems: 'center',
        justifyContent: 'center', color: C.bg, background: C.blue, borderRadius: 12,
        fontSize: 29, fontWeight: 700, transform: `scale(${pressing ? .97 : 1})`,
        transformOrigin: 'center'}}>
        {opened ? '‹ 返回订单列表' : loading ? '正在打开订单…' : '查看我的订单'}
      </div>
      {pulse >= 0 && <div style={{position: 'absolute', left: 365 - 24 - pulse * 24,
        top: 709 - 24 - pulse * 24, width: 48 + pulse * 48, height: 48 + pulse * 48,
        border: `3px solid ${C.blue}`, borderRadius: '50%', opacity: 1 - pulse,
        pointerEvents: 'none'}}/>}
      <Text x={606} y={692} width={480} size={25} color={C.gold} opacity={feedback}>
        订单可查，仍待确认
      </Text>
    </div>
    {opened && <div style={{opacity: chrome}}>
      <Text x={862} y={526} size={23} color={C.muted}>处理进度</Text>
      <Text x={862} y={567} size={31} color={C.gold}>待确认</Text>
    </div>}
    <OrderIdentity mapping={mapping}/>
  </>;
};

const Backstage = ({opacity, mapping, showTarget}: {
  opacity: number; mapping: number; showTarget: boolean;
}) => <div data-product-backstage="stock-record" style={{opacity}}>
  <div style={{position: 'absolute', left: 1230, top: 278, width: 560, height: 504,
    border: `1.5px solid ${C.edge}`, borderRadius: 20, background: C.surface,
    opacity: 1 - mapping}}/>
  <div style={{position: 'absolute', left: 1264, top: 299, height: 50,
    display: 'inline-flex', alignItems: 'center', gap: 12, opacity: 1 - mapping,
    color: C.muted, fontSize: 25, fontWeight: 600}}>
    <DatabaseMark size={44}/><span>后台记录 · 教学透视</span>
  </div>
  <Stock x={lerp(1510,1400,mapping)} value={4} state={mapping > .5 ? '当前库存' : '本单尚未扣减'}
    detail={showTarget ? '目标：扣减后为 3' : ''} color={C.gold}/>
</div>;

/** Functional product UI, followed by the exact records already used in this episode. */
export const ProductScene: React.FC<ProductSceneProps> = ({mode, frame}) => {
  const mapping = mode === 'mapping' ? ease(frame, 24, 68) : 0;
  const opened = mode !== 'opening' || frame >= productSceneEvents.opening.orderOpened;
  const backstage = mode === 'opening' ? ease(frame, 62, 24) : 1;
  const goal = mode === 'mapping' ? ease(frame, 112, 50) : 0;
  const showTarget = mode === 'mapping' && frame >= 105;
  return <div data-product-scene={mode} style={{position: 'absolute', inset: 0,
    fontFamily: FONT, color: C.text, pointerEvents: 'none'}}>
    {/* Covers the old map only in the authorized product work area, never the subtitles. */}
    <div style={{position: 'absolute', left: 0, top: 160, width: 1920, height: 730,
      background: C.bg}}/>
    <Text x={130} y={184} width={1660} size={45}>
      {mode === 'opening' ? '下单未确认，订单为什么还在？'
        : mode === 'mapping' ? '同一笔订单，要满足两个条件'
          : '回到开头：订单出现，还不等于下单成功'}
    </Text>
    {mode === 'return' && <Text x={130} y={244} size={24} color={C.gold}>
      回看开头的待确认订单
    </Text>}
    <ProductUi frame={frame} mapping={mapping} opened={opened}/>
    <Backstage opacity={backstage} mapping={mapping} showTarget={showTarget}/>
    {mode === 'mapping' && <>
      <Line x1={805} y1={530} x2={1115} y2={530} color={C.teal} p={goal}/>
      <MovingChip x1={860} y1={495} x2={1050} y2={495} p={goal}
        width={220} color={C.teal} alpha={goal}>购买 1 件</MovingChip>
      <Chip x={1400} y={722} width={350} color={C.teal} alpha={goal}>
        目标值 3 · 尚未执行
      </Chip>
    </>}
    <Text x={960} y={825} center width={1660} size={31}
      color={mode === 'mapping' ? C.teal : C.gold}>
      {mode === 'opening' ? '订单已经记下；库存安排还没有落实'
        : mode === 'mapping' ? '页面上的同一单，对应记订单和扣库存'
          : '跨了提交边界，业务还需要协作与恢复'}
    </Text>
  </div>;
};
