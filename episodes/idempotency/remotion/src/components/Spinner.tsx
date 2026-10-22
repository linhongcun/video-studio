import React from 'react';
import { P } from '../theme';
import {colorToken, stateAt, UIProps} from './ui';
export const Spinner: React.FC<{
  frame: number;
  color?: string;
}> = ({
  frame,
  color = P.primary
}) => <svg width="100%" height="100%" viewBox="0 0 100 100" style={{
  transform: `rotate(${frame * 10}deg)`
}} aria-label="加载中"><circle cx="50" cy="50" r="38" stroke="#CBD6DE" strokeWidth="8" fill="none" /><path d="M50 12a38 38 0 0 1 38 38" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" /></svg>;

export const SpinnerElement: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame);
  return <Spinner frame={e.spinning ? frame : 0} color={colorToken(e.color)} />;
};
