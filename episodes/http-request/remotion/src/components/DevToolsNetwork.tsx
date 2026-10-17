import React from 'react';
import {useCurrentFrame} from 'remotion';
import {FONT, MONO, P} from '../theme';

export type NetworkRow = {
  name: string;
  method: string;
  status?: number;
  type: string;
  size?: string;
  time?: string;
  pending?: boolean;
  /** Milliseconds on the shared 1000 ms waterfall scale. */
  start?: number;
  duration?: number;
};

/** Illustrative requests and timings, not captured browsing data. */
export const NETWORK_ROWS: readonly NetworkRow[] = [
  {name: 'example.com', method: 'GET', status: 200, type: 'document', size: '1.2 kB', time: '85 ms', start: 0, duration: 85},
  {name: 'style.css', method: 'GET', status: 200, type: 'stylesheet', size: '4.8 kB', time: '64 ms', start: 90, duration: 64},
  {name: 'logo.png', method: 'GET', status: 200, type: 'image', size: '8.6 kB', time: '92 ms', start: 110, duration: 92},
  {name: 'hero.jpg', method: 'GET', status: 200, type: 'image', size: '126 kB', time: '310 ms', start: 120, duration: 310},
  {name: 'font.woff2', method: 'GET', status: 200, type: 'font', size: '32 kB', time: '180 ms', start: 165, duration: 180},
  {name: 'app.js', method: 'GET', status: 200, type: 'script', size: '48 kB', time: '220 ms', start: 170, duration: 220},
  {name: 'theme.css', method: 'GET', status: 200, type: 'stylesheet', size: '2.1 kB', time: '72 ms', start: 220, duration: 72},
  {name: 'card-01.jpg', method: 'GET', status: 200, type: 'image', size: '64 kB', time: '240 ms', start: 260, duration: 240},
  {name: 'card-02.jpg', method: 'GET', status: 200, type: 'image', size: '72 kB', time: '275 ms', start: 285, duration: 275},
  {name: 'icons.svg', method: 'GET', status: 200, type: 'image', size: '3.4 kB', time: '68 ms', start: 340, duration: 68},
  {name: 'menu.js', method: 'GET', status: 200, type: 'script', size: '6.2 kB', time: '110 ms', start: 420, duration: 110},
  {name: 'footer.png', method: 'GET', status: 200, type: 'image', size: '18 kB', time: '160 ms', start: 530, duration: 160},
];

/** Full opacity on integer frames start…start+19; three-frame fades outside. */
export const notFoundOpacity = (frame: number, start: number): number =>
  Math.max(0, Math.min(1, (frame - start + 3) / 3, (start + 22 - frame) / 3));

export type DevToolsNetworkProps = {
  rows?: readonly NetworkRow[];
  /** Marks the first row as pending; individual rows can also set pending. */
  pending?: boolean;
  /** Positive pixel values move rows upward beneath the fixed table header. */
  scrollOffset?: number;
  notFound?: boolean;
  /** Omit for a static card; supply a start frame for the brief animated flash. */
  notFoundStart?: number;
  width?: number;
  height?: number;
  rowStyle?: React.CSSProperties;
  rowElementId?: string;
  rowGroupElementId?: string;
  rowGroupStyle?: React.CSSProperties;
  /** Keep the completed homepage row present while the resource group enters. */
  firstRowAlwaysVisible?: boolean;
  highlightOpacity?: number;
  highlightElementId?: string;
  highlightStyle?: React.CSSProperties;
  /** Local appearance and bar-growth progress for each waterfall row. */
  rowProgress?: readonly number[];
  notFoundStyle?: React.CSSProperties;
  statusStyle?: React.CSSProperties;
  statusElementId?: string;
  visibleRows?: number;
  rowHeight?: number;
  /** Magnify the single homepage request instead of showing secondary columns. */
  focusRequest?: boolean;
  /** Four enlarged columns for the homepage response. */
  responseSummary?: boolean;
  rowFontSize?: number;
  requestLabel?: string;
};

const COLUMNS = 'minmax(360px, 1.1fr) 140px 150px 190px 170px minmax(330px, 1fr)';
const FOCUS_COLUMNS = 'minmax(400px, 1fr) 160px 180px 240px 240px 200px'; // size col widened so '1.2 kB' stays on one line at 56px
const RESPONSE_COLUMNS = 'minmax(0, 1fr) 260px 340px 320px';
export const NETWORK_ROW_HEIGHT = 88;
export const networkMaxScroll = (rowCount: number, height: number, visibleRows?: number, rowHeight = NETWORK_ROW_HEIGHT) => Math.max(0, rowCount * rowHeight - (visibleRows === undefined ? height - 104 - 88 - 72 - 6 : visibleRows * rowHeight));
const Spinner: React.FC<{frame: number}> = ({frame}) => (
  <svg width={44} height={44} viewBox="0 0 32 32" style={{transform: `rotate(${frame * 10}deg)`, flexShrink: 0}} aria-label="等待响应">
    <circle cx={16} cy={16} r={12} fill="none" stroke={P.muted} strokeWidth={4} />
    <path d="M16 4a12 12 0 0 1 12 12" fill="none" stroke={P.primary} strokeWidth={4} strokeLinecap="round" />
  </svg>
);

/** Generic network inspector: fixed headings, clipped rows, and a shared time scale. */
export const DevToolsNetwork: React.FC<DevToolsNetworkProps> = ({
  rows = NETWORK_ROWS, pending = false, scrollOffset = 0, notFound = false,
  notFoundStart, width = 1840, height = 800, rowStyle, rowElementId, rowGroupElementId, rowGroupStyle, firstRowAlwaysVisible = false, highlightOpacity = 0, highlightElementId, highlightStyle, rowProgress, notFoundStyle, statusStyle, statusElementId, focusRequest = false, responseSummary = false, rowFontSize, requestLabel, visibleRows, rowHeight: requestedRowHeight,
}) => {
  const frame = useCurrentFrame();
  const enlarged = focusRequest || responseSummary;
  const fontSize = rowFontSize ?? (enlarged ? 56 : 40);
  const rowHeight = requestedRowHeight ?? (enlarged ? 160 : NETWORK_ROW_HEIGHT);
  // Reserve exactly visibleRows complete rows below the fixed header.
  const titleHeight = visibleRows === undefined ? (enlarged ? 76 : 104) : 0;
  const headerHeight = visibleRows === undefined ? (enlarged ? 80 : 88) : height - 6 - visibleRows * rowHeight;
  const footerHeight = visibleRows === undefined ? 72 : 0;
  const viewportHeight = enlarged ? rowHeight : height - titleHeight - headerHeight - footerHeight - 6;
  const offset = Math.max(0, Math.min(scrollOffset, Math.max(0, rows.length * rowHeight - viewportHeight)));
  const columns = responseSummary ? RESPONSE_COLUMNS : focusRequest ? FOCUS_COLUMNS : COLUMNS;
  const isPending = (row: NetworkRow, i: number) => row.pending || (pending && i === 0);
  const loading = rows.some(isPending);
  const cardOpacity = notFoundStart === undefined ? 1 : notFoundOpacity(frame, notFoundStart);

  return (
    <div style={{position: 'relative', width, height, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', overflow: 'hidden', background: P.bg, color: P.text, border: `3px solid ${P.muted}`, borderRadius: 20, fontFamily: FONT, fontSize: 40, boxShadow: `0 0 28px ${P.secondary}18`}}>
      {titleHeight > 0 && <div style={{height: titleHeight, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 30px', background: P.panel}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 18, fontSize: 40, fontWeight: 700}}><div style={{height: 42, width: 10, borderRadius: 5, background: P.primary}} />Network</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 16, color: loading ? P.accent : P.success}}>{loading && <Spinner frame={frame} />}{loading ? '等待响应' : '请求完成'}</div>
      </div>}
      <div role="table" aria-label="网络请求列表" style={{display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0}}>
        <div role="row" style={{display: 'grid', gridTemplateColumns: columns, alignItems: 'center', height: headerHeight, flexShrink: 0, padding: '0 24px', background: P.panel2, color: P.text2, fontSize: responseSummary ? 48 : Math.max(40, rowFontSize ?? 40), fontWeight: 700}}>
          {(responseSummary ? ['名称', '状态', '大小', '时间'] : focusRequest ? ['名称', '方法', '状态', '类型', '大小', '时间'] : ['名称', '方法', '状态', '大小', '时间', '瀑布图']).map((label, i) => <div role="columnheader" key={label} style={{opacity: focusRequest && !responseSummary && i >= 3 ? 0.55 : 1}}>{label}</div>)}
        </div>
        <div role="rowgroup" style={{flex: enlarged ? `0 0 ${rowHeight}px` : 1, minHeight: 0, position: 'relative', overflow: 'hidden'}}>
          <div data-element={rowGroupElementId} data-component={rowGroupElementId ? 'NetworkRowsScroll' : undefined} style={firstRowAlwaysVisible ? undefined : rowGroupStyle}><div style={{transform: `translateY(${-offset}px)`}}>
            {rows.map((row, i) => {
              const waiting = isPending(row, i);
              const statusColor = row.status === undefined ? P.text2 : row.status >= 400 ? P.danger : row.status >= 200 && row.status < 300 ? P.success : P.accent;
              const start = Math.max(0, Math.min(1000, row.start ?? 0));
              const duration = Math.max(0, Math.min(1000 - start, row.duration ?? 85));
              const groupStyle = firstRowAlwaysVisible && i > 0 ? rowGroupStyle : undefined;
              return (
                <div role="row" data-element={i === 0 ? rowElementId : undefined} data-component={i === 0 && rowElementId ? 'NetworkRow' : undefined} key={`${row.name}-${i}`} style={{position: 'relative', height: rowHeight, boxSizing: 'border-box', display: 'grid', gridTemplateColumns: columns, alignItems: 'center', padding: '0 24px', borderBottom: `1px solid ${P.muted}44`, background: i === 0 && highlightOpacity > 0 ? `rgba(34,211,238,${highlightOpacity * 0.16})` : i % 2 === 0 ? P.panel : P.bg, boxShadow: i === 0 ? `inset 5px 0 rgba(34,211,238,${highlightOpacity})` : undefined, fontFamily: MONO, fontSize, ...rowStyle, ...groupStyle, opacity: Math.min(1, (rowProgress?.[i] ?? 1) * 4) * Number(rowStyle?.opacity ?? 1) * Number(groupStyle?.opacity ?? 1)}}>
                  {i === 0 && highlightElementId && <div data-element={highlightElementId} data-component="RowHighlight" style={{position: 'absolute', inset: 0, pointerEvents: 'none', boxSizing: 'border-box', border: `4px solid ${P.primary}`, background: `${P.primary}18`, ...highlightStyle}} />}
                  <div role="cell" style={{color: i === 0 ? P.primary : P.text, overflow: 'hidden', whiteSpace: 'nowrap', paddingRight: 18, display: 'flex', alignItems: 'center', gap: 32}}><span style={{overflow: 'hidden', textOverflow: 'ellipsis'}}>{row.name}</span>{requestLabel && i === 0 && <span style={{flexShrink: 0, fontFamily: FONT, fontSize: 48, fontWeight: 700, padding: '10px 24px', borderRadius: 12, background: P.primary, color: P.bg}}>{requestLabel}</span>}</div>
                  {!responseSummary && <div role="cell">{row.method}</div>}
                  <div role="cell" style={{color: statusColor, fontWeight: 700}}>{waiting && <Spinner frame={frame} />}<span data-element={i === 0 ? statusElementId : undefined} data-component={i === 0 && statusElementId ? 'StatusCell' : undefined} style={{display: waiting ? 'none' : 'block', ...statusStyle}}>{row.status ?? '—'}</span></div>
                  {focusRequest && !responseSummary && <div role="cell" style={{fontSize: 40, color: P.text2}}>{row.type}</div>}
                  <div role="cell" style={{fontSize: responseSummary ? fontSize : rowFontSize ?? 40, ...(!waiting ? statusStyle : undefined)}}>{waiting ? '—' : row.size ?? '—'}</div>
                  <div role="cell" style={{fontSize: responseSummary ? fontSize : rowFontSize ?? 40, ...(!waiting ? statusStyle : undefined)}}>{waiting ? '—' : row.time ?? '—'}</div>
                  {!enlarged && <div role="cell" aria-label={waiting ? '请求进行中' : `开始 ${start} ms，耗时 ${duration} ms`} style={{height: '100%', position: 'relative', display: 'flex', alignItems: 'center', backgroundImage: `repeating-linear-gradient(to right, ${P.muted}30 0px, ${P.muted}30 1px, transparent 1px, transparent 25%)`}}>
                    <div style={{position: 'absolute', left: `${start / 10}%`, width: `${(waiting ? 180 : duration) / 10 * (rowProgress?.[i] ?? 1)}%`, maxWidth: `${100 - start / 10}%`, height: 18, borderRadius: 5, background: waiting ? P.accent : row.status && row.status >= 400 ? P.danger : i === 0 ? P.primary : P.secondary, opacity: waiting ? 0.55 + 0.45 * (0.5 + 0.5 * Math.sin(frame / 8)) : 1}} />
                  </div>}
                </div>
              );
            })}
          </div></div>
          {rows.length * rowHeight > viewportHeight && <div style={{position: 'absolute', right: 5, top: 8, bottom: 8, width: 6, borderRadius: 3, background: P.panel2}}><div style={{position: 'absolute', width: 6, borderRadius: 3, height: `${100 * viewportHeight / (rows.length * rowHeight)}%`, top: `${100 * offset / (rows.length * rowHeight)}%`, background: P.muted}} /></div>}
        </div>
      </div>
      {footerHeight > 0 && <div style={{height: footerHeight, flexShrink: 0, padding: '0 26px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: P.panel2, fontSize: 40, color: P.text2}}><span>{rows.length} 个请求 · 示例数据</span>{!enlarged && <span>瀑布图刻度：0 — 1000 ms</span>}</div>}
      {notFound && <div role="status" style={{position: 'absolute', right: 72, bottom: 110, display: 'flex', alignItems: 'center', gap: 28, padding: '26px 34px', borderRadius: 16, border: `3px solid ${P.danger}`, background: P.panel, boxShadow: `0 12px 32px ${P.bg}`, ...notFoundStyle, opacity: cardOpacity * (notFoundStyle?.opacity ?? 1)}}><strong style={{fontFamily: MONO, fontSize: 72, color: P.danger}}>404</strong><div><div style={{fontSize: 40, fontWeight: 700}}>未找到资源</div><div style={{fontSize: 40, color: P.text2, marginTop: 6}}>请求的文件不存在</div></div></div>}
    </div>
  );
};
