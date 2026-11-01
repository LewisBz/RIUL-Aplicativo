import { API_BASE, getToken, logout } from './session.js';

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[ch]));
}

export function queryString(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, value);
  });
  const text = search.toString();
  return text ? `?${text}` : '';
}

/** Cliente JSON de la API REST de RIUL. Lanza Error con el mensaje del backend. */
export async function api(path, { method = 'GET', body } = {}) {
  const headers = { Authorization: `Bearer ${getToken()}` };
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData;
  if (body !== undefined && !isForm) headers['Content-Type'] = 'application/json';
  let response;
  try {
    response = await fetch(API_BASE + path, {
      method,
      headers,
      body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    });
  } catch {
    throw new Error('No hay conexión con el servidor.');
  }
  if (response.status === 401) {
    logout();
    throw new Error('Sesión expirada.');
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || 'No fue posible completar la acción.');
  return data;
}
