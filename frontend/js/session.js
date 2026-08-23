export const API_BASE =
  location.protocol === 'file:' || location.port !== '5000'
    ? 'http://localhost:5000'
    : '';

const TOKEN_KEY = 'riul_token';

const ROLE_LABELS = {
  researcher: 'Investigador',
  administrator: 'Administrador',
};

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export async function getSessionUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const response = await fetch(`${API_BASE}/api/auth/me`, {
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
  window.location.href = '/login';
}

export async function requireAuth() {
  const user = await getSessionUser();
  if (!user) {
    window.location.href = '/login';
    return null;
  }
  return user;
}

function fillSlots(user) {
  const displayName = user.full_name || user.email;
  const initial = displayName.trim().charAt(0).toUpperCase();
  document.querySelectorAll('[data-slot="avatar"]').forEach((el) => {
    el.textContent = initial;
  });
  document.querySelectorAll('[data-slot="name"]').forEach((el) => {
    el.textContent = displayName;
  });
  document.querySelectorAll('[data-slot="role"]').forEach((el) => {
    el.textContent = ROLE_LABELS[user.role] ?? user.role;
  });
}

function wireUserDropdown() {
  const userMenuToggle = document.getElementById('userMenuToggle');
  const userPanel = document.getElementById('userPanel');
  if (!userMenuToggle || !userPanel) return;

  const closeUserPanel = () => {
    userPanel.classList.add('hidden');
    userMenuToggle.setAttribute('aria-expanded', 'false');
  };

  userMenuToggle.addEventListener('click', (event) => {
    event.stopPropagation();
    const isOpen = !userPanel.classList.contains('hidden');
    userPanel.classList.toggle('hidden', isOpen);
    userMenuToggle.setAttribute('aria-expanded', String(!isOpen));
  });

  document.addEventListener('click', (event) => {
    if (!userPanel.classList.contains('hidden') && !event.target.closest('.nav-user')) {
      closeUserPanel();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeUserPanel();
  });
}

export async function initSessionUI() {
  const user = await getSessionUser();

  document.querySelectorAll('[data-auth]').forEach((el) => {
    el.classList.toggle('hidden', el.dataset.auth === 'guest' ? Boolean(user) : !user);
  });

  if (user) fillSlots(user);
  wireUserDropdown();

  document.querySelectorAll('[data-action="logout"]').forEach((button) => {
    button.addEventListener('click', () => logout());
  });

  return user;
}
