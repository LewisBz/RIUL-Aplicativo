import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api, escapeHtml } from './api.js';
import { toEvent } from './adapters.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const root = document.getElementById('eventDetail');
const slug = new URLSearchParams(location.search).get('id');

function dateLabel(value) {
  return new Date(value).toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function initials(name) {
  return name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
}

function showNotFound(message) {
  root.innerHTML = `<div class="detail-empty"><span class="material-symbols-outlined">event_busy</span><strong>${escapeHtml(message)}</strong><a href="/events">Volver a eventos</a></div>`;
}

function actionState(item) {
  const isCall = item.kind === 'call';
  if (item.participation === 'registered') {
    return { label: isCall ? 'Cancelar postulación' : 'Cancelar inscripción', icon: 'event_busy', disabled: item.status === 'Cerrado', method: 'DELETE', path: '/registrations/me' };
  }
  if (item.participation === 'closed') return { label: 'Actividad cerrada', icon: 'lock', disabled: true };
  if (item.participation === 'full') return { label: 'Sin cupos disponibles', icon: 'block', disabled: true };
  return { label: isCall ? 'Postularme' : 'Participar', icon: isCall ? 'assignment' : 'event_available', disabled: false, method: 'POST', path: '/registrations' };
}

async function load() {
  if (!slug) return showNotFound('Actividad no indicada');
  let item;
  try {
    item = toEvent((await api(`/api/events/${encodeURIComponent(slug)}`)).event);
  } catch (error) {
    return showNotFound(error.message);
  }
  const isCall = item.kind === 'call';
  const action = actionState(item);
  const capacity = item.capacity ? `${item.registered} de ${item.capacity} cupos ocupados` : isCall ? 'Recepción de propuestas abierta' : `${item.registered} inscritos`;

  root.innerHTML = `<div class="page-heading"><div><a class="body-md" href="/events">← Volver a eventos</a><p class="eyebrow" style="margin-top:var(--space-4);">${escapeHtml(isCall ? 'Convocatoria' : item.type)}</p><h1 class="headline-lg">${escapeHtml(item.title)}</h1><p class="body-lg page-subtitle">${escapeHtml(item.description)}</p></div><span class="status-pill">${escapeHtml(item.status)}</span></div><div class="detail-layout"><div class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Información</h2><dl class="detail-definition"><div><dt>Inicio</dt><dd>${escapeHtml(dateLabel(item.startDate))}</dd></div><div><dt>Cierre</dt><dd>${escapeHtml(dateLabel(item.endDate))}</dd></div><div><dt>Ubicación</dt><dd>${escapeHtml(item.location)}</dd></div><div><dt>Organiza</dt><dd>${escapeHtml(item.organizer)}</dd></div></dl><div class="event-capacity"><span class="material-symbols-outlined">groups</span><strong>${escapeHtml(capacity)}</strong></div><div class="detail-actions"><button class="btn btn-primary label-caps" type="button" id="eventAction" ${action.disabled ? 'disabled' : ''}><span class="material-symbols-outlined">${action.icon}</span>${escapeHtml(action.label)}</button></div><p class="body-md" id="eventMessage" role="alert" style="color:var(--error);"></p></section><section class="glass-card detail-card"><h2 class="headline-md">${isCall ? 'Requisitos de postulación' : 'Requisitos de participación'}</h2><ul class="member-list">${item.requirements.length ? item.requirements.map((requirement) => `<li><span class="member-dot material-symbols-outlined">check</span><span>${escapeHtml(requirement)}</span></li>`).join('') : '<li><span>Sin requisitos adicionales.</span></li>'}</ul></section></div><aside class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Organizadores</h2><ul class="member-list">${item.members.map((member) => `<li><span class="member-dot">${escapeHtml(initials(member))}</span><span>${escapeHtml(member)}</span></li>`).join('')}</ul></section><section class="glass-card detail-card"><h2 class="headline-md">Seguimiento</h2><ul class="timeline">${item.timeline.map((milestone) => `<li class="${milestone.done ? 'done' : ''}"><strong>${escapeHtml(milestone.text)}</strong></li>`).join('')}</ul></section></aside></div>`;

  const button = document.getElementById('eventAction');
  if (action.method) {
    button.addEventListener('click', async () => {
      button.disabled = true;
      try {
        await api(`/api/events/${encodeURIComponent(slug)}${action.path}`, { method: action.method });
        await load();
      } catch (error) {
        document.getElementById('eventMessage').textContent = error.message;
        button.disabled = false;
      }
    });
  }
}

await load();

const APPLICATION_LABELS = { pending: 'Pendiente', accepted: 'Aceptada', rejected: 'Rechazada' };

async function renderApplications(item) {
  const stack = root.querySelector('.detail-stack');
  const card = document.createElement('section');
  card.className = 'glass-card detail-card';
  card.innerHTML = '<h2 class="headline-md">Postulaciones</h2><div data-applications></div><p class="body-md" data-application-message role="status"></p>';
  stack.appendChild(card);
  const list = card.querySelector('[data-applications]');
  const message = card.querySelector('[data-application-message]');

  async function refresh() {
    const { items } = await api(`/api/events/${encodeURIComponent(slug)}/applications`);
    list.innerHTML = items.length
      ? `<div class="table-scroll"><table class="table-data"><thead><tr><th>Postulante</th><th>Tipo</th><th>Estado</th><th></th></tr></thead><tbody>${items.map((app) => `<tr><td>${escapeHtml(app.applicant.name || '—')}</td><td>${app.applicant.kind === 'semillero' ? 'Semillero' : 'Persona'}</td><td>${escapeHtml(APPLICATION_LABELS[app.status] ?? app.status)}</td><td>${app.status === 'pending' ? `<button class="btn btn-primary label-caps" type="button" data-review="accepted" data-id="${app.id}">Aceptar</button> <button class="btn btn-outline label-caps" type="button" data-review="rejected" data-id="${app.id}">Rechazar</button>` : ''}</td></tr>`).join('')}</tbody></table></div>`
      : '<p class="body-md">Aún no hay postulaciones.</p>';
  }

  list.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-review]');
    if (!button) return;
    button.disabled = true;
    try {
      await api(`/api/events/${encodeURIComponent(slug)}/applications/${button.dataset.id}`, {
        method: 'PATCH',
        body: { status: button.dataset.review },
      });
      message.textContent = 'Postulación actualizada.';
      await refresh();
    } catch (error) {
      message.textContent = error.message;
      button.disabled = false;
    }
  });
  await refresh();
}

if (user.role === 'administrator' && slug) {
  const current = toEvent((await api(`/api/events/${encodeURIComponent(slug)}`)).event);
  if (current.kind === 'call') await renderApplications(current);
}