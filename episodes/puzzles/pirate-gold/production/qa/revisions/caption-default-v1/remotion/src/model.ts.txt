import data from '../../model-data.json';
export type Allocation=Record<string,number>;
export type Round={n:number;players:number[];quota:number;allocation:Allocation};
export const rounds=data.rounds as Round[];
export const round=(n:number):Round=>{const r=rounds.find(r=>r.n===n);if(!r)throw Error('No pirate round '+n);return r;};
export const previous=(n:number):Allocation=>n>1?round(n-1).allocation:{};
export const isYes=(n:number,id:number)=>id===round(n).players[0]||round(n).allocation[String(id)]>(previous(n)[String(id)]??0);
export const CX=[280,620,960,1300,1640];
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const tween=(f:number,a:number,b:number)=>{const p=clamp((f-a)/Math.max(1,b-a));return p*p*(3-2*p);};
export const timings=(s:any)=>{const a=s.voice?.[0]?.localStart??0,b=s.voice?.[0]?.localEnd??s.durationInFrames*.45,c=s.voice?.[1]?.localStart??s.durationInFrames*.52,e=s.voice?.[1]?.localEnd??s.durationInFrames-20;return {a,b,c,e};};
/** Ballots enter sequentially. No ballot counts before it arrives in its slot. */
export const election=(s:any,n:number,f:number)=>{const {c,e}=timings(s),r=round(n),start=c+(n===2?40:8),step=Math.min(22,Math.max(14,(e-c-60)/Math.max(1,r.players.length-1))),arrivals=Object.fromEntries(r.players.map((id,i)=>[String(id),start+i*step])),last=start+(r.players.length-1)*step,yes=r.players.filter(id=>f>=arrivals[String(id)]&&isYes(n,id)).length;return {arrivals,yes,quota:r.quota,passAt:last+8,passed:f>=last+8&&yes>=r.quota};};
for(const r of rounds){if(Object.values(r.allocation).reduce((a,b)=>a+b,0)!==100||r.quota!==Math.ceil(r.n/2))throw Error('Invalid model round '+r.n);}
