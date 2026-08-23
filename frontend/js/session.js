const API =
  location.protocol === 'file:' || location.port !== '5000'
    ? 'http://localhost:5000'
    : '';

const TOKEN_KEY = 'riul_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export async function getSessionUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const response = await fetch(`${API}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      localStorage.removeItem(TOKEN_KEY);
      return null;
    }
    const data = await response.json();
    return data.user ?? null;
  } catch {
    return null;
  }
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  window.location.href = 'index.html';
}
