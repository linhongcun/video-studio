import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import storyboard from '../../storyboard.json';
import {SHOT_SCENES, SceneProps, StoryboardElements} from './ShotScenes';
import {shots, totalFrames} from './storyboard';
import {FONT, P} from './theme';
import {shotFrameMode} from './frameMode';

export {totalFrames};
export {SHOT_STILL_FRAMES} from './shotFrames';

// Set by remotion.config.ts from the actual public directory at bundle time.
declare const __HAS_VOICE_AUDIO__: boolean;

export const ShotScene: React.FC<Omit<SceneProps, 'frame'>> = ({shot}) => {
  const frame = useCurrentFrame();
  const Scene = SHOT_SCENES[shot.id];
  if (!Scene) throw new Error(`No scene implementation for ${shot.id}`);
  const subtitle = shot.subtitles.find((line) => frame >= line.from && frame <= line.to);
  const subtitleElement = shot.elements.find((e) => e.id === 'subtitle');
  return <AbsoluteFill data-shot={shot.id} data-direction={shot.direction} data-frame-mode={shotFrameMode(shot, frame)} style={{background: P.bg, color: P.text, fontFamily: FONT}}>
    <Scene shot={shot} frame={frame} />
    <StoryboardElements shot={shot} frame={frame} />
    {subtitleElement && <div data-element="subtitle" style={{position: 'absolute', left: subtitleElement.x, top: subtitleElement.y, width: subtitleElement.w, height: subtitleElement.h, display: 'flex', justifyContent: subtitleElement.align === 'center' ? 'center' : 'flex-start', alignItems: 'center', textAlign: subtitleElement.align, fontSize: subtitleElement.fontSize, lineHeight: 1.4, fontWeight: subtitleElement.fontWeight ?? 500, color: subtitleElement.color, zIndex: subtitleElement.z, background: subtitle ? `${P.bg}EE` : undefined, borderRadius: 12}}>{subtitle?.text}</div>}
  </AbsoluteFill>;
};

export const Main: React.FC = () => {
  const hasVoice = typeof __HAS_VOICE_AUDIO__ !== 'undefined' && __HAS_VOICE_AUDIO__;
  return <AbsoluteFill style={{background: P.bg, fontFamily: FONT}}>
    {/* voice.wav is pre-placed per storyboard shots[].voice (voice/place_v2.py), so it plays continuously from frame 0 */}
    {hasVoice && <Audio src={staticFile('audio/voice.wav')} />}
    {shots.map((shot) => <Sequence key={shot.id} name={`${shot.id} · ${shot.direction}`} from={shot.from} durationInFrames={shot.durationInFrames}><ShotScene shot={shot} /></Sequence>)}
  </AbsoluteFill>;
};

export const MAIN_VIDEO = {
  width: storyboard.meta.width,
  height: storyboard.meta.height,
  fps: storyboard.meta.fps,
  durationInFrames: totalFrames,
};
