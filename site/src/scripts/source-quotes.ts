type SourceControl = {
  root: HTMLElement;
  anchor: HTMLElement;
  trigger: HTMLButtonElement;
  panel: HTMLElement;
  mode: 'preview' | 'pinned';
  restoreFocus: boolean;
};

// The native buttons and popover work without this enhancement. Browsers
// without Popover support keep the complete source in normal reading flow.
function initializeSources() {
  if (!('showPopover' in HTMLElement.prototype)) return;
  const controls: SourceControl[] = [];
  const hover = matchMedia('(hover: hover) and (pointer: fine)');
  let active: SourceControl | undefined;
  let previewTimer: ReturnType<typeof setTimeout> | undefined;
  let closeTimer: ReturnType<typeof setTimeout> | undefined;
  let positionFrame = 0;

  const isOpen = (control: SourceControl) => control.panel.matches(':popover-open');
  const cancelPreview = () => { clearTimeout(previewTimer); previewTimer = undefined; };
  const cancelClose = () => { clearTimeout(closeTimer); closeTimer = undefined; };
  const pin = (control: SourceControl) => {
    cancelPreview();
    cancelClose();
    control.mode = 'pinned';
    control.panel.dataset.sourceState = 'pinned';
  };
  const close = (control: SourceControl, restoreFocus = false) => {
    cancelClose();
    control.restoreFocus ||= restoreFocus;
    if (isOpen(control)) control.panel.hidePopover();
    control.trigger.setAttribute('aria-expanded', 'false');
    if (active === control) active = undefined;
  };

  const position = (control: SourceControl) => {
    if (!isOpen(control)) return;
    const viewport = window.visualViewport;
    const edge = 12;
    const minX = (viewport?.offsetLeft ?? 0) + edge;
    const minY = (viewport?.offsetTop ?? 0) + edge;
    const viewportWidth = viewport?.width ?? innerWidth;
    const viewportHeight = viewport?.height ?? innerHeight;
    const maxX = minX + viewportWidth - edge * 2;
    const maxY = minY + viewportHeight - edge * 2;
    const rect = control.trigger.getBoundingClientRect();
    // Do not leave a detached panel behind after its paragraph scrolls away.
    if (rect.bottom < minY || rect.top > maxY || rect.right < minX || rect.left > maxX) {
      close(control);
      return;
    }
    const width = Math.max(0, Math.min(540, viewportWidth - edge * 2));
    control.panel.style.width = `${width}px`;
    const heightCap = matchMedia('(max-width: 767px)').matches ? Math.min(520, viewportHeight * .7) : 480;
    control.panel.style.maxHeight = `${Math.max(0, Math.min(heightCap, viewportHeight - edge * 2))}px`;
    control.panel.style.margin = '0';
    control.panel.style.right = 'auto';
    control.panel.style.bottom = 'auto';
    const height = control.panel.getBoundingClientRect().height;
    const gap = 10;
    let top = rect.bottom + gap;
    if (top + height > maxY && rect.top - height - gap >= minY) top = rect.top - height - gap;
    top = Math.max(minY, Math.min(top, maxY - height));
    const left = Math.max(minX, Math.min(rect.left, maxX - width));
    control.panel.style.top = `${top}px`;
    control.panel.style.left = `${left}px`;
  };
  const queuePosition = () => {
    if (!active || positionFrame) return;
    positionFrame = requestAnimationFrame(() => {
      positionFrame = 0;
      if (active) position(active);
    });
  };
  const open = (control: SourceControl, mode: 'preview' | 'pinned') => {
    cancelPreview();
    cancelClose();
    if (mode === 'preview' && active?.mode === 'pinned' && active !== control) return;
    if (active && active !== control) close(active);
    active = control;
    control.mode = mode;
    control.restoreFocus = false;
    control.panel.dataset.sourceState = mode;
    if (!isOpen(control)) control.panel.showPopover();
    control.trigger.setAttribute('aria-expanded', 'true');
    position(control);
  };
  const scheduleClose = (control: SourceControl) => {
    cancelClose();
    if (active !== control || control.mode === 'pinned') return;
    closeTimer = setTimeout(() => {
      closeTimer = undefined;
      if (active === control && control.mode === 'preview'
        && !control.panel.contains(document.activeElement)
        && !control.panel.matches(':hover') && !control.trigger.matches(':hover')) close(control);
    }, 240);
  };

  for (const root of document.querySelectorAll<HTMLElement>('[data-source-quote]')) {
    if (root.dataset.sourceReady) continue;
    const anchor = root.querySelector<HTMLElement>('.source-anchor');
    const trigger = root.querySelector<HTMLButtonElement>('[data-source-trigger]');
    const panel = root.querySelector<HTMLElement>('[data-source-panel]');
    if (!anchor || !trigger || !panel) continue;
    root.dataset.sourceReady = 'true';
    trigger.setAttribute('aria-expanded', String(panel.matches(':popover-open')));
    const control: SourceControl = {root, anchor, trigger, panel, mode: 'pinned', restoreFocus: false};
    controls.push(control);
    // Only move the small inline entry. A popover/aside never becomes a child
    // of a paragraph, and we do not mark a whole sentence as a verified claim.
    if (root.previousElementSibling?.tagName === 'P') root.previousElementSibling.append(anchor);

    trigger.addEventListener('click', (event) => {
      event.preventDefault();
      cancelPreview();
      if (isOpen(control)) {
        if (control.mode === 'preview') pin(control);
        else close(control);
      } else open(control, 'pinned');
    });
    trigger.addEventListener('pointerenter', (event) => {
      cancelClose();
      cancelPreview();
      if (!hover.matches || event.pointerType === 'touch' || isOpen(control)
        || (active?.mode === 'pinned' && active !== control)) return;
      previewTimer = setTimeout(() => open(control, 'preview'), 180);
    });
    trigger.addEventListener('pointerleave', (event) => {
      cancelPreview();
      if (!(event.relatedTarget instanceof Node && panel.contains(event.relatedTarget))) scheduleClose(control);
    });
    panel.addEventListener('pointerenter', cancelClose);
    panel.addEventListener('pointerleave', (event) => {
      if (!(event.relatedTarget instanceof Node && trigger.contains(event.relatedTarget))) scheduleClose(control);
    });
    panel.addEventListener('pointerdown', (event) => {
      if (!(event.target instanceof Element && event.target.closest('.source-close'))) pin(control);
    });
    panel.addEventListener('focusin', () => pin(control));
    panel.querySelector('.source-close')?.addEventListener('click', (event) => {
      event.preventDefault();
      close(control, true);
    });
    panel.addEventListener('toggle', () => {
      const opened = isOpen(control);
      trigger.setAttribute('aria-expanded', String(opened));
      if (opened) {
        if (active !== control) {
          active = control;
          pin(control);
        }
        position(control);
      } else {
        if (active === control) active = undefined;
        delete panel.dataset.sourceState;
        if (control.restoreFocus) {
          control.restoreFocus = false;
          trigger.focus({preventScroll: true});
        }
      }
    });
  }

  if (!controls.length) return;
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    cancelPreview();
    if (active && isOpen(active)) active.restoreFocus = true;
    // Native auto popovers handle Escape and outside clicks. The toggle event
    // synchronizes the entry and restores keyboard focus after Escape.
  }, true);
  document.addEventListener('scroll', (event) => {
    if (active && event.target instanceof Node && active.panel.contains(event.target)) return;
    queuePosition();
  }, true);
  window.addEventListener('resize', queuePosition);
  window.visualViewport?.addEventListener('resize', queuePosition);
  window.visualViewport?.addEventListener('scroll', queuePosition);
}

initializeSources();
document.addEventListener('astro:page-load', initializeSources);
