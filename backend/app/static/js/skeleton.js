/* Skeleton loaders: placeholders mientras llegan los datos de la API. */

const VARIANTS = {
  card: () => `
    <article class="skeleton-card" aria-hidden="true">
      <div class="skeleton skeleton-line w-40"></div>
      <div class="skeleton skeleton-line skeleton-title w-80"></div>
      <div class="skeleton skeleton-line w-100"></div>
      <div class="skeleton skeleton-line w-90"></div>
      <div class="skeleton skeleton-line w-60"></div>
      <div class="skeleton-row">
        <div class="skeleton skeleton-btn"></div>
        <div class="skeleton skeleton-btn"></div>
      </div>
    </article>`,
  row: () => `
    <div class="skeleton-item" aria-hidden="true">
      <div class="skeleton skeleton-circle"></div>
      <div class="skeleton-stack">
        <div class="skeleton skeleton-line w-70"></div>
        <div class="skeleton skeleton-line w-40"></div>
      </div>
    </div>`,
  tile: () => `
    <div class="skeleton-tile" aria-hidden="true">
      <div class="skeleton skeleton-circle skeleton-circle-lg"></div>
      <div class="skeleton skeleton-line w-60"></div>
    </div>`,
  post: () => `
    <article class="skeleton-card" aria-hidden="true">
      <div class="skeleton-item">
        <div class="skeleton skeleton-circle"></div>
        <div class="skeleton-stack">
          <div class="skeleton skeleton-line w-50"></div>
          <div class="skeleton skeleton-line w-30"></div>
        </div>
      </div>
      <div class="skeleton skeleton-media"></div>
      <div class="skeleton skeleton-line w-90"></div>
      <div class="skeleton skeleton-line w-70"></div>
    </article>`,
};

export function skeletonHtml(variant = 'card', count = 6) {
  const build = VARIANTS[variant] ?? VARIANTS.card;
  return Array.from({ length: count }, build).join('');
}

/** Pinta skeletons dentro de `container`. El render real los reemplaza con innerHTML/replaceChildren. */
export function showSkeleton(container, variant = 'card', count = 6) {
  if (!container) return;
  container.innerHTML = skeletonHtml(variant, count);
}

/** Skeleton para varios contenedores; devuelve `done()` que los vacía y quita aria-busy. */
export function skeletonFor(targets) {
  const items = targets
    .map(({ id, variant, count }) => ({ el: document.getElementById(id), variant, count }))
    .filter(({ el }) => el);
  items.forEach(({ el, variant, count }) => showSkeleton(el, variant, count ?? 3));
  return () => items.forEach(({ el }) => el.replaceChildren());
}
