/**
 * auth.js — Login / Register UI logic.
 */

const Auth = (() => {

  function parseJwt(token) {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch {
      return null;
    }
  }

  function saveSession(tokenData) {
    Api.setToken(tokenData.access_token);
    const payload = parseJwt(tokenData.access_token);
    if (payload) {
      sessionStorage.setItem('tm_user_id',   payload.sub);
      sessionStorage.setItem('tm_user_email', payload.email);
      sessionStorage.setItem('tm_user_role',  payload.role);
    }
  }

  function clearSession() {
    Api.clearToken();
    sessionStorage.removeItem('tm_user_id');
    sessionStorage.removeItem('tm_user_email');
    sessionStorage.removeItem('tm_user_role');
  }

  function isLoggedIn() { return !!Api.getToken(); }
  function getRole()    { return sessionStorage.getItem('tm_user_role') || 'user'; }

  // ── Init event listeners ──────────────────────────────────
  function init() {
    // Toggle login/register panels
    document.getElementById('show-register').addEventListener('click', e => {
      e.preventDefault();
      document.getElementById('login-form').classList.add('hidden');
      document.getElementById('register-form').classList.remove('hidden');
    });
    document.getElementById('show-login').addEventListener('click', e => {
      e.preventDefault();
      document.getElementById('register-form').classList.add('hidden');
      document.getElementById('login-form').classList.remove('hidden');
    });

    // Password visibility toggles
    document.querySelectorAll('.toggle-password').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = document.getElementById(btn.dataset.target);
        input.type = input.type === 'password' ? 'text' : 'password';
        btn.textContent = input.type === 'password' ? '👁' : '🙈';
      });
    });

    // Login
    document.getElementById('btn-login').addEventListener('click', handleLogin);
    document.getElementById('login-password').addEventListener('keydown', e => {
      if (e.key === 'Enter') handleLogin();
    });

    // Register
    document.getElementById('btn-register').addEventListener('click', handleRegister);
    document.getElementById('reg-password').addEventListener('keydown', e => {
      if (e.key === 'Enter') handleRegister();
    });

    // Logout
    document.getElementById('btn-logout').addEventListener('click', logout);

    // Handle global session expiry
    window.addEventListener('auth:logout', logout);
  }

  async function handleLogin() {
    const email    = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) { Toast.show('Please enter your email and password', 'error'); return; }

    const btn = document.getElementById('btn-login');
    btn.disabled = true; btn.textContent = 'Signing in…';

    try {
      const data = await Api.login({ email, password });
      saveSession(data);
      App.showApp();
    } catch (err) {
      Toast.show(err.message, 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Sign In';
    }
  }

  async function handleRegister() {
    const full_name = document.getElementById('reg-fullname').value.trim();
    const username  = document.getElementById('reg-username').value.trim();
    const email     = document.getElementById('reg-email').value.trim();
    const password  = document.getElementById('reg-password').value;

    if (!username || !email || !password) { Toast.show('Please fill in all required fields', 'error'); return; }

    const btn = document.getElementById('btn-register');
    btn.disabled = true; btn.textContent = 'Creating account…';

    try {
      await Api.register({ full_name, username, email, password });
      Toast.show('Account created! Please sign in.', 'success');
      document.getElementById('register-form').classList.add('hidden');
      document.getElementById('login-form').classList.remove('hidden');
      document.getElementById('login-email').value = email;
    } catch (err) {
      Toast.show(err.message, 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Create Account';
    }
  }

  function logout() {
    clearSession();
    App.showAuth();
    Toast.show('You have been logged out', 'info');
  }

  return { init, isLoggedIn, getRole, clearSession };
})();
