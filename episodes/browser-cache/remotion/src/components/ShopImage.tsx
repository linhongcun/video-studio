import React from 'react';
import {P} from '../theme';
import {Spinner} from './Spinner';
import {stateAt, UIProps} from './ui';

export type ShopImageVariant = 'arc' | 'wave' | 'pattern1' | 'pattern2';
export type ShopImageState = 'placeholder' | 'loading' | 'shown';

/** Pure drawing shared by page images and standalone storyboard images. */
export const ShopImageDrawing: React.FC<{
  variant: ShopImageVariant; state?: ShopImageState; w: number; h: number;
  radius?: number; spinnerSize?: number; frame: number; reveal?: number; id?: string;
}> = ({variant, state = 'shown', w, h, radius = Math.min(w, h) * .18, spinnerSize, frame, reveal = 1, id = variant}) => {
  const gradient = `shop-gradient-${id.replace(/[^a-zA-Z0-9_-]/g, '-')}`;
  return <div data-shop-image={variant} data-image-state={state} style={{position: 'relative', width: w, height: h, borderRadius: radius, overflow: 'hidden', background: '#334155'}}>
    {state === 'shown' && <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden style={{display: 'block', opacity: reveal}}>
      {variant === 'arc' ? <>
        <defs><linearGradient id={gradient} x1="0" y1="0" x2="1" y2="1"><stop stopColor={P.primary} /><stop offset="1" stopColor={P.secondary} /></linearGradient></defs>
        <rect width="100" height="100" fill={`url(#${gradient})`} />
        <path d="M24 66a30 30 0 1 1 52 0M37 59a15 15 0 1 1 26 0" fill="none" stroke={P.bg} strokeWidth="9" strokeLinecap="round" />
        <circle cx="50" cy="75" r="5" fill={P.bg} />
      </> : variant === 'wave' ? <>
        <rect width="100" height="100" fill={P.accent} />
        {[30, 50, 70].map(y => <path key={y} d={`M14 ${y}q18 -18 36 0t36 0`} fill="none" stroke={P.panel} strokeWidth="7" strokeLinecap="round" />)}
      </> : variant === 'pattern1' ? <>
        <rect width="100" height="100" fill={P.panel2} />
        <path d="M0 0h50v50H0ZM50 50h50v50H50Z" fill={P.secondary} />
        <circle cx="50" cy="50" r="31" fill={P.primary} />
        <path d="m50 24 26 26-26 26-26-26Z" fill={P.bg} />
      </> : <>
        <rect width="100" height="100" fill={P.panel} />
        <path d="m0 0 50 50L0 100ZM100 0 50 50l50 50Z" fill={P.accent} />
        <path d="m20 0 50 50-50 50h22l50-50L42 0Z" fill={P.success} />
        <circle cx="24" cy="50" r="12" fill={P.text} />
      </>}
    </svg>}
    {state === 'loading' && <div data-shop-spinner style={{position: 'absolute', left: '50%', top: '50%', width: spinnerSize, height: spinnerSize, transform: 'translate(-50%, -50%)'}}><Spinner frame={frame} /></div>}
  </div>;
};

export const ShopImage: React.FC<UIProps> = ({e: original, frame}) => {
  const e = stateAt(original, frame);
  return <ShopImageDrawing id={e.id} variant={e.variant} state={e.state} w={e.w} h={e.h} radius={e.radius} spinnerSize={e.spinnerSize} frame={frame} />;
};
