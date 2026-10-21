import React from 'react';
import {BrowserChrome} from './BrowserChrome';
import {NotepadWindow} from './NotepadWindow';
import {DevToolsNetwork, NetworkRow, RowHighlight} from './DevToolsNetwork';
import {StyledPage} from './StyledPage';
import {CalloutTag, CornerBadge, BlockHighlight} from './Annotations';
import {stateAt, UIProps} from './ui';
import {InfoCard} from './InfoCard';
export const COMPONENTS: Record<string, React.FC<UIProps>> = {BrowserChrome, NotepadWindow, DevToolsNetwork, NetworkRow, RowHighlight, StyledPage, CalloutTag, CornerBadge, BlockHighlight, InfoCard};
export const StoryboardComponent: React.FC<UIProps> = ({e, frame, canvas, siblings, browserContentLayout}) => {
  const Component = COMPONENTS[e.component];
  if (!Component) throw new Error(`No storyboard component for ${e.component}`);
  return <Component e={stateAt(e, frame)} frame={frame} canvas={canvas} source={e} siblings={siblings} browserContentLayout={browserContentLayout} />;
};
