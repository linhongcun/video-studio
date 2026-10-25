import type {Shot} from './data';
import type {BranchMapSpec, BranchMapShot} from '../../../_shared/branch-map';
import {eventAt} from './motion';

const localNodes = ['goal', 'local', 'joint'];
const localEdges = ['range-local', 'local-joint'];
const splitNodes = ['goal', 'split'];
const splitEdges = ['range-split'];
const problemNodes = [...splitNodes, 'partial', 'unknown'];
const problemEdges = [...splitEdges, 'example-partial', 'example-unknown'];
const recoveryNodes = [...problemNodes, 'recover', 'rules'];
const recoveryEdges = [...problemEdges, 'partial-needs', 'unknown-needs', 'business-constraints'];

/** A concept outline: scope comparisons and problem examples, not one purchase's execution. */
export const branchMapSpec: BranchMapSpec = {
  title: '同一下单目标，先看提交范围',
  overviewTitle: '同一个业务目标，两种管理范围',
  overviewHint: '上下是范围对照；问题是示例，不是业务必经顺序',
  nodes: [
    {id:'goal', label:'同一下单目标', x:190, y:450, w:250, kind:'step'},
    {id:'local', label:'同一笔管理', x:570, y:330, w:260, kind:'step'},
    {id:'joint', label:'共同保存\n或撤销', x:1040, y:330, w:300, kind:'step'},
    {id:'split', label:'各自独立提交', x:570, y:650, w:260, kind:'step'},
    {id:'partial', label:'一边保存\n另一边失败', x:1030, y:520, w:300, kind:'unknown'},
    {id:'unknown', label:'回复未到\n结果未知', x:1030, y:760, w:300, kind:'unknown'},
    {id:'recover', label:'查证进度\n协作与恢复', x:1530, y:650, w:300, kind:'step'},
    {id:'rules', label:'业务先定规则', x:1640, y:330, w:300, kind:'step'},
  ],
  edges: [
    {id:'range-local', from:'goal', to:'local', label:'范围对照', via:[[365,450],[365,330]], labelAt:[365,375]},
    {id:'range-split', from:'goal', to:'split', label:'范围对照', via:[[365,450],[365,650]], labelAt:[365,590]},
    {id:'local-joint', from:'local', to:'joint', label:'共同管理'},
    {id:'example-partial', from:'split', to:'partial', label:'问题示例', via:[[790,650],[790,520]], labelAt:[790,560], dashed:true},
    {id:'example-unknown', from:'split', to:'unknown', label:'问题示例', via:[[790,650],[790,760]], labelAt:[790,720], dashed:true},
    {id:'partial-needs', from:'partial', to:'recover', label:'需要的协作', via:[[1285,520],[1285,650]], labelAt:[1285,560]},
    {id:'unknown-needs', from:'unknown', to:'recover', label:'需要的协作', via:[[1285,760],[1285,650]], labelAt:[1285,720]},
    {id:'business-constraints', from:'rules', to:'recover', label:'业务约束', via:[[1640,465],[1530,465]], labelAt:[1595,440], dashed:true},
  ],
  shots: {
    '01': {focus:'goal',activeNodes:['goal','split','partial'],activeEdges:['range-split','example-partial'],crumb:'问题定位｜订单已记录，库存安排还未落实'},
    '02': {focus:'goal',exit:{zoom:30,hold:10},activeNodes:['goal'],activeEdges:[],crumb:'下单目标｜订单确认，还要满足本例库存规则',overviewTitle:'把同一下单目标，放回管理范围中看'},
    '03': {focus:'goal',enter:{hold:50,zoom:34},activeNodes:['goal','local','split'],activeEdges:['range-local','range-split'],crumb:'大纲起点｜只看记订单与扣库存',overviewTitle:'先认清范围，再看具体动作'},
    '04': {focus:'local',activeNodes:localNodes,activeEdges:localEdges,crumb:'机制对照重置｜回到提交之前：本单待提交、库存4'},
    '05': {focus:'joint',activeNodes:localNodes,activeEdges:localEdges,crumb:'同笔范围｜两处就绪后，一起确认保存'},
    '06': {focus:'joint',activeNodes:localNodes,activeEdges:localEdges,crumb:'另一结果重置｜无本单记录、库存4，再看撤销'},
    '07': {focus:'local',exit:{zoom:24,hold:8},activeNodes:localNodes,activeEdges:localEdges,crumb:'同笔范围回顾｜共同保证来自共同管理',overviewTitle:'范围对照：接着改看两边独立提交'},
    '08': {focus:'split',enter:{hold:50,zoom:34},activeNodes:splitNodes,activeEdges:splitEdges,crumb:'范围对照②｜架构示例重置：无本单记录、库存4',overviewTitle:'另看独立范围，不是接着执行上一笔'},
    '09': {focus:'partial',activeNodes:[...splitNodes,'partial'],activeEdges:[...splitEdges,'example-partial'],crumb:'问题示例①｜先处理订单，再看库存结果'},
    '10': {focus:'split',activeNodes:problemNodes,activeEdges:problemEdges,crumb:'跨范围协作｜订单已记录，整笔业务仍待收尾'},
    '11': {focus:'split',exit:{zoom:28,hold:10},activeNodes:problemNodes,activeEdges:problemEdges,crumb:'判断依据｜看同笔管理范围，不按机器数量',overviewTitle:'回到问题大纲：再看没收到回复的情景'},
    '12': {focus:'unknown',enter:{hold:36,zoom:30},activeNodes:[...splitNodes,'unknown'],activeEdges:[...splitEdges,'example-unknown'],crumb:'问题示例②｜新情景库存4，先发请求、再等回复',overviewTitle:'换问题示例：超时只能说明没有等到',overviewHint:'新情景从库存4开始；它不是上一段失败后的继续执行'},
    '13': {focus:'unknown',activeNodes:[...splitNodes,'unknown'],activeEdges:[...splitEdges,'example-unknown'],crumb:'未知的可能A｜没有执行，库存仍4'},
    '14': {focus:'unknown',exit:{zoom:24,hold:8},activeNodes:[...splitNodes,'unknown'],activeEdges:[...splitEdges,'example-unknown'],crumb:'错误示范B｜起点库存3，再扣会多扣',overviewTitle:'错误操作讲完，回到正确的查证与恢复'},
    '15': {focus:'recover',enter:{hold:35,zoom:28},activeNodes:recoveryNodes,activeEdges:recoveryEdges,crumb:'正确写法重置｜库存4，操作和进度待共同保存',overviewTitle:'查证进度，再继续恢复',overviewHint:'回看正确写法：库存4、记录待保存，不沿用错误示范的2或5'},
    '16': {focus:'recover',activeNodes:recoveryNodes,activeEdges:recoveryEdges,crumb:'安全重送示例｜同一笔已处理，库存仍3'},
    '17': {focus:'recover',activeNodes:['split','recover','rules'],activeEdges:['business-constraints'],crumb:'协作思路对照｜独立示意一：先共同决定'},
    '18': {focus:'recover',activeNodes:['split','recover','rules'],activeEdges:['business-constraints'],crumb:'推进示例｜允许约定中间状态，仍需实际恢复'},
    '19': {focus:'rules',exit:{zoom:30,hold:12},activeNodes:['rules','recover'],activeEdges:['business-constraints'],crumb:'先定业务规则｜能否等待，失败怎样收尾',overviewTitle:'回到全图：规则约束协作与恢复'},
    '20': {focus:'goal',mode:'overview',activeNodes:recoveryNodes.concat(['local','joint']),activeEdges:recoveryEdges.concat(localEdges),crumb:'入门回收｜先理解边界，再按独立机制深入',overviewTitle:'跨了提交边界，就要设计协作与恢复',overviewHint:'范围对照、问题示例与恢复要求；再按独立机制短片继续深入'},
  },
};

export function navigationSpec(s:Shot,f:number):BranchMapSpec {
  const binding:BranchMapShot={...branchMapSpec.shots[s.id]};
  const after=(event:string)=>f>=eventAt(s,event);
  if(s.id==='09'&&after('order-local-committed'))binding.crumb='问题示例①｜订单已保存，等待库存处理结果';
  if(s.id==='09'&&after('stock-failed'))binding.crumb='问题示例①｜库存处理失败，订单一边已保存';
  if(s.id==='09'&&after('stock-local-rolled-back'))binding.crumb='问题示例①｜库存本地回滚，订单仍已保存';
  if(s.id==='12'&&after('remote-stock-committed'))binding.crumb='右侧实际已保存3；调用方仍在等回复';
  if(s.id==='12'&&after('reply-lost'))binding.crumb='回复丢失｜右侧已保存3，调用方尚未拿到结果';
  if(s.id==='12'&&after('caller-timeout-unknown'))binding.crumb='调用方超时未知｜不能据此断言没有执行';
  if(s.id==='13'&&after('switch-to-already-executed-possibility'))binding.crumb='未知的可能B｜已执行、库存3，但回复未到';
  if(s.id==='14'&&after('wrong-double-decrement'))binding.crumb='错误示范B｜起点3，错误重扣后为2';
  if(s.id==='14'&&after('reset-to-never-executed-branch'))binding.crumb='切换错误示范A｜本来未执行，起点库存4';
  if(s.id==='14'&&after('wrong-reverse-increment'))binding.crumb='错误示范A｜起点4，错误返还后为5';
  if(s.id==='15'&&after('stock-and-progress-local-commit'))binding.crumb='正确写法｜库存3与已处理记录，共同本地保存';
  if(s.id==='15'&&after('process-interrupted-record-survives'))binding.crumb='程序中断｜已经保存的库存与进度仍在';
  if(s.id==='15'&&after('recovery-checks-record'))binding.crumb='程序恢复｜查证已保存记录，不凭超时猜结果';
  if(s.id==='16'&&after('separate-business-rejection-branch')){binding.focus='rules';binding.crumb='另一结果示例｜业务拒绝，按约定失败收尾';}
  if(s.id==='17'&&after('switch-to-workflow-illustration'))binding.crumb='协作思路对照｜另一独立示意：各步先完成后推进';
  if(s.id==='18'&&after('recovery-converges'))binding.crumb='推进示例｜本例已收拢，订单确认、库存3';
  if(s.id==='18'&&after('rewind-to-stalled-recovery-branch'))binding.crumb='回看另一结果｜恢复暂停，整单仍待确认';
  return {...branchMapSpec,shots:{...branchMapSpec.shots,[s.id]:binding}};
}
