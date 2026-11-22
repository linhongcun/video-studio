import React from 'react';
import style from './style-v2.json';
import identities from './identities-v1.json';
import {
  FORBIDDEN_HEADER_TITLE,
  resolveLeetcodeHeaderV2,
  type LeetcodeIdentityV2,
} from './header-v2';

const C = {...style.palette, bg: style.palette.background};
const FONT = style.fonts.sans;

export {FORBIDDEN_HEADER_TITLE, resolveLeetcodeHeaderV2, type LeetcodeIdentityV2};

export type LeetcodeHeaderPropsV2 = {
  slug: string;
  detail?: React.ReactNode;
  compact?: boolean;
  identity?: LeetcodeIdentityV2;
};

export const LeetcodeBackdrop = () => (
  <div
    data-leetcode-canvas="true"
    aria-hidden="true"
    style={{
      position: 'absolute',
      inset: 0,
      width: 1920,
      height: 1080,
      background: 'transparent',
      pointerEvents: 'none',
    }}
  />
);

export const LeetcodeHeaderV2 = ({
  slug,
  detail,
  compact = false,
  identity,
}: LeetcodeHeaderPropsV2) => {
  const resolved = resolveLeetcodeHeaderV2({
    slug,
    identity,
    detail,
    compact,
    fallbackEpisodes: identities.episodes,
  });
  const {metrics} = resolved;

  return (
    <div
      data-leetcode-header={slug}
      data-header-version="v2"
      data-header-compact={compact}
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        width: 1920,
        height: metrics.headerHeight,
        pointerEvents: 'none',
        fontFamily: FONT,
      }}
    >
      <div
        data-leetcode-brand="true"
        style={{
          position: 'absolute',
          left: 110,
          top: metrics.top,
          color: C.text,
          fontFamily: style.fonts.brand,
          fontSize: metrics.brandFontSize,
          lineHeight: 1.35,
          fontWeight: 750,
          letterSpacing: -1,
          whiteSpace: 'nowrap',
        }}
      >
        {style.series}
      </div>
      <div
        data-leetcode-number={resolved.numberLabel}
        style={{
          position: 'absolute',
          left: metrics.pillLeft,
          top: metrics.pillTop,
          width: metrics.pillWidth,
          height: metrics.pillHeight,
          background: C.gold,
          borderRadius: 12,
          color: C.bg,
          fontFamily: style.fonts.brand,
          fontSize: metrics.numberFontSize,
          lineHeight: `${metrics.pillHeight}px`,
          textAlign: 'center',
          fontWeight: 750,
          whiteSpace: 'nowrap',
        }}
      >
        {resolved.numberLabel}
      </div>
      <div
        data-leetcode-title="true"
        style={{
          position: 'absolute',
          left: metrics.titleLeft,
          top: metrics.titleTop,
          maxWidth: metrics.titleMaxWidth,
          color: C.teal,
          fontSize: metrics.titleFontSize,
          lineHeight: 1.3,
          fontWeight: 600,
          whiteSpace: 'nowrap',
        }}
      >
        {resolved.primaryLabel}
      </div>
      <div
        data-leetcode-watermark="true"
        style={{
          position: 'absolute',
          right: 110,
          top: metrics.watermarkTop,
          color: C.muted,
          fontSize: metrics.watermarkFontSize,
          lineHeight: 1.3,
          fontWeight: 600,
          whiteSpace: 'nowrap',
        }}
      >
        {style.brand}
      </div>
      {resolved.showDetail && (
        <div
          data-leetcode-detail="true"
          style={{
            position: 'absolute',
            right: 110,
            top: 103,
            maxWidth: 1660,
            color: C.muted,
            fontSize: 20,
            lineHeight: 1.35,
            textAlign: 'right',
            whiteSpace: 'nowrap',
          }}
        >
          {detail}
        </div>
      )}
      <div
        data-leetcode-divider="true"
        style={{
          position: 'absolute',
          left: 110,
          right: 110,
          top: metrics.dividerTop,
          height: 1,
          background: C.edge,
        }}
      />
    </div>
  );
};

export {LeetcodeHeaderV2 as LeetcodeHeader};
