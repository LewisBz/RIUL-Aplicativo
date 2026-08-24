import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { GAMIFICATION, BADGES, RANKING, GAMIFICATION_ACHIEVEMENTS } from './demo-data.js';

await initLayout();
const user = await requireAuth();
if (!user) throw new Error('Sesión requerida');

const percent = Math.min(100, Math.round((GAMIFICATION.xp / GAMIFICATION.nextLevelXp) * 100));
document.getElementById('headerXp').textContent = `${GAMIFICATION.xp} XP`;
document.getElementById('gamLevel').textContent = `Nivel ${GAMIFICATION.level}`;
document.getElementById('gamXp').textContent = `${GAMIFICATION.xp} / ${GAMIFICATION.nextLevelXp} XP`;
document.getElementById('xpFill').style.width = `${percent}%`;
document.getElementById('gamStars').textContent = `${GAMIFICATION.stars} / ${GAMIFICATION.totalStars}`;
document.getElementById('gamAchievements').textContent = GAMIFICATION_ACHIEVEMENTS.filter(({ status }) => status === 'Validado').length;
document.getElementById('gamPosition').textContent = RANKING.find(({ isCurrentUser }) => isCurrentUser)?.position ?? '—';

const badgeGrid = document.getElementById('badgeGrid');
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
  row.innerHTML = `<strong class="ranking-position">${entry.position}</strong><span class="ranking-avatar">${entry.name.split(' ').map((part) => part[0]).join('').slice(0, 2)}</span><span class="ranking-person"><strong></strong><small></small></span><span class="numeric-xp"></span>`;
  row.querySelector('.ranking-person strong').textContent = entry.name;
  row.querySelector('.ranking-person small').textContent = entry.role;
  row.querySelector('.numeric-xp').textContent = `${entry.xp} XP`;
  rankingList.appendChild(row);
});

const achievementList = document.getElementById('achievementList');
GAMIFICATION_ACHIEVEMENTS.forEach((achievement) => {
  const item = document.createElement('li');
  item.className = `achievement-item${achievement.status === 'Validado' ? ' is-validated' : ''}`;
  item.innerHTML = `<span class="material-symbols-outlined achievement-icon">${achievement.icon}</span><div class="achievement-content"><strong></strong><span class="achievement-description"></span><small></small></div><span class="xp-badge"></span>`;
  item.querySelector('strong').textContent = achievement.title;
  item.querySelector('.achievement-description').textContent = achievement.description;
  item.querySelector('small').textContent = achievement.status;
  item.querySelector('.xp-badge').textContent = `+${achievement.xp} XP`;
  achievementList.appendChild(item);
});