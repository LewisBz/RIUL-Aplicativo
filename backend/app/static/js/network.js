/* Red de nodos del hero: semilleros (nodos) conectados por proyectos (líneas).
   Canvas 2D puro. Se pausa fuera de pantalla y con la pestaña oculta; con
   prefers-reduced-motion dibuja un solo cuadro estático. */

const canvas = document.querySelector('.hero-network');

if (canvas) {
  const ctx = canvas.getContext('2d');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const css = getComputedStyle(document.documentElement);
  const INK = css.getPropertyValue('--primary').trim() || '#8c1230';
  const TEAL = css.getPropertyValue('--tertiary').trim() || '#0e5a52';

  let width = 0;
  let height = 0;
  let nodes = [];
  let raf = 0;
  let visible = true;
  const pointer = { x: -9999, y: -9999, active: false };

  function seed() {
    const wide = width > 820;
    const count = Math.round(Math.min(70, Math.max(22, (width * height) / 15000)));
    nodes = Array.from({ length: count }, (_, i) => {
      // En pantallas anchas la densidad se desplaza a la derecha: el texto vive a la izquierda.
      const bias = wide ? 1 - Math.pow(Math.random(), 1.7) * 0.92 : Math.random();
      return {
        x: bias * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.22,
        vy: (Math.random() - 0.5) * 0.22,
        r: i % 9 === 0 ? 3.2 : 1.8 + Math.random() * 0.9,
        hub: i % 9 === 0,
        teal: i % 13 === 0,
      };
    });
  }

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = rect.width;
    height = rect.height;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    seed();
    draw();
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    const link = Math.min(150, Math.max(96, width / 9));
    ctx.lineWidth = 1;

    for (let i = 0; i < nodes.length; i += 1) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j += 1) {
        const b = nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const d = Math.hypot(dx, dy);
        if (d < link) {
          ctx.strokeStyle = INK;
          ctx.globalAlpha = (1 - d / link) * 0.28;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
      if (pointer.active) {
        const d = Math.hypot(a.x - pointer.x, a.y - pointer.y);
        if (d < 170) {
          ctx.strokeStyle = TEAL;
          ctx.globalAlpha = (1 - d / 170) * 0.55;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(pointer.x, pointer.y);
          ctx.stroke();
        }
      }
    }

    ctx.globalAlpha = 1;
    for (const n of nodes) {
      ctx.fillStyle = n.teal ? TEAL : INK;
      ctx.globalAlpha = n.hub ? 0.9 : 0.55;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function step() {
    for (const n of nodes) {
      n.x += n.vx;
      n.y += n.vy;
      if (n.x < -10 || n.x > width + 10) n.vx *= -1;
      if (n.y < -10 || n.y > height + 10) n.vy *= -1;
      if (pointer.active) {
        const dx = n.x - pointer.x;
        const dy = n.y - pointer.y;
        const d = Math.hypot(dx, dy);
        if (d < 120 && d > 0.1) {
          n.x += (dx / d) * 0.35;
          n.y += (dy / d) * 0.35;
        }
      }
    }
    draw();
    raf = requestAnimationFrame(step);
  }

  function start() {
    if (reduce.matches || raf || !visible || document.hidden) return;
    raf = requestAnimationFrame(step);
  }

  function stop() {
    cancelAnimationFrame(raf);
    raf = 0;
  }

  new ResizeObserver(resize).observe(canvas);

  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible) start();
    else stop();
  }).observe(canvas);

  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
  reduce.addEventListener('change', () => (reduce.matches ? (stop(), draw()) : start()));

  // El canvas queda detrás del contenido, así que el puntero se lee en el hero.
  const hero = canvas.closest('.hero') ?? canvas;
  hero.addEventListener('pointermove', (event) => {
    if (event.pointerType === 'touch') return;
    const rect = canvas.getBoundingClientRect();
    pointer.x = event.clientX - rect.left;
    pointer.y = event.clientY - rect.top;
    pointer.active = true;
  });
  hero.addEventListener('pointerleave', () => {
    pointer.active = false;
  });

  resize();
  start();
}
