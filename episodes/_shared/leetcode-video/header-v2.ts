export const FORBIDDEN_HEADER_TITLE = '算法可视化';

export type LeetcodeIdentityV2 = {
  number: number;
  title: string;
  method?: string;
};

export type FallbackIdentityV1 = {
  slug: string;
  number: number;
  title: ReadonlyArray<string>;
  method?: string;
};

export type HeaderV2Metrics = {
  headerHeight: number;
  top: number;
  pillLeft: number;
  pillTop: number;
  pillWidth: number;
  pillHeight: number;
  titleLeft: number;
  titleTop: number;
  titleMaxWidth: number;
  brandFontSize: number;
  numberFontSize: number;
  titleFontSize: number;
  watermarkTop: number;
  watermarkFontSize: number;
  dividerTop: number;
};

export type ResolvedHeaderV2 = {
  slug: string;
  number: number;
  numberLabel: string;
  title: string;
  method: string;
  primaryLabel: string;
  showDetail: boolean;
  metrics: HeaderV2Metrics;
};

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function computeHeaderV2Metrics(number: number, compact = false): HeaderV2Metrics {
  const digits = String(number).length;
  const top = compact ? 20 : 49;
  const pillTop = compact ? 19 : 48;
  const pillHeight = compact ? 42 : 52;
  const pillLeft = 325;
  const extraDigits = Math.max(0, digits - 4);
  const pillWidth =
    digits <= 3 ? 142 : (compact ? 154 : 168) + extraDigits * (compact ? 16 : 20);
  const titleLeft = pillLeft + pillWidth + 27;
  const watermarkReserve = compact ? 124 : 140;
  const titleMaxWidth = 1810 - titleLeft - watermarkReserve;

  return {
    headerHeight: compact ? 84 : 150,
    top,
    pillLeft,
    pillTop,
    pillWidth,
    pillHeight,
    titleLeft,
    titleTop: top + (compact ? 5 : 9),
    titleMaxWidth,
    brandFontSize: compact ? 29 : 36,
    numberFontSize: compact ? 25 : 30,
    titleFontSize: compact ? 22 : 26,
    watermarkTop: top + (compact ? 5 : 8),
    watermarkFontSize: compact ? 22 : 26,
    dividerTop: compact ? 78 : 136,
  };
}

export function isRedundantHeaderDetail(detail: unknown, number: number, title: string): boolean {
  if (typeof detail !== 'string') return false;
  const trimmed = detail.trim();
  if (!trimmed) return true;
  if (trimmed === title) return true;

  const escapedTitle = escapeRegExp(title);
  const prefixThenTitle = new RegExp(
    `^(?:leetcode\\s*|lc\\.?\\s*)${number}\\s*[·•:\\-：—]\\s*${escapedTitle}$`,
    'i',
  );
  if (prefixThenTitle.test(trimmed)) return true;

  const titleThenPrefix = new RegExp(
    `^${escapedTitle}\\s*[·•:\\-：—]\\s*(?:leetcode\\s*|lc\\.?\\s*)${number}$`,
    'i',
  );
  return titleThenPrefix.test(trimmed);
}

export function formatCompactHeaderLabel(title: string, method: string): string {
  const cleanMethod = method.trim();
  if (!cleanMethod || cleanMethod === title) return title;
  if (cleanMethod.startsWith(title)) return cleanMethod;
  return `${title} · ${cleanMethod}`;
}

export function resolveLeetcodeHeaderV2(options: {
  slug: string;
  identity?: LeetcodeIdentityV2;
  detail?: unknown;
  compact?: boolean;
  fallbackEpisodes?: ReadonlyArray<FallbackIdentityV1>;
}): ResolvedHeaderV2 {
  const {slug, identity, detail, compact = false, fallbackEpisodes = []} = options;
  let resolvedNumber: number;
  let resolvedTitle: string;
  let resolvedMethod: string;

  if (identity) {
    resolvedNumber = identity.number;
    resolvedTitle = typeof identity.title === 'string' ? identity.title.trim() : '';
    resolvedMethod = typeof identity.method === 'string' ? identity.method.trim() : '';
  } else {
    const fallback = fallbackEpisodes.find((item) => item.slug === slug);
    if (!fallback) {
      throw new Error(
        `Missing LeetCode v2 identity for slug "${slug}": pass identity={{number, title, method}}`,
      );
    }
    resolvedNumber = fallback.number;
    resolvedTitle = fallback.title.join('').trim();
    resolvedMethod = typeof fallback.method === 'string' ? fallback.method.trim() : '';
  }

  if (!Number.isInteger(resolvedNumber) || resolvedNumber <= 0) {
    throw new Error(`Invalid LeetCode problem number for "${slug}": ${String(resolvedNumber)}`);
  }
  if (!resolvedTitle) {
    throw new Error(`Missing problem title for LeetCode header "${slug}" (LC.${resolvedNumber})`);
  }
  if (resolvedTitle === FORBIDDEN_HEADER_TITLE) {
    throw new Error(
      `LeetcodeHeaderV2 title for "${slug}" must be the problem name, not "${FORBIDDEN_HEADER_TITLE}"`,
    );
  }

  const primaryLabel = compact
    ? formatCompactHeaderLabel(resolvedTitle, resolvedMethod)
    : resolvedTitle;

  const hasDetail = detail !== undefined && detail !== null && detail !== false;
  const showDetail =
    !compact && hasDetail && !isRedundantHeaderDetail(detail, resolvedNumber, resolvedTitle);

  return {
    slug,
    number: resolvedNumber,
    numberLabel: `LC.${resolvedNumber}`,
    title: resolvedTitle,
    method: resolvedMethod,
    primaryLabel,
    showDetail,
    metrics: computeHeaderV2Metrics(resolvedNumber, compact),
  };
}
