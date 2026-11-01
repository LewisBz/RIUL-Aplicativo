import { requireAuth, API_BASE } from './session.js';
import { initLayout } from './layout.js';
import { api } from './api.js';
import { openFormDialog } from './forms.js';
import {
  toGamification,
  projectStatusLabel,
  publicationStatusLabel,
  productTypeLabel,
  isoDate,
} from './adapters.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const ROLE_IN_SEMILLERO = { leader: 'Líder', co_leader: 'Co-líder', member: 'Miembro' };
const ROLE_IN_PROJECT = { leader: 'Investigador Principal', member: 'Integrante' };
const PRODUCT_STATUS = { in_review: 'En revisión', approved: 'Aprobado' };

function starRow(container, total, filled) {
  for (let i = 0; i < total; i++) {
    const icon = document.createElement('span');
    icon.className = 'material-symbols-outlined';
    icon.classList.add(i < filled ? 'star-filled' : 'star-empty');
    icon.textContent = 'star';
    container.appendChild(icon);
  }
}

function text(tag, value, className) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = value;
  return element;
}

async function loadProfile() {
  return (await api('/api/profile')).profile;
}

let profile;
try {
  profile = await loadProfile();
} catch (error) {
  document.querySelector('main').innerHTML = '<div class="detail-empty"><strong></strong></div>';
  document.querySelector('main strong').textContent = error.message;
  throw error;
}

document.getElementById('infoEmail').textContent = profile.user.email;
document.getElementById('infoFaculty').textContent = profile.faculty?.name ?? '—';
document.getElementById('infoProgram').textContent = profile.program?.name ?? '—';
document.getElementById('infoOrcid').textContent = profile.orcid || '—';
document.getElementById('infoBio').textContent = profile.bio || 'Aún no has agregado una biografía.';

const GAMIFICATION = toGamification(profile.gamification);
document.getElementById('gamLevel').textContent = `Nivel ${GAMIFICATION.level}`;
document.getElementById('gamXp').textContent = `${GAMIFICATION.xp} / ${GAMIFICATION.nextLevelXp} XP`;
document.getElementById('xpFill').style.width = `${Math.round((GAMIFICATION.xp / GAMIFICATION.nextLevelXp) * 100)}%`;
starRow(document.getElementById('profileStars'), GAMIFICATION.totalStars, GAMIFICATION.stars);

const badgeRow = document.getElementById('badgeRow');
GAMIFICATION.badges.forEach((badge) => {
  const circle = document.createElement('span');
  circle.className = `badge-circle${badge.highlighted ? ' is-highlighted' : ''}`;
  circle.title = badge.title;
  circle.appendChild(text('span', badge.icon, 'material-symbols-outlined'));
  badgeRow.appendChild(circle);
});

function fillList(id, items, icon, emptyMessage) {
  const list = document.getElementById(id);
  if (!items.length) {
    list.appendChild(text('li', emptyMessage, 'body-md'));
    return;
  }
  items.forEach(({ name, meta }) => {
    const li = document.createElement('li');
    li.className = 'list-row';
    const iconEl = text('span', icon, 'material-symbols-outlined');
    iconEl.style.color = 'var(--primary)';
    const wrapper = document.createElement('div');
    const title = text('p', name, 'list-row-title');
    title.style.margin = '0';
    wrapper.append(title, text('span', meta, 'list-row-meta'));
    li.append(iconEl, wrapper);
    list.appendChild(li);
  });
}

fillList(
  'mySemilleros',
  profile.semilleros.map((s) => ({ name: s.name, meta: `Rol: ${ROLE_IN_SEMILLERO[s.my_role] ?? s.my_role}` })),
  'account_tree',
  'Aún no perteneces a ningún semillero.',
);
fillList(
  'profileProjects',
  profile.projects.map((p) => ({
    name: p.title,
    meta: `Rol: ${ROLE_IN_PROJECT[p.my_role] ?? p.my_role} - Estado: ${projectStatusLabel(p.status)}`,
  })),
  'folder',
  'Aún no participas en proyectos.',
);

function fillTable(id, rows, emptyMessage, columns) {
  const body = document.getElementById(id);
  if (!rows.length) {
    const tr = document.createElement('tr');
    const td = text('td', emptyMessage);
    td.colSpan = columns;
    tr.appendChild(td);
    body.appendChild(tr);
    return;
  }
  rows.forEach((cells) => {
    const tr = document.createElement('tr');
    cells.forEach((cell) => {
      const td = document.createElement('td');
      if (cell instanceof Node) td.appendChild(cell);
      else td.textContent = cell;
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });
}

fillTable(
  'pubsTable',
  profile.publications.map((p) => [p.title, p.venue ?? publicationStatusLabel(p.status), isoDate(p.published_on)]),
  'Sin publicaciones registradas.',
  3,
);
fillTable(
  'productsTable',
  profile.products.map((product) => {
    const approved = product.status === 'approved';
    return [productTypeLabel(product.type), product.name, text('span', PRODUCT_STATUS[product.status], `status-chip ${approved ? 'chip-approved' : 'chip-review'}`)];
  }),
  'Sin productos registrados.',
  3,
);

const timeline = document.getElementById('achievementsTimeline');
if (!GAMIFICATION.achievements.length) {
  timeline.appendChild(text('li', 'Aún no registras logros.', 'body-md'));
}
GAMIFICATION.achievements.forEach((item) => {
  const done = item.status === 'Validado';
  const li = document.createElement('li');
  const node = document.createElement('span');
  node.className = `timeline-node${done ? '' : ' is-pending'}`;
  li.append(
    node,
    text('span', item.title),
    text('small', done ? 'Validado' : item.status === 'Rechazado' ? 'Rechazado' : 'En proceso de validación', 'timeline-meta'),
  );
  timeline.appendChild(li);
});

document.getElementById('editProfileBtn').addEventListener('click', async () => {
  const catalog = await (await fetch(`${API_BASE}/api/auth/catalog`)).json();
  const faculties = catalog.faculties;
  const current = faculties.find((f) => f.id === profile.user.faculty_id);
  const updated = await openFormDialog({
    title: 'Editar perfil',
    fields: [
      { name: 'full_name', label: 'Nombre completo', required: true, value: profile.user.full_name ?? '' },
      {
        name: 'faculty_id',
        label: 'Facultad',
        type: 'select',
        options: faculties.map((f) => ({ value: f.id, label: f.name })),
        value: profile.user.faculty_id ?? '',
      },
      {
        name: 'program_id',
        label: 'Programa',
        type: 'select',
        options: [
          { value: '', label: 'Sin programa' },
          ...faculties.flatMap((f) => f.programs.map((p) => ({ value: p.id, label: `${f.name} — ${p.name}` }))),
        ],
        value: profile.user.program_id ?? '',
      },
      { name: 'orcid', label: 'ORCID', placeholder: '0000-0000-0000-0000', value: profile.orcid ?? '' },
      { name: 'bio', label: 'Biografía', type: 'textarea', value: profile.bio ?? '' },
    ],
    onSubmit: (values) =>
      api('/api/profile', {
        method: 'PATCH',
        body: {
          full_name: values.full_name,
          faculty_id: values.faculty_id ? Number(values.faculty_id) : null,
          program_id: values.program_id ? Number(values.program_id) : null,
          orcid: values.orcid.trim() || null,
          bio: values.bio.trim() || null,
        },
      }),
  });
  if (updated) location.reload();
});
