import type {Shot,HeapEvent} from './data';
export const clamp=(x:number)=>Math.max(0,Math.min(1,x));
export const ease=(x:number)=>{x=clamp(x);return x*x*(3-2*x);};
export const end=(s:Shot)=>s.codeCardFrom??s.durationInFrames-10;
export const at=(s:Shot,i:number,p:number)=>{const a=s.cueFrames?.sentences?.[i]??(i?s.durationInFrames*.5:0),b=s.cueFrames?.sentences?.[i+1]??end(s);return a+(b-a)*p;};
export type Beat=[number,number,number];
export const BEATS:Record<string,{initial:number;beats:Beat[]}>={
 name:{initial:0,beats:[[1,.10,1],[1,.7,2]]},
 'push-two':{initial:2,beats:[[0,.12,3],[0,.48,4],[1,.16,5],[1,.74,6]]},
 'push-three':{initial:6,beats:[[0,.10,7],[0,.46,8],[1,.15,9],[1,.72,10]]},
 'push-four':{initial:10,beats:[[0,.13,11],[0,.58,12],[1,.15,13]]},
 'pop-three':{initial:13,beats:[[0,.10,14],[0,.48,15],[1,.05,16],[1,.24,17],[1,.48,18],[1,.82,19]]},
 'push-five':{initial:19,beats:[[0,.14,20],[0,.60,21],[1,.12,22]]},
 'pop-two':{initial:22,beats:[[0,.06,23],[0,.27,24],[0,.46,25],[0,.60,26],[0,.75,27],[1,.05,28]]},
 'push-six':{initial:28,beats:[[0,.08,29],[0,.35,30],[0,.64,31],[1,.10,32],[1,.41,33],[1,.79,34]]},
 'pop-six':{initial:34,beats:[[0,.18,35],[1,.08,36],[1,.28,37],[1,.44,38],[1,.58,39],[1,.82,40]]},
};
export type Playback={event:HeapEvent;previous:HeapEvent;p:number};
export const fixed=(id:number,events:HeapEvent[]):Playback=>({event:events[id],previous:events[id],p:1});
export function play(s:Shot,f:number,events:HeapEvent[]):Playback{
 const cfg=BEATS[s.visualType];if(!cfg)return fixed(40,events);
 if(!cfg.beats.length||f<at(s,cfg.beats[0][0],cfg.beats[0][1]))return fixed(cfg.initial,events);
 let id=cfg.initial,previous=id,start=0,next=end(s);
 for(let i=0;i<cfg.beats.length;i++){const b=cfg.beats[i],t=at(s,b[0],b[1]);if(f<t){next=t;break;}previous=id;id=b[2];start=t;next=i+1<cfg.beats.length?at(s,cfg.beats[i+1][0],cfg.beats[i+1][1]):end(s);}
 return {event:events[id],previous:events[previous],p:ease((f-start)/Math.max(1,Math.min(24,(next-start)*.7)))};
}

// Pure timing helper for independent motion review; all values are local frames.
export function actionWindows(s:Shot){
 const cfg=BEATS[s.visualType];if(!cfg)return [];
 return cfg.beats.map((b,i)=>{const start=at(s,b[0],b[1]),next=i+1<cfg.beats.length?at(s,cfg.beats[i+1][0],cfg.beats[i+1][1]):end(s);return {eventId:b[2],start,end:start+Math.max(1,Math.min(24,(next-start)*.7)),next};});
}
