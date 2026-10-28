/** Single-partition teaching model. Policy checks describe this application's
 * deliberate processing order, not constraints enforced by Kafka itself. */
export type LogRecord={offset:number;orderId:string};
export type State={log:LogRecord[];confirmedThrough:number;readPosition:number;committedOffset:number|null;processing:string|null;businessResults:string[];pageState:'not-submitted'|'accepted'|'complete'};
export const initial=():State=>({log:[],confirmedThrough:-1,readPosition:0,committedOffset:null,processing:null,businessResults:[],pageState:'not-submitted'});
const demand=(ok:boolean,message:string)=>{if(!ok)throw new Error(message);};
export function append(s:State,orderId:string):State{
 demand(!s.log.some(r=>r.orderId===orderId),'Teaching order identity must be unique');
 return {...s,log:[...s.log,{offset:s.log.length,orderId}]};
}
export function confirmWrite(s:State,offset:number):State{
 demand(Number.isInteger(offset)&&offset>=0&&offset<s.log.length,'Confirm an actual appended record');
 return {...s,confirmedThrough:Math.max(s.confirmedThrough,offset)};
}
export function replyAccepted(s:State,orderId='7042'):State{
 const r=s.log.find(r=>r.orderId===orderId);demand(!!r&&r.offset<=s.confirmedThrough,'This example replies after successful producer confirmation');
 return {...s,pageState:'accepted'};
}
/** Producer confirmation and consumer reads are not globally ordered by Kafka.
 * The main teaching path confirms first, then resumes reading by application choice. */
export function readNext(s:State):State{
 demand(s.processing===null,'Single consumer handles one current task in this example');
 const r=s.log[s.readPosition];demand(!!r,'No record at the current read position');
 return {...s,readPosition:s.readPosition+1,processing:r.orderId};
}
export function saveBusiness(s:State):State{
 demand(s.processing!==null,'Need a task currently being processed');
 return {...s,businessResults:[...s.businessResults,s.processing!],processing:null};
}
export function commit(s:State,nextOffset:number):State{
 demand(Number.isInteger(nextOffset)&&nextOffset>=0&&(s.committedOffset===null||nextOffset>=s.committedOffset)&&nextOffset<=s.readPosition,'Commit progress must be within this example’s read range');
 demand(s.log.filter(r=>r.offset<nextOffset).every(r=>s.businessResults.includes(r.orderId)),'This example commits only after sequential business success');
 return {...s,committedOffset:nextOffset};
}
export function queryResult(s:State,orderId='7042'):State{
 return {...s,pageState:s.businessResults.includes(orderId)?'complete':'accepted'};
}
export const unfinished=(s:State)=>s.log.length-s.businessResults.length;
export function runMainExample(){
 let s=initial();s=append(s,'7042');s=append(s,'7043');s=append(s,'7044');
 const appended=s;
 s=confirmWrite(s,2);s=replyAccepted(s);const accepted=s;
 s=readNext(s);const read=s;
 s=saveBusiness(s);const saved=s;
 s=commit(s,1);const committed=s;
 s=queryResult(s);const queried=s;
 let drained=s;drained=readNext(drained);drained=saveBusiness(drained);drained=commit(drained,2);drained=readNext(drained);drained=saveBusiness(drained);drained=commit(drained,3);
 return {appended,accepted,read,saved,committed,queried,drained};
}
export function flowWindow(seconds:number,perSecondIn=2,perSecondComplete=1){
 demand(Number.isInteger(seconds)&&seconds>=0,'Use complete nonnegative teaching windows');
 const entered=seconds*perSecondIn,completed=seconds*Math.min(perSecondComplete,perSecondIn);
 return {seconds,entered,completed,unfinished:entered-completed};
}
