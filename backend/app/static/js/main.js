import { initSessionUI } from './session.js';

const menuToggle = document.getElementById('menuToggle');
const menuPanel = document.getElementById('menuPanel');

menuToggle?.addEventListener('click', () => {
  if (menuPanel.hasAttribute('data-open')) {
    menuPanel.removeAttribute('data-open');
  } else {
    menuPanel.setAttribute('data-open', '');
  }
});

menuPanel?.addEventListener('click', (event) => {
  if (event.target.closest('a')) menuPanel.removeAttribute('data-open');
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') menuPanel?.removeAttribute('data-open');
});

const track = document.getElementById('eventsTrack');
const step = () => {
  const card = track?.querySelector('.carousel-card');
  return card ? card.getBoundingClientRect().width + 24 : 320;
};

document.getElementById('eventsPrev')?.addEventListener('click', () => {
  track?.scrollBy({ left: -step(), behavior: 'smooth' });
});

document.getElementById('eventsNext')?.addEventListener('click', () => {
  track?.scrollBy({ left: step(), behavior: 'smooth' });
});

await initSessionUI();

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[character]));
}

async function loadHighlights() {
  const semillerosRoot = document.getElementById('featuredSemilleros');
  const projectsRoot = document.getElementById('homeProjects');
  const eventsRoot = document.getElementById('eventsTrack');
  try {
    const [semilleros, projects, activities] = await Promise.all([
      fetch('/api/semilleros').then((response) => response.json()),
      fetch('/api/projects').then((response) => response.json()),
      fetch('/api/activities').then((response) => response.json()),
    ]);
    const groups = (semilleros.items || []).slice(0, 2);
    if (semillerosRoot && groups.length) {
      const explore = semillerosRoot.querySelector('.card-dashed');
      semillerosRoot.querySelectorAll('.card-research').forEach((node) => node.remove());
      groups.forEach((item) => {
        const card = document.createElement('a');
        card.className = 'card-research card-hover col-span-4';
        card.href = `/semilleros?id=${encodeURIComponent(item.slug || item.id)}`;
        card.style.cssText = 'padding:var(--space-4);text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:var(--space-3);';
        card.innerHTML = `<h3 class="title-lg" style="color:var(--primary);margin:0;">${escapeHtml(item.name)}</h3><p class="body-md line-clamp-3" style="color:var(--on-surface-variant);margin:0;">${escapeHtml(item.description || item.area || '')}</p><span class="label-caps" style="color:var(--secondary);">${escapeHtml(item.faculty || '')}</span>`;
        if (explore) semillerosRoot.insertBefore(card, explore);
        else semillerosRoot.appendChild(card);
      });
    }
    const projectItems = (projects.items || []).slice(0, 3);
    if (projectsRoot && projectItems.length) {
      projectsRoot.innerHTML = projectItems.map((item) => `<a class="list-row card-hover" href="/project-detail?id=${encodeURIComponent(item.id)}" style="text-decoration:none;color:inherit;"><div><h4 class="title-lg" style="line-height:1.25;margin:0;">${escapeHtml(item.title)}</h4><p class="label-caps" style="color:var(--secondary);margin:4px 0 0;">${escapeHtml(item.status)}</p></div><span class="material-symbols-outlined">arrow_forward_ios</span></a>`).join('');
    }
    const events = (activities.items || []).filter((item) => item.kind === 'event').slice(0, 3);
    if (eventsRoot && events.length) {
      eventsRoot.innerHTML = events.map((item) => `<a class="card-research carousel-card card-hover" href="/event-detail?id=${encodeURIComponent(item.id)}" style="display:flex;gap:var(--space-4);text-decoration:none;color:inherit;padding:var(--space-4);"><div style="display:flex;flex-direction:column;justify-content:center;gap:var(--space-2);"><h4 class="title-lg" style="color:var(--primary);line-height:1.25;margin:0;">${escapeHtml(item.title)}</h4><p class="body-md" style="color:var(--on-surface-variant);margin:0;">${escapeHtml(item.location)} · ${escapeHtml(item.status)}</p></div></a>`).join('');
    }
  } catch (error) {
    console.error('No se pudieron cargar los destacados.', error);
  }
}

loadHighlights();
