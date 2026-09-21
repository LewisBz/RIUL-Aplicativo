import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { SEMILLEROS, memberTone } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const params = new URLSearchParams(window.location.search);
const requestedId = params.get('id');
const sem = SEMILLEROS.find((s) => s.id === requestedId) ?? SEMILLEROS[0];
const detail = sem.detail;

document.title = `${sem.name} - RIUL`;

const MEMBERS_VISIBLE_COLLAPSED = 4;
let membersExpanded = false;

function initialsFrom(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

function statusPillClass(status) {
  const normalized = status.toLowerCase();
  if (normalized.includes('publicado')) return 'pill pill-published';
  if (normalized.includes('revisión') || normalized.includes('revision')) return 'pill pill-review';
  if (normalized.includes('activo')) return 'pill pill-active';
  return 'pill pill-closed';
}

function tagPillClass(tag) {
  return tag.toLowerCase().includes('prototipo') ? 'pill pill-pending' : 'pill pill-active';
}

document.getElementById('semLogoIcon').textContent = sem.icon;
document.getElementById('semName').textContent = sem.name;
document.getElementById('semAffiliation').textContent =
  detail.affiliation || `${sem.faculty} · ${sem.program}`;
document.getElementById('semAbout').textContent = detail.about;
document.getElementById('semMission').textContent = detail.mission;
document.getElementById('semVision').textContent = detail.vision;
document.getElementById('leaderName').textContent = sem.leader;
document.getElementById('leaderTitle').textContent = detail.leaderTitle;
document.getElementById('leaderInitials').textContent = initialsFrom(sem.leader);

const interestAreas = document.getElementById('interestAreas');
detail.interestAreas.forEach((area) => {
  const pill = document.createElement('span');
  pill.className = 'pill pill-pending';
  pill.textContent = area;
  interestAreas.appendChild(pill);
});

const membersGrid = document.getElementById('membersGrid');
const toggleMembersBtn = document.getElementById('toggleMembers');

function visibleMembers() {
  return membersExpanded ? detail.members : detail.members.slice(0, MEMBERS_VISIBLE_COLLAPSED);
}

function renderMembers() {
  membersGrid.innerHTML = '';
  visibleMembers().forEach((member) => {
    const row = document.createElement('div');
    row.style.cssText =
      'display:flex;align-items:center;gap:var(--space-3);background-color:var(--surface);' +
      'border:1px solid var(--outline-variant);border-radius:var(--radius-sm);padding:var(--space-2);';

    const tone = memberTone(member.tone);
    const avatar = document.createElement('span');
    avatar.style.cssText =
      `width:32px;height:32px;flex-shrink:0;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;` +
      `font-size:12px;font-weight:700;background-color:${tone.bg};color:${tone.fg};`;
    avatar.textContent = member.initials || initialsFrom(member.name);

    const info = document.createElement('div');
    info.style.minWidth = '0';
    const name = document.createElement('p');
    name.className = 'body-md';
    name.style.cssText = 'margin:0;font-weight:600;';
    name.textContent = member.name;
    const role = document.createElement('p');
    role.className = 'body-md';
    role.style.cssText = 'margin:0;color:var(--secondary);font-size:12px;';
    role.textContent = member.role;
    info.append(name, role);

    row.append(avatar, info);
    membersGrid.appendChild(row);
  });
  const hasMore = detail.members.length > MEMBERS_VISIBLE_COLLAPSED;
  toggleMembersBtn.hidden = !hasMore;
  toggleMembersBtn.textContent = membersExpanded
    ? 'Ver Menos'
    : `Ver Todos (${detail.members.length})`;
}

toggleMembersBtn.addEventListener('click', () => {
  membersExpanded = !membersExpanded;
  renderMembers();
});
renderMembers();

const linesList = document.getElementById('linesList');
detail.lines.forEach((line) => {
  const row = document.createElement('div');
  row.style.cssText =
    'display:flex;align-items:center;justify-content:space-between;gap:var(--space-3);' +
    'background-color:var(--surface-container-low);border-radius:var(--radius-md);padding:var(--space-3);';
  const info = document.createElement('div');
  info.style.cssText = 'display:flex;align-items:center;gap:var(--space-3);min-width:0;';
  info.innerHTML =
    `<span class="material-symbols-outlined" style="color:var(--primary);">${line.icon}</span>` +
    `<div><p class="body-md" style="margin:0;font-weight:700;">${line.name}</p>` +
    `<p class="body-md" style="margin:0;color:var(--secondary);font-size:12px;">Coordinador: ${line.coordinator}</p></div>`;
  const status = document.createElement('span');
  status.className = statusPillClass('Activo');
  status.textContent = 'Activo';
  row.append(info, status);
  linesList.appendChild(row);
});

const projectsList = document.getElementById('projectsList');
detail.projects.forEach((project) => {
  const cardEl = document.createElement('article');
  cardEl.className = 'card-research';
  cardEl.style.display = 'flex';
  cardEl.style.flexDirection = 'column';
  cardEl.style.gap = 'var(--space-2)';
  cardEl.innerHTML =
    `<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:var(--space-3);">` +
    `<h3 class="body-md" style="margin:0;font-size:14px;">${project.title}</h3>` +
    `<span class="${tagPillClass(project.tag)}">${project.tag}</span></div>`;
  const description = document.createElement('p');
  description.className = 'body-md';
  description.style.cssText = 'margin:0;color:var(--secondary);';
  description.textContent = project.description;
  const footerRow = document.createElement('div');
  footerRow.style.cssText =
    'display:flex;justify-content:space-between;align-items:center;gap:var(--space-3);flex-wrap:wrap;' +
    'font-size:12px;color:var(--secondary);';
  const role = document.createElement('span');
  role.textContent = project.role;
  const status = document.createElement('span');
  status.textContent = project.status;
  status.style.cssText = 'color:var(--primary);font-weight:600;';
  footerRow.append(role, status);
  cardEl.append(description, footerRow);
  projectsList.appendChild(cardEl);
});

const pubsList = document.getElementById('pubsList');
detail.publications.forEach((pub, index) => {
  const li = document.createElement('li');
  li.style.cssText = `border-left:2px solid ${index === 0 ? 'var(--primary)' : 'var(--outline-variant)'};padding-left:var(--space-3);`;
  li.innerHTML =
    `<p class="body-md" style="margin:0;font-weight:700;font-size:13px;">${pub.title}</p>` +
    `<p class="body-md" style="margin:0;color:var(--secondary);font-size:12px;font-style:italic;">${pub.venue}</p>`;
  const metaRow = document.createElement('div');
  metaRow.style.cssText = 'display:flex;justify-content:space-between;align-items:center;margin-top:var(--space-1);';
  const date = document.createElement('span');
  date.textContent = pub.date;
  date.style.cssText = 'font-size:11px;color:var(--secondary);';
  const statusPill = document.createElement('span');
  statusPill.className = statusPillClass(pub.status);
  statusPill.textContent = pub.status;
  metaRow.append(date, statusPill);
  li.appendChild(metaRow);
  pubsList.appendChild(li);
});

const activitiesList = document.getElementById('activitiesList');
detail.activities.forEach((activity) => {
  const li = document.createElement('li');
  li.innerHTML =
    `<p class="label-caps" style="margin:0;color:var(--primary);">${activity.date}</p>` +
    `<p class="body-md" style="margin:0;font-weight:600;">${activity.title}</p>` +
    `<p class="body-md" style="margin:0;color:var(--secondary);font-size:12px;">${activity.place}</p>`;
  activitiesList.appendChild(li);
});

const followBtn = document.getElementById('followBtn');
const followIcon = document.getElementById('followIcon');
const followLabel = document.getElementById('followLabel');
let following = false;

followBtn.addEventListener('click', () => {
  following = !following;
  followIcon.textContent = following ? 'favorite' : 'favorite_border';
  followIcon.style.fontVariationSettings = following ? "'FILL' 1" : "'FILL' 0";
  followLabel.textContent = following ? 'Siguiendo' : 'Seguir';
  followBtn.classList.toggle('btn-primary', following);
  followBtn.classList.toggle('btn-outline', !following);
});

const linkForm = document.getElementById('linkForm');
const motivationInput = document.getElementById('motivationInput');
const submitLinkBtn = document.getElementById('submitLinkBtn');
const linkStateTag = document.getElementById('linkStateTag');
const linkNote = document.getElementById('linkNote');

linkForm.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!motivationInput.value.trim()) {
    motivationInput.focus();
    return;
  }
  motivationInput.disabled = true;
  submitLinkBtn.disabled = true;
  submitLinkBtn.innerHTML =
    '<span class="material-symbols-outlined">check_circle</span>Solicitud Enviada';
  linkStateTag.textContent = 'Estado: Solicitud enviada';
  linkStateTag.classList.remove('pill-pending');
  linkStateTag.classList.add('pill-active');
  linkNote.textContent = 'Tu solicitud fue registrada y será revisada por el líder del semillero.';
});
