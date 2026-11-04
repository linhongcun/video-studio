import model from '../../model-data.json';
import type {Shot} from './data';
export const hats=model.smallExample.hats;
export const CX=[280,620,960,1300,1640];
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const tween=(f:number,a:number,b:number)=>{const p=clamp((f-a)/Math.max(1,b-a));return p*p*(3-2*p);};
export const word=(bit:number)=>bit?'黑':'白';
export const parity=(bit:number)=>bit?'奇':'偶';
export const state=(speaker:number)=>{const s=model.smallExample.states.find(s=>s.speaker===speaker);if(!s)throw Error('Missing hat state '+speaker);return s;};
/** All animation boundaries derive from measured sentence frames, never estimated voice duration. */
export const timings=(s:Shot)=>{if(s.voice?.length!==2)throw Error('Shot '+s.id+' needs two measured sentences');const [first,last]=s.voice;return {a:first.localStart,b:first.localEnd,c:last.localStart,e:last.localEnd};};
export const answerCues=(s:Shot,part=.43)=>{const {c,e}=timings(s);return {inferAt:Math.round(c+(e-c)*part),sayAt:Math.round(c+(e-c)*.76)};};
if(hats.join(',')!=='0,1,0,1,1'||model.smallExample.signal!==1)throw Error('Unexpected fixed hat example');
for(const s of model.smallExample.states){if(s.answer!==(s.remainingParityBefore^s.visibleParity)||s.remainingParityAfter!==(s.remainingParityBefore^s.answer)||s.knownPriorIds.includes(1))throw Error('Invalid parity model');}
