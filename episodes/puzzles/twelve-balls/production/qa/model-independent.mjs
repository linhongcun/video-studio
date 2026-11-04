#!/usr/bin/env node
// Independent exhaustive model for EP56 / P06 / twelve-balls.
// Run from repo root: node episodes/puzzles/twelve-balls/production/qa/model-independent.mjs
// This program writes only model-independent-results.json and model-independent-report.md
// beside itself, with exclusive creation; it never reads or rewrites production sources.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';

const startedAt = new Date().toISOString();
const directions = ['H', 'l']; // H = heavy; lowercase l = light, never a balance outcome.
const outcomes = ['L', 'B', 'R']; // L = left heavier; B = balance; R = right heavier.
const hypotheses = Array.from({length: 12}, (_, i) =>
  directions.map(direction => ({ball: i + 1, direction, id: `${i + 1}${direction}`}))).flat();
const byId = new Map(hypotheses.map(h => [h.id, h]));
const answer = id => ({answer: id});
const impossible = {impossible: true};

// This tree was constructed independently, before viewing the root Python model.
// Normal references are explicit claims: every claim is checked against ALL
// hypotheses consistent with observations strictly before this weighing.
const nodes = {
  start: {left: [1, 2, 3, 4], right: [5, 6, 7, 8], normalReferences: [],
    next: {L: 'leftSecond', B: 'balanceSecond', R: 'rightSecond'}},
  balanceSecond: {left: [9, 10, 11], right: [1, 2, 3], normalReferences: [1, 2, 3],
    next: {L: 'balanceHeavyThird', B: 'balanceTwelveThird', R: 'balanceLightThird'}},
  balanceHeavyThird: {left: [9], right: [10], normalReferences: [],
    next: {L: answer('9H'), B: answer('11H'), R: answer('10H')}},
  balanceLightThird: {left: [9], right: [10], normalReferences: [],
    next: {L: answer('10l'), B: answer('11l'), R: answer('9l')}},
  balanceTwelveThird: {left: [12], right: [1], normalReferences: [1],
    next: {L: answer('12H'), B: impossible, R: answer('12l')}},
  leftSecond: {left: [1, 2, 5], right: [3, 6, 9], normalReferences: [9],
    next: {L: 'leftSameThird', B: 'leftBalanceThird', R: 'leftReversedThird'}},
  leftSameThird: {left: [1], right: [2], normalReferences: [],
    next: {L: answer('1H'), B: answer('6l'), R: answer('2H')}},
  leftBalanceThird: {left: [7], right: [8], normalReferences: [],
    next: {L: answer('8l'), B: answer('4H'), R: answer('7l')}},
  leftReversedThird: {left: [3], right: [9], normalReferences: [9],
    next: {L: answer('3H'), B: answer('5l'), R: impossible}},
  rightSecond: {left: [1, 2, 5], right: [3, 6, 9], normalReferences: [9],
    next: {L: 'rightReversedThird', B: 'rightBalanceThird', R: 'rightSameThird'}},
  rightSameThird: {left: [1], right: [2], normalReferences: [],
    next: {L: answer('2l'), B: answer('6H'), R: answer('1l')}},
  rightBalanceThird: {left: [7], right: [8], normalReferences: [],
    next: {L: answer('7H'), B: answer('4l'), R: answer('8H')}},
  rightReversedThird: {left: [3], right: [9], normalReferences: [9],
    next: {L: impossible, B: answer('5H'), R: answer('3l')}},
};

const fixtures = [
  {id: 'primary', normalMass: 100n, delta: 1n},
  {id: 'large_delta_positive_light', normalMass: 257n, delta: 256n},
  {id: 'different_units', normalMass: 65537n, delta: 257n},
  {id: 'above_number_safe_integer', normalMass: 100000000000000003n, delta: 7n},
];

const asOutcome = difference => difference > 0n ? 'L' : difference < 0n ? 'R' : 'B';
const signedDelta = hypothesis => hypothesis.direction === 'H' ? 1n : -1n;
function symbolicOutcome(node, hypothesis) {
  const placement = node.left.includes(hypothesis.ball) ? 1n : node.right.includes(hypothesis.ball) ? -1n : 0n;
  return asOutcome(placement * signedDelta(hypothesis));
}
function physicalWeigh(node, hypothesis, fixture) {
  const mass = ball => fixture.normalMass + (ball === hypothesis.ball ? fixture.delta * signedDelta(hypothesis) : 0n);
  const leftMass = node.left.reduce((total, ball) => total + mass(ball), 0n);
  const rightMass = node.right.reduce((total, ball) => total + mass(ball), 0n);
  return {outcome: asOutcome(leftMass - rightMass), leftMass: String(leftMass), rightMass: String(rightMass)};
}
function knownNormal(candidates) {
  const suspects = new Set(candidates.map(h => h.ball));
  return Array.from({length: 12}, (_, i) => i + 1).filter(ball => !suspects.has(ball));
}

const structuralAudit = [];
const unreachableBranches = [];
const leaves = [];
const visitedNodes = new Set();
function auditNode(id, candidates, history) {
  assert(candidates.length > 0, `internal node ${id} must be reachable`);
  assert(history.length < 3, `more than three weighings at ${id}`);
  assert(!visitedNodes.has(id), `node reused or cyclic: ${id}`);
  visitedNodes.add(id);
  const node = nodes[id];
  assert(node, `missing node ${id}`);
  assert.equal(node.left.length, node.right.length, `unequal pan counts at ${id}`);
  assert(node.left.length > 0, `empty weighing at ${id}`);
  const balls = [...node.left, ...node.right];
  assert.equal(new Set(balls).size, balls.length, `duplicate or two-pan ball at ${id}`);
  assert(balls.every(ball => Number.isInteger(ball) && ball >= 1 && ball <= 12), `external ball at ${id}`);
  assert.deepEqual(Object.keys(node.next).sort(), [...outcomes].sort(), `missing outcome at ${id}`);
  const normals = knownNormal(candidates);
  for (const ball of node.normalReferences) {
    assert(balls.includes(ball), `reference ${ball} not weighed at ${id}`);
    assert(normals.includes(ball), `normal ball ${ball} used before proof at ${id}`);
    assert(candidates.every(h => h.ball !== ball), `reference ${ball} could be abnormal at ${id}`);
  }
  const partitions = Object.fromEntries(outcomes.map(outcome =>
    [outcome, candidates.filter(h => symbolicOutcome(node, h) === outcome)]));
  assert.equal(Object.values(partitions).flat().length, candidates.length);
  structuralAudit.push({
    node: id, history: history.join(''), weighingNumber: history.length + 1,
    left: node.left, right: node.right, panCount: node.left.length,
    candidatesBefore: candidates.map(h => h.id), normalBallsBefore: normals,
    normalReferences: node.normalReferences,
    referenceProof: node.normalReferences.length ?
      'Every remaining hypothesis, derived only from earlier outcomes, places the abnormal ball elsewhere.' :
      'No ball is assumed normal for this weighing.',
    partitions: Object.fromEntries(outcomes.map(outcome => [outcome, partitions[outcome].map(h => h.id)])),
  });
  for (const outcome of outcomes) {
    const matching = partitions[outcome];
    const target = node.next[outcome];
    const nextHistory = [...history, outcome];
    if (typeof target === 'string') {
      assert(matching.length > 0, `unreachable internal target ${target}`);
      auditNode(target, matching, nextHistory);
    } else if (target.impossible) {
      assert.equal(matching.length, 0, `declared impossible but reachable: ${nextHistory.join('')}`);
      unreachableBranches.push({history: nextHistory.join(''), fromNode: id, outcome,
        reason: 'No one of the 24 allowed ball-and-direction hypotheses has this history.'});
    } else {
      assert.equal(matching.length, 1, `ambiguous or empty leaf ${nextHistory.join('')}`);
      assert(byId.has(target.answer), `invalid answer ${target.answer}`);
      assert.equal(matching[0].id, target.answer, `wrong leaf ${nextHistory.join('')}`);
      leaves.push({history: nextHistory.join(''), answer: target.answer});
    }
  }
}
auditNode('start', hypotheses, []);
assert.equal(visitedNodes.size, Object.keys(nodes).length, 'unreviewed tree nodes');
assert.equal(visitedNodes.size, 13);
assert.equal(leaves.length, 24);
assert.equal(new Set(leaves.map(leaf => leaf.answer)).size, 24, 'answers not unique');
assert.equal(new Set(leaves.map(leaf => leaf.history)).size, 24, 'histories not unique');
assert.deepEqual(unreachableBranches.map(branch => branch.history).sort(), ['BBB', 'LRR', 'RLL']);

// Each physical run chooses its next weighing from observations alone.
// The hidden hypothesis is used only by the ideal physical balance and the final check.
function run(hypothesis, fixture) {
  let id = 'start';
  let candidates = [...hypotheses];
  const steps = [];
  while (true) {
    assert(steps.length < 3);
    const node = nodes[id];
    const measured = physicalWeigh(node, hypothesis, fixture);
    assert.equal(measured.outcome, symbolicOutcome(node, hypothesis), 'physical/symbolic disagreement');
    const after = candidates.filter(candidate => symbolicOutcome(node, candidate) === measured.outcome);
    assert(after.some(candidate => candidate.id === hypothesis.id), 'actual state eliminated');
    steps.push({
      number: steps.length + 1, node: id, left: node.left, right: node.right,
      normalBallsBefore: knownNormal(candidates), normalReferences: node.normalReferences,
      candidatesBefore: candidates.map(candidate => candidate.id), ...measured,
      candidatesAfter: after.map(candidate => candidate.id),
    });
    candidates = after;
    const target = node.next[measured.outcome];
    if (typeof target === 'string') {id = target; continue;}
    assert(!target.impossible, 'physical allowed state reached impossible outcome');
    assert.equal(candidates.length, 1);
    assert.equal(target.answer, hypothesis.id);
    return {input: hypothesis.id, answer: target.answer, path: steps.map(step => step.outcome).join(''),
      weighings: steps.length, steps};
  }
}
const fixtureRuns = fixtures.map(fixture => {
  assert(fixture.delta > 0n && fixture.normalMass > fixture.delta, 'invalid physical masses');
  const cases = hypotheses.map(hypothesis => run(hypothesis, fixture));
  assert.equal(cases.length, 24);
  assert.equal(new Set(cases.map(result => result.path)).size, 24);
  assert(cases.every(result => result.weighings <= 3));
  return {fixture: {id: fixture.id, normalMass: String(fixture.normalMass), delta: String(fixture.delta)}, cases};
});
for (const fixtureRun of fixtureRuns.slice(1)) {
  assert.deepEqual(fixtureRun.cases.map(result => [result.input, result.path, result.answer]),
    fixtureRuns[0].cases.map(result => [result.input, result.path, result.answer]), 'mass fixture changed protocol');
}

const finishedAt = new Date().toISOString();
const sourcePath = fileURLToPath(import.meta.url);
const sourceSha256 = createHash('sha256').update(await readFile(sourcePath)).digest('hex');
const report = {
  schemaVersion: 1, episode: 'EP56', puzzle: 'P06', slug: 'twelve-balls', status: 'PASS',
  scope: 'Independent, deterministic enumeration of every one of 12 balls times 2 directions; no random sampling.',
  operator: '/root/p06_independent_model', suppliedBaseSha: 'd2548e6',
  baseShaProvenance: 'Task supplied by root; no Git command used by this verifier.',
  startedAt, finishedAt,
  startedAtBeijing: new Date(new Date(startedAt).getTime() + 8 * 3600000).toISOString().replace('Z', '+08:00'),
  engine: {runtime: 'Node.js', node: process.version, v8: process.versions.v8, arch: process.arch, platform: process.platform},
  source: {path: sourcePath, sha256: sourceSha256},
  assumptions: ['Exactly one ball is abnormal.', 'All 11 normal balls have equal mass.',
    'The abnormal ball has fixed nonzero heavier or lighter mass.',
    'Only the existing 12 balls are available, with no weights and no extra normal ball.',
    'An ideal equal-arm balance reports only left-heavy, balance, or right-heavy.',
    'The answer must identify both the ball number and heavier/lighter direction.'],
  notation: {L: 'left pan heavier', B: 'balance', R: 'right pan heavier', H: 'abnormal heavy', l: 'abnormal light'},
  counts: {hypotheses: hypotheses.length, internalWeighingNodes: visitedNodes.size, correctUniqueLeaves: leaves.length,
    unreachableOutcomeBranches: unreachableBranches.length, massFixtures: fixtureRuns.length,
    completePhysicalCases: fixtureRuns.reduce((sum, result) => sum + result.cases.length, 0), maxWeighings: 3},
  checks: {all24Inputs: 'PASS', allLeavesCorrectAndUnique: 'PASS', allPanCountsEqual: 'PASS',
    noExternalBallOrDuplicatePlacement: 'PASS', normalReferencesDerivedFromEarlierResults: 'PASS',
    maximumThreeWeighings: 'PASS', unreachableOutcomesExplicitAndEmpty: 'PASS',
    physicalBigIntMassMatchesSymbolicDirection: 'PASS', deterministicMassFixtureInvariance: 'PASS'},
  lowerBound: {
    twoWeighings: 'Every adaptive protocol with at most two ternary observations has at most 3^2 = 9 terminal histories. Guaranteed identification of 24 distinct ball-and-direction states needs 24 different leaves; therefore two weighings cannot suffice.',
    threeWeighingsCapacity: '3^3 = 27 >= 24 is only a necessary capacity allowance. It does not establish that physically legal equal-count weighings realize a separating decision tree.',
    existenceWitness: 'The concrete 13-node tree, checked exhaustively on all 24 states, is the existence witness that three weighings suffice under the stated ideal assumptions.',
  },
  massIndependence: {
    algebraicReason: 'For equal pan counts k and common normal mass m, leftMass-rightMass is k*m-k*m+s*delta*c = s*delta*c. Here s is +1 for heavy or -1 for light, c is +1 for abnormal on left, -1 on right, 0 off scale. Thus the sign is independent of m and positive delta; require m>delta>0 for positive light-ball mass.',
    fixtureScope: 'Four deterministic BigInt fixtures support implementation checks; finite fixtures alone are not a proof for all real mass units or deltas. The cancellation argument establishes that ideal-model extension.',
  },
  structuralAudit, unreachableBranches, primaryCases: fixtureRuns[0].cases, fixtureRuns,
  limitations: ['Mathematical ideal-balance model, not a physical laboratory measurement.',
    'No production script, storyboard, source quotation, audio, frame, or site was audited in this run.',
    'No claim about audience comprehension, real scale noise, or unequal normal masses.'],
};
const row = result => `| ${result.input} | ${result.path} | ${result.steps.map(step => `${step.left.join(',')}:${step.right.join(',')} ${step.outcome}`).join(' → ')} | ${result.answer} |`;
const nodeRow = entry => `| ${entry.history || '开始'} | ${entry.left.join(',')} : ${entry.right.join(',')} | ${entry.candidatesBefore.join(' ')} | ${outcomes.map(outcome => `${outcome}: ${entry.partitions[outcome].join(' ') || '不可达'}`).join('；')} | ${entry.normalReferences.join(',') || '无'} |`;
const markdown = `# P06 / EP56 十二球独立数学模型核验\n\n` +
  `结果：PASS。实际执行引擎 ${report.engine.runtime} ${report.engine.node} / V8 ${report.engine.v8}。\n\n` +
  `UTC ${startedAt} 至 ${finishedAt}；北京时间 ${report.startedAtBeijing}。\n\n` +
  `执行命令：\n\n\`\`\`sh\nnode episodes/puzzles/twelve-balls/production/qa/model-independent.mjs\n\`\`\`\n\n` +
  `本模型独立设计后先向根代理发送决策树，未读取根代理Python实现。基线 d2548e6 由任务提供，本次没有运行Git。仅新增本目录 model-independent* 文件；不改既有生产稿与历史证据。源代码 SHA-256：${sourceSha256}。\n\n` +
  `记号：L=左重，B=平衡，R=右重；H=异常偏重，l=异常偏轻。题意固定恰好一球异常、其余11球同重，异常方向固定；只用12球，不添正常球或砝码。每次两盘球数相同。\n\n` +
  `## 实际检查范围\n\n` +
  `全12号×轻重两方向，共24个允许输入逐一执行；不是随机模拟。检查13个内部称重节点，两盘等数量、球号范围、无重复上盘、正常参照的历史来源、每叶正确且唯一，以及最多三称。所有24种输入均恰用3称。四组确定性BigInt质量夹具各全跑24种，共96例，结果路径一致。\n\n` +
  `正常球只从先前结果推出：首称平衡，异常球在9—12，故1—8正常；首称不平衡，异常球在1—8，故9—12正常。程序在每个节点先从所有符合此前结果的候选集合求出正常球，再核对明确声明的参照球。第三称1:2或7:8不要求两球正常，按候选异常状态判读。\n\n` +
  `## 完整决策树及正常球来源\n\n` +
  `每行的历史是本次称重前已观察到的结果；分组是这次称重后剩余的候选。所有列出的正常参照都在该节点此前的候选集合中被排除了异常可能。\n\n` +
  `| 先前历史 | 本次左:右 | 先前候选 | 本次结果分组 | 正常参照 |\n|---|---|---|---|---|\n` +
  structuralAudit.map(nodeRow).join('\n') + `\n\n` +
  `## 全24个输入的实际完整路径\n\n` +
  `| 真实输入 | 三次结果 | 三次称重及结果 | 程序输出 |\n|---|---|---|---|\n` +
  fixtureRuns[0].cases.map(row).join('\n') + `\n\n` +
  `三条不可达结果序列明确标为 BBB、LRR、RLL，程序各自核验没有任何允许输入进入；这不是“称到也随便判”的叶子。示例6轻：首1234:5678左重，候选缩为1—4重/5—8轻；二125:369左重，候选仅1重、2重、6轻；三1:2平衡，所以6轻。\n\n` +
  `## 两次不够与三次足够\n\n` +
  `即使可自适应，两次最多形成3²=9个叶子；要求区分12×2=24种状态，每种必须占独立叶子，因此两次必然不够。提前停止不会增加叶子上限。3³=27只说明容量没有立即排除三次，并不证明合法称法存在。这里由具体完整决策树及全24状态核验给出三次足够的构造，所以最坏情况最少三次。\n\n` +
  `## 质量单位与模型边界\n\n` +
  `四组(m,δ)：${fixtures.map(fixture => `(${fixture.normalMass},${fixture.delta})`).join('、')}，均满足m>δ>0；偏轻球质量m−δ，偏重球m+δ。所有质量及加法用BigInt精确运算，包含超过JavaScript Number安全整数的夹具。\n\n` +
  `等数量时两盘正常质量项k·m相消，差仅为s·δ·c，其中s为轻重符号，c为异常球所在盘的符号或0。因此理想天平下结果只依赖符号，不依赖单位或δ大小。四组有限夹具只核验实现，任意合法质量的结论由该消去推导给出。\n\n` +
  `本次是理想数学模型核验，未作实物实验；未审生产文稿、来源原文、配音、画面或网站，也不声称学习效果通过。另有独立子代理只作树与下界的纯逻辑审读，未将其记为代码运行证据。\n`;
await writeFile(new URL('./model-independent-results.json', import.meta.url), `${JSON.stringify(report, null, 2)}\n`, {flag: 'wx'});
await writeFile(new URL('./model-independent-report.md', import.meta.url), markdown, {flag: 'wx'});
process.stdout.write(`${JSON.stringify({status: report.status, startedAt, finishedAt, engine: report.engine,
  counts: report.counts, paths: fixtureRuns[0].cases.map(({input, path, answer}) => ({input, path, answer})),
  unreachable: unreachableBranches.map(branch => branch.history), sourceSha256}, null, 2)}\n`);
