import {World,Trial,Focus,ACTUAL,TEN_POINTS,CHECKPOINTS,emptyWorld,seeded,trialFor,trialView,commit,fullFocus,ease,clamp,mix} from './egg-model';
import {actionWindows,progress,cues,Window} from './timeline';
const fixedTenBefore=seeded('fixed-ten-F99',99,TEN_POINTS.slice(0,-1));
const fixedTenAfter=commit(fixedTenBefore,trialFor(99,1,100));
export const sequenceAt=(initial:World,trials:Trial[],windows:Window[],f:number)=>{
 let world=initial,view:ReturnType<typeof trialView>|null=null;
 for(let i=0;i<trials.length;i++){
  const w=windows[i];if(!w)throw Error('Missing physical trial window');
  if(f<w.start)break;
  view=trialView(world,trials[i],progress(f,w));
  if(f<w.end)return {world:view.world,view};
  world=view.after;
 }
 return {world,view};
};
export const sceneState=(s:any,f:number)=>{
 let world=emptyWorld(s.visualType),trials:Trial[]=[],focus:Focus=fullFocus,planned:number[]=[],selected:number|null=null,extraFloors:number[]=[],mode='',note='';
 switch(s.visualType){
  case 'challenge':mode='题目 · 安全界限固定但未知';break;
  case 'rules':mode='规则示意 · 不属于后面的解题局';trials=[trialFor(40,1,20),trialFor(40,1,60)];break;
  case 'binary-limit':mode='失败思考分支 · 重新从两枚蛋、0次开始，尝试连续对半';world=emptyWorld('binary-limit-hypothesis');trials=[trialFor(12,1,50),trialFor(12,2,25)];extraFloors=[50];break;
  case 'late-break-cost':if(f<cues(s).second){mode='另看固定间隔计划 · 重新从两枚蛋、0次规划';world=emptyWorld('fixed-ten-plan-revision');planned=TEN_POINTS;extraFloors=[10,20];}else{mode='晚碎假设起点：前9次均未碎，已知90楼安全';world=fixedTenBefore;focus={low:90,high:100,amount:ease(clamp((f-cues(s).second)/40))};trials=[trialFor(99,1,100)];}break;
  case 'shrinking-gaps':mode='回看刚才的晚碎分支 · 已完成结果';world=fixedTenAfter;focus={low:90,high:100,amount:1};planned=[91,92,93,94,95,96,97,98,99];break;
  case 'first-fourteen':mode='预算推演① · 假设第1次在14楼碎';world=emptyWorld('budget-break14');focus={low:0,high:14,amount:1};trials=[trialFor(13,1,14)];extraFloors=[1,13];break;
  case 'next-twenty-seven':mode='另一分支起点：14楼没碎，两枚可用';world=seeded('budget-break27',26,[14]);focus={low:14,high:27,amount:1};planned=[27];trials=[trialFor(26,1,27)];extraFloors=[15,26];break;
  case 'decreasing-route':mode='回到14、27楼均没碎的分支 · 后续为计划';world=seeded('budget-survived27',31,[14,27]);planned=[14,27,39,100];extraFloors=[14,27,39];break;
  case 'actual-first-egg':mode='另一局完整示例 · 重新开始，真实界限固定';world=ACTUAL.states[0];focus={low:0,high:45,amount:1};trials=ACTUAL.trials.slice(0,3);break;
  case 'actual-linear':{const p=ease(clamp(f/48));mode='同一局继续 · 只剩第2枚，安全蛋反复使用';world=ACTUAL.states[3];focus={low:mix(0,27,p),high:mix(45,39,p),amount:1};trials=ACTUAL.trials.slice(3,7);break;}
  case 'threshold-found':mode='同一局继续 · 已知31安全，再试32楼';world=ACTUAL.states[7];focus={low:27,high:39,amount:1};trials=ACTUAL.trials.slice(7);break;
  case 'closing':mode='这局已完成 · 实际次数与保证上限分开';world=ACTUAL.world;focus={low:27,high:39,amount:1};break;
  default:throw Error('Unknown visualType '+s.visualType);
 }
 const windows=actionWindows(s),sequence=sequenceAt(world,trials,windows,f);
 return {...sequence,focus,planned,selected,extraFloors,mode,windows,trials,cues:cues(s)};
};
