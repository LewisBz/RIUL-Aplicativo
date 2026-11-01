/* Capa de movimiento de RIUL. JavaScript puro, sin dependencias.
   Cada efecto responde a algo concreto:
   - revelado escalonado: ordena la lectura de bloques que entran en pantalla
   - conteo de métricas: confirma que el número viene de datos
   - foco de luz en tarjetas: indica cuál tarjeta es interactiva
   - titular por palabras: única secuencia de entrada de la landing
   - sombra del topnav y barra de progreso: orientación al desplazarse
   Todo se desactiva con prefers-reduced-motion. */

const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

const REVEAL = [
  '[data-reveal]',
  '.page-heading',
  '.research-card',
  '.card-research',
  '.post-card',
  '.create-post-box',
  '.notification-item',
  '.dash-card',
  '.admin-metric',
  '.list-row',
  '.detail-card',
  '.insignia',
  '.ranking-row',
  '.achievement-item',
  '.profile-banner',
  '.gamification-summary',
].join(',');

const SPOTLIGHT = '.card-research, .research-card, .post-card, .dash-card, .detail-card, .admin-metric, .list-row';

/* ---------- Revelado escalonado ---------- */
function finishReveal(el) {
  el.classList.remove('will-reveal', 'is-visible');
  el.style.removeProperty('--reveal-delay');
}

let revealIO = null;
if (!reduce && 'IntersectionObserver' in window) {
  revealIO = new IntersectionObserver((entries) => {
    const batch = entries.filter((entry) => entry.isIntersecting);
    batch.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top
      || a.boundingClientRect.left - b.boundingClientRect.left);
    batch.forEach((entry, index) => {
      const el = entry.target;
      revealIO.unobserve(el);
      el.style.setProperty('--reveal-delay', `${Math.min(index, 7) * 55}ms`);
      requestAnimationFrame(() => el.classList.add('is-visible'));
      el.addEventListener('transitionend', (event) => {
        if (event.target === el && event.propertyName === 'opacity') finishReveal(el);
      }, { once: true });
      countUp(el);
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });
}

function armReveal(root) {
  if (!revealIO || root.nodeType !== 1) return;
  const targets = [];
  if (root.matches?.(REVEAL)) targets.push(root);
  root.querySelectorAll?.(REVEAL).forEach((el) => targets.push(el));
  for (const el of targets) {
    if (el.dataset.motion || el.closest('.hero')) continue;
    // Una sección revelada ya anima a su contenido: no se anidan.
    if (el.parentElement?.closest('[data-reveal]')) continue;
    el.dataset.motion = 'armed';
    el.classList.add('will-reveal');
    revealIO.observe(el);
  }
}

/* ---------- Conteo de métricas ---------- */
const COUNTERS = '.admin-metric strong, .gamification-stats strong, [data-count]';

function countUp(scope) {
  if (reduce) return;
  const nodes = scope.matches?.(COUNTERS) ? [scope] : [];
  scope.querySelectorAll?.(COUNTERS).forEach((el) => nodes.push(el));
  for (const el of nodes) {
    if (el.dataset.counted) continue;
    const text = el.textContent.trim();
    if (!/^\d{1,7}$/.test(text)) continue;
    el.dataset.counted = '1';
    const target = Number(text);
    if (target < 2) continue;
    const start = performance.now();
    const duration = 900;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = String(Math.round(target * eased));
      if (t < 1) requestAnimationFrame(tick);
    };
    el.textContent = '0';
    requestAnimationFrame(tick);
  }
}

/* ---------- Titular por palabras ---------- */
function splitHeadline(el) {
  const text = el.textContent.trim().replace(/\s+/g, ' ');
  el.setAttribute('aria-label', text);
  el.textContent = '';
  text.split(' ').forEach((word, index, all) => {
    const mask = document.createElement('span');
    mask.className = 'word-mask';
    mask.setAttribute('aria-hidden', 'true');
    const inner = document.createElement('span');
    inner.className = 'word';
    inner.style.setProperty('--w', String(index));
    inner.textContent = word;
    mask.append(inner);
    el.append(mask);
    if (index < all.length - 1) el.append(' ');
  });
  el.classList.add('is-split');
}

/* ---------- Foco de luz en tarjetas ---------- */
function wireSpotlight() {
  if (!fine || reduce) return;
  let frame = 0;
  let last = null;
  document.addEventListener('pointermove', (event) => {
    last = event;
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      const card = last.target.closest?.(SPOTLIGHT);
      if (!card) return;
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--mx', `${last.clientX - rect.left}px`);
      card.style.setProperty('--my', `${last.clientY - rect.top}px`);
    });
  }, { passive: true });
}

/* ---------- Topnav y progreso de lectura ---------- */
function wireChrome() {
  const sentinel = document.createElement('div');
  sentinel.className = 'scroll-sentinel';
  sentinel.setAttribute('aria-hidden', 'true');
  document.body.prepend(sentinel);
  new IntersectionObserver(([entry]) => {
    document.querySelectorAll('.topnav').forEach((nav) => {
      if (entry.isIntersecting) nav.removeAttribute('data-stuck');
      else nav.setAttribute('data-stuck', '');
    });
  }).observe(sentinel);

  if (!reduce && CSS.supports?.('animation-timeline: scroll()')) {
    const bar = document.createElement('div');
    bar.className = 'scroll-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.append(bar);
  }
}

/* ---------- Arranque ---------- */
function init() {
  document.documentElement.classList.add('js-motion');
  wireChrome();
  wireSpotlight();

  const headline = document.querySelector('[data-split]');
  if (headline && !reduce) splitHeadline(headline);

  armReveal(document.body);
  new MutationObserver((records) => {
    for (const record of records) record.addedNodes.forEach((node) => armReveal(node));
  }).observe(document.body, { childList: true, subtree: true });
}

if (document.body) init();
else document.addEventListener('DOMContentLoaded', init, { once: true });
