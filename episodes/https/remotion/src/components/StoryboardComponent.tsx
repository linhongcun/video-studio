import React from 'react';
import {BrowserChrome as Chrome} from './BrowserChrome';
import {NotepadWindow} from './NotepadWindow';
import {CertPopup} from './CertPopup';
import {DevToolsNetwork, NetworkRow, RowHighlight} from './DevToolsNetwork';
import {ScrambleText as Scramble} from './ScrambleText';
import {FlyingLabel as Flying} from './FlyingLabel';
import {StyledPage as Page} from './StyledPage';
import {KeyIcon, WifiIcon, LockIcon, CalloutTag, CornerBadge, RedPulseOutline, BlockHighlight, ArrowLabel, AddressBarTyping, Stopwatch} from './Annotations';
import {Copy, fitSize, UIProps} from './ui';

const BrowserChrome: React.FC<UIProps> = ({e, frame}) => {
  const failed = e.state === 'secureConnectionFailed' || e.state === 'connectionInterrupted';
  const badge = e.browserBadge, typing = e.browserTyping, lock = e.browserLock;
  const badgeWidth = badge && Math.min(badge.element.w, e.w / 4);
  return <>
    <Chrome width={e.w} height={e.h} frame={frame} title={e.title} text={typing?.element.text ?? e.url} typedChars={e.typedChars} showPadlock={e.showPadlock && !failed} padlockElementId={lock?.element.id} padlockStyle={lock?.style} showCursor={!typing && e.state === 'addressSelected'} loading={['connectingToImpersonator', 'loginSubmitted'].includes(e.state)} errorTitle={e.errorTitle ?? (e.state === 'connectionInterrupted' ? '连接已中断' : undefined)} errorColor={e.errorColor} connectionLabel={e.connectionLabel} highlightText={e.highlightText} addressHighlighted={e.addressHighlighted || ['urlHighlighted', 'addressHighlighted'].includes(e.state)} lockHighlighted={e.lockHighlighted}
      addressContent={typing && <div data-element={typing.element.id} data-component={typing.element.component} data-state={typing.element.state} style={typing.style}><AddressBarTyping e={{...typing.element, nativeAddress: true}} frame={frame} /></div>}
      toolbarAccessoryWidth={badgeWidth}
      toolbarAccessory={badge && <div data-element={badge.element.id} data-component={badge.element.component} data-state={badge.element.state} style={badge.style}><CornerBadge e={{...badge.element, w: badgeWidth}} frame={frame} /></div>}>
      {e.page && <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', padding: '0 24px'}}><Copy size={Math.max(24, Math.min(40, e.w / 14))} width={e.w - 48}>{e.page}</Copy></div>}
      {e.state === 'fakeLoginShown' && <div data-page="login" style={{padding: '12% 7%', display: 'grid', gap: 24}}>{e.loginLines?.map((line: string) => <Copy key={line} size={40} width={e.w * .86} style={{padding: 12, border: '2px solid #6B7280', borderRadius: 10}}>{line}</Copy>)}</div>}
    </Chrome>
    {e.stopwatch && <div style={{position: 'absolute', left: e.stopwatch.x - e.x, top: e.stopwatch.y - e.y, width: e.stopwatch.w, height: e.stopwatch.h}}><Stopwatch label={e.stopwatch.label} /></div>}
  </>;
};
const ScrambleText: React.FC<UIProps> = ({e}) => <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center'}}><Scramble text={e.from_ ?? e.text} to={e.to} progress={e.scrambleProgress ?? 0} red={!!e.color} editedIndex={e.editedIndex} label={e.label} style={{fontSize: fitSize(e.to ?? e.from_ ?? e.text ?? '', e.w, e.fontSize ?? 40, true), ...(e.color && e.editedIndex === undefined ? {color: e.color} : {})}} /></div>;
const FlyingLabel: React.FC<UIProps> = ({e}) => <Flying text={e.text} x0={0} y0={0} x1={e.flyTo[0] - e.x} y1={e.flyTo[1] - e.y} progress={e.flightProgress ?? 0} width={e.w} height={e.h} fontSize={Math.max(24, e.fontSize ?? 36)} color={e.color} />;
const StyledPage: React.FC<UIProps> = ({e}) => <Page imagesRevealed={e.imagesRevealed} title={e.title ?? ''} />;
export const COMPONENTS: Record<string, React.FC<UIProps>> = {BrowserChrome, NotepadWindow, DevToolsNetwork, NetworkRow, RowHighlight, CertPopup, ScrambleText, KeyIcon, FlyingLabel, ArrowLabel, AddressBarTyping, WifiIcon, LockIcon, StyledPage, CalloutTag, CornerBadge, RedPulseOutline, BlockHighlight};
export const StoryboardComponent: React.FC<UIProps> = ({e, frame}) => {
  const Component = COMPONENTS[e.component];
  if (!Component) throw new Error(`No storyboard component for ${e.component}`);
  return <Component e={e} frame={frame} />;
};
