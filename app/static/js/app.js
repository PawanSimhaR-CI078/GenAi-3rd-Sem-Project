window.TOLSTOY = window.TOLSTOY || {};
window.TOLSTOY.csrfToken = null;

async function getCsrf() {
  if (window.TOLSTOY.csrfToken) return window.TOLSTOY.csrfToken;
  const r = await fetch('/api/v1/auth/csrf', { credentials: 'same-origin' });
  const j = await r.json();
  if (j.success) window.TOLSTOY.csrfToken = j.data.csrf_token;
  return window.TOLSTOY.csrfToken;
}

// Transparently attach CSRF token to mutating requests
const _origFetch = window.fetch.bind(window);
window.fetch = async function (input, init) {
  init = init || {};
  const method = (init.method || 'GET').toUpperCase();
  if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
    if (!window.TOLSTOY.csrfToken) await getCsrf();
    init.headers = init.headers || {};
    if (window.TOLSTOY.csrfToken && !init.headers['X-CSRFToken']) {
      init.headers['X-CSRFToken'] = window.TOLSTOY.csrfToken;
    }
    init.credentials = init.credentials || 'same-origin';
  }
  return _origFetch(input, init);
};