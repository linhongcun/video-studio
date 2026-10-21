import React from 'react';
import {progress} from '../animation';
import {P} from '../theme';
import {BrowserChrome} from './BrowserChrome';
import {browserPageBox} from './browserLayout';
import {latestKey, rollingNumber} from './pageState';
import {colorToken, Copy, stateAt, UIProps} from './ui';

export const StatusTablePage: React.FC<UIProps> = props => {
  const {frame} = props, e = stateAt(props.e, frame), table = e.table;
  const widths: number[] = table.colWidths, width = widths.reduce((sum, value) => sum + value, 0);
  const pad = table.cellPad ?? 18;
  const rowStyle: React.CSSProperties = {display: 'grid', gridTemplateColumns: widths.map(w => `${w}px`).join(' '), alignItems: 'center', boxSizing: 'border-box'};
  return <BrowserChrome {...props} e={{...e, pageBlank: true}}>
    {e.pageTitle != null && e.pageTitleBox && <div data-status-title style={{...browserPageBox(e, e.pageTitleBox), display: 'flex', alignItems: 'center'}}><Copy size={40} width={e.pageTitleBox[2]} height={e.pageTitleBox[3]} style={{fontWeight: 700}}>{e.pageTitle}</Copy></div>}
    <div role="table" data-status-table style={{...browserPageBox(e, [table.x, table.y, width, table.headerH + e.rows.length * (table.rowH + 4)])}}>
      <div role="row" data-status-header style={{...rowStyle, height: table.headerH, background: P.panel2, color: P.text2}}>{e.columns.map((label: string, i: number) => <div role="columnheader" key={i} style={{padding: `0 ${pad}px`, minWidth: 0}}><Copy size={table.headerFontSize} width={widths[i] - pad * 2} height={table.headerH} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{label}</Copy></div>)}</div>
      {e.rows.map((row, i) => {
        const key = latestKey(row.keys, frame);
        if (!key || frame < (row.appearFrame ?? 0)) return null;
        const tone = e.tones?.[key.tone ?? 'normal'] ?? {}, fade = row.appearFrame > 0 ? progress(frame, row.appearFrame, 6) : 1;
        // The first row touches the header; the 4px gap belongs only between data rows.
        const y = table.headerH + i * (table.rowH + 4);
        const active = rollingNumber(row.keys[0].active, row.keys, 'active', frame, e.countFrames ?? 0);
        const pending = rollingNumber(row.keys[0].pending, row.keys, 'pending', frame, e.countFrames ?? 0);
        const values = [row.name, active, pending, key.status];
        const colors = [tone.text, e.dimCounts ? e.dimColor : tone.text, e.dimCounts ? e.dimColor : key.pendingColor ?? tone.text, key.statusColor ?? tone.text];
        const note = table.side && latestKey(row.notes, frame);
        return <React.Fragment key={row.id}>
          <div role="row" data-status-row={row.id} data-tone={key.tone} data-highlighted={e.highlightRow === row.id} style={{...rowStyle, position: 'absolute', left: 0, top: y, width, height: table.rowH, borderRadius: 8, background: colorToken(tone.bg), color: colorToken(tone.text), opacity: fade * (tone.opacity ?? 1), outline: e.highlightRow === row.id ? `3px solid ${P.accent}` : undefined}}>
            {values.map((value, j) => <div role="cell" key={j} style={{minWidth: 0, padding: `0 ${pad}px`, color: colorToken(colors[j])}}><Copy mono={j === 1 || j === 2} size={table.fontSize} width={widths[j] - pad * 2} height={table.rowH} style={{whiteSpace: 'nowrap', fontWeight: j === 3 ? 700 : 400}}>{String(value ?? '')}</Copy></div>)}
          </div>
          {note?.text != null && <div data-status-note={row.id} style={{position: 'absolute', left: table.side.x - table.x, top: y + 14, width: table.side.w, height: table.rowH - 28, display: 'flex', alignItems: 'center', padding: '0 12px', boxSizing: 'border-box', borderRadius: 8, border: `2px solid ${colorToken(note.color)}`, background: P.bg, color: colorToken(note.color), opacity: fade}}><Copy size={table.side.fontSize} width={table.side.w - 28} height={table.rowH - 32} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{note.text}</Copy></div>}
        </React.Fragment>;
      })}
    </div>
  </BrowserChrome>;
};
