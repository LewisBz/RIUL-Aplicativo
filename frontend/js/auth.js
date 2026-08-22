const API =
  location.protocol === 'file:' || location.port !== '5000'
    ? 'http://localhost:5000'
    : '';

const alertEl = document.getElementById('authAlert');
const alertIcon = document.getElementById('authAlertIcon');
const alertText = document.getElementById('authAlertText');

function showAlert(message, variant = 'error') {
  if (!alertEl) return;
  alertEl.classList.remove('hidden', 'is-success');
  alertIcon.textContent = variant === 'success' ? 'check_circle' : 'error';
  if (variant === 'success') alertEl.classList.add('is-success');
  alertText.textContent = message;
  alertEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function postJson(path, body) {
  const response = await fetch(API + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  return { ok: response.ok, status: response.status, data };
}

function saveSession(token) {
  localStorage.setItem('riul_token', token);
  window.location.href = 'index.html';
}

async function loadCatalog() {
  try {
    const response = await fetch(API + '/api/auth/catalog');
    const { faculties } = await response.json();
    document.querySelectorAll('select[name="faculty_id"]').forEach((facultySelect) => {
      faculties.forEach((faculty) => {
        const option = new Option(faculty.name, faculty.id);
        facultySelect.add(option);
      });
      const programSelect = document.getElementById(facultySelect.dataset.programsTarget);
      facultySelect.addEventListener('change', () => {
        programSelect.innerHTML = '';
        programSelect.add(new Option('Seleccione...', '', true, true));
        const selected = faculties.find((f) => f.id === Number(facultySelect.value));
        selected?.programs.forEach((program) => programSelect.add(new Option(program.name, program.id)));
      });
    });
  } catch {
    showAlert('No se pudo cargar el catálogo de facultades. ¿Está corriendo el backend?');
  }
}

const loginForm = document.getElementById('loginForm');
loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const { ok, data } = await postJson('/api/auth/login', {
    email: formData.get('email'),
    password: formData.get('password'),
  });
  if (ok) {
    saveSession(data.access_token);
  } else {
    showAlert(data.message ?? 'No fue posible iniciar sesión.');
  }
});

const registerForm = document.getElementById('panelRegister');
registerForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  const { ok, data } = await postJson('/api/auth/register', {
    email: formData.get('email'),
    password: formData.get('password'),
    full_name: formData.get('full_name'),
    faculty_id: formData.get('faculty_id') || null,
    program_id: formData.get('program_id') || null,
  });
  if (ok) {
    saveSession(data.access_token);
  } else {
    showAlert(data.message ?? 'No fue posible completar el registro.');
  }
});

const requestForm = document.getElementById('panelRequest');
requestForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(requestForm);
  const { ok, data } = await postJson('/api/auth/request-account', {
    email: formData.get('email'),
    full_name: formData.get('full_name'),
    motivation: formData.get('motivation'),
    faculty_id: formData.get('faculty_id'),
    program_id: formData.get('program_id'),
  });
  if (ok) {
    requestForm.reset();
    showAlert(data.message, 'success');
  } else {
    showAlert(data.message ?? 'No fue posible enviar la solicitud.');
  }
});

document.querySelectorAll('.auth-tabs .tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auth-tabs .tab').forEach((t) => t.classList.remove('active'));
    tab.classList.add('active');
    ['panelRequest', 'panelRegister'].forEach((id) => {
      document.getElementById(id).classList.toggle('hidden', id !== tab.dataset.panel);
    });
    alertEl?.classList.add('hidden');
  });
});

if (document.querySelector('.auth-tabs')) loadCatalog();
