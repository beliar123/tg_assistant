'use strict';

// ════════════════════════════════
//  STATE
// ════════════════════════════════
let currentUser = null;
let reminders = [];
let editingReminderId = null;
let pendingConfirmAction = null;
let sidebarOpen = true;

// ════════════════════════════════
//  HELPERS: sessionStorage
// ════════════════════════════════
const ss = {
  get:   k      => sessionStorage.getItem(k),
  set:   (k, v) => sessionStorage.setItem(k, v),
  clear: ()     => sessionStorage.clear(),
};

function getApiBase() {
  return (ss.get('apiBase') || '').replace(/\/$/, '');
}

function setApiBase(val) {
  ss.set('apiBase', val.replace(/\/$/, ''));
}

// ════════════════════════════════
//  API CLIENT
// ════════════════════════════════
async function apiRequest(method, path, body = null, retry = true) {
  const base = getApiBase();
  if (!base) { showToast('Укажите URL API', 'error'); throw new Error('No API base'); }

  const headers = { 'Content-Type': 'application/json' };
  const token = ss.get('accessToken');
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const opts = { method, headers };
  if (body !== null) opts.body = JSON.stringify(body);

  const res = await fetch(base + path, opts);

  if (res.status === 401 && retry) {
    const refreshed = await tryRefresh();
    if (refreshed) return apiRequest(method, path, body, false);
    handleLogout();
    throw new Error('Unauthorized');
  }

  return res;
}

async function tryRefresh() {
  const refresh = ss.get('refreshToken');
  if (!refresh) return false;
  try {
    const res = await fetch(getApiBase() + '/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    ss.set('accessToken', data.access_token);
    ss.set('refreshToken', data.refresh_token);
    return true;
  } catch { return false; }
}

// ════════════════════════════════
//  TOAST
// ════════════════════════════════

// Static SVG strings — never contain user data
const TOAST_ICONS = {
  success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
  error:   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
  info:    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
};

function showToast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;

  const iconEl = document.createElement('div');
  iconEl.className = `toast-icon ${type}`;
  iconEl.innerHTML = TOAST_ICONS[type] || TOAST_ICONS.info; // static SVG constant

  const p = document.createElement('p');
  p.textContent = msg; // user-visible text via textContent

  el.append(iconEl, p);
  document.getElementById('toast-container').appendChild(el);

  setTimeout(() => {
    el.classList.add('toast-out');
    setTimeout(() => el.remove(), 350);
  }, 3500);
}

// ════════════════════════════════
//  AUTH TABS
// ════════════════════════════════
function switchTab(tab) {
  document.querySelectorAll('.auth-tab').forEach((b, i) => {
    b.classList.toggle('active', (i === 0 && tab === 'login') || (i === 1 && tab === 'register'));
  });
  document.getElementById('login-form').classList.toggle('active', tab === 'login');
  document.getElementById('register-form').classList.toggle('active', tab === 'register');
}

// ════════════════════════════════
//  LOGIN
// ════════════════════════════════
async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const btn = document.getElementById('login-btn');

  setApiBase(document.getElementById('auth-api-url').value.trim());

  const restore = spinBtn(btn);
  try {
    const res = await fetch(getApiBase() + '/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (res.status === 401) { showToast('Неверный логин или пароль', 'error'); return; }
    if (res.status === 403) { showToast('Аккаунт деактивирован', 'error'); return; }
    if (res.status === 429) { showToast('Слишком много попыток. Попробуйте позже.', 'error'); return; }
    if (!res.ok) { showToast('Ошибка сервера', 'error'); return; }

    const data = await res.json();
    ss.set('accessToken', data.access_token);
    ss.set('refreshToken', data.refresh_token);
    await initDashboard();
  } catch { showToast('Не удалось подключиться к API', 'error'); }
  finally { restore(); }
}

// ════════════════════════════════
//  REGISTER
// ════════════════════════════════
async function handleRegister(e) {
  e.preventDefault();
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;
  const name     = document.getElementById('reg-name').value.trim();
  const lastname = document.getElementById('reg-lastname').value.trim();
  const btn = document.getElementById('register-btn');

  setApiBase(document.getElementById('auth-api-url').value.trim());

  const restore = spinBtn(btn);
  try {
    const body = { username, password, name };
    if (lastname) body.lastname = lastname;

    const res = await fetch(getApiBase() + '/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (res.status === 409) { showToast('Пользователь уже существует', 'error'); return; }
    if (res.status === 429) { showToast('Слишком много попыток. Попробуйте позже.', 'error'); return; }
    if (res.status === 422) {
      const err = await res.json().catch(() => ({}));
      const detail = Array.isArray(err.detail)
        ? err.detail.map(d => d.msg).join('; ')
        : (err.detail || 'Ошибка валидации');
      showToast(detail, 'error');
      return;
    }
    if (!res.ok) { showToast('Ошибка регистрации', 'error'); return; }

    const data = await res.json();
    ss.set('accessToken', data.access_token);
    ss.set('refreshToken', data.refresh_token);
    showToast('Аккаунт создан!', 'success');
    await initDashboard();
  } catch { showToast('Не удалось подключиться к API', 'error'); }
  finally { restore(); }
}

function handleLogout() {
  ss.clear();
  currentUser = null;
  reminders = [];
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('dashboard').classList.remove('active');
}

// ════════════════════════════════
//  SPINNER HELPER
// ════════════════════════════════
function spinBtn(btn) {
  const label = btn.textContent;
  btn.disabled = true;
  btn.textContent = '';
  const s = document.createElement('div');
  s.className = 'spinner';
  btn.appendChild(s);
  return () => { btn.disabled = false; btn.textContent = label; };
}

// ════════════════════════════════
//  DASHBOARD
// ════════════════════════════════
async function initDashboard() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('dashboard').classList.add('active');
  document.getElementById('dashboard-api-url').value = getApiBase();
  await Promise.all([loadUser(), loadReminders()]);
}

// ════════════════════════════════
//  USER / PROFILE
// ════════════════════════════════
async function loadUser() {
  try {
    const res = await apiRequest('GET', '/users/me');
    if (!res.ok) return;
    currentUser = await res.json();
    renderProfile();
  } catch {}
}

function renderProfile() {
  if (!currentUser) return;
  const fullname = [currentUser.name, currentUser.lastname].filter(Boolean).join(' ');
  const initials = (currentUser.name?.[0] ?? '') + (currentUser.lastname?.[0] ?? currentUser.username?.[0] ?? '');

  // All user data assigned via textContent — XSS-safe
  document.getElementById('topbar-avatar-btn').textContent = initials.toUpperCase().slice(0, 2);
  document.getElementById('sidebar-avatar').textContent    = initials.toUpperCase().slice(0, 2);
  document.getElementById('sidebar-name').textContent      = fullname || currentUser.username;
  document.getElementById('sidebar-username').textContent  = '@' + currentUser.username;
  document.getElementById('profile-email-val').textContent = currentUser.email || '—';

  const statusEl = document.getElementById('profile-status-val');
  statusEl.textContent = '';
  const badge = document.createElement('span');
  badge.className = currentUser.is_active ? 'badge badge-active' : 'badge badge-inactive';
  badge.textContent = currentUser.is_active ? 'Активен' : 'Неактивен';
  statusEl.appendChild(badge);

  document.getElementById('edit-name').value     = currentUser.name || '';
  document.getElementById('edit-lastname').value = currentUser.lastname || '';
  document.getElementById('edit-email').value    = currentUser.email || '';
}

function toggleEditProfile() {
  document.getElementById('profile-edit').classList.toggle('active');
}

async function saveProfile() {
  const name     = document.getElementById('edit-name').value.trim();
  const lastname = document.getElementById('edit-lastname').value.trim();
  const email    = document.getElementById('edit-email').value.trim();

  const body = {};
  if (name)     body.name = name;
  if (lastname) body.lastname = lastname;
  if (email)    body.email = email;

  try {
    const res = await apiRequest('PATCH', '/users/me', body);
    if (!res.ok) { showToast('Ошибка сохранения', 'error'); return; }
    currentUser = await res.json();
    renderProfile();
    toggleEditProfile();
    showToast('Профиль обновлён', 'success');
  } catch { showToast('Ошибка сети', 'error'); }
}

// ════════════════════════════════
//  REMINDERS
// ════════════════════════════════
async function loadReminders() {
  try {
    const res = await apiRequest('GET', '/reminders/');
    if (!res.ok) return;
    reminders = await res.json();
    renderReminders();
  } catch {}
}

// Static SVG constants — never contain user data
const SVG = {
  reminder: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
  repeat:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
  edit:     '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
  delete:   '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>',
  empty:    '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
};

function renderReminders() {
  const container = document.getElementById('reminders-container');
  document.getElementById('reminder-count').textContent = reminders.length;
  container.textContent = '';

  if (reminders.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = SVG.empty; // static constant
    const p = document.createElement('p');
    p.textContent = 'Напоминаний пока нет. Создайте первое!';
    empty.appendChild(p);
    container.appendChild(empty);
    return;
  }

  const now = new Date();
  const upcoming = reminders.filter(r => new Date(r.event_datetime) >= now);
  const past     = reminders.filter(r => new Date(r.event_datetime) <  now);
  upcoming.sort((a, b) => new Date(a.event_datetime) - new Date(b.event_datetime));
  past.sort((a, b) => new Date(b.event_datetime) - new Date(a.event_datetime));

  if (upcoming.length) {
    container.appendChild(sectionLabel('Предстоящие · ' + upcoming.length));
    upcoming.forEach(r => container.appendChild(reminderCard(r, false)));
  }
  if (past.length) {
    container.appendChild(sectionLabel('Прошедшие · ' + past.length));
    past.forEach(r => container.appendChild(reminderCard(r, true)));
  }
}

function sectionLabel(text) {
  const div = document.createElement('div');
  div.className = 'section-label';
  div.textContent = text;
  return div;
}

function svgChip(innerMarkup, attrs) {
  const el = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
  el.innerHTML = innerMarkup; // static SVG inner markup, never user data
  return el;
}

function reminderCard(r, isPast) {
  const card = document.createElement('div');
  card.className = 'reminder-card' + (isPast ? ' past' : '');

  const iconEl = document.createElement('div');
  iconEl.className = 'reminder-icon';
  iconEl.innerHTML = SVG.reminder; // static constant

  const body = document.createElement('div');
  body.className = 'reminder-body';

  const desc = document.createElement('div');
  desc.className = 'reminder-desc';
  desc.textContent = r.description; // user data — safe via textContent

  const meta = document.createElement('div');
  meta.className = 'reminder-meta';

  // Date chip
  const dateChip = document.createElement('div');
  dateChip.className = 'meta-chip';
  dateChip.appendChild(svgChip(
    '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }
  ));
  const dateSpan = document.createElement('span');
  dateSpan.textContent = fmtDt(new Date(r.event_datetime));
  dateChip.appendChild(dateSpan);

  // Count chip
  const countChip = document.createElement('div');
  countChip.className = 'meta-chip';
  countChip.appendChild(svgChip(
    '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }
  ));
  const countSpan = document.createElement('span');
  countSpan.textContent = r.message_count + ' уведомл.';
  countChip.appendChild(countSpan);

  meta.append(dateChip, countChip);

  if (r.repeat_interval) {
    const chip = document.createElement('div');
    chip.className = 'meta-chip repeat';
    chip.innerHTML = SVG.repeat; // static constant
    const span = document.createElement('span');
    span.textContent = r.repeat_interval; // enum value from API
    chip.appendChild(span);
    meta.appendChild(chip);
  }

  body.append(desc, meta);

  const actions = document.createElement('div');
  actions.className = 'reminder-actions';

  const editBtn = document.createElement('div');
  editBtn.className = 'icon-btn';
  editBtn.title = 'Редактировать';
  editBtn.innerHTML = SVG.edit; // static constant
  editBtn.addEventListener('click', () => openReminderModal(r));

  const delBtn = document.createElement('div');
  delBtn.className = 'icon-btn delete';
  delBtn.title = 'Удалить';
  delBtn.innerHTML = SVG.delete; // static constant
  delBtn.addEventListener('click', () => deleteReminder(r.id));

  actions.append(editBtn, delBtn);
  card.append(iconEl, body, actions);
  return card;
}

function fmtDt(dt) {
  return dt.toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

// ════════════════════════════════
//  REMINDER MODAL
// ════════════════════════════════
function openReminderModal(reminder) {
  editingReminderId = reminder ? reminder.id : null;
  const title     = document.getElementById('reminder-modal-title');
  const submitBtn = document.getElementById('reminder-submit-btn');
  const submitSpan = submitBtn.querySelector('span');

  if (reminder) {
    title.textContent = 'Редактировать напоминание';
    if (submitSpan) submitSpan.textContent = 'Сохранить';
    document.getElementById('reminder-desc').value = reminder.description;
    const dt  = new Date(reminder.event_datetime);
    const pad = n => String(n).padStart(2, '0');
    document.getElementById('reminder-date').value =
      `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`;
    document.getElementById('reminder-time').value =
      `${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
    document.getElementById('reminder-count-input').value = reminder.message_count;
    document.getElementById('reminder-interval').value    = reminder.repeat_interval || '';
  } else {
    title.textContent = 'Новое напоминание';
    if (submitSpan) submitSpan.textContent = 'Создать';
    document.getElementById('reminder-desc').value        = '';
    document.getElementById('reminder-date').value        = '';
    document.getElementById('reminder-time').value        = '';
    document.getElementById('reminder-count-input').value = 3;
    document.getElementById('reminder-interval').value    = '';
  }

  document.getElementById('reminder-modal').classList.add('active');
}

function closeReminderModal() {
  document.getElementById('reminder-modal').classList.remove('active');
  editingReminderId = null;
}

async function submitReminder(e) {
  e.preventDefault();
  const btn = document.getElementById('reminder-submit-btn');
  const restore = spinBtn(btn);

  const desc     = document.getElementById('reminder-desc').value.trim();
  const dateVal  = document.getElementById('reminder-date').value;
  const timeVal  = document.getElementById('reminder-time').value;
  const count    = parseInt(document.getElementById('reminder-count-input').value, 10);
  const interval = document.getElementById('reminder-interval').value;

  const body = {
    description: desc,
    event_datetime: new Date(`${dateVal}T${timeVal}`).toISOString(),
    message_count: count,
  };
  if (interval) body.repeat_interval = interval;

  try {
    const res = editingReminderId
      ? await apiRequest('PUT',  `/reminders/${editingReminderId}`, body)
      : await apiRequest('POST', '/reminders/', body);

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      showToast(err.detail || 'Ошибка сохранения', 'error');
      return;
    }

    const updated = await res.json();
    if (editingReminderId) {
      const idx = reminders.findIndex(r => r.id === editingReminderId);
      if (idx !== -1) reminders[idx] = updated;
      showToast('Напоминание обновлено', 'success');
    } else {
      reminders.push(updated);
      showToast('Напоминание создано', 'success');
    }

    renderReminders();
    closeReminderModal();
  } catch { showToast('Ошибка сети', 'error'); }
  finally { restore(); }
}

async function deleteReminder(id) {
  try {
    const res = await apiRequest('DELETE', `/reminders/${id}`);
    if (res.status === 204 || res.ok) {
      reminders = reminders.filter(r => r.id !== id);
      renderReminders();
      showToast('Напоминание удалено', 'success');
    } else {
      showToast('Ошибка удаления', 'error');
    }
  } catch { showToast('Ошибка сети', 'error'); }
}

// ════════════════════════════════
//  CONFIRM MODAL
// ════════════════════════════════
function showDeleteConfirm() {
  pendingConfirmAction = deleteAccount;
  document.getElementById('confirm-title').textContent   = 'Удалить аккаунт?';
  document.getElementById('confirm-message').textContent = 'Это действие необратимо. Все ваши напоминания будут удалены.';
  document.getElementById('confirm-modal').classList.add('active');
}

function closeConfirmModal() {
  document.getElementById('confirm-modal').classList.remove('active');
  pendingConfirmAction = null;
}

async function confirmAction() {
  if (pendingConfirmAction) await pendingConfirmAction();
  closeConfirmModal();
}

async function deleteAccount() {
  try {
    const res = await apiRequest('DELETE', '/users/me');
    if (res.status === 204 || res.ok) {
      showToast('Аккаунт удалён', 'info');
      ss.clear();
      setTimeout(() => {
        currentUser = null;
        reminders = [];
        document.getElementById('auth-screen').style.display = 'flex';
        document.getElementById('dashboard').classList.remove('active');
      }, 1000);
    } else {
      showToast('Ошибка удаления аккаунта', 'error');
    }
  } catch { showToast('Ошибка сети', 'error'); }
}

// ════════════════════════════════
//  SIDEBAR
// ════════════════════════════════
function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  document.getElementById('sidebar').classList.toggle('collapsed', !sidebarOpen);
}

// ════════════════════════════════
//  WIRE UP EVENT LISTENERS
// ════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Auth tabs
  document.getElementById('tab-login').addEventListener('click',    () => switchTab('login'));
  document.getElementById('tab-register').addEventListener('click', () => switchTab('register'));

  // Auth forms
  document.getElementById('login-form').addEventListener('submit',    handleLogin);
  document.getElementById('register-form').addEventListener('submit', handleRegister);

  // Topbar / sidebar
  document.getElementById('topbar-avatar-btn').addEventListener('click', toggleSidebar);
  document.getElementById('logout-btn').addEventListener('click',         handleLogout);

  // Profile
  document.getElementById('edit-profile-btn').addEventListener('click',   toggleEditProfile);
  document.getElementById('save-profile-btn').addEventListener('click',   saveProfile);
  document.getElementById('cancel-profile-btn').addEventListener('click', toggleEditProfile);
  document.getElementById('delete-account-btn').addEventListener('click', showDeleteConfirm);

  // Reminder list
  document.getElementById('new-reminder-btn').addEventListener('click', () => openReminderModal(null));

  // Reminder modal
  document.getElementById('modal-close-btn').addEventListener('click',     closeReminderModal);
  document.getElementById('reminder-cancel-btn').addEventListener('click', closeReminderModal);
  document.getElementById('reminder-modal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeReminderModal();
  });
  document.getElementById('modal-form').addEventListener('submit', submitReminder);

  // Confirm modal
  document.getElementById('confirm-cancel-btn').addEventListener('click',  closeConfirmModal);
  document.getElementById('confirm-action-btn').addEventListener('click',  confirmAction);
  document.getElementById('confirm-modal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeConfirmModal();
  });

  // API URL sync
  document.getElementById('auth-api-url').addEventListener('input', e => setApiBase(e.target.value.trim()));
  document.getElementById('dashboard-api-url').addEventListener('input', e => setApiBase(e.target.value.trim()));

  // Init
  const savedBase = ss.get('apiBase') || `${location.origin}/api`;
  setApiBase(savedBase);
  document.getElementById('auth-api-url').value = savedBase;

  if (ss.get('accessToken')) initDashboard();
});
