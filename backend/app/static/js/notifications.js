import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { NOTIFICATIONS } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const list = document.getElementById('notificationList');
const search = document.getElementById('notificationSearch');
let filter = 'all';
const localRead = new Set(NOTIFICATIONS.filter(({ read }) => read).map(({ id }) => id));

function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character])); }
function dateLabel(value) { return new Date(value).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' }); }
function isRead(notification) { return localRead.has(notification.id); }
function render() {
  const query = search.value.trim().toLowerCase();
  const visible = NOTIFICATIONS.filter((notification) => (filter === 'all' || !isRead(notification)) && (!query || `${notification.title} ${notification.text}`.toLowerCase().includes(query)));
  const unread = NOTIFICATIONS.filter((notification) => !isRead(notification)).length;
  document.getElementById('notificationCount').textContent = unread ? `${unread} no leídas` : 'Todo al día';
  list.innerHTML = visible.length ? visible.map((notification) => `<article class="notification-item${isRead(notification) ? '' : ' notification-unread'}" data-notification-id="${escapeHtml(notification.id)}"><span class="notification-icon material-symbols-outlined">${escapeHtml(notification.icon)}</span><div class="notification-content"><div class="notification-heading"><h2>${escapeHtml(notification.title)}</h2><time>${escapeHtml(dateLabel(notification.createdAt))}</time></div><p>${escapeHtml(notification.text)}</p><span class="notification-type">${escapeHtml(notification.type)}</span></div><div class="notification-actions">${notification.href ? `<a class="btn btn-outline label-caps" href="${escapeHtml(notification.href)}">Abrir</a>` : ''}${!isRead(notification) ? '<button class="icon-action" type="button" data-action="read" aria-label="Marcar como leída" title="Marcar como leída"><span class="material-symbols-outlined">done</span></button>' : ''}</div></article>`).join('') : '<div class="research-empty"><span class="material-symbols-outlined">notifications_off</span><strong>No hay notificaciones</strong><span>Cuando ocurra algo importante, aparecerá aquí.</span></div>';
}

document.querySelector('[role="tablist"]').addEventListener('click', (event) => { const tab = event.target.closest('[role="tab"]'); if (!tab) return; filter = tab.dataset.filter; document.querySelectorAll('[role="tab"]').forEach((item) => { const active = item === tab; item.classList.toggle('active', active); item.setAttribute('aria-selected', String(active)); }); render(); });
list.addEventListener('click', (event) => { const button = event.target.closest('[data-action="read"]'); if (!button) return; localRead.add(button.closest('[data-notification-id]').dataset.notificationId); render(); });
search.addEventListener('input', render);
render();