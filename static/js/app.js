/* static/js/app.js
   Utilidades globales: gestión de sesión, fetch con token y control de nav.
   Funciona sin modules. */

(function () {
  // CONFIG: si pruebas local deja localhost, en producción deja '' para mismo dominio.
  const IS_LOCAL = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
  const LOCAL_API = 'http://localhost:8000'; // cambia a tu backend si lo necesitas
  window.API_BASE = IS_LOCAL ? LOCAL_API : ''; // si backend y frontend en mismo dominio, deja ''

  // SESSION
  window.saveSession = function (token, rol) {
    localStorage.setItem('token', token);
    localStorage.setItem('rol', rol || '');
  };
  window.getToken = function () { return localStorage.getItem('token'); };
  window.getRol = function () { return localStorage.getItem('rol'); };
  window.clearSession = function () { localStorage.removeItem('token'); localStorage.removeItem('rol'); };

  // fetch con token + manejo 401
  window.apiFetch = async function (path, options = {}) {
    const token = window.getToken();
    const headers = Object.assign(
      { 'Content-Type': 'application/json' },
      options.headers || {}
    );
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const final = Object.assign({}, options, { headers });
    const url = window.API_BASE + path;

    let resp;
    try {
      resp = await fetch(url, final);
    } catch (err) {
      // red offline
      throw new Error('network');
    }

    if (resp.status === 401) {
      // token inválido, limpiar sesión y redirigir a login
      window.clearSession();
      if (location.pathname !== '/login') location.href = '/login';
      throw new Error('unauthorized');
    }

    return resp;
  };

  // Nav: mostrar/ocultar botones de login/logout
  function updateNav() {
    const btnLogout = document.getElementById('btn-logout');
    const navLogin = document.getElementById('nav-login');
    if (!btnLogout || !navLogin) return;

    if (window.getToken()) {
      btnLogout.classList.remove('hidden');
      navLogin.classList.add('hidden');
    } else {
      btnLogout.classList.add('hidden');
      navLogin.classList.remove('hidden');
    }
  }

  // logout handler
  document.addEventListener('DOMContentLoaded', function () {
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.addEventListener('click', function () {
        window.clearSession();
        location.href = '/login';
      });
    }
    updateNav();
  });

  

})();
