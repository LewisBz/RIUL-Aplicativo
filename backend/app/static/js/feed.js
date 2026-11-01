import { API_BASE, requireAuth, getToken, logout } from './session.js';
import { initLayout } from './layout.js';
import { showSkeleton } from './skeleton.js';

const CATEGORY_LABELS = {
  article: 'Artículo',
  project_advance: 'Avance de Proyecto',
  presentation: 'Ponencia',
  event: 'Evento',
  community: 'Comunidad',
};

const state = { category: 'community', page: 1, total: 0, me: null };

const feedGrid = document.getElementById('feedGrid');
const composerForm = document.getElementById('createPostForm');
const composerTextarea = document.getElementById('postContent');
const composerFile = document.getElementById('postFile');
const attachBtn = document.getElementById('attachBtn');
const attachPreview = document.getElementById('attachPreview');
const attachPreviewName = document.getElementById('attachPreviewName');
const attachRemove = document.getElementById('attachRemove');
const publishBtn = document.getElementById('publishBtn');

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let response;
  try {
    response = await fetch(API_BASE + path, { ...options, headers });
  } catch {
    throw new Error('No hay conexión con el backend. ¿Está corriendo docker compose?');
  }
  if (response.status === 401) {
    logout();
    throw new Error('sesión expirada');
  }
  return response;
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[ch]));
}

function initials(fullName) {
  const parts = String(fullName || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return '?';
  const letters = parts.length === 1 ? parts[0].slice(0, 2) : parts[0][0] + parts[parts.length - 1][0];
  return letters.toUpperCase();
}

function timeAgo(isoDate) {
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(isoDate).getTime()) / 1000));
  if (seconds < 60) return 'hace un momento';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h`;
  const days = Math.floor(hours / 24);
  if (days <= 7) return `${days} d`;
  return new Date(isoDate).toLocaleDateString('es', { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatSize(bytes) {
  if (!bytes && bytes !== 0) return '';
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

function attachmentUrl(attachment) {
  return `${API_BASE}${attachment.url}?token=${encodeURIComponent(getToken() || '')}`;
}

function attachmentHtml(attachment) {
  if (!attachment) return '';
  if (attachment.kind === 'image') {
    return `<img class="attachment-image" src="${escapeHtml(attachmentUrl(attachment))}" alt="Adjunto de la publicación">`;
  }
  return `
    <a class="attachment-file" href="${escapeHtml(attachmentUrl(attachment))}" target="_blank" rel="noopener">
      <div class="attachment-file-icon"><span class="material-symbols-outlined">description</span></div>
      <div>
        <h4>${escapeHtml(attachment.file_name)}</h4>
        <p>${escapeHtml(formatSize(attachment.file_size))}</p>
      </div>
    </a>`;
}

function postCardHtml(post, viewerId) {
  const isCommunity = post.category === 'community';
  const isAuthor = post.author.id === viewerId;
  const menuButton = isAuthor
    ? `<button class="icon-action" data-action="delete" data-post-id="${post.id}" aria-label="Eliminar publicación" title="Eliminar">
         <span class="material-symbols-outlined">more_horiz</span>
       </button>`
    : '';
  const contentBlock = post.content
    ? `<p class="post-text">${escapeHtml(post.content)}</p>`
    : '';
  const linkBlock = post.link_url
    ? `<a class="post-link" href="${escapeHtml(post.link_url)}" target="_blank" rel="noopener">${escapeHtml(post.link_url)}</a>`
    : '';
  const attachment = post.attachments[0];
  const attachmentBlock = attachment
    ? attachmentHtml(attachment)
    : `<div class="attachment-placeholder"><span class="material-symbols-outlined">image</span></div>`;
  return `
    <article class="post-card${isCommunity ? ' community' : ''}" data-post-card="${post.id}">
      <div class="post-header">
        <div class="post-header-info">
          <span class="avatar avatar-md">${escapeHtml(initials(post.author.full_name))}</span>
          <div>
            <h3>${escapeHtml(post.author.full_name || 'Investigador')}</h3>
            <time datetime="${escapeHtml(post.created_at)}">${escapeHtml(timeAgo(post.created_at))}</time>
          </div>
        </div>
        <div class="post-header-side">
          <span class="category-badge${isCommunity ? ' community' : ''}">${CATEGORY_LABELS[post.category] || post.category}</span>
          ${menuButton}
        </div>
      </div>
      <div class="post-body">
        ${contentBlock}
        ${linkBlock}
        ${attachmentBlock}
      </div>
      <div class="post-actions">
        <button class="post-action-btn${post.reacted_by_me ? ' reacted' : ''}" data-action="react" data-post-id="${post.id}">
          <span class="material-symbols-outlined${post.reacted_by_me ? ' filled' : ''}">thumb_up</span>
          <span data-reaction-count>${post.reaction_count}</span> Reacciones
        </button>
        <button class="post-action-btn" data-action="comments" data-post-id="${post.id}" aria-expanded="false">
          <span class="material-symbols-outlined">chat_bubble_outline</span>
          <span data-comment-count>${post.comment_count ?? 0}</span> Comentarios
        </button>
        <button class="post-action-btn${post.shared_by_me ? ' reacted' : ''}" data-action="share" data-post-id="${post.id}">
          <span class="material-symbols-outlined${post.shared_by_me ? ' filled' : ''}">share</span>
          <span data-share-count>${post.share_count ?? 0}</span> Compartir
        </button>
      </div>
      <section class="post-comments" data-comments-for="${post.id}" hidden></section>
    </article>`;
}

function renderFeed(posts, { append = false } = {}) {
  const viewerId = state.me?.id;
  const html = posts.map((post) => postCardHtml(post, viewerId)).join('');
  if (!append) feedGrid.innerHTML = '';
  document.getElementById('loadMoreBtn')?.remove();
  if (!html && !append) {
    feedGrid.innerHTML = `
      <div class="feed-empty">
        <span class="material-symbols-outlined">forum</span>
        <strong>No hay publicaciones todavía</strong>
        <span class="body-md">Sé el primero en compartir algo con la comunidad.</span>
      </div>`;
    return;
  }
  feedGrid.insertAdjacentHTML('beforeend', html);
  const remaining = state.total - feedGrid.querySelectorAll('.post-card').length;
  if (remaining > 0) {
    feedGrid.insertAdjacentHTML('beforeend', `
      <button class="btn btn-secondary label-caps" id="loadMoreBtn" style="grid-column:1/-1;justify-self:center;">
        Ver más (${remaining})
      </button>`);
  }
}

async function loadFeed({ append = false, page = 1 } = {}) {
  state.page = page;
  const params = new URLSearchParams({ page: String(page) });
  if (state.category) params.set('category', state.category);
  const response = await api(`/api/posts?${params}`);
  if (!response.ok) {
    const { message } = await response.json().catch(() => ({}));
    throw new Error(message || 'No fue posible cargar el feed.');
  }
  const payload = await response.json();
  state.total = payload.total;
  renderFeed(payload.items, { append });
}

function setActiveChip(category) {
  document.querySelectorAll('#categoryChips .chip-outline').forEach((chip) => {
    chip.classList.toggle('active', chip.dataset.category === category);
  });
}

document.getElementById('categoryChips').addEventListener('click', async (event) => {
  const chip = event.target.closest('.chip-outline');
  if (!chip) return;
  state.category = chip.classList.contains('active') ? null : chip.dataset.category;
  setActiveChip(state.category);
  feedGrid.innerHTML = `
    <div class="feed-empty">
      <span class="material-symbols-outlined">hourglass_empty</span>
      <span class="body-md">Cargando publicaciones…</span>
    </div>`;
  try {
    await loadFeed();
  } catch (error) {
    feedGrid.innerHTML = `
      <div class="feed-empty">
        <span class="material-symbols-outlined">error</span>
        <span class="body-md">${escapeHtml(error.message)}</span>
      </div>`;
  }
});

function commentHtml(comment, postId) {
  const mine = comment.author?.id === state.me?.id || state.me?.role === 'administrator';
  return `
    <div class="post-comment" data-comment="${comment.id}" style="display:flex;gap:var(--space-2);align-items:flex-start;margin-top:var(--space-2);">
      <span class="avatar avatar-sm">${escapeHtml(initials(comment.author?.full_name))}</span>
      <div style="flex:1;min-width:0;">
        <strong>${escapeHtml(comment.author?.full_name || 'Investigador')}</strong>
        <time style="margin-left:var(--space-2);font-size:12px;" datetime="${escapeHtml(comment.created_at)}">${escapeHtml(timeAgo(comment.created_at))}</time>
        <p class="body-md" style="margin:0;">${escapeHtml(comment.body)}</p>
      </div>
      ${mine ? `<button class="icon-action" data-action="delete-comment" data-post-id="${postId}" data-comment-id="${comment.id}" aria-label="Eliminar comentario" title="Eliminar"><span class="material-symbols-outlined">delete</span></button>` : ''}
    </div>`;
}

async function refreshComments(postId) {
  const box = document.querySelector(`[data-comments-for="${postId}"]`);
  const response = await api(`/api/posts/${postId}/comments`);
  if (!response.ok) return;
  const { items } = await response.json();
  box.querySelector('[data-comment-list]').innerHTML = items.map((item) => commentHtml(item, postId)).join('');
  document.querySelector(`[data-post-card="${postId}"] [data-comment-count]`).textContent = items.length;
}

async function toggleComments(button, postId) {
  const box = document.querySelector(`[data-comments-for="${postId}"]`);
  const open = box.hidden;
  button.setAttribute('aria-expanded', String(open));
  box.hidden = !open;
  if (!open || box.dataset.ready) return;
  box.dataset.ready = '1';
  box.innerHTML = `
    <div data-comment-list></div>
    <form data-comment-form style="display:flex;gap:var(--space-2);margin-top:var(--space-3);">
      <input class="input-base" name="body" maxlength="2000" required placeholder="Escribe un comentario…" aria-label="Escribe un comentario">
      <button class="btn btn-primary label-caps" type="submit">Comentar</button>
    </form>
    <p class="body-md" data-comment-error role="alert" style="color:var(--error);margin:var(--space-1) 0 0;"></p>`;
  box.querySelector('[data-comment-form]').addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const input = form.elements.body;
    const errorEl = box.querySelector('[data-comment-error]');
    errorEl.textContent = '';
    const response = await api(`/api/posts/${postId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body: input.value.trim() }),
    });
    if (!response.ok) {
      errorEl.textContent = (await response.json().catch(() => ({}))).message || 'No fue posible comentar.';
      return;
    }
    input.value = '';
    await refreshComments(postId);
  });
  await refreshComments(postId);
}

feedGrid.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-action]');
  if (!button) return;
  const action = button.dataset.action;
  const postId = button.dataset.postId;

  if (action === 'react') {
    button.disabled = true;
    try {
      const response = await api(`/api/posts/${postId}/reactions`, { method: 'POST' });
      if (response.ok) {
        const { reaction_count, reacted_by_me } = await response.json();
        button.querySelector('[data-reaction-count]').textContent = reaction_count;
        button.classList.toggle('reacted', reacted_by_me);
        button.querySelector('.material-symbols-outlined').classList.toggle('filled', reacted_by_me);
      }
    } finally {
      button.disabled = false;
    }
  }

  if (action === 'share') {
    const permalink = `${location.origin}${location.pathname.replace(/#.*$/, '')}#post-${postId}`;
    button.disabled = true;
    try {
      const response = await api(`/api/posts/${postId}/shares`, { method: 'POST' });
      if (response.ok) {
        const { share_count, shared_by_me } = await response.json();
        button.querySelector('[data-share-count]').textContent = share_count;
        button.classList.toggle('reacted', shared_by_me);
        button.querySelector('.material-symbols-outlined').classList.toggle('filled', shared_by_me);
        if (shared_by_me) {
          await navigator.clipboard.writeText(permalink).catch(() => {});
          button.title = '¡Enlace copiado!';
          setTimeout(() => { button.title = ''; }, 1500);
        }
      }
    } finally {
      button.disabled = false;
    }
  }

  if (action === 'comments') {
    await toggleComments(button, postId);
  }

  if (action === 'delete-comment') {
    const { commentId } = button.dataset;
    const response = await api(`/api/posts/${postId}/comments/${commentId}`, { method: 'DELETE' });
    if (response.ok || response.status === 204) {
      await refreshComments(postId);
    }
  }

  if (action === 'delete') {
    if (!window.confirm('¿Eliminar esta publicación? Esta acción no se puede deshacer.')) return;
    const response = await api(`/api/posts/${postId}`, { method: 'DELETE' });
    if (response.ok || response.status === 204) {
      document.querySelector(`[data-post-card="${postId}"]`)?.remove();
      state.total = Math.max(0, state.total - 1);
      if (!feedGrid.querySelector('.post-card')) await loadFeed();
    }
  }
});

feedGrid.addEventListener('click', async (event) => {
  if (!event.target.closest('#loadMoreBtn')) return;
  event.target.closest('#loadMoreBtn')?.setAttribute('disabled', '');
  await loadFeed({ append: true, page: state.page + 1 });
});

attachBtn.addEventListener('click', () => composerFile.click());

composerFile.addEventListener('change', () => {
  const file = composerFile.files[0];
  if (!file) {
    attachPreview.classList.add('hidden');
    return;
  }
  attachPreviewName.textContent = `${file.name} (${formatSize(file.size)})`;
  attachPreview.classList.remove('hidden');
});

attachRemove.addEventListener('click', () => {
  composerFile.value = '';
  attachPreview.classList.add('hidden');
});

function setComposerError(message) {
  let errorEl = document.getElementById('composerError');
  if (!message) {
    errorEl?.remove();
    return;
  }
  if (!errorEl) {
    errorEl = document.createElement('span');
    errorEl.id = 'composerError';
    errorEl.className = 'pill pill-review';
    composerForm.querySelector('div:last-of-type').prepend(errorEl);
  }
  errorEl.textContent = message;
}

composerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  setComposerError(null);
  const hasText = composerTextarea.value.trim().length > 0;
  const hasFile = composerFile.files.length > 0;
  if (!hasText && !hasFile) {
    setComposerError('Escribe algo o adjunta un archivo.');
    return;
  }
  const formData = new FormData();
  formData.append('category', 'community');
  formData.append('content', composerTextarea.value.trim());
  if (hasFile) formData.append('file', composerFile.files[0]);

  publishBtn.disabled = true;
  try {
    const response = await api('/api/posts', { method: 'POST', body: formData });
    if (!response.ok) {
      const { message } = await response.json().catch(() => ({}));
      setComposerError(message || 'No fue posible publicar.');
      return;
    }
    const { post } = await response.json();
    composerTextarea.value = '';
    composerFile.value = '';
    attachPreview.classList.add('hidden');
    state.total += 1;
    document.querySelector('.feed-empty')?.remove();
    feedGrid.insertAdjacentHTML('afterbegin', postCardHtml(post, state.me?.id));
  } catch (error) {
    setComposerError(error.message);
  } finally {
    publishBtn.disabled = false;
  }
});

async function init() {
  const user = await requireAuth();
  if (!user) throw new Error('Sesión requerida');
  await initLayout();

  state.me = user;
  const composerAvatar = document.getElementById('composerAvatar');
  if (composerAvatar) composerAvatar.textContent = initials(user.full_name || 'Investigador');

  try {
    showSkeleton(feedGrid, 'post', 3);
    await loadFeed();
    const hashPostId = location.hash.match(/^#post-(\d+)$/);
    if (hashPostId) {
      document.querySelector(`[data-post-card="${hashPostId[1]}"]`)
        ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  } catch (error) {
    feedGrid.innerHTML = `
      <div class="feed-empty">
        <span class="material-symbols-outlined">cloud_off</span>
        <span class="body-md">${escapeHtml(error.message)}</span>
      </div>`;
  }
}

init();

