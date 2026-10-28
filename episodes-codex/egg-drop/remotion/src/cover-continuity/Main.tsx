import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {shots} from '../data';
import {C,FONT} from './theme';
import {PuzzleCanvas} from '../../../../_shared/puzzles-video/Frame';
import {Head,Note,T,Panel} from './primitives';
import {Building} from './Building';
import {sceneState} from '../scene-state';
import {remaining,resolved,detailY,clamp,ease} from '../egg-model';
import {useLayoutAudit} from '../LayoutAudit';
declare const __HAS_VOICE_AUDIO__:boolean;
const trialLines=(q:ReturnType<typeof sceneState>)=>{
 const pending=q.view?.landed&&!q.view.committed,w=q.world;
 return [{label:'已确认试验次数',value:pending?'结果确认中':`${w.drops}次`},{label:'可用鸡蛋',value:pending?'结果待记入':`${remaining(w)}枚`},{label:'已确认答案范围',value:resolved(w)?`${w.safe}楼`:`${w.safe}～${w.breaking-1}楼`,color:resolved(w)?C.teal:C.text},{label:'当前状态',value:pending?'结果确认中':resolved(w)?'答案已确定':remaining(w)?'继续缩小范围':'答案仍未知',size:30,color:resolved(w)?C.teal:remaining(w)?C.muted:C.red}];
};
export const Scene=({s,f}:{s:any;f:number})=>{
 const q=sceneState(s,f),w=q.world,pending=q.view?.landed&&!q.view.committed,done=!!q.view?.committed,second=f>=q.cues.second;
 const building=<Building {...q}/>;
 let title='',sub='',note='',panel:any=null,extra:any=null;
 switch(s.visualType){
  case 'challenge':title='两枚鸡蛋，怎样保证14次内找到答案？';sub='100层楼；要确定最高安全层，可能从0到100。';note='先找安排试验的方法，再用一局完整示例走一遍';panel=<Panel title="题目与目标" lines={[{label:'给定',value:'两枚相同鸡蛋'},{label:'可试楼层',value:'1～100楼'},{label:'要找',value:'最高安全层',color:C.teal}]}/>;break;
  case 'rules':title='没碎可复用；碎了就少一枚';sub='低于安全界限不碎；高于界限必碎，结果不是随机的。';note=second?'若两枚都碎，且范围内仍有多个答案，就无法继续':'同一枚蛋先在低处没碎，再带到高处试';panel=<Panel title="规则示意" lines={trialLines(q)}/>;break;
  case 'binary-limit':title=w.drops===2?'一直对半，不能保证找到答案':w.drops===1?'50楼已碎，接着用最后一枚试25楼':'试试二分：先50楼，再25楼';sub='失败思考分支：假设连续两次都碎，安全界限始终固定。';note=pending?'落地结果确认中，随后记入次数、蛋数和答案范围':w.drops===2?'两枚蛋已用完；最高安全层仍可能是0～24楼':w.drops===1?'50楼已知会碎，范围0～49楼；再用最后一枚试25楼':'重新从两枚蛋、0次开始，先看50楼这一次试验';panel=<Panel title="二分尝试：失败假设" lines={trialLines(q)}/>;break;
  case 'late-break-cost':title=!second?'换个思路：第一枚圈范围，最后一枚逐层查':done?'100楼才碎：还留下9层待查':'另一晚碎假设：前9次已安全到90楼';sub=!second?'虚线10、20……100楼是计划；两枚蛋、0次，尚未实际试验。':'假设第一枚已在10～90楼试过9次，全都没碎。';note=!second?'第一枚碎后，最后一枚从已知安全层的上一层逐层查':pending?'100楼已碎，正在确认第10次试验结果':done?'91～99楼是待测楼层，最多再用9次，尚未执行':'这是另一个假设分支，先看第10次从100楼落地';panel=!second?<Panel title="固定10层：计划分工" lines={[{label:'第一枚',value:'每隔10层向上试'},{label:'它碎了之后',value:'圈定较小范围'},{label:'最后一枚',value:'从安全层上一层查'}]}/>:<Panel title="固定10层：晚碎代价" lines={[{label:'已确认用掉',value:pending?'结果确认中':`${w.drops}次`},{label:'剩下待测',value:done?'91～99楼':'等100楼结果'},{label:'第二枚最多再试',value:done?'9次':'先看这次落地'},{label:'最坏合计',value:done?'10 + 9 = 19':'等待结果',color:C.gold,size:32}]}/>;break;
  case 'shrinking-gaps':title=second?'越往后，间隔应该越小':'前面已用更多次，后面仍留同样大区间';sub='固定10层的间隔没有变，晚碎时却已经花掉更多次数。';note='要控制最坏次数，先给碎后的逐层查找留够机会';panel=<Panel title="从刚才的代价想办法" lines={[{label:'先前已经用掉',value:'10次'},{label:'同样宽的区间',value:'还要最多9次'},{label:'要调整的是',value:second?'后面的间隔':'剩余查找预算',color:C.gold}]}/>;break;
  case 'first-fourteen':title=done?'若14楼就碎：1次＋最多13次':'以14次为预算，第一步先试14楼';sub='这是预算推演的一个条件分支，尚不是后面的完整示例。';note=done?'最高安全层可能0～13楼；第二枚只需从1到13楼逐层查':'先让第一枚从14楼落地，再看碎后的预算';panel=<Panel title="总预算14次" lines={[{label:'已确认用掉',value:pending?'结果确认中':`${w.drops}次`},{label:'碎后待测',value:done?'1～13楼':'若碎才走此分支'},{label:'最后一枚最多用',value:done?'13次':'先预留13次'},{label:'合计上限',value:done?'1 + 13 = 14':'先看第1次结果',size:31,color:C.gold}]}/>;break;
  case 'next-twenty-seven':title=done?'若27楼碎：2次＋最多12次':'换到14楼没碎的分支：下一次到27楼';sub='分支起点：第一次已安全，还剩13次；所以这次只再跨13层。';note=pending?'27楼已碎，正在确认并记入本次结果':done?'最高安全层可能14～26楼；待测15～26楼，共12层':'当前分支的起点是14楼没碎；接下来试27楼';panel=<Panel title="预算推演：第2次" lines={[{label:'已确认用掉',value:pending?'结果确认中':`${w.drops}次`},{label:'若27楼碎，待测',value:'15～26楼'},{label:'最后一枚最多用',value:'12次'},{label:'合计上限',value:done?'2 + 12 = 14':'先给收尾留12次',size:31,color:C.gold}]}/>;break;
  case 'decreasing-route':title='多试一次，后面的间隔就少跨一层';sub='回到14、27楼都没碎的分支：下一次计划到39楼，再跨12层。';note='后续按剩余预算继续；到了100楼就封顶，不再越过楼顶';panel=<Panel title="同一份14次预算" lines={[{label:'第一次：到14楼',value:'跨14层'},{label:'第二次：到27楼',value:'再跨13层'},{label:'第三次：到39楼',value:'再跨12层',color:C.gold},{label:'后续计划',value:'……100楼封顶',size:30}]}/>;extra=<g>{[[0,14,'14层'],[14,27,'＋13层'],[27,39,'＋12层']].map(([low,high,text]:any)=><g key={high}><path d={`M592 ${detailY(low,q.focus)}h-12V${detailY(high,q.focus)}h12`} fill="none" stroke={C.gold} strokeWidth={2}/><T x={490} y={(detailY(low,q.focus)+detailY(high,q.focus))/2+9} size={25} color={C.gold}>{text}</T></g>)}</g>;break;
  case 'actual-first-egg':title='另一局完整演示：从0次开始';sub='真实安全界限已经固定，暂不揭示；先试14、27，再试39楼。';note=pending?'落地结果确认中，随后记入次数与已知边界':w.drops===3?'第3次39楼碎；已知27安全，39会碎':q.view?.phase==='fall'?`第${w.drops+1}次：从${q.view.trial.floor}楼投下，等待落地`:q.view?.phase==='settled'?`第${w.drops}次没碎：该楼层已确认安全`:w.drops===0?'新的完整示例：从两枚蛋、0次试验开始':'没碎的第1枚可以复用，继续带到下一楼层';panel=<Panel title="完整示例 · 从0次开始" lines={trialLines(q)}/>;break;
  case 'actual-linear':title='只剩第2枚：从28楼开始逐层试';sub='39楼碎时，起初圈定27～38楼；39楼已知会碎，不必再试。';note='每次落地没碎后，才把已知安全线推进到该楼层';panel=<Panel title="同一局：逐层缩小范围" lines={trialLines(q)}/>;break;
  case 'threshold-found':title=done?'31楼安全、32楼会碎，答案就是31楼':'31楼已经安全，接着试32楼';sub=done?'这局第8次完成；两枚都碎，最高安全层也已经唯一确定。':'同一枚第2枚鸡蛋，从32楼投下，到地面后再确认结果。';note=done?'最高安全层是31楼；32楼是会碎的楼层':'已知安全31楼，接着看32楼的落地结果';panel=<Panel title={done?'答案已确定':'同一局：最后一次试验'} lines={trialLines(q)}/>;break;
  case 'closing':title='这局用了8次，方案保证最多14次';sub='每次往上跨之前，先给碎后的逐层查找留足次数。';note='IT小村 · 原创';panel=<Panel title="两种次数，分开来看" lines={[{label:'这局最高安全层',value:'31楼',color:C.teal},{label:'本局实际试验',value:'8次',color:C.teal},{label:'方案的保证上限',value:'最多14次',color:C.gold},{label:'适用于',value:'任意安全界限',size:28}]}/>;break;
  default:throw Error('Unknown visualType '+s.visualType);
 }
 return <><Head title={title} sub={sub}/><T x={120} y={268} size={22} color={C.gold} data-world-mode="true">{q.mode}</T>{building}{panel}{extra}<Note>{note}</Note><g data-visual-state={JSON.stringify({type:s.visualType,frame:f,world:w,trial:q.view?{p:q.view.p,trial:q.view.trial,phase:q.view.phase,landed:q.view.landed,committed:q.view.committed}:null,focus:q.focus,mode:q.mode})}/></>;
};
const ShotView=({s,hideSubtitles=false,auditLayout=false}:any)=>{
 const f=useCurrentFrame(),caption=(s.subtitles??[]).find((x:any)=>f>=x.from&&f<(x.to!==undefined?x.to+1:x.from+(x.duration??0)));useLayoutAudit(auditLayout,'main',s.from+f);
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT,color:C.text}}><svg data-audit-scene="true" width={1920} height={1080} viewBox="0 0 1920 1080"><PuzzleCanvas/><Scene s={s} f={f}/><T x={1795} y={82} size={26} color={C.muted} anchor="end">IT小村</T></svg>{!hideSubtitles&&caption&&<div data-subtitle="true" style={{position:'absolute',left:160,right:160,bottom:54,textAlign:'center',fontFamily:FONT,fontSize:31,lineHeight:1.45,color:C.text}}>{caption.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false,auditLayout=false}:{hideSubtitles?:boolean;auditLayout?:boolean})=><AbsoluteFill style={{background:C.bg}}>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles} auditLayout={auditLayout}/></Sequence>)}</AbsoluteFill>;
