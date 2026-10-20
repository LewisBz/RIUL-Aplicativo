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

function fillSelect(select, values, placeholder) {
  if (!select) return;
  const current = select.value || 'all';
  select.innerHTML = '';
  const allOption = document.createElement('option');
  allOption.value = 'all';
  allOption.textContent = placeholder;
  select.appendChild(allOption);
  [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es')).forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
  select.value = [...select.options].some((option) => option.value === current) ? current : 'all';
}

let catalog = [];
try {
  const catalogResponse = await fetch(`${API_BASE}/api/auth/catalog`);
  if (catalogResponse.ok) catalog = (await catalogResponse.json()).faculties || [];
} catch (error) {
  console.error('No se pudo cargar el catálogo.', error);
}

function programNames() {
  if (state.faculty === 'all') {
    return catalog.length
      ? catalog.flatMap((faculty) => (faculty.programs || []).map((program) => program.name))
      : semillerosList.map((item) => item.program);
  }
  const faculty = catalog.find((item) => item.name === state.faculty);
  if (faculty) return (faculty.programs || []).map((program) => program.name);
  return semillerosList.filter((item) => item.faculty === state.faculty).map((item) => item.program);
}

function refillFilters() {
  fillSelect(
    filterFaculty,
    catalog.length ? catalog.map((faculty) => faculty.name) : semillerosList.map((item) => item.faculty),
    'Todas las facultades',
  );
  fillSelect(filterProgram, programNames(), 'Todos los programas');
  fillSelect(filterArea, semillerosList.map((item) => item.area), 'Todas las áreas');
}

refillFilters();

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

function detailHref(id) {
  return `/semilleros?id=${encodeURIComponent(id)}`;
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[character]));
}

async function showDetail(id, anchor) {
  const panel = document.getElementById('semilleroDetail');
  const response = await fetch(`${API_BASE}/api/semilleros/${encodeURIComponent(id)}`);
  const data = await response.json();
  if (!response.ok || !data.semillero) {
    panel.innerHTML = '<p class="body-lg">No fue posible cargar este semillero.</p>';
    return;
  }
  const record = data.semillero;
  const members = (record.members || []).map((member) => `<li class="body-md">${escapeHtml(member.full_name)} · ${escapeHtml(member.role_in_semillero)}</li>`).join('');
  panel.innerHTML = `
    <p class="label-caps" style="margin:0;color:var(--secondary);">${escapeHtml(record.faculty)} / ${escapeHtml(record.program)}</p>
    <h2 class="headline-md" style="margin:0;">${escapeHtml(record.name)}</h2>
    <p class="body-md" style="margin:0;">${escapeHtml(record.description || '')}</p>
    <p class="body-md" style="margin:0;"><strong>Líder:</strong> ${escapeHtml(record.leader)}</p>
    <h3 class="card-label">Misión</h3>
    <p class="body-md" style="margin:0;">${escapeHtml(record.mission || 'Sin misión registrada.')}</p>
    <h3 class="card-label">Visión</h3>
    <p class="body-md" style="margin:0;">${escapeHtml(record.vision || 'Sin visión registrada.')}</p>
    <h3 class="card-label">Integrantes</h3>
    <ul style="margin:0;padding-left:1.2rem;display:flex;flex-direction:column;gap:var(--space-2);">${members || '<li>Sin integrantes activos.</li>'}</ul>
    <form id="linkForm" style="display:flex;flex-direction:column;gap:var(--space-3);">
      <label class="label-caps" for="motivationInput">Solicitar vinculación</label>
      <textarea class="input-base" id="motivationInput" rows="4" required placeholder="Por qué quieres unirte"></textarea>
      <button class="btn btn-primary label-caps" type="submit">Enviar solicitud</button>
      <p class="body-md" id="linkNote" style="margin:0;"></p>
    </form>`;
  const url = detailHref(id) + (anchor ? `#${anchor}` : '');
  history.replaceState(null, '', url);
  document.getElementById('linkForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const token = localStorage.getItem('riul_token');
    const join = await fetch(`${API_BASE}/api/semilleros/${encodeURIComponent(id)}/join`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ motivation: document.getElementById('motivationInput').value }),
    });
    const body = await join.json().catch(() => ({}));
    document.getElementById('linkNote').textContent = join.ok
      ? 'Solicitud enviada. Queda pendiente de aprobación del líder.'
      : (body.message || 'No se pudo enviar la solicitud.');
  });
  if (anchor) document.getElementById('linkForm')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
  titleLink.addEventListener('click', (event) => {
    event.preventDefault();
    showDetail(sem.id);
  });
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
  viewButton.addEventListener('click', () => { showDetail(sem.id); });

  const joinButton = document.createElement('button');
  joinButton.type = 'button';
  joinButton.className = 'btn btn-primary label-caps';
  joinButton.style.flex = '1';
  joinButton.textContent = 'Solicitar Vinculación';
  joinButton.addEventListener('click', () => { showDetail(sem.id, 'vinculacion'); });

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

function showFiltered() {
  const list = filteredSemilleros();
  render();
  const panel = document.getElementById('semilleroDetail');
  if (list.length === 1) {
    showDetail(list[0].id);
    return;
  }
  if (!list.length) {
    panel.innerHTML = '<p class="body-lg" style="margin:0;">Ningún semillero coincide con ese filtro.</p>';
    return;
  }
  if (state.faculty === 'all' && state.program === 'all' && state.area === 'all' && !state.query) return;
  panel.innerHTML = `<p class="body-md" style="margin:0;">${list.length} semilleros con ese filtro. Elige uno para ver misión, integrantes y vinculación.</p><ul style="margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:var(--space-3);">${list.map((item) => `<li><button class="btn btn-outline label-caps" type="button" data-open="${item.id}">${item.name}</button><p class="body-md" style="margin:var(--space-2) 0 0;">${item.faculty} · ${item.program} · ${item.area}</p></li>`).join('')}</ul>`;
  panel.querySelectorAll('[data-open]').forEach((button) => {
    button.addEventListener('click', () => showDetail(button.dataset.open));
  });
}

filterFaculty.addEventListener('change', () => {
  state.faculty = filterFaculty.value;
  state.program = 'all';
  fillSelect(filterProgram, programNames(), 'Todos los programas');
  showFiltered();
});
filterProgram.addEventListener('change', () => {
  state.program = filterProgram.value;
  showFiltered();
});
filterArea.addEventListener('change', () => {
  state.area = filterArea.value;
  showFiltered();
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
  fillSelect(filterProgram, programNames(), 'Todos los programas');
  render();
});

render();
const requested = new URLSearchParams(location.search).get('id');
if (requested) showDetail(requested, location.hash.replace('#', ''));
