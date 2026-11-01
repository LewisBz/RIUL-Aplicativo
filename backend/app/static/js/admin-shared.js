import { API_BASE, getToken, logout } from './session.js';

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[ch]));
}

const NAV = [
  { id: 'overview', label: 'Resumen', icon: 'dashboard', href: '/admin' },
  { id: 'users', label: 'Usuarios', icon: 'person', href: '/admin#users' },
  { id: 'achievements', label: 'Logros', icon: 'military_tech', href: '/admin#achievements' },
  { id: 'analytics', label: 'Reportes', icon: 'assessment', href: '/admin-analytics' },
  { id: 'support', label: 'Soporte', icon: 'support_agent', href: '/support' },
];

export function renderAdminNav(activeId) {
  const nav = document.getElementById('adminNav');
  if (!nav) return;
  nav.innerHTML = NAV.map(
    (item) => `<a class="admin-nav-item${item.id === activeId ? ' active' : ''}" href="${item.href}"><span class="material-symbols-outlined">${item.icon}</span>${item.label}</a>`
  ).join('');
}

export async function adminRequest(path, { method = 'GET', body } = {}) {
  const headers = { Authorization: `Bearer ${getToken()}` };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error('No hay conexión con el servidor.');
  }
  if (response.status === 401) {
    logout();
    throw new Error('Sesión no válida.');
  }
  const data = await response.json().catch(() => ({}));
  if (response.status === 403) throw new Error('No tienes permisos de administrador.');
  if (!response.ok) throw new Error(data.message || 'No fue posible completar la acción.');
  return data;
}

export function showState(container, title, message, action = '') {
  container.innerHTML = `<section class="admin-state"><span class="material-symbols-outlined">${action ? 'lock' : 'error'}</span><h1 class="headline-md">${escapeHtml(title)}</h1><p>${escapeHtml(message)}</p>${action ? `<a class="btn btn-primary label-caps" href="${action}">Continuar</a>` : ''}</section>`;
}

/** Valida sesión y rol administrador. Devuelve el usuario o null tras mostrar el estado. */
export async function guardAdmin(container, activeId) {
  document.getElementById('adminLogout')?.addEventListener('click', logout);
  renderAdminNav(activeId);
  if (!getToken()) {
    showState(container, 'Sesión requerida', 'Inicia sesión para acceder al panel administrativo.', '/login');
    return null;
  }
  try {
    const identity = await adminRequest('/api/auth/me');
    if (identity.user?.role !== 'administrator') {
      showState(container, 'Acceso restringido', 'Esta ruta está reservada para administradores activos.', '/dashboard');
      return null;
    }
    return identity.user;
  } catch (error) {
    showState(container, 'No se pudo verificar la sesión', error.message);
    return null;
  }
}

export function downloadCsv(filename, rows) {
  const csv = rows
    .map((row) => row.map((cell) => `"${String(cell ?? '').replace(/"/g, '""')}"`).join(','))
    .join('\n');
  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export const TICKET_CATEGORIES = {
  technical_bug: 'Error técnico',
  feature_request: 'Solicitud de función',
  account_issue: 'Problema de cuenta',
  other: 'Otro',
};

export const TICKET_STATUS_LABELS = {
  open: 'Abierto',
  in_progress: 'En progreso',
  resolved: 'Resuelto',
};

export function initials(name) {
  return String(name || '?').trim().split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase() ?? '').join('') || '?';
}
