const ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', href: '/dashboard' },
  { id: 'profile', label: 'Perfil', icon: 'person', href: '/profile' },
  { id: 'semilleros', label: 'Semillero', icon: 'account_tree', href: '#' },
  { id: 'proyectos', label: 'Proyectos', icon: 'folder', href: '#' },
  { id: 'comunidad', label: 'Comunidad', icon: 'group', href: '#' },
  { id: 'eventos', label: 'Eventos', icon: 'event', href: '#' },
  { id: 'gamificacion', label: 'Gamificación', icon: 'military_tech', href: '#' },
  { id: 'notificaciones', label: 'Notificaciones', icon: 'notifications', href: '#' },
];

export function renderSidebar() {
  const mount = document.getElementById('sidenavMount');
  if (!mount) return;

  const active = document.body.dataset.navActive ?? '';
  const nav = document.createElement('nav');
  nav.className = 'sidenav';
  nav.setAttribute('aria-label', 'Navegación principal');

  ITEMS.forEach((item) => {
    const link = document.createElement('a');
    link.className = `sidenav-item${item.id === active ? ' is-active' : ''}`;
    link.href = item.href;
    const icon = document.createElement('span');
    icon.className = 'material-symbols-outlined';
    icon.textContent = item.icon;
    const label = document.createElement('span');
    label.className = 'label-caps';
    label.textContent = item.label;
    link.append(icon, label);
    nav.appendChild(link);
  });

  mount.replaceChildren(nav);
}
