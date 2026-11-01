import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api, escapeHtml } from './api.js';
import { memberTone, toSemilleroDetail } from './adapters.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const requestedId = new URLSearchParams(window.location.search).get('id');
if (!requestedId) {
  window.location.replace('/semilleros');
  throw new Error('Semillero no indicado');
}

async function fetchSemillero() {
  return toSemilleroDetail((await api(`/api/semilleros/${encodeURIComponent(requestedId)}`)).semillero);
}

let sem;
try {
  sem = await fetchSemillero();
} catch (error) {
  document.querySelector('main').innerHTML =
    `<div class="detail-empty"><strong></strong><a href="/semilleros">Volver a semilleros</a></div>`;
  document.querySelector('main strong').textContent = error.message;
  throw error;
}
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
    `<span class="material-symbols-outlined" style="color:var(--primary);">${escapeHtml(line.icon)}</span>` +
    `<div><p class="body-md" style="margin:0;font-weight:700;">${escapeHtml(line.name)}</p>` +
    `<p class="body-md" style="margin:0;color:var(--secondary);font-size:12px;">Coordinador: ${escapeHtml(line.coordinator)}</p></div>`;
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
    `<h3 class="body-md" style="margin:0;font-size:14px;">${escapeHtml(project.title)}</h3>` +
    `<span class="${tagPillClass(project.tag)}">${escapeHtml(project.tag)}</span></div>`;
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
    `<p class="body-md" style="margin:0;font-weight:700;font-size:13px;">${escapeHtml(pub.title)}</p>` +
    `<p class="body-md" style="margin:0;color:var(--secondary);font-size:12px;font-style:italic;">${escapeHtml(pub.venue)}</p>`;
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
    `<p class="label-caps" style="margin:0;color:var(--primary);">${escapeHtml(activity.date)}</p>` +
    `<p class="body-md" style="margin:0;font-weight:600;">${escapeHtml(activity.title)}</p>` +
    `<p class="body-md" style="margin:0;color:var(--secondary);font-size:12px;">${escapeHtml(activity.place)}</p>`;
  activitiesList.appendChild(li);
});

const base = `/api/semilleros/${encodeURIComponent(sem.id)}`;

document.getElementById('semProgress').textContent =
  `Nivel ${sem.progress.level} · ${sem.progress.xp} XP · ${sem.followerCount} ` +
  `${sem.followerCount === 1 ? 'seguidor' : 'seguidores'}`;

const followBtn = document.getElementById('followBtn');
const followIcon = document.getElementById('followIcon');
const followLabel = document.getElementById('followLabel');

function renderFollow() {
  followIcon.textContent = sem.following ? 'favorite' : 'favorite_border';
  followLabel.textContent = sem.following ? 'Siguiendo' : 'Seguir';
  followBtn.setAttribute('aria-pressed', String(sem.following));
}
renderFollow();

followBtn.addEventListener('click', async () => {
  followBtn.disabled = true;
  try {
    await api(`${base}/follow`, { method: sem.following ? 'DELETE' : 'POST' });
    sem.following = !sem.following;
    sem.followerCount += sem.following ? 1 : -1;
    document.getElementById('semProgress').textContent =
      `Nivel ${sem.progress.level} · ${sem.progress.xp} XP · ${sem.followerCount} ` +
      `${sem.followerCount === 1 ? 'seguidor' : 'seguidores'}`;
    renderFollow();
  } catch (error) {
    linkNote.textContent = error.message;
  } finally {
    followBtn.disabled = false;
  }
});

const linkForm = document.getElementById('linkForm');
const motivationInput = document.getElementById('motivationInput');
const submitLinkBtn = document.getElementById('submitLinkBtn');
const linkStateTag = document.getElementById('linkStateTag');
const linkNote = document.getElementById('linkNote');

// Estados de vinculación: sin solicitud | pending | active | rejected (el líder es active).
const MEMBERSHIP_VIEW = {
  none: {
    tag: 'Estado: No vinculado',
    pill: 'pill-pending',
    button: 'Solicitar Vinculación',
    note: 'Tu solicitud será revisada por el líder del semillero.',
  },
  pending: {
    tag: 'Estado: Solicitud pendiente',
    pill: 'pill-review',
    button: 'Cancelar Solicitud',
    note: 'El líder del semillero revisará tu solicitud.',
  },
  rejected: {
    tag: 'Estado: Solicitud rechazada',
    pill: 'pill-closed',
    button: 'Volver a Solicitar',
    note: 'Tu solicitud anterior fue rechazada. Puedes intentarlo nuevamente.',
  },
  active: {
    tag: 'Estado: Vinculado',
    pill: 'pill-active',
    button: 'Abandonar Semillero',
    note: 'Eres parte de este semillero. Puedes salir cuando quieras.',
  },
};
const MEMBERSHIP_PILLS = ['pill-pending', 'pill-review', 'pill-closed', 'pill-active'];

const isLeader = sem.myRole === 'leader';

function membershipKey() {
  return sem.myStatus ?? 'none';
}

function renderMembership() {
  const key = membershipKey();
  const view = MEMBERSHIP_VIEW[key];
  linkStateTag.textContent = view.tag;
  linkStateTag.classList.remove(...MEMBERSHIP_PILLS);
  linkStateTag.classList.add(view.pill);
  const needsMotivation = key === 'none' || key === 'rejected';
  motivationInput.hidden = !needsMotivation;
  motivationInput.required = false;
  submitLinkBtn.disabled = isLeader;
  submitLinkBtn.textContent = isLeader ? 'Eres el líder de este semillero' : view.button;
  linkNote.textContent = isLeader ? 'El líder no puede abandonar su propio semillero.' : view.note;
}
renderMembership();

linkForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  submitLinkBtn.disabled = true;
  try {
    const key = membershipKey();
    if (key === 'pending' || key === 'active') {
      await api(`${base}/members/me`, { method: 'DELETE' });
    } else {
      await api(`${base}/members`, { method: 'POST' });
    }
    window.location.reload();
  } catch (error) {
    linkNote.textContent = error.message;
    submitLinkBtn.disabled = false;
  }
});

// Gestión de solicitudes (líder, co-líder o administrador).
const pendingBox = document.getElementById('pendingBox');
const pendingList = document.getElementById('pendingList');
const pendingNote = document.getElementById('pendingNote');

function renderPending() {
  pendingList.innerHTML = '';
  pendingBox.hidden = detail.pendingMembers.length === 0;
  detail.pendingMembers.forEach((request) => {
    const row = document.createElement('div');
    row.style.cssText =
      'display:flex;align-items:center;justify-content:space-between;gap:var(--space-2);flex-wrap:wrap;' +
      'background-color:var(--surface);border:1px solid var(--outline-variant);' +
      'border-radius:var(--radius-sm);padding:var(--space-2);';
    const name = document.createElement('span');
    name.className = 'body-md';
    name.style.fontWeight = '600';
    name.textContent = request.name;

    const actions = document.createElement('div');
    actions.style.cssText = 'display:flex;gap:var(--space-2);';
    [
      ['active', 'Aprobar', 'btn btn-primary label-caps'],
      ['rejected', 'Rechazar', 'btn btn-outline label-caps'],
    ].forEach(([status, label, cls]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = cls;
      button.textContent = label;
      button.setAttribute('aria-label', `${label} solicitud de ${request.name}`);
      button.addEventListener('click', () => reviewRequest(request, status, actions));
      actions.appendChild(button);
    });
    row.append(name, actions);
    pendingList.appendChild(row);
  });
}

async function reviewRequest(request, status, actions) {
  actions.querySelectorAll('button').forEach((button) => (button.disabled = true));
  try {
    await api(`${base}/members/${request.id}`, { method: 'PATCH', body: { status } });
    sem = await fetchSemillero();
    detail.pendingMembers = sem.detail.pendingMembers;
    detail.members = sem.detail.members;
    pendingNote.textContent =
      status === 'active' ? `${request.name} fue vinculado al semillero.` : 'Solicitud rechazada.';
    renderMembers();
    renderPending();
  } catch (error) {
    pendingNote.textContent = error.message;
    actions.querySelectorAll('button').forEach((button) => (button.disabled = false));
  }
}
renderPending();