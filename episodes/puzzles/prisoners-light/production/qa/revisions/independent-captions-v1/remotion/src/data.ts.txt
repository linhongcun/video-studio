import storyboard from '@storyboard';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;from:number;durationInFrames:number;voice:{localStart:number;localEnd:number}[];subtitles?:Subtitle[];[key:string]:any};
export const PROVISIONAL=Boolean(storyboard.meta?.provisionalTiming||storyboard.meta?.pendingAudio);
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((scene:any)=>scene.shots??[]).map((s:any)=>{
  if(!s.voice||s.voice.length!==2||s.voice.some((v:any)=>!Number.isFinite(v.localStart)||!Number.isFinite(v.localEnd)||v.localEnd<=v.localStart))throw Error('P10 requires two measured sentence windows: '+s.id);
  const shot={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=s.durationInFrames;return shot;
});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:Math.max(1,offset)};
