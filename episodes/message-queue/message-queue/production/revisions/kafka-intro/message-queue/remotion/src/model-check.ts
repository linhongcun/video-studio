import assert from 'node:assert/strict';
import {initial,append,confirmWrite,replyAccepted,readNext,saveBusiness,commit,queryResult,unfinished,runMainExample,flowWindow} from './model.ts';
const states=runMainExample();
assert.deepEqual(states.read.log,states.appended.log);
assert.deepEqual(states.saved.log,states.appended.log);
assert.deepEqual(states.committed.log,states.appended.log);
assert.deepEqual(states.drained.log,states.appended.log);
assert.equal(states.read.readPosition,1);assert.equal(states.read.committedOffset,null);assert.equal(states.read.businessResults.length,0);
assert.equal(states.saved.committedOffset,null);assert.deepEqual(states.saved.businessResults,['7042']);assert.equal(states.saved.pageState,'accepted');
assert.equal(states.committed.committedOffset,1);assert.equal(states.committed.pageState,'accepted');
assert.equal(states.queried.pageState,'complete');assert.equal(states.queried.committedOffset,1);
assert.equal(unfinished(states.drained),0);assert.equal(states.drained.log.length,3);assert.equal(states.drained.committedOffset,3);
assert.throws(()=>replyAccepted(append(initial(),'7042')));
assert.throws(()=>commit(states.read,1));
assert.throws(()=>commit(initial(),-1));
assert.throws(()=>commit(states.saved,2));
assert.throws(()=>readNext(states.read));
assert.equal(queryResult(states.accepted).pageState,'accepted');
assert.deepEqual(states.appended.log.map(r=>[r.offset,r.orderId]),[[0,'7042'],[1,'7043'],[2,'7044']]);
for(let second=0;second<=20;second++){
 const f=flowWindow(second);assert.equal(f.entered-f.completed,f.unfinished);assert.equal(f.unfinished,second);
}
assert.deepEqual(flowWindow(4),{seconds:4,entered:8,completed:4,unfinished:4});
console.log(JSON.stringify({passed:true,scope:'deterministic single-partition teaching model; not a live Kafka experiment',mainStates:Object.keys(states),retainedAfterDrain:states.drained.log.length,unfinishedAfterDrain:unfinished(states.drained),flowWindowsChecked:21}));
