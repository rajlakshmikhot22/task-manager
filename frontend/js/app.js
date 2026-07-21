/**
 * app.js — Application bootstrap, routing, theme toggle, toast helper.
 */

// ── Toast Helper ─────────────────────────────────────────────
const Toast = (() => {
  const ICONS = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };

  function show(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${ICONS[type] || ICONS.info}</span>
      <span class="toast-msg">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
  }

  return { show };
})();

// ── Loader ────────────────────────────────────────────────────
const Loader = {
  show() { document.getElementById('global-loader').classList.remove('hidden'); },
  hide() { document.getElementById('global-loader').classList.add('hidden'); },
};

// ── App Controller ────────────────────────────────────────────
const App = (() => {
  let currentPage = 'dashboard';

  function showAuth() {
    document.getElementById('app').classList.add('hidden');
    document.getElementById('auth-overlay').classList.remove('hidden');
    // Reset login form
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('login-form').classList.remove('hidden');
  }

  function showApp() {
    document.getElementById('auth-overlay').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    navigateTo('dashboard');

    // Show admin nav if admin role
    if (Auth.getRole() === 'admin') {
      document.getElementById('admin-nav-item').style.display = '';
    }
    // Load profile info to populate sidebar/topbar
    Profile.load();
  }

  function navigateTo(page) {
    currentPage = page;

    // Update page title
    const titles = { dashboard: 'Dashboard', tasks: 'My Tasks', profile: 'Profile', admin: 'Admin Panel' };
    document.getElementById('page-title').textContent = titles[page] || page;

    // Show correct page
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const el = document.getElementById(`page-${page}`);
    if (el) el.classList.add('active');

    // Update nav items
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const nav = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (nav) nav.classList.add('active');

    // Close sidebar on mobile
    closeSidebar();

    // Load page data
    switch (page) {
      case 'dashboard': Dashboard.load(); Dashboard.setGreeting(); break;
      case 'tasks':     Tasks.load(1);    break;
      case 'profile':   Profile.load();   break;
      case 'admin':
        if (Auth.getRole() === 'admin') Admin.load();
        else { Toast.show('Access denied', 'error'); navigateTo('dashboard'); }
        break;
    }
  }

  function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('visible');
  }

  function initSidebar() {
    document.getElementById('menu-toggle').addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('open');
      document.getElementById('sidebar-overlay').classList.toggle('visible');
    });
    document.getElementById('sidebar-close').addEventListener('click', closeSidebar);
    document.getElementById('sidebar-overlay').addEventListener('click', closeSidebar);

    // Nav links
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', e => {
        e.preventDefault();
        navigateTo(item.dataset.page);
      });
    });
  }

  function initTheme() {
    const btn = document.getElementById('theme-toggle');
    const current = localStorage.getItem('tm_theme') || 'dark';
    applyTheme(current);

    btn.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('tm_theme', next);
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.getElementById('theme-toggle').textContent = theme === 'dark' ? '🌙' : '☀️';
  }

  function init() {
    // Apply saved theme immediately
    const savedTheme = localStorage.getItem('tm_theme') || 'dark';
    applyTheme(savedTheme);

    // Init sub-modules
    Auth.init();
    Tasks.init();
    Profile.init();
    initSidebar();
    initTheme();

    // Check existing session
    if (Auth.isLoggedIn()) {
      showApp();
    } else {
      showAuth();
    }
  }

  return { init, showAuth, showApp, navigateTo };
})();

// ── Boot ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => App.init());
