/* Iconos SVG en línea, sin dependencias ni fuentes remotas.
   Contrato: cualquier elemento con la clase .material-symbols-outlined cuyo texto
   sea un nombre conocido se convierte en <svg>. Observa el DOM para cubrir
   el contenido que los módulos de cada página inyectan después de cargar.
   Rejilla 24x24, trazo 1.75, extremos redondeados. Prefijo "f:" = relleno. */

const ICONS = {
  account_balance: 'M3 10 12 4l9 6M5 10v8M9 10v8M15 10v8M19 10v8M3 21h18',
  account_tree: 'M4 4h6v5H4zM14 4h6v5h-6zM14 15h6v5h-6zM10 6.5h4M12 6.5V17.5h2',
  add: 'M12 5v14M5 12h14',
  api: 'M4 9h4v6H4zM16 9h4v6h-4zM8 12h8M12 6v12',
  calendar_month: 'M4 6h16v14H4zM4 10h16M8 3v4M16 3v4M8 14h2M14 14h2M8 17h2',
  chat_bubble: 'M4 5h16v11H9l-5 4z',
  cloud_upload: 'M7 18a4 4 0 01-.6-7.9A6 6 0 0118 9.5 4.3 4.3 0 0117 18M12 12v7M9 14.5l3-3 3 3',
  download: 'M12 4v11M7 11l5 5 5-5M5 20h14',
  mic: 'M9 4h6v8a3 3 0 01-6 0zM6 11a6 6 0 0012 0M12 17v4M9 21h6',
  support_agent: 'M5 13v-2a7 7 0 0114 0v2M4 13h3v5H4zM17 13h3v5h-3zM17 18c0 2-2 3-5 3',
  trending_up: 'M3 17l6-6 4 4 8-8M15 7h6v6',
  verified: 'M12 3l2.5 2 3.2-.3.9 3.1 2.7 1.8-1.3 3 1.3 3-2.7 1.8-.9 3.1-3.2-.3L12 21l-2.5-2-3.2.3-.9-3.1L2.7 14.4 4 11.4 2.7 8.4l2.7-1.8.9-3.1 3.2.3zM8.5 12.5l2.5 2.5 4.5-5',
  arrow_back: 'M19 12H5M11 6l-6 6 6 6',
  arrow_drop_down: 'M7 10l5 5 5-5',
  arrow_forward: 'M5 12h14M13 6l6 6-6 6',
  arrow_forward_ios: 'M9 5l7 7-7 7',
  article: 'M5 4h14v16H5zM8 8h8M8 12h8M8 16h5',
  assessment: 'M4 4h16v16H4zM8 16v-4M12 16V8M16 16v-6',
  biotech: 'M8 3c0 5 8 5 8 9s-8 4-8 9M16 3c0 5-8 5-8 9s8 4 8 9M9 7h6M9 17h6',
  bolt: 'M13 3 5 14h6l-1 7 8-11h-6z',
  chat_bubble_outline: 'M4 5h16v11H9l-5 4z',
  check_circle: 'M12 3a9 9 0 100 18 9 9 0 000-18zM8 12.5l3 3 5-6',
  chevron_left: 'M15 5l-7 7 7 7',
  chevron_right: 'M9 5l7 7-7 7',
  close: 'M6 6l12 12M18 6 6 18',
  cloud_off: 'M3 3l18 18M7 18h10a4 4 0 001.5-7.7M9.5 6.2A6 6 0 0117.7 9M5.5 10.5A4.5 4.5 0 007 18',
  dashboard: 'M4 4h7v9H4zM13 4h7v5h-7zM13 11h7v9h-7zM4 15h7v5H4z',
  description: 'M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6',
  done: 'M5 12.5l4.5 4.5L19 7',
  edit: 'M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4',
  emoji_events: 'M8 4h8v5a4 4 0 01-8 0zM8 6H4v1a3 3 0 003 3M16 6h4v1a3 3 0 01-3 3M12 13v4M8 20h8M10 17h4',
  error: 'M12 3a9 9 0 100 18 9 9 0 000-18zM12 8v5M12 16v.5',
  event: 'M4 6h16v14H4zM4 10h16M8 3v4M16 3v4',
  event_busy: 'M4 6h16v14H4zM4 10h16M8 3v4M16 3v4M10 13l4 4M14 13l-4 4',
  expand_more: 'M6 9l6 6 6-6',
  favorite_border: 'M12 20s-7-4.5-7-10a4 4 0 017-2.5A4 4 0 0119 10c0 5.5-7 10-7 10z',
  filter_list: 'M4 7h16M7 12h10M10 17h4',
  folder: 'M3 6h6l2 2h10v11H3z',
  folder_off: 'M3 3l18 18M3 6h6l2 2h8M21 11v8H5',
  folder_open: 'M3 7V6h6l2 2h8v3M3 19l2-8h17l-2 8z',
  forum: 'M4 4h12v8H8l-4 3zM10 14h6l4 3V8h-3',
  forward_to_inbox: 'M3 6h18v7M3 6l9 7 3-2.5M3 6v13h9M17 18h5M19.5 15.5 22 18l-2.5 2.5',
  group: 'M9 11a3 3 0 100-6 3 3 0 000 6zM3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M16 5.5a3 3 0 010 5.5M18 14.5c1.8.8 3 2.6 3 5.5',
  groups: 'M9 11a3 3 0 100-6 3 3 0 000 6zM3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M16 5.5a3 3 0 010 5.5M18 14.5c1.8.8 3 2.6 3 5.5',
  handshake: 'M2 11l5-4 4 1 3-1 5 4M2 11l7 7 2-1M22 11l-7 7-2-1-2 2-2-2',
  hourglass_empty: 'M6 3h12M6 21h12M7 3c0 5 5 6 5 9s-5 4-5 9M17 3c0 5-5 6-5 9s5 4 5 9',
  image: 'M4 5h16v14H4zM4 16l5-5 4 4 3-3 4 4M9 9.5h.01',
  info: 'M12 3a9 9 0 100 18 9 9 0 000-18zM12 11v5M12 8h.01',
  insights: 'M3 17l5-5 4 4 8-9M15 7h5v5',
  location_on: 'M12 21s6-5.5 6-11a6 6 0 10-12 0c0 5.5 6 11 6 11zM12 12a2 2 0 100-4 2 2 0 000 4z',
  lock: 'M6 11h12v9H6zM8 11V8a4 4 0 018 0v3',
  login: 'M14 4h6v16h-6M4 12h11M11 8l4 4-4 4',
  logout: 'M10 4H4v16h6M9 12h11M16 8l4 4-4 4',
  mail: 'M3 5h18v14H3zM3 6l9 7 9-7',
  memory: 'M7 7h10v10H7zM10 10h4v4h-4zM9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4',
  menu: 'M4 7h16M4 12h16M4 17h16',
  menu_book: 'M3 5c3-1 6-1 9 1v14c-3-2-6-2-9-1zM21 5c-3-1-6-1-9 1v14c3-2 6-2 9-1z',
  military_tech: 'M12 14a5 5 0 100-10 5 5 0 000 10zM9 13.5 7 21l5-3 5 3-2-7.5',
  monitoring: 'M3 4h18v12H3zM8 20h8M12 16v4M6 12l3-3 3 2 4-4',
  more_horiz: 'f:M6 10.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM12 10.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM18 10.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3z',
  notifications: 'M6 17v-6a6 6 0 0112 0v6l2 2H4zM10 21h4',
  notifications_off: 'M3 3l18 18M6.5 7A6 6 0 0118 11v6l2 2H8M4 19l2-2v-6M10 21h4',
  person: 'M12 12a4 4 0 100-8 4 4 0 000 8zM4 21c0-4 3.5-7 8-7s8 3 8 7',
  person_add: 'M10 12a4 4 0 100-8 4 4 0 000 8zM3 21c0-4 3-7 7-7M18 8v6M15 11h6',
  progress_activity: 'M12 3a9 9 0 109 9',
  psychology: 'M9 4a3 3 0 00-3 3 3 3 0 00-2 3 3 3 0 002 3 3 3 0 003 4h1V4zM15 4a3 3 0 013 3 3 3 0 012 3 3 3 0 01-2 3 3 3 0 01-3 4h-1V4z',
  school: 'M2 9l10-5 10 5-10 5zM6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5M22 9v6',
  science: 'M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3M7.5 15h9',
  search: 'M11 18a7 7 0 100-14 7 7 0 000 14zM20 20l-4-4',
  search_insights: 'M11 18a7 7 0 100-14 7 7 0 000 14zM20 20l-4-4M8 13v-2M11 13V9M14 13v-3',
  search_off: 'M11 18a7 7 0 100-14 7 7 0 000 14zM20 20l-4-4M3 3l18 18',
  security: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z',
  send: 'M21 3 10 14M21 3l-7 18-4-7-7-4z',
  settings: 'M12 15a3 3 0 100-6 3 3 0 000 6zM12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1',
  share: 'M18 9a3 3 0 100-6 3 3 0 000 6zM6 15a3 3 0 100-6 3 3 0 000 6zM18 21a3 3 0 100-6 3 3 0 000 6zM8.7 10.6l6.6-3.2M8.7 13.4l6.6 3.2',
  star: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z',
  thumb_up: 'M7 11v9H4v-9zM7 11l4-8c2 0 3 1 3 3v3h5a2 2 0 012 2.3l-1 6A2 2 0 0118 20H7',
  upload_file: 'M6 3h8l4 4v14H6zM14 3v4h4M12 17v-6M9 13l3-3 3 3',
  verified_user: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6zM8.5 12l2.5 2.5 4.5-5',
  visibility: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 15a3 3 0 100-6 3 3 0 000 6z',
  wind_power: 'M12 12v9M10 21h4M12 12l-1-9M12 12l8 4M12 12l-8 4',
  workspace_premium: 'M12 13a5 5 0 100-10 5 5 0 000 10zM9 12.5 8 21l4-2 4 2-1-8.5',
};

const FALLBACK = 'M12 4a8 8 0 100 16 8 8 0 000-16z';
const SVG_NS = 'http://www.w3.org/2000/svg';

function build(name) {
  const raw = ICONS[name] ?? FALLBACK;
  const filled = raw.startsWith('f:');
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('class', 'icon');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('focusable', 'false');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '1.75');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  const path = document.createElementNS(SVG_NS, 'path');
  path.setAttribute('d', filled ? raw.slice(2) : raw);
  if (filled) {
    path.setAttribute('fill', 'currentColor');
    path.setAttribute('stroke', 'none');
  }
  svg.append(path);
  return svg;
}

function render(el) {
  const name = el.textContent.trim();
  if (!name) return; // ya convertido (solo contiene el SVG)
  el.dataset.icon = name;
  el.replaceChildren(build(name));
}

function scan(root) {
  if (root.nodeType !== 1) return;
  if (root.matches('.material-symbols-outlined')) render(root);
  root.querySelectorAll?.('.material-symbols-outlined').forEach(render);
}

let queued = false;
const pending = new Set();
function flush() {
  queued = false;
  pending.forEach(scan);
  pending.clear();
}

const observer = new MutationObserver((records) => {
  for (const record of records) {
    if (record.type === 'characterData') {
      const host = record.target.parentElement?.closest('.material-symbols-outlined');
      if (host) pending.add(host);
    } else {
      record.addedNodes.forEach((node) => {
        if (node.nodeType === 1) pending.add(node);
        else if (node.parentElement?.closest('.material-symbols-outlined')) {
          pending.add(node.parentElement.closest('.material-symbols-outlined'));
        }
      });
    }
  }
  if (pending.size && !queued) {
    queued = true;
    queueMicrotask(flush);
  }
});

scan(document.documentElement);
observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
