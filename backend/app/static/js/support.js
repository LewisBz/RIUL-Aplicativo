import {
  TICKET_CATEGORIES,
  TICKET_STATUS_LABELS,
  adminRequest,
  escapeHtml,
  guardAdmin,
  initials,
  showState,
} from './admin-shared.js';
import { openFormDialog } from './forms.js';

const content = document.getElementById('adminContent');
let tickets = [];

const QUICK_ACTIONS = [
  { icon: 'group', title: 'Gestionar usuarios', text: 'Aprobar cuentas y revisar roles.', href: '/admin#users', tone: '' },
  { icon: 'assessment', title: 'Generar reportes', text: 'Analítica y exportación de datos.', href: '/admin-analytics', tone: 'teal' },
  { icon: 'verified', title: 'Validar logros', text: 'Aprobar hitos gamificados.', href: '/admin#achievements', tone: 'gold' },
  { icon: 'api', title: 'Documentación API', text: 'Contratos y endpoints de RIUL.', href: '/docs', tone: 'neutral' },
];

const DOCS = [
  { title: 'Documentación de la API', text: 'Contratos REST y ejemplos.', href: '/docs' },
  { title: 'Política de privacidad', text: 'Cumplimiento y tratamiento de datos.', href: '/privacidad' },
  { title: 'Términos de uso', text: 'Reglas de la comunidad académica.', href: '/terminos' },
];

const STATUS_CLASS = { open: 'ticket-open', in_progress: 'ticket-progress', resolved: 'ticket-resolved' };

function quickActions() {
  return `<section><h2 class="title-lg support-heading">Acciones rápidas</h2><div class="support-actions">${QUICK_ACTIONS.map((a) => `<a class="glass-card support-action ${a.tone}" href="${a.href}" data-search="${escapeHtml((a.title + ' ' + a.text).toLowerCase())}"><span class="support-action-icon material-symbols-outlined">${a.icon}</span><strong>${a.title}</strong><span>${a.text}</span></a>`).join('')}</div></section>`;
}

function ticketRows(items) {
  if (!items.length) return '<tr><td colspan="5">No hay tickets de soporte.</td></tr>';
  return items.map((ticket) => `<tr>
    <td><span class="ticket-user"><span class="ticket-avatar">${escapeHtml(initials(ticket.user.full_name || ticket.user.email))}</span><span>${escapeHtml(ticket.user.full_name || ticket.user.email)}</span></span></td>
    <td>${escapeHtml(ticket.user.faculty || '—')}</td>
    <td>${escapeHtml(TICKET_CATEGORIES[ticket.category] || ticket.category)}<br><small class="ticket-subject">${escapeHtml(ticket.subject)}</small></td>
    <td><span class="status-pill ${STATUS_CLASS[ticket.status] || ''}">${escapeHtml(TICKET_STATUS_LABELS[ticket.status] || ticket.status)}</span></td>
    <td><button class="btn btn-outline label-caps" type="button" data-ticket-id="${ticket.id}">Responder</button></td>
  </tr>`).join('');
}

function render() {
  content.innerHTML = `
    <section class="glass-card support-hero"><div><h1 class="headline-lg">Centro de soporte y ayuda</h1><p class="body-lg page-subtitle">Gestiona las consultas de los usuarios, accede a la documentación y monitorea los tickets abiertos del ecosistema RIUL.</p></div>
      <label class="support-search"><span class="material-symbols-outlined">search</span><input class="input-base" id="helpSearch" type="search" placeholder="Buscar artículos de ayuda..." aria-label="Buscar artículos de ayuda"></label></section>
    ${quickActions()}
    <div class="support-columns">
      <section class="glass-card admin-panel"><div class="section-heading"><h2 class="headline-md">Tickets recientes</h2><label class="body-md">Estado <select class="input-base ticket-filter" id="ticketFilter"><option value="">Todos</option>${Object.entries(TICKET_STATUS_LABELS).map(([v, l]) => `<option value="${v}">${l}</option>`).join('')}</select></label></div>
        <div class="table-scroll"><table class="table-data"><thead><tr><th>Usuario</th><th>Facultad</th><th>Categoría</th><th>Estado</th><th>Acción</th></tr></thead><tbody id="ticketsBody">${ticketRows(tickets)}</tbody></table></div></section>
      <div class="support-side">
        <section class="glass-card admin-panel" id="docsPanel"><h2 class="headline-md">Documentación</h2><ul class="doc-list">${DOCS.map((d) => `<li data-search="${escapeHtml((d.title + ' ' + d.text).toLowerCase())}"><a href="${d.href}"><strong>${d.title}</strong><span>${d.text}</span></a></li>`).join('')}</ul></section>
        <section class="glass-card admin-panel"><h2 class="headline-md">¿Necesitas ayuda escalada?</h2><p class="body-md">Contacta al equipo de desarrollo ante fallas críticas o solicitudes de configuración.</p><a class="btn btn-primary btn-block label-caps" href="mailto:investigaciones@unilibre.edu.co?subject=Soporte%20RIUL">Contactar soporte técnico</a></section>
      </div>
    </div>`;
}

async function loadTickets(status = '') {
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  tickets = (await adminRequest(`/api/admin/support/tickets${query}`)).items;
  const body = document.getElementById('ticketsBody');
  if (body) body.innerHTML = ticketRows(tickets);
}

async function reply(ticketId) {
  const ticket = tickets.find((t) => t.id === ticketId);
  if (!ticket) return;
  const saved = await openFormDialog({
    title: `Responder: ${ticket.subject}`,
    submitLabel: 'Enviar respuesta',
    fields: [
      { name: 'message_preview', label: 'Mensaje del usuario', type: 'textarea', value: ticket.message },
      { name: 'reply', label: 'Respuesta', type: 'textarea', value: ticket.admin_reply || '', required: true },
      {
        name: 'status',
        label: 'Estado',
        type: 'select',
        options: Object.entries(TICKET_STATUS_LABELS).map(([value, label]) => ({ value, label })),
        value: ticket.status === 'open' ? 'in_progress' : ticket.status,
      },
    ],
    onSubmit: ({ reply: text, status }) =>
      adminRequest(`/api/admin/support/tickets/${ticketId}`, { method: 'PATCH', body: { reply: text, status } }),
  });
  if (saved) await loadTickets(document.getElementById('ticketFilter').value);
}

function wire() {
  document.getElementById('ticketsBody').addEventListener('click', (event) => {
    const button = event.target.closest('[data-ticket-id]');
    if (button) reply(Number(button.dataset.ticketId));
  });
  document.getElementById('ticketFilter').addEventListener('change', async (event) => {
    try { await loadTickets(event.target.value); } catch (error) { alert(error.message); }
  });
  document.getElementById('helpSearch').addEventListener('input', (event) => {
    const term = event.target.value.trim().toLowerCase();
    document.querySelectorAll('[data-search]').forEach((el) => {
      el.hidden = Boolean(term) && !el.dataset.search.includes(term);
    });
  });
}

async function init() {
  const user = await guardAdmin(content, 'support');
  if (!user) return;
  try {
    await loadTickets();
    render();
    wire();
  } catch (error) {
    showState(content, 'No se pudo cargar el soporte', error.message);
  }
}

init();
