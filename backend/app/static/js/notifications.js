import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api, escapeHtml } from './api.js';
import { toNotification } from './adapters.js';
import { showSkeleton } from './skeleton.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const list = document.getElementById('notificationList');
const search = document.getElementById('notificationSearch');
let filter = 'all';
let notifications = [];

function dateLabel(value) {
  return new Date(value).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' });
}

async function load() {
  showSkeleton(list, 'row', 5);
  try {
    notifications = (await api('/api/notifications')).items.map(toNotification);
  } catch (error) {
    list.innerHTML = `<div class="research-empty"><strong>${escapeHtml(error.message)}</strong></div>`;
    return;
  }
  render();
}

function render() {
  const query = search.value.trim().toLowerCase();
  const visible = notifications.filter((notification) => (filter === 'all' || !notification.read) && (!query || `${notification.title} ${notification.text}`.toLowerCase().includes(query)));
  const unread = notifications.filter((notification) => !notification.read).length;
  document.getElementById('notificationCount').textContent = unread ? `${unread} no leídas` : 'Todo al día';
  list.innerHTML = visible.length ? visible.map((notification) => `<article class="notification-item${notification.read ? '' : ' notification-unread'}" data-notification-id="${notification.id}"><span class="notification-icon material-symbols-outlined">${escapeHtml(notification.icon)}</span><div class="notification-content"><div class="notification-heading"><h2>${escapeHtml(notification.title)}</h2><time>${escapeHtml(dateLabel(notification.createdAt))}</time></div><p>${escapeHtml(notification.text)}</p><span class="notification-type">${escapeHtml(notification.type)}</span></div><div class="notification-actions">${notification.href ? `<a class="btn btn-outline label-caps" href="${escapeHtml(notification.href)}">Abrir</a>` : ''}${!notification.read ? '<button class="icon-action" type="button" data-action="read" aria-label="Marcar como leída" title="Marcar como leída"><span class="material-symbols-outlined">done</span></button>' : ''}</div></article>`).join('') : '<div class="research-empty"><span class="material-symbols-outlined">notifications_off</span><strong>No hay notificaciones</strong><span>Cuando ocurra algo importante, aparecerá aquí.</span></div>';
}

document.querySelector('[role="tablist"]').addEventListener('click', (event) => {
  const tab = event.target.closest('[role="tab"]');
  if (!tab) return;
  filter = tab.dataset.filter;
  document.querySelectorAll('[role="tab"]').forEach((item) => {
    const active = item === tab;
    item.classList.toggle('active', active);
    item.setAttribute('aria-selected', String(active));
  });
  render();
});

list.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-action="read"]');
  if (!button) return;
  const id = Number(button.closest('[data-notification-id]').dataset.notificationId);
  button.disabled = true;
  try {
    await api(`/api/notifications/${id}`, { method: 'PATCH', body: { read: true } });
    notifications = notifications.map((item) => (item.id === id ? { ...item, read: true } : item));
    render();
  } catch (error) {
    button.disabled = false;
  }
});

const markAll = document.createElement('button');
markAll.type = 'button';
markAll.className = 'btn btn-outline label-caps';
markAll.textContent = 'Marcar todas como leídas';
document.querySelector('.notification-toolbar').appendChild(markAll);
markAll.addEventListener('click', async () => {
  await api('/api/notifications/read-all', { method: 'POST' });
  notifications = notifications.map((item) => ({ ...item, read: true }));
  render();
});

search.addEventListener('input', render);
await load();
