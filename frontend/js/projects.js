import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { PROJECTS } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const grid = document.getElementById('projectsGrid');
const search = document.getElementById('projectSearch');
const filters = {
  type: document.getElementById('projectType'),
  status: document.getElementById('projectStatus'),
  faculty: document.getElementById('projectFaculty'),
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[character]));
}

function fillFilter(select, values) {
  values.forEach((value) => select.insertAdjacentHTML('beforeend', `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`));
}

function projectCard(project) {
  return `<article class="research-card glass-card">
    <div class="research-card-top"><span class="project-icon material-symbols-outlined">folder_open</span><span class="status-pill status-${project.status.toLowerCase().replaceAll(' ', '-')}">${escapeHtml(project.status)}</span></div>
    <p class="eyebrow">${escapeHtml(project.type)}</p>
    <h3 class="title-lg">${escapeHtml(project.title)}</h3>
    <p class="body-md research-description">${escapeHtml(project.description)}</p>
    <div class="research-meta"><span class="material-symbols-outlined">account_tree</span>${escapeHtml(project.seedbed)}<span class="material-symbols-outlined">school</span>${escapeHtml(project.faculty)}</div>
    <div class="research-progress"><div class="progress-label"><span>Avance</span><strong>${project.progress}%</strong></div><div class="progress-mini"><span class="progress-fill fill-primary" style="width:${project.progress}%"></span></div></div>
    <div class="research-card-footer"><span class="body-md"><span class="material-symbols-outlined">person</span>${escapeHtml(project.leader)}</span><a class="btn btn-outline label-caps" href="/project-detail?id=${encodeURIComponent(project.id)}">Ver detalle</a></div>
  </article>`;
}

function render() {
  const query = search.value.trim().toLowerCase();
  const visible = PROJECTS.filter((project) => {
    const matchesQuery = !query || [project.title, project.description, project.leader, project.seedbed].some((value) => value.toLowerCase().includes(query));
    return matchesQuery && (!filters.type.value || project.type === filters.type.value) && (!filters.status.value || project.status === filters.status.value) && (!filters.faculty.value || project.faculty === filters.faculty.value);
  });
  document.getElementById('projectCount').textContent = `${visible.length} ${visible.length === 1 ? 'proyecto' : 'proyectos'}`;
  grid.innerHTML = visible.length ? visible.map(projectCard).join('') : '<div class="research-empty"><span class="material-symbols-outlined">search_off</span><strong>No encontramos proyectos</strong><span>Prueba con otros filtros o términos de búsqueda.</span></div>';
}

fillFilter(filters.type, [...new Set(PROJECTS.map((project) => project.type))]);
fillFilter(filters.status, [...new Set(PROJECTS.map((project) => project.status))]);
fillFilter(filters.faculty, [...new Set(PROJECTS.map((project) => project.faculty))]);
search.addEventListener('input', render);
Object.values(filters).forEach((select) => select.addEventListener('change', render));
render();