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

// Mobile sidebar drawer: one pattern for user and admin layouts.
(function () {
  function setupDrawer() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('[data-sidebar-toggle]');
    const backdrop = document.querySelector('[data-sidebar-backdrop]');
    const closeButton = document.querySelector('[data-sidebar-close]');
    if (!sidebar || !toggle || !backdrop) return;

    function setOpen(open) {
      sidebar.classList.toggle('open', open);
      backdrop.classList.toggle('show', open);
      document.body.classList.toggle('drawer-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      if (open && closeButton) closeButton.focus();
      if (!open && window.innerWidth <= 768) toggle.focus();
    }

    toggle.addEventListener('click', function () {
      setOpen(!sidebar.classList.contains('open'));
    });
    if (closeButton) closeButton.addEventListener('click', function () { setOpen(false); });
    backdrop.addEventListener('click', function () { setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('open')) setOpen(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768 && sidebar.classList.contains('open')) setOpen(false);
    });
    sidebar.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 768) setOpen(false);
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setupDrawer);
  else setupDrawer();
})();

// Icon-only sidebar rail, remembered for the tab across page loads.
(function () {
  const button = document.querySelector('[data-sidebar-collapse]');
  if (!button) return;
  const root = document.documentElement;
  function setCollapsed(collapsed) {
    root.classList.toggle('sidebar-collapsed', collapsed);
    button.setAttribute('aria-expanded', String(!collapsed));
    button.setAttribute('aria-label', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
    button.querySelector('i').textContent = collapsed ? 'chevron_right' : 'chevron_left';
    sessionStorage.setItem('tolstoy_sidebar_collapsed', collapsed ? '1' : '0');
  }
  button.addEventListener('click', () => setCollapsed(!root.classList.contains('sidebar-collapsed')));
  // The class is already applied in <head>, so this only syncs the control state.
  setCollapsed(root.classList.contains('sidebar-collapsed'));
})();

// Closing the tab clears sessionStorage, so a load without the marker ends the session.
// shortcut: this also logs out a tab opened by hand while signed in, matching "close tab = sign out".
(function () {
  if (!document.body || !document.body.hasAttribute('data-auth')) return;
  if (sessionStorage.getItem('tolstoy_tab') === '1') return;
  fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'same-origin' })
    .catch(function () {})
    .then(function () { location.replace('/login'); });
})();