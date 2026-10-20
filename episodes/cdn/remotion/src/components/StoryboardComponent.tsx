import React from 'react';
import {BrowserChrome} from './BrowserChrome';
import {NotepadWindow} from './NotepadWindow';
import {DevToolsNetwork, NetworkRow, RowHighlight} from './DevToolsNetwork';
import {StyledPage} from './StyledPage';
import {CalloutTag, CornerBadge, BlockHighlight} from './Annotations';
import {stateAt, UIProps} from './ui';
import {WorldMap, WorldMapPage} from './WorldMap';
export const COMPONENTS: Record<string, React.FC<UIProps>> = {BrowserChrome, NotepadWindow, DevToolsNetwork, NetworkRow, RowHighlight, StyledPage, CalloutTag, CornerBadge, BlockHighlight, WorldMap, WorldMapPage};
export const StoryboardComponent: React.FC<UIProps> = ({e, frame, siblings, browserContentLayout}) => {
  const Component = COMPONENTS[e.component];
  if (!Component) throw new Error(`No storyboard component for ${e.component}`);
  return <Component e={stateAt(e, frame)} frame={frame} source={e} siblings={siblings} browserContentLayout={browserContentLayout} />;
};
