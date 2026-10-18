import { API_BASE, requireAuth } from './session.js';
import { initLayout } from './layout.js';
await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const grid = document.getElementById('semillerosGrid');
const resultsCount = document.getElementById('resultsCount');
const emptyState = document.getElementById('emptyState');
let semillerosList;
try {
  const response = await fetch(`${API_BASE}/api/semilleros`);
  if (!response.ok) {
    throw new Error(`El servidor respondió ${response.status}.`);
  }
  const data = await response.json();
  if (!Array.isArray(data.items)) {
    throw new Error('La respuesta del servidor no contiene la lista de semilleros.');
  }
  semillerosList = data.items.map((item) => ({
    id: item.slug || String(item.id),
    name: item.name,
    faculty: item.faculty,
    program: item.program,
    area: item.area || 'Investigación General',
    description: item.description || '',
    leader: item.leader || 'Por asignar',
    memberCount: item.member_count ?? item.memberCount ?? 0,
    icon: 'groups',
    topBadge: null,
  }));
} catch (error) {
  console.error('No se pudieron cargar los semilleros.', error);
  const message = document.createElement('p');
  message.className = 'body-lg';
  message.setAttribute('role', 'alert');
  message.textContent = 'No fue posible cargar los semilleros. Intenta recargar la página.';
  grid.replaceChildren(message);
  resultsCount.textContent = '';
  emptyState.hidden = true;
  return;
}

const state = { query: '', faculty: 'all', program: 'all', area: 'all' };

const searchInput = document.getElementById('searchInput');
const filterFaculty = document.getElementById('filterFaculty');
const filterProgram = document.getElementById('filterProgram');
const filterArea = document.getElementById('filterArea');
const clearFiltersBtn = document.getElementById('clearFilters');
const searchBtn = document.getElementById('searchBtn');

function normalize(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function fillSelect(select, values) {
  select.innerHTML = '';
  const allOption = document.createElement('option');
  allOption.value = 'all';
  allOption.textContent = '(Todas)';
  select.appendChild(allOption);
  [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es')).forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

fillSelect(filterFaculty, semillerosList.map((s) => s.faculty));
fillSelect(filterProgram, semillerosList.map((s) => s.program));
fillSelect(filterArea, semillerosList.map((s) => s.area));

function filteredSemilleros() {
  const query = normalize(state.query.trim());
  return semillerosList.filter((s) => {
    if (state.faculty !== 'all' && s.faculty !== state.faculty) return false;
    if (state.program !== 'all' && s.program !== state.program) return false;
    if (state.area !== 'all' && s.area !== state.area) return false;
    if (!query) return true;
    const haystack = normalize(
      [s.name, s.description, s.leader, s.faculty, s.program, s.area].join(' ')
    );
    return haystack.includes(query);
  });
}

function detailHref(id, anchor) {
  return `/semillero-detalle?id=${encodeURIComponent(id)}${anchor ? `#${anchor}` : ''}`;
}

function buildCard(sem) {
  const card = document.createElement('article');
  card.className = 'glass-card dash-card';
  card.style.borderTop = '4px solid transparent';

  const headRow = document.createElement('div');
  headRow.style.display = 'flex';
  headRow.style.alignItems = 'flex-start';
  headRow.style.gap = 'var(--space-4)';

  const logo = document.createElement('div');
  logo.style.cssText =
    'width:64px;height:64px;flex-shrink:0;border-radius:var(--radius-md);background-color:var(--surface-container-low);' +
    'border:1px solid var(--outline-variant);display:inline-flex;align-items:center;justify-content:center;';
  const icon = document.createElement('span');
  icon.className = 'material-symbols-outlined';
  icon.style.cssText = 'font-size:32px;color:var(--primary);';
  icon.textContent = sem.icon;
  logo.appendChild(icon);

  const headText = document.createElement('div');
  headText.style.minWidth = '0';

  const titleRow = document.createElement('div');
  titleRow.style.cssText = 'display:flex;align-items:center;gap:var(--space-2);flex-wrap:wrap;';

  const titleLink = document.createElement('a');
  titleLink.href = detailHref(sem.id);
  titleLink.textContent = sem.name;
  titleLink.className = 'headline-md';
  titleLink.style.cssText = 'font-size:18px;line-height:1.3;color:var(--primary);text-decoration:none;margin:0;';
  titleLink.addEventListener('mouseenter', () => { titleLink.style.color = 'var(--surface-tint)'; });
  titleLink.addEventListener('mouseleave', () => { titleLink.style.color = 'var(--primary)'; });

  titleRow.appendChild(titleLink);

  if (sem.topBadge) {
    const badge = document.createElement('span');
    badge.className = 'pill';
    badge.style.cssText = 'background-color:rgba(255,184,0,0.2);color:#8a6d00;';
    badge.textContent = sem.topBadge;
    titleRow.appendChild(badge);
  }

  const programLine = document.createElement('p');
  programLine.className = 'label-caps';
  programLine.style.cssText = 'margin:var(--space-1) 0 0;color:var(--secondary);';
  programLine.textContent = `${sem.faculty} / ${sem.program}`;

  headText.append(titleRow, programLine);
  headRow.append(logo, headText);

  const description = document.createElement('p');
  description.className = 'body-md';
  description.style.cssText = 'margin:0;color:var(--on-surface-variant);flex:1;';
  description.textContent = sem.description;

  const metaBox = document.createElement('div');
  metaBox.style.cssText =
    'display:flex;justify-content:space-between;align-items:center;gap:var(--space-3);' +
    'background-color:var(--surface-container-low);border-radius:var(--radius-md);padding:var(--space-3);';
  const leader = document.createElement('span');
  leader.className = 'body-md';
  leader.style.minWidth = '0';
  const leaderLabel = document.createElement('strong');
  leaderLabel.style.color = 'var(--secondary)';
  leaderLabel.textContent = 'Líder: ';
  leader.append(leaderLabel, document.createTextNode(sem.leader));
  const count = document.createElement('span');
  count.className = 'body-md';
  count.style.cssText = 'display:inline-flex;align-items:center;gap:var(--space-1);flex-shrink:0;';
  const countIcon = document.createElement('span');
  countIcon.className = 'material-symbols-outlined';
  countIcon.style.cssText = 'font-size:16px;color:var(--secondary);';
  countIcon.textContent = 'group';
  count.append(countIcon, document.createTextNode(String(sem.memberCount)));
  metaBox.append(leader, count);

  const actionsRow = document.createElement('div');
  actionsRow.style.cssText = 'display:flex;gap:var(--space-2);margin-top:auto;';

  const viewButton = document.createElement('button');
  viewButton.type = 'button';
  viewButton.className = 'btn btn-outline label-caps';
  viewButton.style.flex = '1';
  viewButton.textContent = 'Ver Detalle';
  viewButton.addEventListener('click', () => { location.href = detailHref(sem.id); });

  const joinButton = document.createElement('button');
  joinButton.type = 'button';
  joinButton.className = 'btn btn-primary label-caps';
  joinButton.style.flex = '1';
  joinButton.textContent = 'Solicitar Vinculación';
  joinButton.addEventListener('click', () => { location.href = detailHref(sem.id, 'vinculacion'); });

  actionsRow.append(viewButton, joinButton);
  card.append(headRow, description, metaBox, actionsRow);
  return card;
}

function render() {
  const list = filteredSemilleros();
  grid.innerHTML = '';
  list.forEach((sem) => grid.appendChild(buildCard(sem)));
  resultsCount.textContent = `Mostrando ${list.length} de ${semillerosList.length}`;
  emptyState.hidden = list.length !== 0;
}

searchInput.addEventListener('input', (event) => {
  state.query = event.target.value;
  render();
});
searchBtn.addEventListener('click', () => {
  state.query = searchInput.value;
  render();
});

[filterFaculty, filterProgram, filterArea].forEach((select) => {
  select.addEventListener('change', () => {
    state.faculty = filterFaculty.value;
    state.program = filterProgram.value;
    state.area = filterArea.value;
    render();
  });
});

clearFiltersBtn.addEventListener('click', () => {
  state.query = '';
  state.faculty = 'all';
  state.program = 'all';
  state.area = 'all';
  searchInput.value = '';
  filterFaculty.value = 'all';
  filterProgram.value = 'all';
  filterArea.value = 'all';
  render();
});

render();
