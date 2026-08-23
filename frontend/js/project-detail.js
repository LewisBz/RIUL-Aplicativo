import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { PROJECTS } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const root = document.getElementById('projectDetail');
const project = PROJECTS.find(({ id }) => id === new URLSearchParams(location.search).get('id'));

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
}

function initials(name) {
  return name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
}

if (!project) {
  root.innerHTML = '<div class="detail-empty"><span class="material-symbols-outlined">folder_off</span><strong>Proyecto no encontrado</strong><a href="/projects">Volver a proyectos</a></div>';
} else {
  root.innerHTML = `<div class="page-heading"><div><a class="body-md" href="/projects">← Volver a proyectos</a><p class="eyebrow" style="margin-top:var(--space-4);">${escapeHtml(project.type)}</p><h1 class="headline-lg">${escapeHtml(project.title)}</h1><p class="body-lg page-subtitle">${escapeHtml(project.description)}</p></div><span class="status-pill status-${project.status.toLowerCase().replaceAll(' ', '-')}">${escapeHtml(project.status)}</span></div>
    <div class="detail-layout"><div class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Información general</h2><dl class="detail-definition"><div><dt>Facultad</dt><dd>${escapeHtml(project.faculty)}</dd></div><div><dt>Línea de investigación</dt><dd>${escapeHtml(project.line)}</dd></div><div><dt>Fecha de inicio</dt><dd>${escapeHtml(project.startDate)}</dd></div><div><dt>Fecha de cierre</dt><dd>${escapeHtml(project.endDate)}</dd></div></dl><div class="research-progress" style="margin-top:var(--space-6);"><div class="progress-label"><span>Avance del proyecto</span><strong>${project.progress}%</strong></div><div class="progress-mini"><span class="progress-fill fill-primary" style="width:${project.progress}%"></span></div></div><div class="detail-actions"><button class="btn btn-primary label-caps" type="button" disabled><span class="material-symbols-outlined">edit</span>Editar proyecto</button><button class="btn btn-outline label-caps" type="button" disabled>Registrar avance</button></div></section><section class="glass-card detail-card"><h2 class="headline-md">Productos y evidencias</h2>${project.products.length ? `<div class="table-scroll"><table class="table-data"><thead><tr><th>Tipo</th><th>Nombre</th><th>Estado</th></tr></thead><tbody>${project.products.map((product) => `<tr><td>${escapeHtml(product.type)}</td><td>${escapeHtml(product.name)}</td><td>${escapeHtml(product.status)}</td></tr>`).join('')}</tbody></table></div>` : '<p class="body-md">Aún no hay productos registrados.</p>'}</section></div><aside class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Equipo de investigación</h2><p class="body-md"><strong>Líder</strong><br>${escapeHtml(project.leader)}</p><ul class="member-list">${project.members.map((member) => `<li><span class="member-dot">${initials(member)}</span><span>${escapeHtml(member)}</span></li>`).join('')}</ul></section><section class="glass-card detail-card"><h2 class="headline-md">Avances</h2><ul class="timeline">${project.milestones.map((milestone) => `<li class="${milestone.done ? 'done' : ''}"><strong>${escapeHtml(milestone.text)}</strong></li>`).join('')}</ul></section></aside></div>`;
}