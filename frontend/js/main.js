import { initSessionUI } from './session.js';

const menuToggle = document.getElementById('menuToggle');
const menuPanel = document.getElementById('menuPanel');

menuToggle?.addEventListener('click', () => {
  if (menuPanel.hasAttribute('data-open')) {
    menuPanel.removeAttribute('data-open');
  } else {
    menuPanel.setAttribute('data-open', '');
  }
});

menuPanel?.addEventListener('click', (event) => {
  if (event.target.closest('a')) menuPanel.removeAttribute('data-open');
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') menuPanel?.removeAttribute('data-open');
});

const track = document.getElementById('eventsTrack');
const step = () => {
  const card = track?.querySelector('.carousel-card');
  return card ? card.getBoundingClientRect().width + 24 : 320;
};

document.getElementById('eventsPrev')?.addEventListener('click', () => {
  track?.scrollBy({ left: -step(), behavior: 'smooth' });
});

document.getElementById('eventsNext')?.addEventListener('click', () => {
  track?.scrollBy({ left: step(), behavior: 'smooth' });
});

await initSessionUI();
