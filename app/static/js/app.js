// TOLSTOY shared JS helpers
window.TOLSTOY = window.TOLSTOY || {};
window.TOLSTOY.csrfToken = null;
async function getCsrf(){ if(window.TOLSTOY.csrfToken) return window.TOLSTOY.csrfToken; const r=await fetch('/api/v1/auth/csrf',{credentials:'same-origin'}); const j=await r.json(); if(j.success){ window.TOLSTOY.csrfToken=j.data.csrf_token; } return window.TOLSTOY.csrfToken; }