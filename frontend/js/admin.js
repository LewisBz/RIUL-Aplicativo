import { API_BASE, getToken, logout } from './session.js';

const content = document.getElementById('adminContent');
document.getElementById('adminLogout').addEventListener('click', logout);

function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character])); }
function showMessage(title, message, action = '') { content.innerHTML = `<section class="admin-state"><span class="material-symbols-outlined">${action ? 'lock' : 'error'}</span><h1 class="headline-md">${escapeHtml(title)}</h1><p>${escapeHtml(message)}</p>${action ? `<a class="btn btn-primary label-caps" href="${action}">Continuar</a>` : ''}</section>`; }

async function request(path) {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, { headers: { Authorization: `Bearer ${token}` } });
  if (response.status === 401) { logout(); throw new Error('Sesión no válida.'); }
  if (response.status === 403) throw new Error('No tienes permisos de administrador.');
  if (!response.ok) throw new Error('No fue posible cargar el panel.');
  return response.json();
}

function metric(label, value, icon, tone = '') { return `<article class="admin-metric ${tone}"><span class="admin-metric-icon material-symbols-outlined">${icon}</span><div><strong>${value}</strong><span>${label}</span></div></article>`; }
function unavailable(label, icon) { return `<article class="admin-unavailable"><span class="material-symbols-outlined">${icon}</span><div><strong>${label}</strong><span>Disponible cuando exista su módulo de datos.</span></div></article>`; }

async function init() {
  const token = getToken();
  if (!token) { showMessage('Sesión requerida', 'Inicia sesión para acceder al panel administrativo.', '/login'); return; }
  try {
    const identity = await request('/api/auth/me');
    if (identity.user?.role !== 'administrator') { showMessage('Acceso restringido', 'Esta ruta está reservada para administradores activos.', '/dashboard'); return; }
    const overview = await request('/api/admin/overview');
    const pending = overview.users.pending;
    content.innerHTML = `<div class="admin-heading"><div><p class="eyebrow">Control institucional</p><h1 class="headline-lg">Dashboard administrativo</h1><p class="body-lg page-subtitle">Supervisa la actividad de RIUL desde un solo lugar.</p></div><span class="admin-role"><span class="material-symbols-outlined">verified_user</span>Administrador</span></div><section class="admin-metrics">${metric('Usuarios totales', overview.users.total, 'group')}${metric('Usuarios activos', overview.users.active, 'check_circle', 'teal')}${metric('Pendientes de revisión', pending, 'pending_actions', pending ? 'warning' : '')}${metric('Publicaciones', overview.posts, 'forum')}</section><div class="admin-columns"><section class="glass-card admin-panel" id="users"><div class="section-heading"><h2 class="headline-md">Usuarios pendientes</h2><span class="status-pill">${pending} pendientes</span></div>${pending ? '<p class="body-md">Hay solicitudes que requieren revisión administrativa.</p><button class="btn btn-primary label-caps" type="button" disabled>Gestionar usuarios</button>' : '<div class="admin-empty"><span class="material-symbols-outlined">check_circle</span><span>No hay solicitudes pendientes.</span></div>'}</section><section class="glass-card admin-panel"><div class="section-heading"><h2 class="headline-md">Actividad disponible</h2><span class="body-md">Fuentes reales</span></div><div class="admin-unavailable-list">${unavailable('Facultades', 'account_balance')}${unavailable('Programas', 'school')}${unavailable('Semilleros', 'psychology')}</div></section></div><section class="admin-section" id="overview"><div class="section-heading"><h2 class="headline-md">Catálogos institucionales</h2><span class="body-md">Resumen actual</span></div><div class="admin-metrics admin-metrics-small">${metric('Facultades', overview.faculties, 'account_balance')}${metric('Programas', overview.programs, 'school')}</div></section>`;
  } catch (error) { showMessage('No se pudo cargar el panel', error.message); }
}

init();