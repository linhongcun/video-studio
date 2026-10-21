import React from 'react';
import {progress} from '../animation';
import {P} from '../theme';
import {BrowserChrome} from './BrowserChrome';
import {browserPageBox} from './browserLayout';
import {latestKey, rollingNumber} from './pageState';
import {colorToken, Copy, stateAt, textWidth, UIProps} from './ui';

export const StatusTablePage: React.FC<UIProps> = props => {
  const {frame} = props, e = stateAt(props.e, frame), table = e.table;
  const widths: number[] = table.colWidths, width = widths.reduce((sum, value) => sum + value, 0);
  const pad = table.cellPad ?? 18;
  const legacy = !e.valueFields, fields: string[] = e.valueFields ?? ['name', 'active', 'pending', 'status'];
  const rowGap = table.rowGap ?? 4;
  const rowStyle: React.CSSProperties = {display: 'grid', gridTemplateColumns: widths.map(w => `${w}px`).join(' '), alignItems: 'center', boxSizing: 'border-box'};
  return <BrowserChrome {...props} e={{...e, pageBlank: true}}>
    {e.pageTitle != null && e.pageTitleBox && <div data-status-title style={{...browserPageBox(e, e.pageTitleBox), display: 'flex', alignItems: 'center'}}><Copy size={e.pageTitleSize ?? 40} width={e.pageTitleBox[2]} height={e.pageTitleBox[3]} style={{fontWeight: 700}}>{e.pageTitle}</Copy></div>}
    <div role="table" data-status-table style={{...browserPageBox(e, [table.x, table.y, width, table.headerH + e.rows.length * table.rowH + Math.max(0, e.rows.length - 1) * rowGap])}}>
      <div role="row" data-status-header style={{...rowStyle, height: table.headerH, background: P.panel2, color: P.text2}}>{e.columns.map((label: string, i: number) => <div role="columnheader" key={i} style={{padding: `0 ${pad}px`, minWidth: 0}}><Copy size={table.headerFontSize} width={widths[i] - pad * 2} height={table.headerH} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{label}</Copy></div>)}</div>
      {e.rows.map((row, i) => {
        const key = latestKey(row.keys, frame);
        if (!key || frame < (row.appearFrame ?? 0)) return null;
        const tone = e.tones?.[key.tone ?? 'normal'] ?? {}, fade = row.appearFrame > 0 ? progress(frame, row.appearFrame, 6) : 1;
        const y = table.headerH + i * (table.rowH + rowGap);
        const values = fields.map((field, j) => j === 0 ? row.name : legacy && (field === 'active' || field === 'pending')
          ? rollingNumber(row.keys[0][field], row.keys, field, frame, e.countFrames ?? 0) : key[field]);
        const colors = fields.map(field => legacy && e.dimCounts && (field === 'active' || field === 'pending')
          ? e.dimColor : key[`${field}Color`] ?? tone.text ?? 'text');
        const note = table.side && latestKey(row.notes, frame);
        return <React.Fragment key={row.id}>
          <div role="row" data-status-row={row.id} data-tone={key.tone} data-highlighted={e.highlightRow === row.id} style={{...rowStyle, position: 'absolute', left: 0, top: y, width, height: table.rowH, borderRadius: 8, background: colorToken(tone.bg), color: colorToken(tone.text), opacity: fade * (tone.opacity ?? 1), outline: e.highlightRow === row.id ? `3px solid ${P.accent}` : undefined}}>
            {values.map((value, j) => {
              const cellWidth = Math.max(1, widths[j] - pad * 2), text = String(value ?? '');
              const hasNote = j === 0 && !!row.nameNote, noteSize = table.noteFontSize ?? table.fontSize;
              // Reserve both strings together; Copy measures each font within its share.
              const nameWidth = textWidth(text, table.fontSize) * 1.03, noteWidth = textWidth(String(row.nameNote ?? ''), noteSize) * 1.03;
              const scale = Math.min(1, Math.max(0, cellWidth - 12) / Math.max(1, nameWidth + noteWidth));
              return <div role="cell" key={j} style={{minWidth: 0, padding: `0 ${pad}px`, color: colorToken(colors[j]), display: 'flex', alignItems: 'center', gap: hasNote ? 12 : undefined}}>
                <Copy mono={legacy && (j === 1 || j === 2)} size={hasNote ? table.fontSize * scale : table.fontSize} width={hasNote ? nameWidth * scale : cellWidth} height={table.rowH} style={{whiteSpace: 'nowrap', fontWeight: j === values.length - 1 ? 700 : 400}}>{text}</Copy>
                {hasNote && <Copy size={noteSize * scale} width={noteWidth * scale} height={table.rowH} style={{whiteSpace: 'nowrap', color: P.text2}}>{row.nameNote}</Copy>}
              </div>;
            })}
            {row.progress && <div data-row-progress style={{position: 'absolute', left: 0, bottom: 0, height: table.progressH, width: width * (row.progress.endFrame <= row.progress.startFrame ? 1 : progress(frame, row.progress.startFrame, row.progress.endFrame - row.progress.startFrame)), background: colorToken(row.progress.color)}} />}
          </div>
          {note?.text != null && <div data-status-note={row.id} style={{position: 'absolute', left: table.side.x - table.x, top: y + 14, width: table.side.w, height: table.rowH - 28, display: 'flex', alignItems: 'center', padding: '0 12px', boxSizing: 'border-box', borderRadius: 8, border: `2px solid ${colorToken(note.color)}`, background: P.bg, color: colorToken(note.color), opacity: fade}}><Copy size={table.side.fontSize} width={table.side.w - 28} height={table.rowH - 32} style={{whiteSpace: 'nowrap', fontWeight: 700}}>{note.text}</Copy></div>}
        </React.Fragment>;
      })}
    </div>
  </BrowserChrome>;
};
