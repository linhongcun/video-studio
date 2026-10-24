import type {BranchMapSpec} from '../../../_shared/branch-map';
import {actualNavState,navigationEvents} from '../../../_shared/branch-map';
import type {Shot} from './data';
import {W} from './motion';

export const branchMap:BranchMapSpec={
 title:'同一条依赖调用：三个状态，按条件切换',
 overviewTitle:'一处故障，怎样暂停调用并谨慎恢复？',
 overviewHint:'关闭时正常转发，打开时阻断；下游修复仍需另外处理。',
 nodes:[
  {id:'closed',label:'关闭\n正常转发请求',x:400,y:430,w:360,color:'#56E4D3'},
  {id:'open',label:'打开\n不再调用下游',x:960,y:430,w:360,color:'#FF929B'},
  {id:'half',label:'半开\n只放少量探测',x:1520,y:430,w:360,color:'#FFCC70'},
  {id:'baseline',label:'没有熔断保护\n等待逐步积累',x:400,y:740,w:340,color:'#91A5BA'},
 ],
 edges:[
  {id:'closed-open',from:'closed',to:'open',label:'失败达到设定条件',labelAt:[680,397],color:'#FF929B'},
  {id:'open-half',from:'open',to:'half',label:'等待条件满足',labelAt:[1240,397],color:'#FFCC70'},
  {id:'half-open',from:'half',to:'open',label:'探测失败，再等待',via:[[1520,650],[960,650]],labelAt:[1240,650],color:'#FF929B'},
  {id:'half-closed',from:'half',to:'closed',label:'满足恢复条件',via:[[1520,285],[400,285]],labelAt:[960,285],color:'#56E4D3'},
 ],
 shots:{
  '01':{focus:'open',activeNodes:['closed','open','half'],activeEdges:['closed-open','open-half'],crumb:'问题 → 可选依赖故障，订单仍能提交',exit:{zoom:24,hold:30},overviewHint:'先看无保护对照，再看三种调用状态；它们不是订单的成功与失败。'},
  '02':{focus:'baseline',activeNodes:['baseline'],activeEdges:[],crumb:'教学对照 → 无保护时，请求持续等待',enter:{hold:18,zoom:24},overviewTitle:'先看无保护对照：等待为何会累积？',overviewHint:'灰色区域是教学对照，不属于上述三态。'},
  '03':{focus:'baseline',activeNodes:['baseline'],activeEdges:[],crumb:'教学对照 → 等待占满共享资源',exit:{zoom:24,hold:28},overviewTitle:'对照看完，再加入调用保护',overviewHint:'无保护与有保护是两种教学情景，之间没有状态转移箭头。'},
  '04':{focus:'closed',activeNodes:['closed'],activeEdges:['closed-open'],crumb:'关闭 → 仍然转发，同时观察近期失败',enter:{hold:16,zoom:24},exit:{zoom:24,hold:20},overviewTitle:'关闭仍会转发，失败达条件才打开',overviewHint:'先观察调用结果；只有满足条件，才切换为阻断该依赖。'},
  '05':{focus:'open',activeNodes:['open'],activeEdges:[],crumb:'打开 → 请求不再访问故障下游',enter:{hold:18,zoom:24},overviewTitle:'打开：阻断调用，立即反馈不可用',overviewHint:'打开不是修好下游，而是暂时不再向它发送调用。'},
  '06':{focus:'open',activeNodes:['open'],activeEdges:[],crumb:'打开的反馈 → 业务规则另行决定是否继续'},
  '07':{focus:'open',activeNodes:['open'],activeEdges:['open-half'],crumb:'打开 → 等待条件满足，再少量试探',exit:{zoom:24,hold:18},overviewTitle:'等待后少量试探，不直接恢复全量',overviewHint:'必要库存和支付校验照常进行；恢复取决于探测结果。'},
  '08':{focus:'half',activeNodes:['half'],activeEdges:['half-open'],crumb:'半开 → 只放少量请求验证下游',enter:{hold:18,zoom:24},exit:{zoom:24,hold:24},overviewTitle:'若少量探测失败，就回到打开',overviewHint:'若探测失败，返回打开并重新等待；满足恢复条件才回关闭。'},
  '09':{focus:'half',activeNodes:['half'],activeEdges:['open-half'],crumb:'等待后新一轮 → 少量探测，验证恢复条件',enter:{hold:26,zoom:26},exit:{zoom:20,hold:8},overviewTitle:'等待后，再做一轮少量试探',overviewHint:'上一轮失败后先等待，再开始新一轮；满足条件才恢复正常调用。'},
  '10':{focus:'closed',mode:'overview',activeNodes:['closed','open','half'],activeEdges:['closed-open','open-half','half-open','half-closed'],overviewTitle:'回到全局：阻断、探测，再按条件恢复',overviewHint:'熔断控制调用；业务处置与下游修复各有自己的责任。'},
 }
};

export const breakerTermVisible=(s:Shot,f:number)=>Number(s.id)>5||(s.id==='05'&&f>=Number(s.cueFrames?.breakerLabel??1));
export const comparisonHeading=(s:Shot,f:number)=>breakerTermVisible(s,f)?'教学对照（不属于熔断状态）':'教学对照（不属于上述三态）';

export function navigationSpec(s:Shot,f:number):BranchMapSpec {
 let binding={...branchMap.shots[s.id]};
 if(s.id==='04'&&f>=W.failures[2])binding={...binding,activeNodes:['open'],crumb:'失败达到条件 → 切换打开，阻断该依赖'};
 if(s.id==='08'&&f>=W.failedProbeReply[1])binding={...binding,activeNodes:['open'],crumb:'探测仍失败 → 回到打开，重新等待',overviewTitle:'探测失败后，回到打开并重新等待'};
 if(s.id==='09'){
  if(f<26)binding={...binding,activeNodes:['open'],crumb:'上轮失败后等待 → 即将开始新一轮试探'};
  if(f>=W.newProbeReply[1])binding={...binding,activeNodes:['closed'],activeEdges:['half-closed'],crumb:'探测满足恢复条件 → 切回关闭，恢复正常转发',overviewTitle:'满足恢复条件，回到关闭并正常转发'};
 }
 const nodes=branchMap.nodes.map(n=>n.id==='baseline'&&!breakerTermVisible(s,f)?{...n,label:'没有调用保护\n等待逐步积累'}:n);
 return {...branchMap,nodes,shots:{...branchMap.shots,[s.id]:binding}};
}
export function navigationContext(s:Shot,f:number){return {spec:navigationSpec(s,f),shotId:s.id,frame:f,durationInFrames:s.durationInFrames};}
export function navigationState(s:Shot,f:number){return actualNavState(navigationSpec(s,f),s.id,f,s.durationInFrames);}
export function navigationFrameSamples(s:Shot){return navigationEvents(branchMap,s.id,s.durationInFrames);}
