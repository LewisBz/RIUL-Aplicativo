import { requireAuth, API_BASE } from './session.js';
import { initLayout } from './layout.js';
import {
  GAMIFICATION,
  BADGES,
  MY_SEMILLEROS,
  PROFILE_PROJECTS,
  PROFILE_PUBLICATIONS,
  PRODUCTS,
  ACHIEVEMENTS,
} from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

function starRow(container, total, filled) {
  for (let i = 0; i < total; i++) {
    const icon = document.createElement('span');
    icon.className = 'material-symbols-outlined';
    icon.classList.add(i < filled ? 'star-filled' : 'star-empty');
    icon.textContent = 'star';
    container.appendChild(icon);
  }
}

try {
  const response = await fetch(`${API_BASE}/api/auth/catalog`);
  const catalog = await response.json();
  const faculty = catalog.faculties.find((f) => f.id === user.faculty_id);
  const program = faculty?.programs?.find((p) => p.id === user.program_id);
  document.getElementById('infoFaculty').textContent = faculty?.name ?? '—';
  document.getElementById('infoProgram').textContent = program?.name ?? '—';
} catch {
  document.getElementById('infoFaculty').textContent = '—';
  document.getElementById('infoProgram').textContent = '—';
}
document.getElementById('infoEmail').textContent = user.email;

document.getElementById('gamLevel').textContent = `Nivel ${GAMIFICATION.level}`;
document.getElementById('gamXp').textContent = `${GAMIFICATION.xp} / ${GAMIFICATION.nextLevelXp} XP`;
const percent = Math.round((GAMIFICATION.xp / GAMIFICATION.nextLevelXp) * 100);
document.getElementById('xpFill').style.width = `${percent}%`;

starRow(document.getElementById('profileStars'), GAMIFICATION.totalStars, GAMIFICATION.stars);

const badgeRow = document.getElementById('badgeRow');
BADGES.forEach((badge) => {
  const circle = document.createElement('span');
  circle.className = `badge-circle${badge.highlighted ? ' is-highlighted' : ''}`;
  circle.title = badge.title;
  circle.innerHTML = `<span class="material-symbols-outlined">${badge.icon}</span>`;
  badgeRow.appendChild(circle);
});

function fillList(id, items, nameKey, metaKey) {
  const list = document.getElementById(id);
  items.forEach((item) => {
    const li = document.createElement('li');
    li.className = 'list-row';
    const icon = document.createElement('span');
    icon.className = 'material-symbols-outlined';
    icon.style.color = 'var(--primary)';
    icon.textContent = id === 'mySemilleros' ? 'account_tree' : 'folder';
    const text = document.createElement('div');
    const title = document.createElement('p');
    title.className = 'list-row-title';
    title.style.margin = '0';
    title.textContent = item[nameKey];
    const meta = document.createElement('span');
    meta.className = 'list-row-meta';
    meta.textContent = item[metaKey];
    text.append(title, meta);
    li.append(icon, text);
    list.appendChild(li);
  });
}

fillList('mySemilleros', MY_SEMILLEROS, 'name', 'role');
fillList('profileProjects', PROFILE_PROJECTS, 'name', 'meta');

const pubsTable = document.getElementById('pubsTable');
PROFILE_PUBLICATIONS.forEach((pub) => {
  const tr = document.createElement('tr');
  [pub.title, pub.venue, pub.date].forEach((value) => {
    const td = document.createElement('td');
    td.textContent = value;
    tr.appendChild(td);
  });
  pubsTable.appendChild(tr);
});

const productsTable = document.getElementById('productsTable');
PRODUCTS.forEach((product) => {
  const tr = document.createElement('tr');
  const typeTd = document.createElement('td');
  typeTd.textContent = product.type;
  const nameTd = document.createElement('td');
  nameTd.textContent = product.name;
  const statusTd = document.createElement('td');
  const chip = document.createElement('span');
  chip.className = `status-chip ${product.status === 'Aprobado' ? 'chip-approved' : 'chip-review'}`;
  chip.textContent = product.status;
  statusTd.appendChild(chip);
  tr.append(typeTd, nameTd, statusTd);
  productsTable.appendChild(tr);
});

const timeline = document.getElementById('achievementsTimeline');
ACHIEVEMENTS.forEach((item) => {
  const li = document.createElement('li');
  const node = document.createElement('span');
  node.className = `timeline-node${item.done ? '' : ' is-pending'}`;
  const text = document.createElement('span');
  text.textContent = item.text;
  const meta = document.createElement('small');
  meta.className = 'timeline-meta';
  meta.textContent = item.done ? 'Validado' : 'En proceso de validación';
  li.append(node, text, meta);
  timeline.appendChild(li);
});
