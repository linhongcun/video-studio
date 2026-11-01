/**
 * Design-pattern cover diagrams. Each is an explanatory overview of the actual
 * current episode, not a new runtime execution or a product screenshot.
 * Landscape viewBox: 0 0 1200 250; portrait viewBox: 0 0 600 400.
 * All visible text >=22px landscape / >=23px portrait; no external resources.
 * A target contract is a relation/label, never another runtime forwarding node.
 */
const C = Object.freeze({
  bg:'#E8E0CF', surface:'#F2EEE3', text:'#20355D', muted:'#647086',
  edge:'#BCC3CE', blue:'#315FD1', orange:'#B84C2D', cyan:'#3F778E',
});
const esc=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[x]));
const attrs=o=>Object.entries(o).map(([k,v])=>` ${k}="${esc(v)}"`).join('');
const tag=(name,a,body='')=>`<${name}${attrs(a)}>${body}</${name}>`;
const t=(name,x,y,s,size=26,fill=C.text,extra={})=>tag('text',{
  'data-element':`diagram-${name}`,x,y,'font-size':size,fill,
  'font-weight':600,'text-anchor':'middle',...extra,
},esc(s));
const box=(x,y,w,h,stroke=C.blue)=>tag('rect',{
  x,y,width:w,height:h,rx:15,fill:C.surface,stroke,'stroke-width':3,
});
const line=(x1,y1,x2,y2,color=C.blue,width=3,extra={})=>tag('line',{
  x1,y1,x2,y2,stroke:color,'stroke-width':width,'stroke-linecap':'round',...extra,
});
const arrow=(x1,y1,x2,y2,color=C.blue)=>{
  const a=Math.atan2(y2-y1,x2-x1),d=10,z=6;
  const ax=x2-d*Math.cos(a),ay=y2-d*Math.sin(a);
  return line(x1,y1,x2,y2,color)
    +tag('path',{d:`M ${ax+z*Math.sin(a)} ${ay-z*Math.cos(a)} L ${x2} ${y2} L ${ax-z*Math.sin(a)} ${ay+z*Math.cos(a)}`,fill:'none',stroke:color,'stroke-width':3,'stroke-linecap':'round','stroke-linejoin':'round'});
};

function strategy(p){
  // Alternatives share one input contract. No chain 100->90->80 is implied;
  // exactly one is configured for a settlement. Strategy selection stays outside.
  if(p)return box(55,16,490,94)
    +t('choice',300,58,'选择方',29,C.blue)
    +t('choice-detail',300,96,'每次只选择一种',23,C.muted)
    +arrow(300,117,300,131)
    +box(55,138,490,94)
    +t('checkout',300,180,'结算 · 原价100元',30)
    +t('contract',300,219,'按共同约定使用当前策略',23,C.muted)
    +arrow(300,239,300,253,C.orange)
    +box(55,260,490,94,C.orange)
    +t('strategy',300,300,'定价策略 · 择一使用',28,C.orange)
    +t('pricing-alternatives',300,341,'会员90元 / 活动80元',25)
    +t('non-stacking',300,382,'同一原价重算 · 优惠不叠加',23,C.muted);
  return box(40,38,300,172)
    +t('choice',190,99,'选择方',35,C.blue)
    +t('choice-detail',190,155,'每次只选择一种',26,C.muted)
    +arrow(352,124,427,124)
    +box(440,38,300,172)
    +t('checkout',590,99,'结算',35)
    +t('checkout-input',590,153,'同一原价100元',28,C.muted)
    +arrow(752,124,827,124,C.orange)
    +box(840,18,320,212,C.orange)
    +t('strategy',1000,64,'定价策略 · 择一',31,C.orange)
    +t('member',1000,119,'会员九折 → 90元',28)
    +t('campaign',1000,167,'活动八折 → 80元',28)
    +t('contract',1000,210,'原价 → 应付金额',23,C.muted)
    +t('use-contract',590,238,'按共同约定使用',22,C.muted);
}

function observer(p){
  // The moment after payment while BOTH current receivers remain subscribed.
  // Two separate branches, not competing consumers. No reliable delivery,
  // ordering or sync/async implementation claim is encoded.
  if(p)return box(150,18,300,110)
    +t('source',300,62,'订单17 · 已付款',30,C.blue)
    +t('source-detail',300,104,'维护订阅关系',24,C.muted)
    +line(300,136,300,187)
    +line(155,187,445,187)
    +arrow(155,187,155,235)
    +arrow(445,187,445,235,C.orange)
    +t('notify',300,225,'通知当前订阅者',25,C.blue)
    +box(30,244,250,108)
    +t('summary',155,286,'订单摘要',29)
    +t('summary-response',155,330,'更新显示',24,C.muted)
    +box(320,244,250,108,C.orange)
    +t('log',445,286,'变化记录',29)
    +t('log-response',445,330,'追加记录',24,C.muted)
    +t('subscription-first',300,382,'先订阅，再接收变化',23,C.muted);
  return box(65,53,325,144)
    +t('source',227.5,105,'订单17',35,C.blue)
    +t('source-state',227.5,163,'已付款',31)
    +line(402,125,635,125)
    +line(635,62,635,188)
    +arrow(635,62,827,62)
    +arrow(635,188,827,188,C.orange)
    +t('notify',610,43,'通知当前订阅者',27,C.blue)
    +t('subscription-first',570,239,'先订阅，再接收变化',23,C.muted)
    +box(840,14,295,96)
    +t('summary',987.5,53,'订单摘要',30)
    +t('summary-response',987.5,99,'更新显示',24,C.muted)
    +box(840,140,295,96,C.orange)
    +t('log',987.5,179,'变化记录',30)
    +t('log-response',987.5,225,'追加记录',24,C.muted);
}

function adapter(p){
  // Actual request path: business -> adapter -> existing service. The business
  // contract is a label/relation, not a fourth runtime forwarding component.
  // The service executes submission. The adapter translates AND delegates.
  if(p)return box(80,15,440,87)
    +t('business',300,53,'发货提醒',29,C.blue)
    +t('business-input',300,92,'收件人 · 正文',23,C.muted)
    +arrow(300,110,300,148)
    +t('business-contract',325,138,'按业务通知约定',23,C.muted,{'text-anchor':'start'})
    +box(80,158,440,90,C.orange)
    +t('adapter',300,195,'适配器',30,C.orange)
    +t('adapter-role',300,239,'转换 · 委托',23)
    +arrow(300,256,300,290,C.orange)
    +box(80,300,440,90)
    +t('service',300,336,'外部服务',29)
    +t('service-role',300,376,'执行提交',23,C.muted);
  return box(40,42,300,168)
    +t('business',190,92,'发货提醒',33,C.blue)
    +t('business-contract',190,138,'依自己的通知约定',23,C.muted)
    +t('business-input',190,180,'收件人 · 正文',25)
    +arrow(352,125,427,125)
    +box(440,42,300,168,C.orange)
    +t('adapter',590,111,'适配器',36,C.orange)
    +t('adapter-role',590,169,'转换 · 委托',28)
    +arrow(752,125,827,125,C.orange)
    +box(840,42,320,168)
    +t('service',1000,111,'外部服务',35)
    +t('service-role',1000,169,'执行提交',28,C.muted)
    +t('boundary',600,238,'业务自己定约定 · 外部细节留在接入处',23,C.muted);
}

const DRAW=new Map([
  ['strategy-pattern',strategy],['observer-pattern',observer],['adapter-pattern',adapter],
]);
export const SUPPORTED_SLUGS=Object.freeze([...DRAW.keys()]);
export function diagram(slug,portrait=false){
  const draw=DRAW.get(slug);if(!draw)throw new RangeError(`Unsupported design-pattern slug: ${slug}`);
  return tag('g',{'data-pattern-diagram':slug,'font-family':'Noto Sans CJK SC,sans-serif','shape-rendering':'geometricPrecision','text-rendering':'optimizeLegibility'},draw(Boolean(portrait)));
}
