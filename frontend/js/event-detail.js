import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { EVENTS } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const root = document.getElementById('eventDetail');
const item = EVENTS.find(({ id }) => id === new URLSearchParams(location.search).get('id'));

function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character])); }
function dateLabel(value) { return new Date(value).toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' }); }
function initials(name) { return name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase(); }

if (!item) {
  root.innerHTML = '<div class="detail-empty"><span class="material-symbols-outlined">event_busy</span><strong>Actividad no encontrada</strong><a href="/events">Volver a eventos</a></div>';
} else {
  const isCall = item.kind === 'call';
  const isRegistered = item.participationStatus === 'registered';
  const isClosed = item.status === 'Cerrado';
  const actionLabel = isRegistered ? 'Ya estás inscrito' : isClosed ? 'Actividad cerrada' : isCall ? 'Postularme' : 'Participar';
  const actionIcon = isRegistered ? 'check_circle' : isCall ? 'assignment' : 'event_available';
  const capacity = item.capacity ? `${item.registered} de ${item.capacity} cupos ocupados` : 'Recepción de propuestas abierta';
  root.innerHTML = `<div class="page-heading"><div><a class="body-md" href="/events">← Volver a eventos</a><p class="eyebrow" style="margin-top:var(--space-4);">${escapeHtml(isCall ? 'Convocatoria' : item.type)}</p><h1 class="headline-lg">${escapeHtml(item.title)}</h1><p class="body-lg page-subtitle">${escapeHtml(item.description)}</p></div><span class="status-pill">${escapeHtml(item.status)}</span></div><div class="detail-layout"><div class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Información</h2><dl class="detail-definition"><div><dt>Inicio</dt><dd>${escapeHtml(dateLabel(item.startDate))}</dd></div><div><dt>Cierre</dt><dd>${escapeHtml(dateLabel(item.endDate))}</dd></div><div><dt>Ubicación</dt><dd>${escapeHtml(item.location)}</dd></div><div><dt>Organiza</dt><dd>${escapeHtml(item.organizer)}</dd></div></dl><div class="event-capacity"><span class="material-symbols-outlined">groups</span><strong>${escapeHtml(capacity)}</strong></div><div class="detail-actions"><button class="btn btn-primary label-caps" type="button" ${isClosed || isRegistered ? 'disabled' : ''}><span class="material-symbols-outlined">${actionIcon}</span>${actionLabel}</button></div></section><section class="glass-card detail-card"><h2 class="headline-md">${isCall ? 'Requisitos de postulación' : 'Requisitos de participación'}</h2><ul class="member-list">${item.requirements.length ? item.requirements.map((requirement) => `<li><span class="material-symbols-outlined" style="color:var(--tertiary);">check_circle</span><span>${escapeHtml(requirement)}</span></li>`).join('') : '<li>No hay requisitos adicionales.</li>'}</ul></section></div><aside class="detail-stack"><section class="glass-card detail-card"><h2 class="headline-md">Organizadores</h2><p class="body-md"><strong>${escapeHtml(item.organizer)}</strong></p><ul class="member-list">${item.members.map((member) => `<li><span class="member-dot">${initials(member)}</span><span>${escapeHtml(member)}</span></li>`).join('')}</ul></section><section class="glass-card detail-card"><h2 class="headline-md">Seguimiento</h2><ul class="timeline">${item.timeline.map((milestone) => `<li class="${milestone.done ? 'done' : ''}"><strong>${escapeHtml(milestone.text)}</strong></li>`).join('')}</ul></section></aside></div>`;
}