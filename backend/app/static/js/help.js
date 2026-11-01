import { requireAuth } from './session.js';
import { initLayout } from './layout.js';
import { api } from './api.js';
import { TICKET_CATEGORIES, TICKET_STATUS_LABELS, escapeHtml } from './admin-shared.js';

const form = document.getElementById('ticketForm');
const list = document.getElementById('ticketList');
const errorEl = document.getElementById('ticketError');
const submit = document.getElementById('ticketSubmit');

document.getElementById('ticketCategory').innerHTML = Object.entries(TICKET_CATEGORIES)
  .map(([value, label]) => `<option value="${value}">${label}</option>`)
  .join('');

const STATUS_CLASS = { open: 'ticket-open', in_progress: 'ticket-progress', resolved: 'ticket-resolved' };

function dateLabel(iso) {
  return iso ? new Date(iso).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
}

function ticketCard(ticket) {
  const reply = ticket.admin_reply
    ? `<div class="ticket-reply"><strong>Respuesta de soporte</strong><p>${escapeHtml(ticket.admin_reply)}</p></div>`
    : '<p class="body-md ticket-waiting">Aún sin respuesta.</p>';
  return `<article class="ticket-card"><header><strong>${escapeHtml(ticket.subject)}</strong><span class="status-pill ${STATUS_CLASS[ticket.status] || ''}">${escapeHtml(TICKET_STATUS_LABELS[ticket.status] || ticket.status)}</span></header><p class="body-md ticket-meta">${escapeHtml(TICKET_CATEGORIES[ticket.category] || ticket.category)} · ${dateLabel(ticket.created_at)}</p><p class="body-md">${escapeHtml(ticket.message)}</p>${reply}</article>`;
}

async function loadTickets() {
  const { items } = await api('/api/support/tickets');
  list.innerHTML = items.length
    ? items.map(ticketCard).join('')
    : '<p class="body-md">Todavía no has enviado tickets.</p>';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  errorEl.textContent = '';
  const body = Object.fromEntries(new FormData(form).entries());
  if (body.subject.trim().length < 3) { errorEl.textContent = 'El asunto debe tener al menos 3 caracteres.'; return; }
  if (body.message.trim().length < 10) { errorEl.textContent = 'El mensaje debe tener al menos 10 caracteres.'; return; }
  submit.disabled = true;
  try {
    await api('/api/support/tickets', { method: 'POST', body });
    form.reset();
    await loadTickets();
  } catch (error) {
    errorEl.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

async function init() {
  const user = await requireAuth();
  if (!user) return;
  await initLayout();
  try {
    await loadTickets();
  } catch (error) {
    list.innerHTML = `<p class="body-md" style="color:var(--error);">${escapeHtml(error.message)}</p>`;
  }
}

init();
