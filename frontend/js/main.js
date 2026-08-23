import { getSessionUser, logout } from './session.js';

const menuToggle = document.getElementById('menuToggle');
const menuPanel = document.getElementById('menuPanel');

menuToggle?.addEventListener('click', () => {
  if (menuPanel.hasAttribute('data-open')) {
    menuPanel.removeAttribute('data-open');
  } else {
    menuPanel.setAttribute('data-open', '');
  }
});

menuPanel?.addEventListener('click', (event) => {
  if (event.target.closest('a')) menuPanel.removeAttribute('data-open');
});

const userMenuToggle = document.getElementById('userMenuToggle');
const userPanel = document.getElementById('userPanel');

function closeUserPanel() {
  userPanel?.classList.add('hidden');
  userMenuToggle?.setAttribute('aria-expanded', 'false');
}

userMenuToggle?.addEventListener('click', (event) => {
  event.stopPropagation();
  const isOpen = !userPanel.classList.contains('hidden');
  userPanel.classList.toggle('hidden', isOpen);
  userMenuToggle.setAttribute('aria-expanded', String(!isOpen));
});

document.addEventListener('click', (event) => {
  if (!userPanel?.classList.contains('hidden') && !event.target.closest('.nav-user')) {
    closeUserPanel();
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeUserPanel();
    menuPanel?.removeAttribute('data-open');
  }
});

document.querySelectorAll('[data-action="logout"]').forEach((button) => {
  button.addEventListener('click', () => logout());
});

const track = document.getElementById('eventsTrack');
const step = () => {
  const card = track?.querySelector('.carousel-card');
  return card ? card.getBoundingClientRect().width + 24 : 320;
};

document.getElementById('eventsPrev')?.addEventListener('click', () => {
  track?.scrollBy({ left: -step(), behavior: 'smooth' });
});

document.getElementById('eventsNext')?.addEventListener('click', () => {
  track?.scrollBy({ left: step(), behavior: 'smooth' });
});

const ROLE_LABELS = {
  researcher: 'Investigador',
  administrator: 'Administrador',
};

const user = await getSessionUser();

document.querySelectorAll('[data-auth]').forEach((el) => {
  el.classList.toggle('hidden', el.dataset.auth === 'guest' ? Boolean(user) : !user);
});

if (user) {
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
