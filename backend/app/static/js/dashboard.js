import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api } from './api.js';
import { toGamification, toNotification, projectStatusLabel, publicationStatusLabel, roleLabel } from './adapters.js';
import { skeletonFor } from './skeleton.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const clearSkeleton = skeletonFor([
  { id: 'projectsList', variant: 'row', count: 3 },
  { id: 'pubsList', variant: 'row', count: 3 },
  { id: 'notifsList', variant: 'row', count: 3 },
]);
let dashboard;
try {
  dashboard = (await api('/api/dashboard')).dashboard;
  clearSkeleton();
} catch (error) {
  document.querySelector('main').innerHTML = '<div class="detail-empty"><strong></strong></div>';
  document.querySelector('main strong').textContent = error.message;
  throw error;
}
const PROJECTS_SUMMARY = dashboard.projects.map((p) => ({
  id: p.slug,
  title: p.title,
  status: projectStatusLabel(p.status),
}));
const PUBLICATIONS = dashboard.publications.map((p) => ({
  icon: 'article',
  title: p.title,
  meta: [p.venue, p.published_on?.slice(0, 4)].filter(Boolean).join(' • ') || publicationStatusLabel(p.status),
}));
const SEMILLERO = dashboard.semillero
  ? {
      name: dashboard.semillero.name,
      members: `${dashboard.semillero.member_count} Miembros activos`,
      activities: `${dashboard.semillero.activities_this_month} Actividades este mes`,
      slug: dashboard.semillero.slug,
    }
  : { name: 'Sin semillero', members: 'Únete a un semillero para colaborar', activities: '' };
const NOTIFICATIONS = dashboard.notifications.map(toNotification);
const GAMIFICATION = toGamification(dashboard.gamification);
document.getElementById('snippetLevel').textContent = `Nivel ${GAMIFICATION.level} · ${roleLabel(user.role)}`;

function starRow(container, total, filled) {
  for (let i = 0; i < total; i++) {
    const icon = document.createElement('span');
    icon.className = 'material-symbols-outlined';
    icon.classList.add(i < filled ? 'star-filled' : 'star-empty');
    icon.textContent = 'star';
    container.appendChild(icon);
  }
}

const count = document.getElementById('projectsCount');
count.textContent = `${PROJECTS_SUMMARY.filter((p) => p.status === 'En curso').length} Activos`;

const projectsList = document.getElementById('projectsList');
PROJECTS_SUMMARY.forEach((project) => {
  const row = document.createElement('div');
  row.className = 'list-row';
  const info = document.createElement('div');
  const title = document.createElement('p');
  title.className = 'list-row-title';
  title.style.margin = '0';
  title.textContent = project.title;
  const status = document.createElement('span');
  status.className = 'list-row-meta';
  status.textContent = `Estado: ${project.status}`;
  info.append(title, status);
  const arrow = document.createElement('button');
  arrow.className = 'icon-btn-round';
  arrow.type = 'button';
  arrow.setAttribute('aria-label', 'Ver proyecto');
  arrow.addEventListener('click', () => {
    window.location.href = `/project-detail?id=${encodeURIComponent(project.id)}`;
  });
  arrow.innerHTML = '<span class="material-symbols-outlined">arrow_forward</span>';
  row.append(info, arrow);
  projectsList.appendChild(row);
});

const pubsList = document.getElementById('pubsList');
PUBLICATIONS.forEach((pub) => {
  const li = document.createElement('li');
  li.className = 'list-row';
  const icon = document.createElement('span');
  icon.className = 'material-symbols-outlined';
  icon.style.color = 'var(--primary)';
  icon.textContent = pub.icon;
  const text = document.createElement('div');
  const title = document.createElement('p');
  title.className = 'list-row-title';
  title.style.margin = '0';
  title.textContent = pub.title;
  const meta = document.createElement('span');
  meta.className = 'list-row-meta';
  meta.textContent = pub.meta;
  text.append(title, meta);
  li.append(icon, text);
  pubsList.appendChild(li);
});

document.getElementById('semName').textContent = SEMILLERO.name;
document.getElementById('semMembers').textContent = SEMILLERO.members;
document.getElementById('semActivities').textContent = SEMILLERO.activities;

const notifsList = document.getElementById('notifsList');
NOTIFICATIONS.forEach((notif) => {
  const li = document.createElement('li');
  li.className = 'list-row';
  const icon = document.createElement('span');
  icon.className = 'material-symbols-outlined';
  icon.style.color = 'var(--tertiary-fixed)';
  icon.textContent = notif.icon;
  const text = document.createElement('span');
  text.className = 'body-md';
  text.textContent = notif.text;
  li.append(icon, text);
  notifsList.appendChild(li);
});

starRow(document.getElementById('snippetStars'), GAMIFICATION.totalStars, GAMIFICATION.stars);
