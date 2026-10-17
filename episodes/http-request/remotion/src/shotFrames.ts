import {shots} from './storyboard';

/** Local review points after each shot's main action. The response shot samples
 * the brief 404 plateau; 16a keeps the ongoing waterfall for 16b; all values exported below are absolute video frames. */
export const SHOT_LOCAL_STILL_FRAMES: Record<string, number> = {
  '01-hook': 120,
  '02-typing': 180,
  '03-cache-look': 222,
  '04-cache-hit': 240,
  '05-cache-miss': 205,
  '06-contacts': 175,
  '07a-dns-ask': 112,
  '07b-dns-ask': 160,
  '08-dns-remember': 200,
  '09a-handshake': 112,
  '09b-handshake': 160,
  '10a-lock': 215,
  '10b-lock': 82,
  '11-wifi': 215,
  '12-slow': 250,
  '13a-devtools-request': 190,
  '13b-devtools-request': 80,
  '14-server-work': 240,
  '15-response': 214,
  '16a-waterfall': 177,
  '16b-waterfall': 94,
  '17-html': 220,
  '18a-css': 185,
  '18b-css': 94,
  '19a-paint': 125,
  '19b-paint': 176,
  '20a-recap': 175,
  '20b-recap': 205,
  '20c-recap': 230,
};

export const SHOT_STILL_FRAMES: Record<string, number> = Object.fromEntries(shots.map((shot) => {
  const local = SHOT_LOCAL_STILL_FRAMES[shot.id];
  if (local === undefined || local < 0 || local >= shot.durationInFrames) throw new Error(`Invalid still frame for ${shot.id}`);
  return [shot.id, shot.from + local];
}));
