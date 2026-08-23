import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { SEMILLEROS, memberTone } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const state = { query: '', faculty: 'all', program: 'all', area: 'all' };

const grid = document.getElementById('semillerosGrid');
const resultsCount = document.getElementById('resultsCount');
const emptyState = document.getElementById('emptyState');
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
  [...new Set(values)].sort((a, b) => a.localeCompare(b, 'es')).forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

fillSelect(filterFaculty, SEMILLEROS.map((s) => s.faculty));
fillSelect(filterProgram, SEMILLEROS.map((s) => s.program));
fillSelect(filterArea, SEMILLEROS.map((s) => s.area));

function filteredSemilleros() {
  const query = normalize(state.query.trim());
  return SEMILLEROS.filter((s) => {
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
  logo.innerHTML = `<span class="material-symbols-outlined" style="font-size:32px;color:var(--primary);">${sem.icon}</span>`;

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
  metaBox.innerHTML =
    `<span class="body-md" style="min-width:0;"><strong style="color:var(--secondary);">Líder:</strong> ${sem.leader}</span>` +
    `<span class="body-md" style="display:inline-flex;align-items:center;gap:var(--space-1);flex-shrink:0;">` +
    `<span class="material-symbols-outlined" style="font-size:16px;color:var(--secondary);">group</span>${sem.memberCount}</span>`;

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
  resultsCount.textContent = `Mostrando ${list.length} de ${SEMILLEROS.length}`;
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
