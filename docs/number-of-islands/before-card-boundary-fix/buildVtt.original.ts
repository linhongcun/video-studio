export function buildVtt(slug: string) {
  if (!fs.existsSync(path.join(EP_DIR, slug, 'storyboard.json'))) return 'WEBVTT\n';
  const {fps, scenes} = shotPlan(slug);
  const ts = (f: number) => {
    const s = f / fps;
    const hh = Math.floor(s / 3600), mm = Math.floor((s % 3600) / 60), ss = (s % 60).toFixed(3).padStart(6, '0');
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${ss}`;
  };
  const v2 = scenes.some((s: any) => s.chapterId);
  const n = (s: string) => s.replace(v2 ? /[\s，。：？！；、,.:?!;—“”"()（）]/g : /[\s，。：？！,.:?!—]/g, '').length || 1;
  const cues: string[] = [];
  for (const sc of scenes) for (const {sh, from, dur, audioFrames} of sc.shots) {
    const subs = sh.subtitles ?? [];
    const timed = subs.length > 0 && subs.every((s: any, i: number) =>
      Number.isInteger(s.from) && Number.isInteger(s.to) && s.from >= 0 && s.to >= s.from && s.to < dur
      && (i === 0 || s.from > subs[i - 1].to));
    if (timed) {
      subs.forEach((s: any) => cues.push(`${ts(from + s.from)} --> ${ts(from + s.to + 1)}\n${s.text}`));
      continue;
    }
    const total = subs.reduce((a: number, s: any) => a + n(s.text), 0);
    let t = 0;
    subs.forEach((s: any, i: number) => {
      const a = Math.round((t / total) * audioFrames);
      t += n(s.text);
      const b = i === subs.length - 1 ? audioFrames + 6 : Math.round((t / total) * audioFrames) - 1;
      cues.push(`${ts(from + a)} --> ${ts(from + b + 1)}\n${s.text}`);
    });
  }
  return `WEBVTT\n\n${cues.join('\n\n')}\n`;
}

