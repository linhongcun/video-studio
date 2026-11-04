import protocol from '../../model-data.json';
import {Shot} from './data';
export const model=protocol;
export const example=protocol.mainExample;
export type State=typeof example.initial;
export type Step=typeof example.steps[number];
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const between=(n:number,a:number,b:number)=>clamp((n-a)/Math.max(1,b-a));
export const ease=(n:number)=>{const p=clamp(n);return p*p*(3-2*p);};
export const times=(s:Shot)=>({a:s.voice[0].localStart,b:s.voice[0].localEnd,c:s.voice[1].localStart,e:s.voice[1].localEnd});
export const windowAt=(a:number,b:number,p:number)=>a+(b-a)*p;
export const EVENTS_BY_SHOT:Record<number,number[]>={5:[0],6:[1,2],7:[3,4],8:[5,6],9:[7,8],10:[9,10],11:[11]};
export type Presentation={state:State;event:Step|null;actor:number|null;progress:number;stage:'before'|'observe'|'switch'|'remember-or-count'|'settled';actionCommitted:boolean;completedVisits:number;transitioning:boolean;declarationVisible:boolean};
/** The authoritative before/after states come from the verified protocol data.
 * Microsteps explain one isolated visit: no other actor enters mid-operation.
 * Stable states are exact model states; switch-to-memory/count is explicitly in-flight.
 */
export const walkPresentation=(s:Shot,f:number):Presentation=>{
  const q=Number(s.id),indices=EVENTS_BY_SHOT[q];if(!indices)throw Error('Not a main-example shot: '+s.id);
  const {a,b,c,e}=times(s),first=example.steps[indices[0]];
  const windows=indices.map((index,i)=>({step:example.steps[index],start:q===5?c:i===0?a:c,end:q===5?e:i===0?b:e}));
  let current=windows[0];
  if(windows.length===2&&f>=windows[1].start)current=windows[1];
  if(f<current.start)return {state:first.before,event:null,actor:null,progress:0,stage:'before',actionCommitted:false,completedVisits:first.visitNumber-1,transitioning:false,declarationVisible:false};
  const step=current.step,p=between(f,current.start,current.end),state={...step.before,sentIds:[...step.before.sentIds]};
  const isSend=step.action==='send_once',isReceive=step.action==='receive_and_increment',switchAt=.43,memoryAt=.66,commitAt=.78;
  let stage:Presentation['stage']=p<switchAt?'observe':p<memoryAt?'switch':p<commitAt?'remember-or-count':'settled';
  if(isSend&&p>=switchAt)state.light=true,state.lightState='on';
  if(isReceive&&p>=switchAt)state.light=false,state.lightState='off';
  if(p>=memoryAt){state.sentIds=[...step.after.sentIds];state.count=step.after.count;}
  const committed=p>=commitAt;
  if(committed)Object.assign(state,step.after);
  // The final declaration follows OFF and the counter increment, at the start
  // of the second explanatory sentence, rather than appearing with the visitor.
  const declarationVisible=state.declared&&(q!==11||f>=c+(e-c)*.12);
  return {state,event:step,actor:step.actorId,progress:p,stage,actionCommitted:committed,completedVisits:committed?step.visitNumber:step.visitNumber-1,transitioning:(isSend||isReceive)&&p>=switchAt&&p<commitAt,declarationVisible};
};
export const actionText=(p:Presentation)=>{
  if(!p.event)return '等待下一次进入';
  const a=p.event.action;
  if(p.progress<.22)return '先观察灯态和自己的记忆';
  if(a==='send_once')return p.progress<.43?'未发 ＋ 灯灭，可以发送':p.progress<.66?'先开灯，留下一份待收信号':p.progress<.78?'再记住自己已成功发过':'本次成功发送；累计值暂不增加';
  if(a==='receive_and_increment')return p.progress<.43?'看见灯亮，有一份信号可收':p.progress<.66?'先关灯，接收这一份':p.progress<.78?'私有累计 ＋1':'本次接收完成';
  if(a==='wait_light_on_keep_eligibility')return '灯亮，先不动；自己的资格仍在';
  if(a==='already_sent_noop')return '已经成功发过，亮灭都不再开灯';
  return '灯灭，没有新信号；累计不变';
};
