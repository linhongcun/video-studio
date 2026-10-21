import {Shot} from './storyboard';

/** Keep trailing punctuation attached to its sentence without changing source cues. */
export function mergeSubtitlePunctuation(lines: Shot['subtitles']): Shot['subtitles'] {
  const merged: Shot['subtitles'] = [];
  for (const line of lines) {
    const previous = merged[merged.length - 1];
    if (previous && !/[\p{L}\p{Script=Han}]/u.test(line.text)) {
      previous.text += line.text;
      previous.to = line.to;
    } else {
      merged.push({...line});
    }
  }
  return merged;
}
