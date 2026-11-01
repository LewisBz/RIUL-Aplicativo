import { API_BASE, getToken, logout, requireAuth } from './session.js';
import { initLayout } from './layout.js';

const CATEGORIES = [
  { value: 'article', label: 'Artículo', icon: 'article' },
  { value: 'project_advance', label: 'Avance de proyecto', icon: 'trending_up' },
  { value: 'presentation', label: 'Ponencia', icon: 'mic' },
  { value: 'event', label: 'Evento', icon: 'event' },
  { value: 'community', label: 'Comunidad', icon: 'chat_bubble' },
];
const MAX_BYTES = 10 * 1024 * 1024;

const form = document.getElementById('publishForm');
const errorEl = document.getElementById('publishError');
const publishBtn = document.getElementById('publishBtn');
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('postFile');
const dropzoneText = document.getElementById('dropzoneText');
const DEFAULT_DROP_TEXT = dropzoneText.innerHTML;

document.getElementById('categoryOptions').innerHTML = CATEGORIES.map(
  (c, i) => `<label class="category-option"><input type="radio" name="category" value="${c.value}" ${i === 0 ? 'checked' : ''}><span class="material-symbols-outlined">${c.icon}</span>${c.label}</label>`
).join('');

function setFile(file) {
  if (!file) {
    fileInput.value = '';
    dropzoneText.innerHTML = DEFAULT_DROP_TEXT;
    return;
  }
  if (file.size > MAX_BYTES) {
    errorEl.textContent = 'El archivo supera el límite de 10 MB.';
    return;
  }
  errorEl.textContent = '';
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  dropzoneText.textContent = `${file.name} (${Math.max(1, Math.round(file.size / 1024))} KB) — clic para cambiar`;
}

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    fileInput.click();
  }
});
fileInput.addEventListener('change', () => setFile(fileInput.files[0]));
['dragenter', 'dragover'].forEach((name) =>
  dropzone.addEventListener(name, (event) => {
    event.preventDefault();
    dropzone.classList.add('dragover');
  })
);
['dragleave', 'drop'].forEach((name) =>
  dropzone.addEventListener(name, (event) => {
    event.preventDefault();
    dropzone.classList.remove('dragover');
  })
);
dropzone.addEventListener('drop', (event) => setFile(event.dataTransfer.files[0]));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  errorEl.textContent = '';
  const title = form.elements.title.value.trim();
  const body = form.elements.content.value.trim();
  const link = form.elements.link_url.value.trim();
  const file = fileInput.files[0];
  if (!title && !body && !link && !file) {
    errorEl.textContent = 'Escribe un título o contenido, o adjunta un enlace o archivo.';
    return;
  }
  const content = [title, body].filter(Boolean).join('\n\n');
  const data = new FormData();
  data.append('category', form.elements.category.value);
  data.append('content', content);
  if (link) data.append('link_url', link);
  if (file) data.append('file', file);

  publishBtn.disabled = true;
  try {
    const response = await fetch(`${API_BASE}/api/posts`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: data,
    });
    if (response.status === 401) {
      logout();
      return;
    }
    if (!response.ok) {
      const { message } = await response.json().catch(() => ({}));
      errorEl.textContent = message || 'No fue posible publicar.';
      return;
    }
    window.location.href = '/feed';
  } catch {
    errorEl.textContent = 'No hay conexión con el servidor.';
  } finally {
    publishBtn.disabled = false;
  }
});

async function init() {
  const user = await requireAuth();
  if (!user) return;
  await initLayout();
}

init();
