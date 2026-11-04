#!/usr/bin/env node
/** Independent protocol model, derived from the stated rules, without importing production code. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SELF = fileURLToPath(import.meta.url);
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const bit = id => 1n << BigInt(id);
const cardinality = mask => [...mask.toString(2)].filter(x => x === '1').length;
const members = (mask, n) => Array.from({length:n}, (_, i) => i).filter(i => (mask & bit(i)) !== 0n);
const initial = n => ({n, lamp:false, sent:0n, received:0n, pending:null, count:0, visited:0n, declared:false});
const protocolKey = s => [s.n, Number(s.lamp), s.sent.toString(), s.count, Number(s.declared)].join(':');
const fullKey = s => [protocolKey(s), s.received.toString(), s.pending ?? '-', s.visited.toString()].join(':');
const rank = s => cardinality(s.sent) + s.count;
let assertionCount = 0;
const claims = {};
function check(name, condition) {
  assertionCount++;
  claims[name] = (claims[name] ?? 0) + 1;
  assert.ok(condition, name);
}

function inspect(s) {
  const workers = ((1n << BigInt(s.n)) - 1n) ^ 1n;
  check('only_worker_ids_can_send', (s.sent & ~workers) === 0n);
  check('received_contributions_are_a_subset_of_sent', (s.received & ~s.sent) === 0n);
  check('every_sent_worker_has_visited', (s.sent & ~s.visited) === 0n);
  check('counter_equals_distinct_received_workers', s.count === cardinality(s.received));
  check('sent_equals_count_plus_lamp', cardinality(s.sent) === s.count + Number(s.lamp));
  check('pending_identity_exists_exactly_when_lamp_on', s.lamp === (s.pending !== null));
  check('at_most_one_unreceived_contribution', cardinality(s.sent & ~s.received) === Number(s.lamp));
  check('pending_is_the_unique_unreceived_contribution', s.pending === null ? s.sent === s.received : (s.sent & ~s.received) === bit(s.pending));
  check('counter_range_is_zero_to_n_minus_one', s.count >= 0 && s.count <= s.n - 1);
  check('nonzero_count_requires_counter_visit', s.count === 0 || (s.visited & 1n) !== 0n);
  check('declaration_iff_target_received', s.declared === (s.count === s.n - 1));
  check('declaration_implies_every_person_has_visited', !s.declared || s.visited === (1n << BigInt(s.n)) - 1n);
}

function advance(before, actor) {
  assert.ok(Number.isInteger(actor) && actor >= 0 && actor < before.n);
  const after = {...before, visited:before.visited | bit(actor)};
  let action = 'keep';
  if (actor === 0) {
    if (before.lamp) {
      after.lamp = false;
      after.count++;
      after.received |= bit(before.pending);
      after.pending = null;
      action = 'receive';
    }
  } else if (!before.lamp && (before.sent & bit(actor)) === 0n) {
    after.lamp = true;
    after.sent |= bit(actor);
    after.pending = actor;
    action = 'send';
  }
  after.declared = after.count === before.n - 1;
  check('sender_flags_never_revert', (before.sent & ~after.sent) === 0n);
  check('only_counter_can_turn_lamp_off', !before.lamp || after.lamp || actor === 0);
  check('send_only_once_and_only_on_empty_lamp', action !== 'send' || (actor !== 0 && !before.lamp && (before.sent & bit(actor)) === 0n));
  check('count_changes_only_on_counter_receipt', after.count - before.count === Number(action === 'receive'));
  check('one_visit_adds_at_most_one_contribution', cardinality(after.sent) - cardinality(before.sent) === Number(action === 'send'));
  check('protocol_progress_is_strict_rank_increase', action === 'keep' ? rank(after) === rank(before) : rank(after) === rank(before) + 1);
  check('protocol_stay_really_preserves_local_and_shared_protocol_memory', (action === 'keep') === (protocolKey(before) === protocolKey(after)));
  inspect(after);
  return {before, actor, action, after};
}

function enumerate(n) {
  const start = initial(n);
  inspect(start);
  const states = [start], seen = new Set([fullKey(start)]);
  let edges = 0, progressEdges = 0, stayEdges = 0, auditOnlyEdges = 0, terminal = 0;
  let nonterminal = 0, maxRank = 0, minProgressActors = n;
  for (let head = 0; head < states.length; head++) {
    const s = states[head];
    let enabledActors = 0;
    if (s.declared) terminal++; else nonterminal++;
    maxRank = Math.max(maxRank, rank(s));
    for (let actor = 0; actor < n; actor++) {
      const t = advance(s, actor);
      edges++;
      if (t.action === 'keep') {
        stayEdges++;
        if (fullKey(t.after) !== fullKey(s)) auditOnlyEdges++;
      } else {
        progressEdges++;
        enabledActors++;
      }
      const key = fullKey(t.after);
      if (!seen.has(key)) {seen.add(key); states.push(t.after);}
    }
    if (!s.declared) {
      check('each_nonterminal_protocol_state_has_a_progress_actor', enabledActors > 0);
      minProgressActors = Math.min(minProgressActors, enabledActors);
      check('nonterminal_progress_actor_identifiable_by_lamp_case', s.lamp || cardinality(s.sent) < n - 1);
    } else check('completed_protocol_has_no_more_progress', enabledActors === 0);
  }
  return {people:n, reachableAuditedStates:states.length, actorTransitions:edges,
    protocolProgressTransitions:progressEdges, protocolStayTransitions:stayEdges,
    protocolStayButAuditVisitSetChanges:auditOnlyEdges,
    terminalStates:terminal, nonterminalStates:nonterminal,
    maximumProgressRank:maxRank, expectedMaximumProgressRank:2*(n-1),
    minimumProgressActorsInNonterminalState:minProgressActors};
}

function expose(s) {
  return {lamp:s.lamp, sentIds:members(s.sent,s.n), receivedIdsForAudit:members(s.received,s.n),
    pendingSenderForAudit:s.pending, count:s.count, visitedIdsForAudit:members(s.visited,s.n),
    declared:s.declared, rank:rank(s)};
}
function trace(n, actors) {
  let state = initial(n);
  const steps = [];
  for (const [i, actor] of actors.entries()) {
    const t = advance(state,actor);
    steps.push({step:i+1, actor, action:t.action, before:expose(t.before), after:expose(t.after),
      actorObservationBefore:actor === 0 ? {lamp:t.before.lamp,ownCounter:t.before.count} :
        {lamp:t.before.lamp,ownAlreadySent:(t.before.sent & bit(actor)) !== 0n},
      allVisitedForAudit:t.after.visited === (1n << BigInt(n))-1n});
    state=t.after;
  }
  return {people:n, actors, steps, final:expose(state)};
}

/** Deliberately wrong variants for controls; these do not call the checked protocol transition. */
function badVariant(n, actors, {consumeFirstVisit=false, allowResend=false, initiallyOn=false}={}) {
  let on=initiallyOn, count=0;
  const unavailable=new Set(),visited=new Set(), events=[];
  for (const actor of actors) {
    visited.add(actor);
    let action='keep';
    if (actor === 0) {
      if(on){on=false;count++;action='receive';}
    } else {
      const eligible=allowResend || !unavailable.has(actor);
      if(eligible && !on){on=true;unavailable.add(actor);action='send';}
      if(consumeFirstVisit)unavailable.add(actor);
    }
    events.push({actor,action,on,count,visited:[...visited].sort((a,b)=>a-b)});
  }
  return {on,count,unavailable:[...unavailable].sort((a,b)=>a-b),visited:[...visited].sort((a,b)=>a-b),
    declared:count>=n-1,allVisited:visited.size===n,events};
}

function execute() {
  const startedAtUTC=new Date().toISOString();
  const enumeration=Array.from({length:7},(_,i)=>enumerate(i+2));
  const teaching=trace(4,[1,2,1,0,1,2,3,0,0,3,3,0]);
  check('teaching_waiting_first_visit_retains_send_eligibility', !teaching.steps[1].after.sentIds.includes(2));
  check('teaching_successful_sender_does_not_resend_on_off_lamp', teaching.steps[4].action==='keep' && !teaching.steps[4].after.lamp);
  check('teaching_all_visited_does_not_make_counter_omniscient', teaching.steps[6].allVisitedForAudit && !teaching.steps[6].after.declared);
  check('teaching_counter_off_visit_does_not_increment', teaching.steps[8].action==='keep' && teaching.steps[8].after.count===2);
  check('teaching_declaration_first_occurs_at_step_twelve', teaching.steps.find(s=>s.after.declared)?.step===12 && teaching.final.count===3);
  const hundred=trace(100,Array.from({length:99},(_,i)=>[i+1,0]).flat());
  check('hundred_people_example_receives_99_and_everyone_visited', hundred.final.count===99 && hundred.final.visitedIdsForAudit.length===100 && hundred.final.declared);
  const consumed=badVariant(4,[1,2,3,0,...Array(5).fill([0,1,2,3]).flat()],{consumeFirstVisit:true});
  check('bad_first_visit_consumption_has_a_fair_self_loop_suffix', consumed.count===1 && consumed.unavailable.length===3 && !consumed.on && consumed.allVisited && !consumed.declared);
  const repeated=badVariant(4,[1,0,1,0,1,0],{allowResend:true});
  check('bad_resending_can_declare_without_all_visiting', repeated.declared && !repeated.allVisited && repeated.visited.join(',')==='0,1');
  const phantom=badVariant(4,[0,1,0,2,0],{initiallyOn:true});
  check('bad_unknown_initial_on_can_create_a_phantom_contribution', phantom.declared && !phantom.allVisited && !phantom.visited.includes(3));
  const delays=[0,1,37,1000].map(delay=>{
    const t=trace(4,Array(delay).fill(0));
    check('finite_delay_fixture_has_no_announcement_or_worker_visit', !t.final.declared && t.final.sentIds.length===0 && t.final.count===0 && !t.final.visitedIdsForAudit.includes(3));
    return {delayVisits:delay,count:t.final.count,declared:t.final.declared,unvisitedPerson:3};
  });
  return {schemaVersion:1,episode:'prisoners-light',puzzle:'P10',ep:57,
    executor:'AI agent /root/p10_independent_model',startedAtUTC,endedAtUTC:new Date().toISOString(),
    runtime:{node:process.version,v8:process.versions.v8},scriptSHA256:hash(SELF),
    independentMethod:'Native Node.js exhaustive BFS derived directly from the protocol rules. No production Python, model data, narrative or source file is imported or read by this execution.',
    productionInputsReadByThisExecution:[],enumeration,
    totals:{reachableAuditedStates:enumeration.reduce((s,r)=>s+r.reachableAuditedStates,0),
      actorTransitions:enumeration.reduce((s,r)=>s+r.actorTransitions,0),assertionCount},
    claims,teachingTrace:teaching,hundredPeopleExample:{people:100,visits:hundred.steps.length,final:hundred.final},
    negativeControls:{firstVisitConsumesEligibility:consumed,repeatedSignals:repeated,unknownInitialOn:phantom},
    noUniformVisitBoundFixtures:delays,
    mathematicalArguments:{
      safety:'For any N>=2, each noncounter sends at most once, and only an off lamp can accept a new signal. With known initial off, S=C+L, and the lit lamp represents the sole unreceived contribution. C=N-1 therefore proves all N-1 distinct workers visited; the receiving counter is present too. Pending identity and visit/received sets are audit variables and never appear in an actor observation.',
      livenessUnderFairness:'R=S+C is initially zero and is bounded by 2(N-1). Each send or receipt increases R by exactly one. Thus an infinite run could have only finitely many progress actions and would eventually have a constant protocol state. In a nonterminal constant state either the lamp is on, enabling the counter, or it is off with an unsent worker. That enabled person is selected infinitely often by the stipulated individual fairness, contradicting permanent nonprogress. Hence the target is eventually reached.',
      noUniformBound:'For every finite T, the legal prefix consisting of T+1 visits by the counter alone keeps the lamp off, the count zero and all workers unvisited. Append an infinite cyclic schedule through every person: the extension is fair. Therefore no fixed number of visits, and without a visit-rate assumption no fixed number of days, guarantees completion.',
      enumerationBoundary:'The finite BFS executes N=2..8 only. General-N safety/liveness/no-bound claims use the separate mathematical arguments, not random testing or extrapolation from finite enumeration.'},
    passed:true};
}

const report=execute();
const target=path.join(HERE,'model-independent.json');
fs.writeFileSync(target,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:report.passed,scriptSHA256:report.scriptSHA256,
  reportSHA256:hash(target),totals:report.totals,enumeration:report.enumeration,
  traceVisits:report.teachingTrace.steps.length,hundredPeopleVisits:report.hundredPeopleExample.visits}));
