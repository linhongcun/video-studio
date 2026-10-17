import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {flushSync} from 'react-dom';
import {cancelRender, continueRender, delayRender} from 'remotion';
import {P} from '../theme';
import {colorToken, stateAt, UIProps} from './ui';

const useBrowserLayoutEffect = typeof document === 'undefined' ? useEffect : useLayoutEffect;

/** Measure the rendered Copy, including fitting, font fallback, borders and camera scale. */
export const TextHighlight: React.FC<UIProps> = ({e, frame, siblings = []}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [geometry, setGeometry] = useState<{left: number; width: number} | null>(null);
  useBrowserLayoutEffect(() => {
    const highlight = ref.current;
    const layer: HTMLElement | null = highlight?.parentElement ?? null;
    const scene = layer?.closest<HTMLElement>('[data-storyboard-scene]');
    if (!e.highlightText || !layer || !scene) {
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
      if (context && scale > 0) for (const original of siblings) {
        const sibling = stateAt(original, frame);
        if (frame < (sibling.appearFrame ?? 0) || frame >= (sibling.disappearFrame ?? Infinity) || sibling.state === 'hidden') continue;
        const source = Array.from(scene.children).find(child => child.getAttribute('data-element') === sibling.id) as HTMLElement | undefined;
        if (!source) continue;
        const texts = sibling.component === 'NotepadWindow'
          ? Array.from(source.querySelectorAll<HTMLElement>('[data-terminal-line]')).map(line => line.firstElementChild as HTMLElement)
          : sibling.component === 'BrowserChrome'
            ? Array.from(source.querySelectorAll<HTMLElement>('[data-address-box]')).map(address => address.lastElementChild as HTMLElement)
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
      // Put the four-pixel border outside the substring; retain the storyboard's vertical extent.
      flushSync(() => setGeometry(best ? {left: (best.left - authored.left) / scale - 4, width: best.width / scale + 8} : null));
    };
    void measure().catch(cancelRender).finally(() => continueRender(handle));
    return () => {cancelled = true; continueRender(handle);};
  }, [e, frame, siblings]);
  const color = colorToken(e.color) ?? P.primary;
  return <div ref={ref} data-highlight-text={e.highlightText} style={{position: 'absolute', top: 0, bottom: 0, left: geometry?.left ?? 0, width: geometry?.width ?? '100%', pointerEvents: 'none', boxSizing: 'border-box', border: `4px solid ${color}`, borderRadius: 10, background: `${color}18`}} />;
};
