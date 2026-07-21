/**
 * api.js — Centralised HTTP client for the Task Manager API.
 * All fetch calls go through this module so auth headers,
 * base URL, and error handling are handled in one place.
 */

const API_BASE = (window.API_BASE_URL || 'http://localhost:8000') + '/api/v1';

const Api = (() => {
  // ── Token storage ──────────────────────────────────────────
  const TOKEN_KEY = 'tm_access_token';

  function getToken()         { return localStorage.getItem(TOKEN_KEY); }
  function setToken(t)        { localStorage.setItem(TOKEN_KEY, t); }
  function clearToken()       { localStorage.removeItem(TOKEN_KEY); }

  // ── Core request helper ────────────────────────────────────
  async function request(method, path, body = null, opts = {}) {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const config = {
      method,
      headers,
      ...opts,
    };

    if (body && !(body instanceof FormData)) {
      config.body = JSON.stringify(body);
    } else if (body instanceof FormData) {
      // Let browser set multipart content-type automatically
      delete headers['Content-Type'];
      config.headers = headers;
      config.body = body;
    }

    const res = await fetch(`${API_BASE}${path}`, config);

    if (res.status === 401) {
      clearToken();
      window.dispatchEvent(new CustomEvent('auth:logout'));
      throw new Error('Session expired. Please log in again.');
    }

    let data;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      data = await res.json();
    } else {
      data = await res.text();
    }

    if (!res.ok) {
      const msg =
        (data && data.detail) ||
        (typeof data === 'string' ? data : null) ||
        `Request failed (${res.status})`;
      throw new Error(msg);
    }

    return data;
  }

  // ── Public API ─────────────────────────────────────────────
  return {
    getToken, setToken, clearToken,

    // Auth
    register:  (payload) => request('POST', '/auth/register', payload),
    login:     (payload) => request('POST', '/auth/login', payload),

    // Tasks
    getTasks:  (params = {}) => {
      const qs = new URLSearchParams(
        Object.fromEntries(Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== ''))
      ).toString();
      return request('GET', `/tasks${qs ? '?' + qs : ''}`);
    },
    getTaskStats: ()          => request('GET', '/tasks/stats'),
    createTask:   (payload)   => request('POST', '/tasks', payload),
    updateTask:   (id, p)     => request('PUT', `/tasks/${id}`, p),
    deleteTask:   (id)        => request('DELETE', `/tasks/${id}`),

    // Profile
    getProfile:     ()        => request('GET', '/profile'),
    updateProfile:  (p)       => request('PUT', '/profile', p),
    changePassword: (p)       => request('PUT', '/profile/password', p),
    uploadAvatar:   (form)    => request('POST', '/profile/avatar', form),

    // Admin
    adminGetUsers:  (p = 1, s = 20) => request('GET', `/admin/users?page=${p}&size=${s}`),
    adminDeleteUser:(id)       => request('DELETE', `/admin/users/${id}`),
    adminToggleUser:(id)       => request('PATCH', `/admin/users/${id}/toggle-active`),
  };
})();
