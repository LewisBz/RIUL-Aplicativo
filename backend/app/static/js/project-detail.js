import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api, escapeHtml } from './api.js';
import { toProject } from './adapters.js';
import { openFormDialog } from './forms.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const root = document.getElementById('projectDetail');
const slug = new URLSearchParams(location.search).get('id');

const STATUS_OPTIONS = [
  { value: 'planned', label: 'Planeado' },
  { value: 'in_progress', label: 'En curso' },
  { value: 'review', label: 'Revisión' },
  { value: 'completed', label: 'Completado' },
];

function initials(name) {
  return name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
}

function showNotFound(message) {
  root.innerHTML = `<div class="detail-empty"><span class="material-symbols-outlined">folder_off</span><strong>${escapeHtml(message)}</strong><a href="/projects">Volver a proyectos</a></div>`;
}

async function load() {
  if (!slug) return showNotFound('Proyecto no indicado');
  let project;
  try {
    project = toProject((await api(`/api/projects/${encodeURIComponent(slug)}`)).project);
  } catch (error) {
    return showNotFound(error.message);
  }
  const canEdit = project.myRole === 'leader' || user.role === 'administrator';
  const canContribute = Boolean(project.myRole) || user.role === 'administrator';
  const actions = [
    canEdit ? '<button class="btn btn-primary label-caps" type="button" id="editProject"><span class="material-symbols-outlined">edit</span>Actualizar estado y avance</button>' : '',
    canContribute ? '<button class="btn btn-outline label-caps" type="button" id="addProduct">Agregar producto</button>' : '',
  ].join('');

  root.innerHTML = `<div class="page-heading"><div><a class="body-md" href="/projects">← Volver a proyectos</a><p class="eyebrow" style="margin-top:var(--space-4);">${escapeHtml(project.type)}</p><h1 class="headline-lg">${escapeHtml(project.title)}</h1><p class="body-lg page-subtitle">${escapeHtml(project.description)}</p></div><span class="status-pill status-${escapeHtml(project.status.toLowerCase().replaceAll(' ', '-'))}">${escapeHtml(project.status)}</span></div>
    <div class="detail-layout"><div class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Información general</h2><dl class="detail-definition"><div><dt>Facultad</dt><dd>${escapeHtml(project.faculty)}</dd></div><div><dt>Línea de investigación</dt><dd>${escapeHtml(project.line)}</dd></div><div><dt>Fecha de inicio</dt><dd>${escapeHtml(project.startDate)}</dd></div><div><dt>Fecha de cierre</dt><dd>${escapeHtml(project.endDate)}</dd></div></dl><div class="research-progress" style="margin-top:var(--space-6);"><div class="progress-label"><span>Avance del proyecto</span><strong>${project.progress}%</strong></div><div class="progress-mini"><span class="progress-fill fill-primary" style="width:${project.progress}%"></span></div></div><div class="detail-actions">${actions}</div></section><section class="glass-card detail-card"><h2 class="headline-md">Productos y evidencias</h2>${project.products.length ? `<div class="table-scroll"><table class="table-data"><thead><tr><th>Tipo</th><th>Nombre</th><th>Estado</th></tr></thead><tbody>${project.products.map((product) => `<tr><td>${escapeHtml(product.type)}</td><td>${escapeHtml(product.name)}</td><td>${escapeHtml(product.status)}</td></tr>`).join('')}</tbody></table></div>` : '<p class="body-md">Aún no hay productos registrados.</p>'}</section></div><aside class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Equipo de investigación</h2><p class="body-md"><strong>Líder</strong><br>${escapeHtml(project.leader)}</p><ul class="member-list">${project.members.map((member) => `<li><span class="member-dot">${escapeHtml(initials(member))}</span><span>${escapeHtml(member)}</span></li>`).join('')}</ul></section><section class="glass-card detail-card"><h2 class="headline-md">Avances</h2><ul class="timeline">${project.milestones.map((milestone) => `<li class="${milestone.done ? 'done' : ''}"><strong>${escapeHtml(milestone.text)}</strong>${canContribute ? `<button class="btn btn-outline label-caps" type="button" data-milestone="${milestone.id}" data-done="${!milestone.done}" style="margin-left:var(--space-3);">${milestone.done ? 'Reabrir' : 'Completar'}</button>` : ''}</li>`).join('')}</ul></section></aside></div>`;

  document.getElementById('editProject')?.addEventListener('click', async () => {
    const updated = await openFormDialog({
      title: 'Actualizar proyecto',
      fields: [
        { name: 'status', label: 'Estado', type: 'select', options: STATUS_OPTIONS, value: project.statusCode },
        { name: 'progress', label: 'Avance (%)', type: 'number', min: 0, value: project.progress },
        { name: 'description', label: 'Descripción', type: 'textarea', value: project.description },
      ],
      onSubmit: (values) => api(`/api/projects/${encodeURIComponent(slug)}`, {
        method: 'PATCH',
        body: { ...values, progress: Number(values.progress) },
      }),
    });
    if (updated) load();
  });

  document.getElementById('addProduct')?.addEventListener('click', async () => {
    const added = await openFormDialog({
      title: 'Agregar producto',
      fields: [
        { name: 'type', label: 'Tipo (Artículo, Informe, Patente…)', required: true },
        { name: 'name', label: 'Nombre', required: true },
      ],
      onSubmit: (values) => api(`/api/projects/${encodeURIComponent(slug)}/products`, { method: 'POST', body: values }),
    });
    if (added) load();
  });

  root.querySelectorAll('[data-milestone]').forEach((button) => {
    button.addEventListener('click', async () => {
      button.disabled = true;
      try {
        await api(`/api/projects/${encodeURIComponent(slug)}/milestones/${button.dataset.milestone}`, {
          method: 'PATCH',
          body: { done: button.dataset.done === 'true' },
        });
        load();
      } catch (error) {
        button.disabled = false;
        alert(error.message);
      }
    });
  });
}

await load();
