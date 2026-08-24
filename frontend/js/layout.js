import { initSessionUI } from './session.js';

export const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', href: '/dashboard' },
  { id: 'profile', label: 'Perfil', icon: 'person', href: '/profile' },
  { id: 'semilleros', label: 'Semillero', icon: 'account_tree', href: '/semilleros' },
  { id: 'proyectos', label: 'Proyectos', icon: 'folder', href: '/projects' },
  { id: 'comunidad', label: 'Comunidad', icon: 'group', href: '/feed' },
  { id: 'eventos', label: 'Eventos', icon: 'event', href: '/events' },
  { id: 'gamificacion', label: 'Gamificación', icon: 'military_tech', href: '/gamification' },
  { id: 'notificaciones', label: 'Notificaciones', icon: 'notifications', href: '/notifications' },
];

const TOPNAV_LINKS = [
  { label: 'Semilleros', href: '/semilleros' },
  { label: 'Proyectos', href: '/projects' },
  { label: 'Eventos', href: '/events' },
];

const FOOTER_LINKS = [
  { label: 'Privacidad', href: '#' },
  { label: 'Términos', href: '#' },
  { label: 'Contacto', href: '#' },
];

function topnavHtml() {
  const links = TOPNAV_LINKS.map(
    ({ label, href }) => `<a class="nav-link label-caps" href="${href}">${label}</a>`
  ).join('');
  return `
    <div class="container-main" style="display:flex;align-items:center;justify-content:space-between;width:100%;">
      <div style="display:flex;align-items:center;">
        <a class="topnav-brand" href="index.html">RIUL</a>
      </div>
      <nav class="only-desktop">${links}</nav>
      <div style="display:flex;align-items:center;gap:16px;">
        <a class="icon-action notification-link" href="/notifications" aria-label="Notificaciones"><span class="material-symbols-outlined">notifications</span></a>
        <button class="icon-action only-desktop" aria-label="Configuración"><span class="material-symbols-outlined">settings</span></button>
        <div class="nav-user">
          <button class="profile-chip only-desktop" type="button" id="userMenuToggle" aria-haspopup="true" aria-expanded="false" title="Perfil">
            <span class="avatar avatar-sm" data-slot="avatar"></span>
            <span class="label-caps">Perfil</span>
            <span class="material-symbols-outlined" style="font-size:18px;">arrow_drop_down</span>
          </button>
          <div class="nav-dropdown hidden" id="userPanel">
            <a class="nav-dropdown-item label-caps" href="/dashboard">Dashboard</a>
            <a class="nav-dropdown-item label-caps" href="/profile">Mi perfil</a>
            <button class="nav-dropdown-item as-button label-caps" type="button" data-action="logout">Cerrar sesión</button>
          </div>
        </div>
        <button class="topnav-menu-btn" id="menuToggle" aria-label="Abrir menú">
          <span class="material-symbols-outlined">menu</span>
        </button>
      </div>
    </div>`;
}

function menuPanelHtml() {
  return TOPNAV_LINKS.concat({ label: 'Comunidad', href: '/feed' })
    .map(({ label, href }) => `<a class="nav-link label-caps" href="${href}">${label}</a>`)
    .join('');
}

function sidebarHtml(activeId) {
  const items = NAV_ITEMS.map((item) => `
    <a class="nav-item label-caps${item.id === activeId ? ' active' : ''}" href="${item.href}">
      <span class="material-symbols-outlined">${item.icon}</span>${item.label}
    </a>`).join('');
  return `
    <div class="sidebar-profile">
      <span class="avatar avatar-xl" data-slot="avatar"></span>
      <h2 class="headline-md" data-slot="name">Investigador</h2>
      <p class="body-md" data-slot="role">&nbsp;</p>
    </div>
    <nav class="sidebar-nav">${items}</nav>
    <div class="sidebar-footer">
      <button class="btn btn-primary btn-block label-caps" type="button">Nuevo Proyecto</button>
    </div>`;
}

function footerHtml() {
  const links = FOOTER_LINKS.map(
    ({ label, href }) => `<a class="nav-link" href="${href}">${label}</a>`
  ).join('');
  return `
    <div class="footer-landing-inner">
      <p class="body-md" style="margin:0;color:var(--on-surface-variant);text-align:center;">© 2026 RIUL - Luis, Hector, Javier. Barranquilla, Atlántico</p>
      <nav class="footer-links">${links}</nav>
    </div>`;
}

function wireMobileMenu() {
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

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') menuPanel?.removeAttribute('data-open');
  });
}

export async function initLayout() {
  const activeId = document.body.dataset.navActive ?? '';

  const topnavMount = document.getElementById('topnavMount');
  topnavMount?.insertAdjacentHTML('afterbegin', topnavHtml());
  topnavMount?.insertAdjacentHTML('afterend',
    `<nav class="topnav-menu-panel" id="menuPanel">${menuPanelHtml()}</nav>`);

  document.getElementById('sidenavMount')?.classList.add('sidebar', 'custom-scrollbar', 'app-sidebar');
  document.getElementById('sidenavMount')?.insertAdjacentHTML('afterbegin', sidebarHtml(activeId));
  document.getElementById('footerMount')?.classList.add('footer-landing');
  document.getElementById('footerMount')?.insertAdjacentHTML('afterbegin', footerHtml());

  wireMobileMenu();
  await initSessionUI();
}
