export type EggId=1|2;
export type Outcome={egg:EggId;floor:number;broke:boolean;drop:number};
export type World={id:string;safe:number;breaking:number;drops:number;intact:[boolean,boolean];history:Outcome[]};
export type Trial={egg:EggId;floor:number;broke:boolean};
export const CHECKPOINTS=[14,27,39,50,60,69,77,84,90,95,99,100];
export const TEN_POINTS=[10,20,30,40,50,60,70,80,90,100];
export const emptyWorld=(id:string):World=>({id,safe:0,breaking:101,drops:0,intact:[true,true],history:[]});
export const possible=(w:World)=>[w.safe,w.breaking-1] as const;
export const resolved=(w:World)=>w.breaking-w.safe===1;
export const remaining=(w:World)=>w.intact.filter(Boolean).length;
export const commit=(w:World,t:Trial):World=>{
 if(!w.intact[t.egg-1])throw Error('Broken egg cannot be used');
 if(!Number.isInteger(t.floor)||t.floor<1||t.floor>100)throw Error('Trial must be on an existing floor');
 if(t.floor<=w.safe||t.floor>=w.breaking)throw Error('Trial must split the unknown interval');
 const intact=[...w.intact] as [boolean,boolean];if(t.broke)intact[t.egg-1]=false;
 return {...w,safe:t.broke?w.safe:t.floor,breaking:t.broke?t.floor:w.breaking,drops:w.drops+1,intact,history:[...w.history,{...t,drop:w.drops+1}]};
};
export const trialFor=(F:number,egg:EggId,floor:number):Trial=>({egg,floor,broke:floor>F});
export const run=(F:number,points=CHECKPOINTS)=>{
 if(!Number.isInteger(F)||F<0||F>100)throw Error('F is between 0 and 100');
 let world=emptyWorld('F-'+F);const states=[world],trials:Trial[]=[];
 const test=(egg:EggId,floor:number)=>{const t=trialFor(F,egg,floor);trials.push(t);world=commit(world,t);states.push(world);return t.broke;};
 for(const floor of points){
  if(resolved(world))break;
  if(test(1,floor)){
   while(!resolved(world)){if(test(2,world.safe+1))break;}
   break;
  }
 }
 if(!resolved(world)||world.safe!==F)throw Error('Strategy did not identify threshold');
 return {F,world,states,trials};
};
export const clamp=(v:number,a=0,b=1)=>Math.min(b,Math.max(a,v));
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const ease=(p:number)=>{const t=clamp(p);return t*t*(3-2*t);};
export const STAGES={carry:.22,release:.36,land:.74,commit:.88};
export const trialView=(before:World,trial:Trial,p:number)=>{
 const q=clamp(p),after=commit(before,trial),committed=q>=STAGES.commit;
 return {before,after,world:committed?after:before,trial,p:q,committed,landed:q>=STAGES.land,
  phase:q<STAGES.carry?'carry':q<STAGES.release?'ready':q<STAGES.land?'fall':q<STAGES.commit?'impact':'settled'};
};
export const GROUND=850,EGG_GROUND=820,DETAIL_TOP=350,DETAIL_BOTTOM=806;
export type Focus={low:number;high:number;amount:number};
export const fullFocus:Focus={low:0,high:100,amount:0};
// The detailed façade is explicitly not to scale. Floors outside the focus
// interval are compressed monotonically; ground remains the actual ground.
export const detailY=(floor:number,focus:Focus)=>{
 const global=mix(810,350,floor/100),{low,high,amount}=focus;
 let local:number;
 if(floor<low)local=mix(810,DETAIL_BOTTOM,floor/Math.max(1,low));
 else if(floor>high)local=mix(DETAIL_TOP,318,(floor-high)/Math.max(1,100-high));
 else local=mix(DETAIL_BOTTOM,DETAIL_TOP,(floor-low)/Math.max(1,high-low));
 return mix(global,local,clamp(amount));
};
export const overviewY=(floor:number)=>mix(810,350,floor/100);
export const LANES={1:1135,2:1305};
export const eggPose=(id:EggId,world:World,view:ReturnType<typeof trialView>|null,focus:Focus)=>{
 const base={x:LANES[id],y:world.intact[id-1]?EGG_GROUND:GROUND-24,broke:!world.intact[id-1],holder:false,active:false};
 if(!view||view.trial.egg!==id)return base;
 const p=view.p,top=detailY(view.trial.floor,focus)-30;
 const y=p<STAGES.carry?mix(EGG_GROUND,top,ease(p/STAGES.carry)):p<STAGES.release?top:p<STAGES.land?mix(top,EGG_GROUND,Math.pow((p-STAGES.release)/(STAGES.land-STAGES.release),2)):EGG_GROUND;
 return {...base,y:view.landed&&view.trial.broke?GROUND-24:y,broke:view.landed&&view.trial.broke,holder:p<STAGES.release&&y<=GROUND-60,active:true};
};
export const seeded=(id:string,F:number,floors:number[])=>floors.reduce((w,f)=>commit(w,trialFor(F,1,f)),emptyWorld(id));
export const ACTUAL=run(31);
