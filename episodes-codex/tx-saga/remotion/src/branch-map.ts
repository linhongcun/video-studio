import type {Shot} from './data';
import type {BranchMapSpec, BranchMapShot} from '../../../_shared/branch-map';
import {eventAt} from './motion';

const spineNodes = ['start', 'charge', 'stock'];
const spineEdges = ['purchase-charge', 'charge-stock'];
const refundNodes = [...spineNodes, 'refund'];
const refundEdges = [...spineEdges, 'stock-refund'];
const completedNodes = [...refundNodes, 'refunded'];
const completedEdges = [...refundEdges, 'refund-completed'];
const pendingNodes = [...refundNodes, 'recover'];
const pendingEdges = [...refundEdges, 'refund-pending'];

/** A map of alternatives; highlighted nodes locate the explanation, not a global commit. */
export const sagaBranchMap: BranchMapSpec = {
  title: '这笔订单的全局路径',
  overviewTitle: '扣款成功，缺货了怎么办？',
  overviewHint: '先看两处分叉：库存结果，以及退款是否真正完成',
  nodes: [
    {id: 'start', label: '本次购买', x: 200, y: 450, w: 250, kind: 'step'},
    {id: 'charge', label: '本地扣款保存', x: 510, y: 450, w: 250, kind: 'step'},
    {id: 'stock', label: '库存结果', x: 820, y: 450, w: 250, kind: 'decision'},
    {id: 'success', label: '订单确认', x: 1160, y: 310, w: 270, kind: 'success'},
    {id: 'refund', label: '新的退款', x: 1160, y: 600, w: 270, kind: 'step'},
    {id: 'refunded', label: '退款完成', x: 1535, y: 495, w: 270, kind: 'success'},
    {id: 'recover', label: '等待恢复\n尚未结束', x: 1535, y: 740, w: 270, kind: 'unknown'},
  ],
  edges: [
    {id: 'purchase-charge', from: 'start', to: 'charge'},
    {id: 'charge-stock', from: 'charge', to: 'stock'},
    {id: 'stock-success', from: 'stock', to: 'success', label: '成功', via: [[980, 450], [980, 310]], labelAt: [980, 355], color: '#56E4D3'},
    {id: 'stock-refund', from: 'stock', to: 'refund', label: '缺货', via: [[980, 450], [980, 600]], labelAt: [980, 553], color: '#FFCC70'},
    {id: 'refund-completed', from: 'refund', to: 'refunded', label: '完成', via: [[1340, 600], [1340, 495]], labelAt: [1340, 542], color: '#56E4D3'},
    {id: 'refund-pending', from: 'refund', to: 'recover', label: '未完成', via: [[1340, 600], [1340, 740]], labelAt: [1340, 704], color: '#FFCC70', dashed: true},
  ],
  shots: {
    '01': {focus: 'stock', mode: 'focus', enter: {hold: 70, zoom: 42}, activeNodes: spineNodes, activeEdges: spineEdges,
      crumb: '问题定位 → 扣款已保存，库存缺货', overviewHint: '先认清流程：库存有两个结果，退款也有两个去向'},
    '02': {focus: 'charge', activeNodes: ['start', 'charge'], activeEdges: ['purchase-charge'],
      crumb: '全局 → 成功情景重置：从1000元、库存4开始'},
    '03': {focus: 'charge', activeNodes: ['start', 'charge'], activeEdges: ['purchase-charge'],
      crumb: '全局 → 本地扣款 → 各步先提交'},
    '04': {focus: 'charge', activeNodes: ['start', 'charge'], activeEdges: ['purchase-charge'],
      crumb: '全局 → 第一步：账户库本地提交'},
    '05': {focus: 'stock', exit: {zoom: 28, hold: 8}, activeNodes: spineNodes, activeEdges: spineEdges,
      crumb: '全局 → 已扣款 → 处理库存', overviewTitle: '先缩回全局，再换一种库存结果', overviewHint: '刚才走成功分支；接着从同一处分叉重新演示'},
    '06': {focus: 'stock', enter: {hold: 64, zoom: 42}, activeNodes: ['stock'], activeEdges: [],
      crumb: '库存分叉 → 新情景：账户1000，库存0', overviewTitle: '换个结果：回到库存这一处分叉', overviewHint: '另一情景重置：账户从1000元、库存从0开始'},
    '07': {focus: 'charge', activeNodes: ['start', 'charge'], activeEdges: ['purchase-charge'],
      crumb: '缺货情景 → 先保存扣款，再查看库存结果'},
    '08': {focus: 'refund', activeNodes: refundNodes, activeEdges: refundEdges,
      crumb: '全局 → 缺货 → 已提交的扣款需要新动作收尾'},
    '09': {focus: 'refund', activeNodes: refundNodes, activeEdges: refundEdges,
      crumb: '全局 → 缺货 → 新的退款处理中'},
    '10': {focus: 'refund', activeNodes: refundNodes, activeEdges: refundEdges,
      crumb: '全局 → 新退款 → 等待本地保存'},
    '11': {focus: 'refunded', exit: {zoom: 28, hold: 8}, activeNodes: completedNodes, activeEdges: completedEdges,
      crumb: '全局 → 退款完成 → 相同退款重复送来，不再加钱', overviewTitle: '再回到退款这一处分叉', overviewHint: '重复退款不是新结局；接下来回看尚未完成的情景'},
    '12': {focus: 'refund', enter: {hold: 64, zoom: 42}, activeNodes: refundNodes, activeEdges: refundEdges,
      crumb: '退款分叉 → 新情景：余额800，退款尚未完成', overviewTitle: '换个结果：退款还没有完成', overviewHint: '从已扣款800、待退款开始；这次不沿用刚才的1000元'},
    '13': {focus: 'recover', activeNodes: pendingNodes, activeEdges: pendingEdges,
      crumb: '全局 → 退款未完成 → 留下进度，继续恢复'},
    '14': {focus: 'charge', exit: {zoom: 48, hold: 65}, activeNodes: ['start', 'charge'], activeEdges: ['purchase-charge'],
      crumb: '回看本地提交后的阶段 → 中间状态可能可见', overviewTitle: '回到全图：不同结果，分别完成或继续收尾', overviewHint: '这些是互斥情景；金色的待恢复，仍然没有结束'},
  },
};

/** The detail camera stays full-size between shots; only the locator follows real events. */
export function sagaMapForFrame(s: Shot, frame: number): BranchMapSpec {
  const base = sagaBranchMap.shots[s.id];
  const binding: BranchMapShot = {...base};
  const after = (event: string) => frame >= eventAt(s, event);
  if (s.id === '05' && after('order-confirmed')) {
    binding.focus = 'success'; binding.activeNodes = [...spineNodes, 'success'];
    binding.activeEdges = [...spineEdges, 'stock-success']; binding.crumb = '全局 → 库存完成 → 订单确认';
  }
  if (s.id === '07' && after('charge-local-commit')) {
    binding.focus = 'stock'; binding.activeNodes = spineNodes; binding.activeEdges = spineEdges;
    binding.crumb = '缺货情景 → 扣款已保存，等待库存结果';
    if (after('stock-business-rejected')) {
      binding.activeNodes = refundNodes; binding.activeEdges = refundEdges;
      binding.crumb = '全局 → 库存明确拒绝 → 需要新的退款';
    }
  }
  if (s.id === '10' && after('refund-local-commit')) {
    binding.focus = 'refunded'; binding.activeNodes = completedNodes; binding.activeEdges = completedEdges;
    binding.crumb = '全局 → 新退款已保存 → 原扣款与新退款都保留';
  }
  if (s.id === '12' && after('refund-attempt-failed')) {
    binding.focus = 'recover'; binding.activeNodes = pendingNodes; binding.activeEdges = pendingEdges;
    binding.crumb = '全局 → 退款未完成 → 余额800，仍待恢复';
  }
  if (s.id === '14' && frame >= s.durationInFrames - 1 - 48 - 65) {
    binding.activeNodes = sagaBranchMap.nodes.map(n => n.id);
    binding.activeEdges = sagaBranchMap.edges.map(e => e.id);
  }
  // Keep the decision generic: both outgoing edges remain valid alternatives.
  // The fixed conflict title and breadcrumb identify this example's shortage.
  const nodes = s.id === '01' ? sagaBranchMap.nodes.map(n => n.id === 'charge' ? {...n, label: '扣款已保存'} : n) : sagaBranchMap.nodes;
  return {...sagaBranchMap, nodes, shots: {...sagaBranchMap.shots, [s.id]: binding}};
}

// Shared QA discovery names; production uses the descriptive names above.
export const navigationSpec = sagaMapForFrame;
export const branchMapFor = sagaMapForFrame;
