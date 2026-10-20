import { API_BASE, requireAuth } from './session.js';
import { initLayout } from './layout.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const params = new URLSearchParams(window.location.search);
const requestedId = params.get('id');
const pageContent = document.querySelector('.dash-grid');
let record;
try {
  if (!requestedId) throw new Error('Falta el identificador del semillero.');
  const response = await fetch(
    `${API_BASE}/api/semilleros/${encodeURIComponent(requestedId)}`
  );
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || `El servidor respondió ${response.status}.`);
  }
  if (!data.semillero) throw new Error('El servidor no devolvió el semillero solicitado.');
  record = data.semillero;
} catch (error) {
  console.error('No se pudo cargar el detalle del semillero.', error);
  const message = document.createElement('p');
  message.className = 'body-lg';
  message.setAttribute('role', 'alert');
  message.textContent = requestedId
    ? 'No fue posible cargar este semillero. Verifica el enlace o intenta recargar la página.'
    : 'Falta el identificador del semillero. Regresa al listado y selecciona uno.';
  pageContent.hidden = true;
  document.getElementById('vinculacion').hidden = true;
  pageContent.before(message);
  return;
}

const sem = {
  name: record.name,
  faculty: record.faculty,
  program: record.program,
  leader: record.leader,
  icon: 'groups',
};
const detail = {
  affiliation: [record.faculty, record.program].filter(Boolean).join(' · '),
  about: record.description || 'Sin descripción registrada.',
  mission: record.mission || 'Sin misión registrada.',
  vision: record.vision || 'Sin visión registrada.',
  interestAreas: record.area ? [record.area] : [],
  leaderTitle: 'Docente líder',
  members: (record.members || []).map((member) => ({
    initials: member.initials,
    name: member.full_name,
    role: member.role_in_semillero,
  })),
};

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
if (detail.interestAreas.length === 0) interestAreas.closest('div').hidden = true;
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

    const avatar = document.createElement('span');
    avatar.style.cssText =
      `width:32px;height:32px;flex-shrink:0;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;` +
      'font-size:12px;font-weight:700;background-color:var(--surface-container-high);color:var(--primary);';
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

document.getElementById('linkForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const motivation = document.getElementById('motivationInput').value;
  const response = await fetch(`${API_BASE}/api/semilleros/${encodeURIComponent(requestedId)}/join`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('riul_token')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ motivation }),
  });
  const data = await response.json().catch(() => ({}));
  document.getElementById('linkNote').textContent = response.ok
    ? 'Solicitud enviada. Estado: pendiente de aprobación del líder.'
    : (data.message || 'No se pudo enviar la solicitud.');
});

if (record.leader && user.full_name && record.leader === user.full_name) {
  const pendingResponse = await fetch(`${API_BASE}/api/semilleros/${encodeURIComponent(requestedId)}/pending`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('riul_token')}` },
  });
  const pending = pendingResponse.ok ? (await pendingResponse.json()).items || [] : [];
  const box = document.getElementById('vinculacion');
  pending.forEach((item) => {
    const row = document.createElement('div');
    row.className = 'body-md';
    row.textContent = `${item.name} (${item.email})`;
    const approve = document.createElement('button');
    approve.className = 'btn btn-teal label-caps';
    approve.type = 'button';
    approve.textContent = 'Aprobar';
    approve.addEventListener('click', async () => {
      await fetch(`${API_BASE}/api/semilleros/${encodeURIComponent(requestedId)}/members/${item.user_id}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('riul_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'active' }),
      });
      location.reload();
    });
    row.append(approve);
    box.append(row);
  });
}

document.getElementById('researchDetails').hidden = true;
document.getElementById('publicationsSection').hidden = true;
document.getElementById('activitiesSection').hidden = true;
