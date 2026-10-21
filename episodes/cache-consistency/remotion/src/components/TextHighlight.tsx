import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {flushSync} from 'react-dom';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {P} from '../theme';
import {colorToken, stateAt, UIProps} from './ui';
import {clipHighlightBox, HighlightBox} from './highlightClip';

const useBrowserLayoutEffect = typeof document === 'undefined' ? useEffect : useLayoutEffect;

/** Measure the rendered Copy, including fitting, font fallback, borders and camera scale. */
export const TextHighlight: React.FC<UIProps> = ({e: original, frame, siblings = []}) => {
  const e = stateAt(original, frame);
  const ref = useRef<HTMLDivElement>(null);
  const [geometry, setGeometry] = useState<HighlightBox | null>(null);
  useBrowserLayoutEffect(() => {
    const highlight = ref.current;
    const layer: HTMLElement | null = highlight?.parentElement ?? null;
    const scene = layer?.closest<HTMLElement>('[data-storyboard-scene], [data-cover-scene]') ?? layer?.parentElement;
    if (!layer || !scene) {
      setGeometry(null);
      return;
    }
    // Wait on every seek, so a frame never captures fallback metrics or a previous frame's box.
    const handle = delayRender(`Measure highlight ${e.id}`);
    let cancelled = false;
    const measure = async () => {
      await document.fonts.ready;
      if (cancelled) return;
      const context = document.createElement('canvas').getContext('2d');
      const authored = layer.getBoundingClientRect();
      const scale = authored.width / parseFloat(getComputedStyle(layer).width);
      let best: {left: number; width: number; distance: number} | null = null;
      if (e.highlightText && context && scale > 0) for (const original of siblings) {
        const sibling = stateAt(original, frame);
        if (frame < (sibling.appearFrame ?? 0) || frame >= (sibling.disappearFrame ?? Infinity) || sibling.state === 'hidden') continue;
        const source = Array.from(scene.children).find(child => child.getAttribute('data-element') === sibling.id) as HTMLElement | undefined;
        if (!source) continue;
        const texts = sibling.component === 'NotepadWindow'
          ? Array.from(source.querySelectorAll<HTMLElement>('[data-terminal-line]')).map(line => line.firstElementChild as HTMLElement)
          : sibling.component === 'BrowserChrome'
            ? Array.from(source.querySelectorAll<HTMLElement>('[data-address-box]')).map(address => address.lastElementChild as HTMLElement)
            : sibling.component === 'DevToolsNetwork'
              ? Array.from(source.querySelectorAll<HTMLElement>('[data-header-line] > [data-fitted-text], [data-storage-row] > [data-fitted-text]'))
            : [];
        const sourceScale = source.getBoundingClientRect().width / parseFloat(getComputedStyle(source).width);
        for (const text of texts) {
          const style = getComputedStyle(text), bounds = text.getBoundingClientRect();
          if (style.visibility === 'hidden' || !text.getClientRects().length || bounds.bottom <= authored.top || bounds.top >= authored.bottom) continue;
          context.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
          const content = text.textContent ?? '';
          for (let index = content.indexOf(e.highlightText); index !== -1; index = content.indexOf(e.highlightText, index + 1)) {
            const left = bounds.left + context.measureText(content.slice(0, index)).width * sourceScale;
            const width = context.measureText(e.highlightText).width * sourceScale;
            // Repeated substrings (e.g. @ns.example and shop.example) use the closest authored box.
            const distance = Math.abs(left + width / 2 - (authored.left + authored.width / 2));
            if (!best || distance < best.distance) best = {left, width, distance};
          }
        }
      }
      // Pad the measured substring and keep the authored vertical extent.
      const box = {left: best ? (best.left - authored.left) / scale - 8 : 0, top: 0, width: best ? best.width / scale + 16 : parseFloat(getComputedStyle(layer).width), height: parseFloat(getComputedStyle(layer).height)};
      flushSync(() => setGeometry(clipHighlightBox(scene, layer, box, siblings, frame)));
    };
    void measure().catch(cancelRender).finally(() => continueRender(handle));
    return () => {cancelled = true; continueRender(handle);};
  }, [e.highlightText, e.id, e.x, e.y, e.w, e.h, frame, siblings]);
  const color = colorToken(e.color) ?? P.primary;
  return <div ref={ref} data-highlight-text={e.highlightText} style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}><div data-text-highlight-box style={{display: geometry && (geometry.width <= 0 || geometry.height <= 0) ? 'none' : undefined, position: 'absolute', top: geometry?.top ?? 0, height: geometry?.height ?? '100%', left: geometry?.left ?? 0, width: geometry?.width ?? '100%', pointerEvents: 'none', boxSizing: 'border-box', border: `4px solid ${color}`, borderRadius: 10, background: `${color}18`}} /></div>;
};
