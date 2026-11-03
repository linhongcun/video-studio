/** A fixed DISTINCT conditional example, not a sample of random groups.
 * Each number is a zero-based day of a common year; people never choose dates.
 * The model probabilities below enumerate the birthday conditions directly.
 */
export const EXAMPLE_DAYS = [13, 44, 100, 179, 227, 286, 332, 60, 85, 121, 151, 201, 255, 306, 353, 5, 28, 72, 143, 190, 240, 274, 319] as const;
if (new Set(EXAMPLE_DAYS).size !== 23) throw Error('Conditional example must have distinct dates');
export const dateLabel = (day: number) => {
  const lengths = [31,28,31,30,31,30,31,31,30,31,30,31];
  let month = 0, rest = day;
  while (rest >= lengths[month]) rest -= lengths[month++];
  return `${month + 1}月${rest + 1}日`;
};
export const allDifferent = (people: number) => {
  if (people > 365) return 0;
  let probability = 1;
  for (let k = 0; k < people; k++) probability *= (365 - k) / 365;
  return probability;
};
export const collision = (people: number) => 1 - allDifferent(people);
export const P22 = collision(22);
export const P23 = collision(23);
export const percent = (p: number) => (100 * p).toFixed(2) + '%';
export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const ease = (p: number) => {const q = clamp(p); return q * q * (3 - 2 * q);};
export const tween = (f: number, start: number, end: number) => ease((f - start) / Math.max(1, end - start));
