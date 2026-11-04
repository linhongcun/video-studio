#!/usr/bin/env node
/** Cross-check production data only after the separate independent model has completed. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const HERE=path.dirname(fileURLToPath(import.meta.url)),D=path.dirname(HERE);
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const own=read(path.join(HERE,'model-independent.json'));
assert.ok(own.passed);
assert.equal(own.scriptSHA256,hash(path.join(HERE,'model-independent.mjs')));
const inputNames=['model-data.json','model-verification.json','verify_protocol.py','script.md','article.mdx','plan.json','pronunciation.md','visual-direction.md','references.json','research-evidence.json'];
const before=Object.fromEntries(inputNames.map(n=>[n,hash(path.join(D,n))]));
const model=read(path.join(D,'model-data.json')),verification=read(path.join(D,'model-verification.json'));
const startedAtUTC=new Date().toISOString(),checks=[];
let comparisons=0;
const eq=(actual,expected,label)=>{comparisons++;assert.deepEqual(actual,expected,label);};
const ascending=n=>Array.from({length:n},(_,i)=>i);
const senders=n=>Array.from({length:n},(_,i)=>i+1);
const state=(s,n)=>({lamp:s.light,sentIds:s.sentIds,receivedIdsForAudit:s.receivedIdsForAudit,
  pendingSenderForAudit:s.pendingSenderForAudit,count:s.count,visitedIdsForAudit:s.visitedIdsForAudit,
  declared:s.declared,rank:s.sentIds.length+s.count});
const action=step=>step.actor===0 ? (step.before.lamp?'receive_and_increment':'counter_off_noop') :
  step.before.sentIds.includes(step.actor)?'already_sent_noop':step.before.lamp?'wait_light_on_keep_eligibility':'send_once';

eq(model.rules.initialLamp,'off','known initial OFF');
eq(model.rules.counterId,0,'unique counter');
eq(model.rules.targetCount,99,'one hundred people require 99 other contributions');
eq(model.rules.senderIds,senders(99),'the 99 noncounter identities');
eq(model.rules.uniformRandomArrivalRequired,false,'random selection is not a protocol premise');
eq(model.rules.fixedCompletionDeadlineClaimed,false,'no fixed deadline');
eq(model.mainExample.visits,own.teachingTrace.actors,'all 12 teaching visitor identities');
eq(model.mainExample.steps.length,12,'12 teaching steps');
for(const [i,p] of model.mainExample.steps.entries()){
  const t=own.teachingTrace.steps[i];
  eq(p.id,`e${String(i+1).padStart(2,'0')}`,'event id');
  eq(p.actorId,t.actor,'visitor');
  eq(state(p.before,4),t.before,'before state all audited and actual variables');
  eq(state(p.after,4),t.after,'after state all audited and actual variables');
  eq(p.action,action(t),'explicit action class');
  eq(p.newlySent,t.action==='send','one-time send flag');
  eq(p.newlyCounted,t.action==='receive','receipt flag');
  eq(p.newlyDeclared,!t.before.declared&&t.after.declared,'announcement moment');
  eq(p.countDelta,t.after.count-t.before.count,'counter increment');
  eq(p.after.allPeopleActuallyVisitedForAudit,t.allVisitedForAudit,'all visited is audit-only');
  const expectedObservation=t.actor===0?{actorId:0,role:'counter',observedLight:t.before.lamp,privateCountBefore:t.before.count}:
    {actorId:t.actor,role:'sender',observedLight:t.before.lamp,privateSentOnceBefore:t.before.sentIds.includes(t.actor)};
  eq(p.actorLocalObservation,expectedObservation,'actor observation has no sender identity or global roster');
}
eq(state(model.mainExample.final,4),own.teachingTrace.final,'four-person final');
checks.push({name:'four-person trace',passed:true,visits:12,stateBoundaries:24,includesActorObservationAndAnnouncement:true});

const hundred=model.hundredPersonFixture;
eq(hundred.visits,Array.from({length:99},(_,i)=>[i+1,0]).flat(),'hundred-person visits are the existence fixture');
eq(hundred.steps.length,198,'hundred-person fixture length');
// Independently known closed form for alternating sender k, counter; no production transition code is used.
for(let k=1;k<=99;k++){
  const send=hundred.steps[(k-1)*2],receive=hundred.steps[(k-1)*2+1];
  const off={lamp:false,sentIds:senders(k-1),receivedIdsForAudit:senders(k-1),pendingSenderForAudit:null,count:k-1,
    visitedIdsForAudit:k===1?[]:ascending(k),declared:false,rank:2*(k-1)};
  const on={lamp:true,sentIds:senders(k),receivedIdsForAudit:senders(k-1),pendingSenderForAudit:k,count:k-1,
    visitedIdsForAudit:k===1?[1]:ascending(k+1),declared:false,rank:2*k-1};
  const received={lamp:false,sentIds:senders(k),receivedIdsForAudit:senders(k),pendingSenderForAudit:null,count:k,
    visitedIdsForAudit:ascending(k+1),declared:k===99,rank:2*k};
  eq(send.actorId,k,'alternating sender identity');eq(receive.actorId,0,'alternating counter');
  eq(state(send.before,100),off,'sender closed-form before');eq(state(send.after,100),on,'sender closed-form after');
  eq(state(receive.before,100),on,'counter closed-form before');eq(state(receive.after,100),received,'counter closed-form after');
  eq(send.action,'send_once','send action');eq(receive.action,'receive_and_increment','receive action');
}
eq(state(hundred.final,100),own.hundredPeopleExample.final,'hundred-person final');
checks.push({name:'hundred-person existence fixture',passed:true,visits:198,stateBoundaries:396,
  scope:'Checks this constructed trace; it is not a runtime bound, minimum or expected time.'});

eq(verification.totalReachableStates,own.totals.reachableAuditedStates,'independent and production state totals');
eq(verification.totalTransitions,own.totals.actorTransitions,'independent and production edge totals');
for(const r of own.enumeration){
  const p=verification.finiteGraphExplorations.find(x=>x.totalPeople===r.people);
  assert.ok(p);
  eq(p.reachableStates,r.reachableAuditedStates,'reachable states by N');
  eq(p.transitions,r.actorTransitions,'transitions by N');
  eq(p.selfLoopTransitions,r.protocolStayTransitions-r.protocolStayButAuditVisitSetChanges,'full audited self-loops');
  eq(p.terminalStates,r.terminalStates,'terminal audited states');
  eq(r.maximumProgressRank,r.expectedMaximumProgressRank,'independent protocol rank bound is reached');
}
checks.push({name:'finite graph cross-check',passed:true,people:own.enumeration.map(x=>x.people),
  note:'Invariant/assertion counts differ because the implementations instrument different checks. Protocol-stay edges that update only the audit visit set are distinguished from full audited self-loops.'});

const script=fs.readFileSync(path.join(D,'script.md'),'utf8'),article=fs.readFileSync(path.join(D,'article.mdx'),'utf8');
const plan=read(path.join(D,'plan.json'));
const sections=[...script.matchAll(/^### (\d{2}) ([^\n]+)\n镜题：([^\n]+)\n旁白：([^\n]+)$/gm)];
eq(sections.length,14,'14 script scenes');eq(plan.length,14,'14 plan entries');
for(const [i,m]of sections.entries()){
  eq([plan[i].id,plan[i].slug],[m[1],m[2]],'script-plan id and slug');
  eq((m[4].match(/[。！？]/g)??[]).length,2,'exactly two narration sentences per scene');
}
eq(sections.reduce((n,m)=>n+(m[4].match(/[。！？]/g)??[]).length,0),28,'28 sentences');
eq([...new Set(plan.map(p=>p.chapterId))],['problem','protocol','walkthrough','guarantee','conclusion'],'five chapters');
const rows=[...article.matchAll(/^\| (e\d{2}) \| ([^|]+) \| ([^|]+) \| (亮|灭) \| ([^|]+) \| (\d+) \|$/gm)];
eq(rows.length,12,'article complete 12-event table');
for(const [i,m]of rows.entries()){
  const t=own.teachingTrace.steps[i];
  eq(m[1],`e${String(i+1).padStart(2,'0')}`,'table event id');
  eq(m[2].includes('计数员')?0:Number(m[2].replace('号','')),t.actor,'table actor');
  eq(m[4]==='亮',t.after.lamp,'table light');
  eq(m[5].trim()==='无'?[]:m[5].trim().split('、').map(Number),t.after.sentIds,'table sent set');
  eq(Number(m[6]),t.after.count,'table count');
}
const referenceIds=read(path.join(D,'references.json')).sources.map(s=>s.id);
eq([...article.matchAll(/<SourceQuote sourceId="([^"]+)"/g)].map(m=>m[1]),['R1','R2'],'two quotations have real source IDs');
assert.ok(['R1','R2'].every(id=>referenceIds.includes(id)));
checks.push({name:'script-plan and article state table',passed:true,scenes:14,sentences:28,chapters:5,articleRows:12,
  scope:'Structural parsing and exact actor/light/sent/count cells; explanatory prose and role-knowledge boundaries were separately read by the AI agent.'});

const after=Object.fromEntries(inputNames.map(n=>[n,hash(path.join(D,n))]));
eq(after,before,'production inputs remained unchanged during cross-check');
const report={schemaVersion:1,episode:'prisoners-light',executor:'AI agent /root/p10_independent_model',
  startedAtUTC,endedAtUTC:new Date().toISOString(),scriptSHA256:hash(fileURLToPath(import.meta.url)),
  independentExecutionReportSHA256:hash(path.join(HERE,'model-independent.json')),
  independentExecutionCompletedBeforeProductionComparison:true,productionInputSHA256:before,
  exactComparisons:comparisons,checks,passed:true,
  excluded:{figureTimingAndImages:'Two Figure TODOs/0-second positions remain placeholders and are not approved by this mathematical/static check.',
    publicSourceVerification:'Only local reference identities/support descriptions were read here; original external-source dates, titles and quotes are owned by the actual source researcher.',
    audiovisual:'No dynamic render, full real-time viewing, speech ASR, word alignment, semantic hearing, physical-phone test or media/site publication is claimed.'}};
const target=path.join(HERE,'model-independent-crosscheck.json');
fs.writeFileSync(target,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:true,exactComparisons:comparisons,reportSHA256:hash(target),checks}));
