import storyboard from '@storyboard';
export type Subtitle={text:string;from:number;to?:number;duration?:number};
export type Shot={id:string;durationInFrames:number;from:number;visualType:string;subtitles?:Subtitle[];cueFrames?:Record<string,any>;[key:string]:any};
let offset=0;
export const shots:Shot[]=(storyboard.scenes??[]).flatMap((scene:any)=>scene.shots??[]).map((shot:any)=>{
 const item={...shot,id:String(shot.id).padStart(2,'0'),from:offset};offset+=shot.durationInFrames;return item;
});
export const VIDEO={width:1920,height:1080,fps:30,durationInFrames:offset};
export const NUMS=[1,3,5,7,9,11,13,15];
