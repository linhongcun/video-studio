import type {Shot} from './data';
export const at=(s:Shot,sentence:number,ratio:number)=>{
 const starts=s.cueFrames?.sentences??[9,Math.round(s.durationInFrames/2)];
 const a=Number(starts[sentence]??0),b=Number(starts[sentence+1]??s.durationInFrames-15);
 return Math.round(a+(b-a)*ratio);
};
export const events=(s:Shot):[string,number][]=>{
 const p=(i:number,r:number)=>at(s,i,r);
 return ({
  'local-commit':[['joint-local-commit',p(1,.52)]],
  'local-rollback':[['stock-failed',p(0,.55)],['pending-order-discarded',p(1,.58)]],
  'split-boundaries':[['independent-boundaries',p(1,.16)]],
  'partial-success':[['order-local-committed',p(0,.28)],['stock-failed',p(0,.7)],['stock-local-rolled-back',p(1,.55)]],
  'timeout':[['remote-stock-committed',p(0,.44)],['reply-lost',p(0,.79)],['caller-timeout-unknown',p(1,.22)]],
  'two-possibilities':[['switch-to-already-executed-possibility',p(0,.56)]],
  'unsafe-retry':[['wrong-double-decrement',p(0,.67)],['reset-to-never-executed-branch',p(1,.03)],['wrong-reverse-increment',p(1,.66)]],
  'durable-progress':[['stock-and-progress-local-commit',p(0,.57)],['process-interrupted-record-survives',p(1,.25)],['recovery-checks-record',p(1,.67)]],
  'safe-retry':[['duplicate-recognized-stock-unchanged',p(0,.68)],['separate-business-rejection-branch',p(1,.2)]],
  'decision-or-workflow':[['durable-shared-decision',p(0,.42)],['first-participant-applies',p(0,.62)],['second-participant-applies',p(0,.82)],['switch-to-workflow-illustration',p(1,.02)],['workflow-first-step-complete',p(1,.28)],['workflow-second-step-complete',p(1,.7)]],
  'eventual-consistency':[['recovery-converges',p(0,.7)],['rewind-to-stalled-recovery-branch',p(1,.03)],['recovery-pauses-business-pending',p(1,.4)]],
 } as Record<string,[string,number][]>)[s.visualType]??[];
};
export const eventAt=(s:Shot,name:string)=>events(s).find(([n])=>n===name)?.[1]??0;
