import type {Shot} from './data';
import {eventAt} from './motion';
import {actualNavState} from '../../../_shared/branch-map';

// Only real TCC operations form the tree. Retries stay in their selected leaf.
const BASE:any={
 title:'先预留，再选择一个结局',
 overviewTitle:'一件库存，先留住，再按结果处理',
 overviewHint:'确认与释放是互斥结局；同一笔操作只选择一条。',
 nodes:[
  {id:'reserve',label:'检查并预留',x:380,y:510,w:290,kind:'step',color:'#FFCC70'},
  {id:'decide',label:'各方都能完成？',x:900,y:510,w:310,kind:'decision'},
  {id:'confirm',label:'确认：转为已售',x:1490,y:350,w:340,kind:'success'},
  {id:'cancel',label:'取消：释放预留',x:1490,y:710,w:340,kind:'failure'},
 ],
 edges:[
  {id:'reserve-decide',from:'reserve',to:'decide'},
  {id:'confirm-path',from:'decide',to:'confirm',label:'都已就绪',via:[[1165,510],[1165,350]]},
  {id:'cancel-path',from:'decide',to:'cancel',label:'有一方拒绝',via:[[1165,510],[1165,710]]},
 ],
 shots:{
  '01':{focus:'reserve',mode:'overview',activeNodes:[],activeEdges:[],crumb:'先看冲突 → 认识完整处理路线'},
  '02':{focus:'reserve',mode:'overview',activeNodes:['reserve'],activeEdges:[],crumb:'全图：先预留，后面两种结果'},
  '03':{focus:'reserve',mode:'focus',activeNodes:['reserve'],activeEdges:[],crumb:'当前位置：检查与预留',enter:{hold:0,zoom:30}},
  '04':{focus:'reserve',mode:'focus',activeNodes:['reserve'],activeEdges:[],crumb:'预留：真正保存本单的一件'},
  '05':{focus:'reserve',mode:'focus',activeNodes:['reserve'],activeEdges:[],crumb:'预留后：本单资源归属'},
  '06':{focus:'decide',mode:'focus',activeNodes:['reserve','decide'],activeEdges:['reserve-decide'],crumb:'共同前置 → 协调各方并记录决定',exit:{zoom:24,hold:0}},
  '07':{focus:'confirm',mode:'focus',activeNodes:['reserve','decide','confirm'],activeEdges:['reserve-decide','confirm-path'],crumb:'成功路径：使用本单预留',enter:{hold:0,zoom:30}},
  '08':{focus:'confirm',mode:'focus',activeNodes:['confirm'],activeEdges:['confirm-path'],crumb:'仍在确认结局：同一请求安全重放',exit:{zoom:24,hold:0}},
  '09':{focus:'reserve',mode:'focus',activeNodes:['reserve'],activeEdges:[],crumb:'另一种结果：从初始状态重新演示',enter:{hold:30,zoom:30}},
  '10':{focus:'decide',mode:'focus',activeNodes:['reserve','decide'],activeEdges:['reserve-decide'],crumb:'失败路径 → 先记录取消决定',exit:{zoom:24,hold:0}},
  '11':{focus:'cancel',mode:'focus',activeNodes:['reserve','decide','cancel'],activeEdges:['reserve-decide','cancel-path'],crumb:'失败路径：只释放本单预留',enter:{hold:0,zoom:30}},
  '12':{focus:'cancel',mode:'focus',activeNodes:['cancel'],activeEdges:['cancel-path'],crumb:'仍在释放结局：同一请求安全重放',exit:{zoom:24,hold:0}},
  '13':{focus:'reserve',mode:'focus',activeNodes:['reserve'],activeEdges:[],crumb:'回看预留规则 · 不是取消后再次执行',enter:{hold:20,zoom:30},exit:{zoom:24,hold:0}},
  '14':{focus:'decide',mode:'overview',activeNodes:['reserve','decide'],activeEdges:['reserve-decide'],crumb:'全图回顾：两个结局只能选择其一'},
 },
};
export const branchMapFor=(s:Shot,f:number)=>{
 const current={...BASE.shots[s.id]};
 let overviewTitle=BASE.overviewTitle,overviewHint=BASE.overviewHint;
 if(s.id==='01'){
  overviewTitle='问题：直接售出后被拒绝，怎么收尾？';
  overviewHint='接下来换用预留方案；刚才的直接售出是反例。';
 }
 if(s.id==='02'){
  overviewTitle=f>=Number(s.cueFrames?.labels?.TCC??1)?'TCC：先预留，再按决定处理':'一件库存，先留住再决定';
  overviewHint='先看共同前置：预留；再分别看确认和释放。';
 }
 if(s.id==='06'){
  const decided=f>=eventAt(s,'confirm-decision-durable');
  current.activeNodes=decided?['reserve','decide','confirm']:['reserve','decide'];
  current.activeEdges=decided?['reserve-decide','confirm-path']:['reserve-decide'];
  overviewHint=decided?'确认决定已记录，接下来进入成功路径。':'库存已预留为3/1/0，协调者等待各方结果。';
 }
 if(s.id==='09'){
  const reserved=f>=eventAt(s,'second-branch-reservation'),refused=f>=eventAt(s,'other-side-refused');
  current.activeNodes=reserved?['reserve','decide']:['reserve'];
  current.activeEdges=reserved?['reserve-decide']:[];
  overviewTitle='另一种结果：从初始状态重置演示';
  overviewHint=refused?'本分支已预留，但另一边拒绝；接着看取消。':reserved?'本分支先预留：3/1/0，等待其他方结果。':'另一结果：从4/0/0重新演示，未接在成功之后。';
 }
 if(s.id==='10'){
  const cancelled=f>=eventAt(s,'cancel-decision-durable');
  current.activeNodes=cancelled?['reserve','decide','cancel']:['reserve','decide'];
  current.activeEdges=cancelled?['reserve-decide','cancel-path']:['reserve-decide'];
  overviewHint=cancelled?'取消决定已记录，只释放本单预留。':'收到拒绝，先记录取消；预留还没有释放。';
 }
 if(s.id==='13'){
  overviewTitle='回看前置规则：预留为什么能继续被管理？';
  overviewHint='回看预留规则，不代表取消后再次预留。';
 }
 if(s.id==='14'){
  const cancelled=f>=eventAt(s,'switch-to-separate-cancel-outcome'),confirmed=f>=eventAt(s,'show-confirm-outcome');
  current.activeNodes=cancelled?['reserve','decide','cancel']:confirmed?['reserve','decide','confirm']:['reserve','decide'];
  current.activeEdges=cancelled?['reserve-decide','cancel-path']:confirmed?['reserve-decide','confirm-path']:['reserve-decide'];
  overviewTitle=cancelled?'全图回顾：另一条互斥的取消结局':'全图回顾：先预留，再选择一种结果';
  overviewHint=cancelled?'这里回看另一路，不表示确认后再取消；重复请求不另开结局。':confirmed?'成功路径用掉本单预留；接下来回看另一种结果。':'共同前置是先预留，确认与释放只能选择一条。';
 }
 return {...BASE,overviewTitle,overviewHint,shots:{...BASE.shots,[s.id]:current}};
};

export const navigationState=(s:Shot,f:number)=>s.id==='01'&&f<90
 ? {phase:'opening-conflict',progress:1,focusId:'problem',camera:{cx:960,cy:450,scale:1,tx:0,ty:0}}
 : actualNavState(branchMapFor(s,f),s.id,f,s.durationInFrames);
