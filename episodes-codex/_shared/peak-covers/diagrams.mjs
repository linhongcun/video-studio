import fs from 'node:fs';
const C=JSON.parse(fs.readFileSync(new URL('./style-v1.json',import.meta.url),'utf8')).palette;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
let index=0;
const ink=()=>`data-ink="diagram-${++index}"`;
const t=(x,y,s,size=28,color=C.text,extra='')=>`<text data-element="diagram-label" x="${x}" y="${y}" fill="${color}" font-size="${size}" font-weight="600" ${extra}>${esc(s)}</text>`;
const box=(x,y,w,h,color=C.edge,fill=C.background)=>`<rect ${ink()} x="${x}" y="${y}" width="${w}" height="${h}" rx="16" stroke="${color}" stroke-width="2.5" fill="${fill}"/>`;
const p=(d,color=C.cyan,dash='')=>`<path ${ink()} d="${d}" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" ${dash}/>`;
const arrow=(x1,y1,x2,y2,color=C.cyan)=>{const a=Math.atan2(y2-y1,x2-x1),r=11;return p(`M${x1} ${y1}L${x2} ${y2}M${x2-r*Math.cos(a-.55)} ${y2-r*Math.sin(a-.55)}L${x2} ${y2}L${x2-r*Math.cos(a+.55)} ${y2-r*Math.sin(a+.55)}`,color);};
export function diagram(slug){
 index=0;
 if(slug==='rate-limit')return `${t(380,34,'教学额度：容量 2',28,C.muted,'text-anchor="middle"')}
 ${box(230,61,275,245)}${t(367,99,'同一入口',28,C.muted,'text-anchor="middle"')}
 ${[129,199,269].map((y,i)=>`${box(20,y-31,115,51,i===2?C.coral:C.cyan)}${t(77,y+5,['甲','乙','丙'][i],30,C.text,'text-anchor="middle"')}${arrow(144,y-5,218,y-5,i===2?C.coral:C.cyan)}${t(367,y+5,['扣 1 个额度','再扣 1 个额度','剩余 0 个额度'][i],25,i===2?C.coral:C.text,'text-anchor="middle"')}${i===2?p('M519 264H589M563 248L579 280M579 248L563 280',C.coral):arrow(519,y-5,601,y-5)}${t(652,y+5,i===2?'拒绝':'放行',30,i===2?C.coral:C.cyan,'text-anchor="middle"')}`).join('')}
 ${t(380,347,'先扣额度，再放行',28,C.yellow,'text-anchor="middle"')}`;
 if(slug==='idempotency')return `${t(380,34,'同一笔支付 · 编号 7042',28,C.muted,'text-anchor="middle"')}
 ${box(20,64,180,87)}${t(110,99,'首次请求',27,C.text,'text-anchor="middle"')}${t(110,133,'7042',28,C.cyan,'text-anchor="middle"')}
 ${box(20,209,180,87)}${t(110,244,'重复请求',27,C.text,'text-anchor="middle"')}${t(110,278,'7042',28,C.cyan,'text-anchor="middle"')}
 ${p('M211 106H246V178H271')}${p('M211 253H246V178')}${arrow(249,178,276,178)}
 ${box(287,103,202,150,C.cyan)}${t(388,143,'7042',32,C.cyan,'text-anchor="middle"')}${t(388,182,'已完成并记录',25,C.text,'text-anchor="middle"')}${t(388,224,'复用已有结果',23,C.muted,'text-anchor="middle"')}
 ${arrow(502,178,537,178)}${box(550,85,188,186,C.yellow)}${t(644,122,'累计扣款',25,C.muted,'text-anchor="middle"')}${t(644,166,'30 元',43,C.yellow,'text-anchor="middle"')}${t(644,209,'余额 100 → 70',22,C.text,'text-anchor="middle"')}${t(644,245,'业务效果不增加',21,C.muted,'text-anchor="middle"')}
 ${t(380,347,'重复的是请求，扣款仍为一次',27,C.yellow,'text-anchor="middle"')}`;
 if(slug==='circuit-breaker')return `${t(380,34,'暂停故障调用，保留必要校验',27,C.muted,'text-anchor="middle"')}
 ${box(18,148,173,88)}${t(104,199,'订单流程',29,C.text,'text-anchor="middle"')}
 ${p('M202 192H232V91H321',C.coral)}${p('M335 68V114M353 68V114',C.coral)}${p('M370 91H516',C.edge,'stroke-dasharray="9 9"')}${t(388,65,'暂停调用',24,C.coral,'text-anchor="middle"')}
 ${box(529,55,211,85,C.coral)}${t(634,91,'可选运费险',25,C.text,'text-anchor="middle"')}${t(634,123,'暂不可用',22,C.coral,'text-anchor="middle"')}
 ${arrow(204,192,300,244)}${box(313,200,194,89,C.cyan)}${t(410,252,'库存等校验',27,C.text,'text-anchor="middle"')}
 ${arrow(519,244,557,244)}${box(570,200,170,89,C.cyan)}${t(655,252,'按条件继续',26,C.cyan,'text-anchor="middle"')}
 ${t(380,347,'暂停失败调用，保住其他请求',27,C.yellow,'text-anchor="middle"')}`;
 if(slug==='degradation')return `${t(380,34,'同一商品 · 7042',28,C.muted,'text-anchor="middle"')}
 ${box(20,61,327,237,C.edge)}${t(183,104,'搜索页',29,C.text,'text-anchor="middle"')}${t(183,166,'199 元',57,C.text,'text-anchor="middle"')}${t(183,211,'未计红包',28,C.yellow,'text-anchor="middle"')}${t(183,255,'以结算为准',24,C.muted,'text-anchor="middle"')}
 ${box(413,61,327,237,C.cyan)}${t(576,104,'结算页',29,C.text,'text-anchor="middle"')}${t(576,166,'179 元',57,C.cyan,'text-anchor="middle"')}${t(576,211,'核验红包 −20',26,C.yellow,'text-anchor="middle"')}${t(576,255,'确认金额再下单',24,C.muted,'text-anchor="middle"')}
 ${t(380,347,'减少搜索预估，保留结算核验',27,C.yellow,'text-anchor="middle"')}`;
 throw new Error('No checked mechanism diagram for '+slug);
}
