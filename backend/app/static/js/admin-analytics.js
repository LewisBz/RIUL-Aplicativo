import { adminRequest, downloadCsv, escapeHtml, guardAdmin, showState } from './admin-shared.js';

const content = document.getElementById('adminContent');
const exportBtn = document.getElementById('exportBtn');

const MONTHS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
const number = new Intl.NumberFormat('es-CO');

function monthLabel(key) {
  return MONTHS[Number(key.split('-')[1]) - 1];
}

function metric(label, value, icon, tone = '') {
  return `<article class="admin-metric ${tone}"><span class="admin-metric-icon material-symbols-outlined">${icon}</span><div><strong>${number.format(value)}</strong><span>${label}</span></div></article>`;
}

function lineChart(production) {
  const width = 640;
  const height = 220;
  const pad = { left: 36, right: 12, top: 12, bottom: 28 };
  const max = Math.max(1, ...production.flatMap((m) => [m.publications, m.projects]));
  const x = (index) => pad.left + (index * (width - pad.left - pad.right)) / (production.length - 1);
  const y = (value) => pad.top + (1 - value / max) * (height - pad.top - pad.bottom);
  const path = (key) => production.map((m, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(m[key]).toFixed(1)}`).join(' ');
  const grid = [0, 0.5, 1].map((t) => {
    const value = Math.round(max * t);
    return `<line x1="${pad.left}" x2="${width - pad.right}" y1="${y(value)}" y2="${y(value)}" class="chart-grid"/><text x="${pad.left - 6}" y="${y(value) + 4}" text-anchor="end" class="chart-label">${value}</text>`;
  }).join('');
  const labels = production.map((m, i) => `<text x="${x(i)}" y="${height - 8}" text-anchor="middle" class="chart-label">${monthLabel(m.month)}</text>`).join('');
  return `<svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Producción mensual de publicaciones y proyectos">${grid}${labels}<path d="${path('publications')}" class="chart-line chart-line-primary"/><path d="${path('projects')}" class="chart-line chart-line-tertiary"/></svg>
    <div class="chart-legend"><span><i class="legend-dot legend-primary"></i>Publicaciones</span><span><i class="legend-dot legend-tertiary"></i>Proyectos</span></div>`;
}

function facultyBars(items) {
  if (!items.length) return '<p class="body-md admin-empty-text">Aún no hay semilleros registrados.</p>';
  const max = Math.max(...items.map((item) => item.count));
  return `<ul class="bar-list">${items.map((item) => `<li><span class="bar-label">${escapeHtml(item.faculty)}</span><span class="bar-track"><span class="bar-fill" style="width:${(item.count / max) * 100}%"></span></span><strong>${item.count}</strong></li>`).join('')}</ul>`;
}

function topTable(items) {
  if (!items.length) return '<p class="body-md admin-empty-text">Aún no hay logros validados en semilleros.</p>';
  return `<div class="table-scroll"><table class="table-data"><thead><tr><th>Semillero</th><th>Facultad</th><th>XP total</th></tr></thead><tbody>${items.map((item) => `<tr><td>${escapeHtml(item.name)}</td><td>${escapeHtml(item.faculty || 'Sin facultad')}</td><td><strong>${number.format(item.xp)}</strong></td></tr>`).join('')}</tbody></table></div>`;
}

function donut(status) {
  const total = status.total || 0;
  const part = (value) => (total ? (value / total) * 100 : 0);
  const active = part(status.active);
  const pending = part(status.pending);
  const gradient = total
    ? `conic-gradient(var(--primary) 0 ${active}%, var(--accent-gold) ${active}% ${active + pending}%, var(--outline) ${active + pending}% 100%)`
    : 'var(--surface-container-high)';
  const row = (label, value, tone) => `<li><span><i class="legend-dot ${tone}"></i>${label}</span><strong>${Math.round(part(value))}%</strong></li>`;
  return `<div class="donut" style="background:${gradient}"><div class="donut-hole"><strong>${number.format(total)}</strong><span>Total</span></div></div>
    <ul class="donut-legend">${row('Activas', status.active, 'legend-primary')}${row('Pendientes', status.pending, 'legend-gold')}${row('Rechazadas', status.rejected, 'legend-outline')}</ul>`;
}

function render(data) {
  const { totals } = data;
  content.innerHTML = `
    <div class="admin-heading"><div><p class="eyebrow">Reportes</p><h1 class="headline-lg">Analítica</h1><p class="body-lg page-subtitle">Métricas de investigación institucional de los últimos 12 meses.</p></div><span class="admin-role"><span class="material-symbols-outlined">calendar_month</span>Últimos 12 meses</span></div>
    <section class="admin-metrics">${metric('Publicaciones', totals.publications, 'menu_book')}${metric('Proyectos activos', totals.active_projects, 'science', 'teal')}${metric('Semilleros', totals.semilleros, 'psychology')}${metric('XP validado', totals.validated_xp, 'military_tech')}</section>
    <div class="analytics-grid">
      <section class="glass-card admin-panel analytics-wide"><div class="section-heading"><h2 class="headline-md">Producción de investigación</h2></div>${lineChart(data.production)}</section>
      <section class="glass-card admin-panel"><div class="section-heading"><h2 class="headline-md">Semilleros por facultad</h2></div>${facultyBars(data.semilleros_by_faculty)}</section>
      <section class="glass-card admin-panel analytics-wide"><div class="section-heading"><h2 class="headline-md">Semilleros con mayor XP</h2></div>${topTable(data.top_semilleros)}</section>
      <section class="glass-card admin-panel"><div class="section-heading"><h2 class="headline-md">Estado de cuentas</h2></div>${donut(data.account_status)}</section>
      <section class="glass-card admin-panel analytics-wide" id="reportsPanel"><div class="section-heading"><h2 class="headline-md">Reportes institucionales</h2></div>
        <form id="reportForm" class="admin-user-actions" style="flex-wrap:wrap;align-items:flex-end;gap:var(--space-3);margin-bottom:var(--space-4);">
          <label class="label-base">Tipo<select class="input-base" name="kind" required><option value="report">Reporte de producción</option><option value="ranking">Ranking de semilleros</option></select></label>
          <label class="label-base">Desde<input class="input-base" type="date" name="period_start" required></label>
          <label class="label-base">Hasta<input class="input-base" type="date" name="period_end" required></label>
          <button class="btn btn-primary label-caps" type="submit">Generar reporte</button>
        </form>
        <p class="body-md" id="reportMessage" role="status"></p>
        <div id="reportList"></div>
      </section>
    </div>`;
}

const REPORT_KIND_LABELS = { report: 'Producción', ranking: 'Ranking' };

async function loadReports() {
  const { items } = await adminRequest('/api/admin/reports');
  const list = document.getElementById('reportList');
  list.innerHTML = items.length
    ? `<div class="table-scroll"><table class="table-data"><thead><tr><th>Tipo</th><th>Periodo</th><th>Generado por</th><th>Estado</th><th></th></tr></thead><tbody>${items.map((item) => `<tr><td>${REPORT_KIND_LABELS[item.kind] ?? escapeHtml(item.kind)}</td><td>${escapeHtml(item.period_start)} → ${escapeHtml(item.period_end)}</td><td>${escapeHtml(item.generated_by.full_name || '—')}</td><td><span class="status-pill">${item.published ? 'Publicado' : 'Borrador'}</span></td><td>${item.published ? '' : `<button class="btn btn-teal label-caps" type="button" data-publish="${item.id}">Publicar</button>`}</td></tr>`).join('')}</tbody></table></div>`
    : '<p class="body-md admin-empty-text">Aún no se han generado reportes.</p>';
}

function initReports() {
  const message = document.getElementById('reportMessage');
  document.getElementById('reportForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    message.textContent = '';
    const body = Object.fromEntries(new FormData(event.currentTarget).entries());
    try {
      await adminRequest('/api/admin/reports', { method: 'POST', body });
      message.textContent = 'Reporte generado como borrador.';
      await loadReports();
    } catch (error) {
      message.textContent = error.message;
    }
  });
  document.getElementById('reportList').addEventListener('click', async (event) => {
    const button = event.target.closest('[data-publish]');
    if (!button) return;
    button.disabled = true;
    try {
      await adminRequest(`/api/admin/reports/${button.dataset.publish}/publication`, { method: 'POST' });
      message.textContent = 'Reporte publicado.';
      await loadReports();
    } catch (error) {
      message.textContent = error.message;
      button.disabled = false;
    }
  });
  return loadReports();
}

function exportData(data) {
  const rows = [
    ['Métrica', 'Valor'],
    ['Publicaciones', data.totals.publications],
    ['Proyectos activos', data.totals.active_projects],
    ['Semilleros', data.totals.semilleros],
    ['XP validado', data.totals.validated_xp],
    [],
    ['Mes', 'Publicaciones', 'Proyectos'],
    ...data.production.map((m) => [m.month, m.publications, m.projects]),
    [],
    ['Facultad', 'Semilleros'],
    ...data.semilleros_by_faculty.map((i) => [i.faculty, i.count]),
    [],
    ['Semillero', 'Facultad', 'XP'],
    ...data.top_semilleros.map((i) => [i.name, i.faculty || '', i.xp]),
    [],
    ['Estado de cuenta', 'Total'],
    ['Activas', data.account_status.active],
    ['Pendientes', data.account_status.pending],
    ['Rechazadas', data.account_status.rejected],
  ];
  downloadCsv('riul-analitica.csv', rows);
}

async function init() {
  const user = await guardAdmin(content, 'analytics');
  if (!user) return;
  try {
    const data = await adminRequest('/api/admin/analytics');
    render(data);
    await initReports();
    exportBtn.hidden = false;
    exportBtn.addEventListener('click', () => exportData(data));
  } catch (error) {
    showState(content, 'No se pudo cargar la analítica', error.message);
  }
}

init();
