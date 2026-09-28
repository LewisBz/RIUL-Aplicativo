import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { EVENTS } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const grid = document.getElementById('eventsGrid');
const search = document.getElementById('eventSearch');
const filters = { type: document.getElementById('eventType'), location: document.getElementById('eventLocation'), period: document.getElementById('eventPeriod') };
let activeKind = 'event';

function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character])); }
function dateLabel(value) { return new Date(value).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' }); }
function fillFilter(select, values) { values.forEach((value) => select.insertAdjacentHTML('beforeend', `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)); }

function eventCard(item) {
  const participation = item.participationStatus === 'registered' ? 'Inscrito' : item.status;
  const capacity = item.capacity ? `${item.registered} / ${item.capacity} cupos` : 'Postulación abierta';
  return `<article class="research-card glass-card event-card"><div class="event-date"><strong>${new Date(item.startDate).getDate()}</strong><span>${new Date(item.startDate).toLocaleDateString('es-CO', { month: 'short' })}</span></div><div class="research-card-top"><span class="eyebrow">${escapeHtml(item.type)}</span><span class="status-pill">${escapeHtml(participation)}</span></div><h3 class="title-lg">${escapeHtml(item.title)}</h3><p class="body-md research-description">${escapeHtml(item.description)}</p><div class="research-meta"><span class="material-symbols-outlined">location_on</span>${escapeHtml(item.location)}<span class="material-symbols-outlined">groups</span>${escapeHtml(capacity)}</div><div class="research-card-footer"><span class="body-md">${escapeHtml(dateLabel(item.startDate))}</span><a class="btn btn-outline label-caps" href="/event-detail?id=${encodeURIComponent(item.id)}">Ver detalle</a></div></article>`;
}

function render() {
  const query = search.value.trim().toLowerCase();
  const visible = EVENTS.filter((item) => item.kind === activeKind && (!query || [item.title, item.description, item.organizer, item.location].some((value) => value.toLowerCase().includes(query))) && (!filters.type.value || item.type === filters.type.value) && (!filters.location.value || item.location === filters.location.value) && (!filters.period.value || item.startDate.startsWith(filters.period.value)));
  document.getElementById('eventCount').textContent = `${visible.length} ${visible.length === 1 ? 'resultado' : 'resultados'}`;
  grid.innerHTML = visible.length ? visible.map(eventCard).join('') : '<div class="research-empty"><span class="material-symbols-outlined">event_busy</span><strong>No encontramos resultados</strong><span>Prueba con otros filtros o términos de búsqueda.</span></div>';
}

function renderMyEvents() { document.getElementById('myEventsTable').innerHTML = EVENTS.filter((item) => item.participationStatus !== 'available').map((item) => `<tr><td>${escapeHtml(item.title)}</td><td>${escapeHtml(item.kind === 'call' ? 'Convocatoria' : item.type)}</td><td><span class="status-pill">${escapeHtml(item.participationStatus === 'registered' ? 'Inscrito' : item.participationStatus === 'pending' ? 'Postulación pendiente' : 'Cerrado')}</span></td></tr>`).join(''); }
function setupFilters() { fillFilter(filters.type, [...new Set(EVENTS.map((item) => item.type))]); fillFilter(filters.location, [...new Set(EVENTS.map((item) => item.location))]); [...new Set(EVENTS.map((item) => item.startDate.slice(0, 7)))].forEach((value) => filters.period.insertAdjacentHTML('beforeend', `<option value="${value}">${dateLabel(`${value}-01`)}</option>`)); }

document.querySelector('[role="tablist"]').addEventListener('click', (event) => { const tab = event.target.closest('[role="tab"]'); if (!tab) return; activeKind = tab.dataset.kind; document.querySelectorAll('[role="tab"]').forEach((item) => { const active = item === tab; item.classList.toggle('active', active); item.setAttribute('aria-selected', String(active)); }); document.getElementById('eventsPanel').textContent = activeKind === 'event' ? 'Próximos eventos' : 'Convocatorias disponibles'; render(); });
search.addEventListener('input', render); Object.values(filters).forEach((select) => select.addEventListener('change', render)); setupFilters(); render(); renderMyEvents();