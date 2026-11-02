import storyboard from '@storyboard';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;durationInFrames:number;from:number;narration?:string;subtitles?:Subtitle[];voice?:{localStart:number;localEnd:number}[];[key:string]:any};
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((s:any)=>s.shots??[]).map((s:any)=>{
 const item={...s,id:String(s.id).padStart(2,'0'),from:offset};offset+=s.durationInFrames;return item;
});
export const PREVOICE=(storyboard.meta?.timingSource as any)?.kind==='PREVOICE_ESTIMATED_NOT_ACTUAL_VOICE';
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
