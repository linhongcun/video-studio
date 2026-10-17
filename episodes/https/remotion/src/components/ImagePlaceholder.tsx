import React from 'react';
import {P} from '../theme';

export type ImagePlaceholderProps = {
  progress?: number;
  variant?: 'hero' | 'left' | 'right';
  greyColor?: string;
};

/** Keep the slot neutral until its image is ready, then show crisp artwork. */
export const ImagePlaceholder: React.FC<ImagePlaceholderProps> = ({progress = 0, variant = 'hero', greyColor = '#6B7280'}) => {
  const p = Math.max(0, Math.min(1, progress));
  return (
    <div style={{position: 'relative', width: '100%', height: '100%', overflow: 'hidden', background: greyColor, borderRadius: 12}}>
      <svg width="100%" height="100%" viewBox="0 0 400 220" preserveAspectRatio="xMidYMid slice" aria-label={p < 1 ? '等待图片' : '抽象示例图片'} style={{display: 'block', opacity: p}}>
        <rect width={400} height={220} fill={variant === 'right' ? P.primary : P.secondary} />
        {variant === 'hero' ? <>
          <circle cx={296} cy={66} r={66} fill={P.primary} />
          <path d="M-30 240 132 48 294 240Z" fill={P.bg} />
          <path d="m154 240 130-144 146 144Z" fill={P.panel2} />
          <circle cx={108} cy={84} r={22} fill={P.accent} />
        </> : variant === 'left' ? <>
          <rect x={52} y={48} width={168} height={168} rx={28} fill={P.primary} transform="rotate(-18 136 132)" />
          <circle cx={284} cy={94} r={62} fill={P.accent} />
          <rect x={208} y={158} width={170} height={32} rx={16} fill={P.bg} />
        </> : <>
          <circle cx={100} cy={144} r={90} fill={P.secondary} />
          <path d="m182 188 82-160 84 160Z" fill={P.panel} />
          <circle cx={312} cy={68} r={28} fill={P.accent} />
        </>}
      </svg>
    </div>
  );
};
