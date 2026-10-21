import React from 'react';
import {InfoCard} from './InfoCard';
import {UIProps} from './ui';

/** Additional storyboard components alongside the episode's directed scenes. */
export const COMPONENTS: Record<string, React.FC<UIProps>> = {InfoCard};
export const StoryboardComponent: React.FC<UIProps> = ({e, frame, canvas}) => {
  const Component = COMPONENTS[e.component];
  if (!Component) throw new Error(`No storyboard component for ${e.component}`);
  return <Component e={e} frame={frame} canvas={canvas} />;
};
