import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api } from './api.js';
import { toGamification, toRankingEntry } from './adapters.js';
import { openFormDialog } from './forms.js';
import { skeletonFor } from './skeleton.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const clearSkeleton = skeletonFor([
  { id: 'badgeGrid', variant: 'tile', count: 6 },
  { id: 'rankingList', variant: 'row', count: 5 },
  { id: 'achievementList', variant: 'row', count: 4 },
]);
let GAMIFICATION;
let RANKING = [];
try {
  [GAMIFICATION, RANKING] = await Promise.all([
    api('/api/gamification/me').then((data) => toGamification(data.gamification)),
    api('/api/gamification/ranking').then((data) => data.items.map(toRankingEntry)),
  ]);
  clearSkeleton();
} catch (error) {
  document.querySelector('main').innerHTML = '<div class="detail-empty"><strong></strong></div>';
  document.querySelector('main strong').textContent = error.message;
  throw error;
}
const BADGES = GAMIFICATION.badges;
const ACHIEVEMENTS = GAMIFICATION.achievements;

const percent = Math.min(100, Math.round((GAMIFICATION.xp / GAMIFICATION.nextLevelXp) * 100));
document.getElementById('headerXp').textContent = `${GAMIFICATION.xp} XP`;
document.getElementById('gamLevel').textContent = `Nivel ${GAMIFICATION.level}`;
document.getElementById('gamXp').textContent = `${GAMIFICATION.xp} / ${GAMIFICATION.nextLevelXp} XP`;
document.getElementById('xpFill').style.width = `${percent}%`;
document.getElementById('gamStars').textContent = `${GAMIFICATION.stars} / ${GAMIFICATION.totalStars}`;
document.getElementById('gamAchievements').textContent = ACHIEVEMENTS.filter(({ statusCode }) => statusCode === 'approved').length;
document.getElementById('gamPosition').textContent = RANKING.find(({ isCurrentUser }) => isCurrentUser)?.position ?? '—';

const badgeGrid = document.getElementById('badgeGrid');
if (!BADGES.length) {
  badgeGrid.textContent = 'Aún no tienes insignias. Valida logros para obtenerlas.';
}
BADGES.forEach((badge) => {
  const item = document.createElement('div');
  item.className = `insignia${badge.highlighted ? '' : ' locked'}`;
  item.title = badge.title;
  const icon = document.createElement('span');
  icon.className = 'material-symbols-outlined';
  icon.textContent = badge.icon;
  const title = document.createElement('span');
  title.className = 'badge-title';
  title.textContent = badge.title;
  item.append(icon, title);
  badgeGrid.appendChild(item);
});

const rankingList = document.getElementById('rankingList');
RANKING.forEach((entry) => {
  const row = document.createElement('div');
  row.className = `ranking-row${entry.isCurrentUser ? ' ranking-self' : ''}`;
  row.innerHTML = '<strong class="ranking-position"></strong><span class="ranking-avatar"></span><span class="ranking-person"><strong></strong><small></small></span><span class="numeric-xp"></span>';
  row.querySelector('.ranking-position').textContent = entry.position;
  row.querySelector('.ranking-avatar').textContent = entry.name.split(' ').map((part) => part[0]).join('').slice(0, 2);
  row.querySelector('.ranking-person strong').textContent = entry.name;
  row.querySelector('.ranking-person small').textContent = entry.role;
  row.querySelector('.numeric-xp').textContent = `${entry.xp} XP`;
  rankingList.appendChild(row);
});

const achievementList = document.getElementById('achievementList');
if (!ACHIEVEMENTS.length) {
  achievementList.innerHTML = '<li class="body-md">Todavía no registras logros.</li>';
}
ACHIEVEMENTS.forEach((achievement) => {
  const item = document.createElement('li');
  item.className = `achievement-item${achievement.statusCode === 'approved' ? ' is-validated' : ''}`;
  item.innerHTML = '<span class="material-symbols-outlined achievement-icon"></span><div class="achievement-content"><strong></strong><span class="achievement-description"></span><small></small></div><span class="xp-badge"></span>';
  item.querySelector('.achievement-icon').textContent = achievement.icon;
  item.querySelector('strong').textContent = achievement.title;
  item.querySelector('.achievement-description').textContent = achievement.description;
  const origin = achievement.origin ? ` · ${achievement.origin.kindLabel}: ${achievement.origin.label ?? ''}` : '';
  const evidence = achievement.evidenceCount
    ? ` · ${achievement.evidenceCount} ${achievement.evidenceCount === 1 ? 'evidencia' : 'evidencias'}`
    : '';
  item.querySelector('small').textContent = `${achievement.status}${origin}${evidence}`;
  if (achievement.statusCode !== 'rejected') {
    const attach = document.createElement('button');
    attach.type = 'button';
    attach.className = 'btn btn-outline label-caps';
    attach.textContent = 'Adjuntar evidencia';
    attach.setAttribute('aria-label', `Adjuntar evidencia a ${achievement.title}`);
    attach.addEventListener('click', () => attachEvidence(achievement));
    item.querySelector('.achievement-content').appendChild(attach);
  }
  item.querySelector('.xp-badge').textContent = `+${achievement.xp} XP`;
  achievementList.appendChild(item);
});

const EVIDENCE_ACCEPT = '.pdf,.png,.jpg,.jpeg,.doc,.docx';

function uploadEvidence(achievementId, file) {
  const body = new FormData();
  body.append('file', file);
  return api(`/api/gamification/achievements/${achievementId}/evidences`, { method: 'POST', body });
}

async function attachEvidence(achievement) {
  const done = await openFormDialog({
    title: `Evidencia: ${achievement.title}`,
    submitLabel: 'Subir evidencia',
    fields: [{ name: 'file', label: 'Archivo (PDF, imagen o documento)', type: 'file', accept: EVIDENCE_ACCEPT, required: true }],
    onSubmit: ({ file }) => uploadEvidence(achievement.id, file),
  });
  if (done) location.href = '/gamification';
}

// Cada logro nace de exactamente un origen que el usuario puede acreditar.
const ORIGIN_KINDS = [
  { value: 'event', label: 'Evento en el que participé' },
  { value: 'project', label: 'Proyecto de investigación' },
  { value: 'product', label: 'Producto de investigación' },
  { value: 'semillero', label: 'Semillero' },
  { value: 'post', label: 'Publicación propia' },
];

async function loadOrigins(kind) {
  if (kind === 'event') {
    const { items } = await api('/api/events');
    return items
      .filter((item) => item.kind === 'event' && item.participation === 'registered')
      .map((item) => ({ value: item.slug, label: item.title }));
  }
  if (kind === 'post') {
    const { items } = await api('/api/posts');
    return items
      .filter((item) => item.author?.id === user.id)
      .map((item) => ({ value: item.id, label: (item.content || `Publicación #${item.id}`).slice(0, 70) }));
  }
  const { projects, products, semilleros } = await api('/api/profile');
  if (kind === 'project') return projects.map((item) => ({ value: item.slug, label: item.title }));
  if (kind === 'product') return products.map((item) => ({ value: item.id, label: item.name }));
  return semilleros.map((item) => ({ value: item.slug, label: item.name }));
}

async function registerAchievement() {
  const step = await openFormDialog({
    title: 'Registrar logro',
    submitLabel: 'Continuar',
    fields: [{ name: 'kind', label: '¿De dónde proviene el logro?', type: 'select', options: ORIGIN_KINDS, required: true }],
    onSubmit: async ({ kind }) => ({ kind, options: await loadOrigins(kind) }),
  });
  if (!step) return;
  if (!step.options.length) {
    await openFormDialog({
      title: 'Sin orígenes disponibles',
      submitLabel: 'Entendido',
      fields: [],
      onSubmit: async () => true,
    });
    return;
  }
  const created = await openFormDialog({
    title: 'Registrar logro',
    submitLabel: 'Enviar a validación',
    fields: [
      { name: 'origin', label: ORIGIN_KINDS.find(({ value }) => value === step.kind).label, type: 'select', options: step.options, required: true },
      { name: 'title', label: 'Título', placeholder: 'Ej. Ponencia en congreso nacional' },
      { name: 'description', label: 'Descripción', type: 'textarea' },
      { name: 'achieved_on', label: 'Fecha', type: 'date' },
      { name: 'file', label: 'Evidencia (opcional)', type: 'file', accept: EVIDENCE_ACCEPT },
    ],
    onSubmit: async ({ origin, file, ...rest }) => {
      const body = { [step.kind]: origin, ...Object.fromEntries(Object.entries(rest).filter(([, value]) => value !== '')) };
      const { achievement } = await api('/api/gamification/achievements', { method: 'POST', body });
      if (file && file.name) await uploadEvidence(achievement.id, file);
      return achievement;
    },
  });
  if (created) location.href = '/gamification';
}
document.querySelector('.page-heading').insertAdjacentHTML('beforeend', '<button class="btn btn-primary label-caps" type="button" id="newAchievementBtn"><span class="material-symbols-outlined">add</span>Registrar logro</button>');
document.getElementById('newAchievementBtn').addEventListener('click', registerAchievement);
if (new URLSearchParams(location.search).get('new')) registerAchievement();
