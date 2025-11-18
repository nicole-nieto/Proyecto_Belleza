// static/js/app.js
const BACKEND = window.BACKEND_URL || (window.location.origin.includes("http") ? window.location.origin : "https://spas-a-tu-servicio.onrender.com");
const tokenKey = "bn_access_token";
const roleKey = "bn_user_role";

function getAuthHeaders() {
  const token = localStorage.getItem(tokenKey);
  return token ? { "Authorization": `Bearer ${token}` } : {};
}

function setLoggedState(isLogged, role){
  const btnLogout = document.getElementById("btn-logout");
  const navLogin = document.getElementById("nav-login");
  if(isLogged){
    btnLogout.classList.remove("hidden");
    navLogin.classList.add("hidden");
    if(role) localStorage.setItem(roleKey, role);
  } else {
    btnLogout.classList.add("hidden");
    navLogin.classList.remove("hidden");
    localStorage.removeItem(roleKey);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Inicial UI
  const token = localStorage.getItem(tokenKey);
  setLoggedState(!!token, localStorage.getItem(roleKey));

  // Logout
  const btnLogout = document.getElementById("btn-logout");
  if(btnLogout) btnLogout.addEventListener("click", () => {
    localStorage.removeItem(tokenKey);
    localStorage.removeItem(roleKey);
    setLoggedState(false);
    window.location.href = "/login";
  });

  // If on login page: handle login
  const loginForm = document.getElementById("login-form");
  if(loginForm){
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();
      const msg = document.getElementById("login-msg");
      try {
        const body = new URLSearchParams();
        body.append("username", email); // OAuth2Password uses username
        body.append("password", password);

        const res = await fetch(`${BACKEND}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body
        });
        const data = await res.json();
        if(!res.ok){
          msg.textContent = data.detail || data.message || "Error";
          return;
        }
        // Guardar token
        localStorage.setItem(tokenKey, data.access_token);
        localStorage.setItem(roleKey, data.rol || "");
        setLoggedState(true, data.rol);
        window.location.href = "/"; // redirigir home
      } catch (err){
        msg.textContent = "Error de conexión";
      }
    });
  }

  // Home page: buscar spas
  const searchBtn = document.getElementById("btn-buscar-spa");
  if(searchBtn){
    searchBtn.addEventListener("click", async () => {
      const nombre = document.getElementById("search-nombre").value.trim();
      const zona = document.getElementById("search-zona").value.trim();
      await loadSpas({ nombre, zona });
    });
    // cargar inicial
    loadSpas({});
  }

  // Spas page: refresh, crear
  const refreshSpasBtn = document.getElementById("btn-refresh-spas");
  if(refreshSpasBtn) refreshSpasBtn.addEventListener("click", () => loadSpas({}));

  const newSpaBtn = document.getElementById("btn-new-spa");
  if(newSpaBtn) {
    newSpaBtn.addEventListener("click", () => {
      document.getElementById("spa-form-panel").classList.remove("hidden");
      document.getElementById("spa-form-title").textContent = "Crear Spa";
      document.getElementById("spa-form").dataset.mode = "create";
    });
  }

  const spaForm = document.getElementById("spa-form");
  if(spaForm){
    spaForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const nombre = document.getElementById("spa-nombre").value.trim();
      const direccion = document.getElementById("spa-direccion").value.trim();
      const zona = document.getElementById("spa-zona").value.trim();
      const horario = document.getElementById("spa-horario").value.trim();
      const mode = spaForm.dataset.mode || "create";
      let url = `${BACKEND}/spas/`;
      let method = "POST";
      if(mode === "update"){
        const id = spaForm.dataset.spaId;
        url = `${BACKEND}/spas/${id}`;
        method = "PATCH";
      }
      try {
        const res = await fetch(url, {
          method,
          headers: { "Content-Type": "application/json", ...getAuthHeaders() },
          body: JSON.stringify({ nombre, direccion, zona, horario })
        });
        const data = await res.json();
        if(!res.ok){
          alert(data.detail || data.message || "Error al guardar spa");
        } else {
          alert("Spa guardado");
          document.getElementById("spa-form-panel").classList.add("hidden");
          spaForm.reset();
          loadSpas({});
        }
      } catch(err){ alert("Error de conexión"); }
    });

    document.getElementById("spa-cancel").addEventListener("click", () => {
      document.getElementById("spa-form-panel").classList.add("hidden");
    });
  }

  // Usuarios page: botones
  const btnCrearAdminSpa = document.getElementById("btn-crear-admin-spa");
  if(btnCrearAdminSpa){
    btnCrearAdminSpa.addEventListener("click", () => {
      document.getElementById("usuario-form-panel").classList.remove("hidden");
    });
  }
  const usuarioForm = document.getElementById("usuario-form");
  if(usuarioForm){
    usuarioForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const nombre = document.getElementById("u-nombre").value.trim();
      const correo = document.getElementById("u-correo").value.trim();
      const contrasena = document.getElementById("u-contrasena").value.trim();
      try {
        const res = await fetch(`${BACKEND}/usuarios/crear_admin_spa`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...getAuthHeaders() },
          body: JSON.stringify({ nombre, correo, contrasena })
        });
        const data = await res.json();
        if(!res.ok){
          alert(data.detail || data.message || "Error al crear admin spa");
        } else {
          alert("Admin spa creado");
          document.getElementById("usuario-form-panel").classList.add("hidden");
          loadUsuarios();
        }
      } catch(err){ alert("Error de conexión"); }
    });
    document.getElementById("u-cancel").addEventListener("click", () => {
      document.getElementById("usuario-form-panel").classList.add("hidden");
    });
  }

  // Materiales page: crear
  const newMaterialBtn = document.getElementById("btn-new-material");
  if(newMaterialBtn) newMaterialBtn.addEventListener("click", () => {
    document.getElementById("material-form-panel").classList.remove("hidden");
  });
  const materialForm = document.getElementById("material-form");
  if(materialForm){
    materialForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const nombre = document.getElementById("m-nombre").value.trim();
      const tipo = document.getElementById("m-tipo").value.trim();
      try {
        const res = await fetch(`${BACKEND}/materiales/`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...getAuthHeaders() },
          body: JSON.stringify({ nombre, tipo })
        });
        const data = await res.json();
        if(!res.ok) alert(data.detail || "Error");
        else { alert("Material creado"); document.getElementById("material-form-panel").classList.add("hidden"); loadMateriales(); }
      } catch(err){ alert("Error"); }
    });
    document.getElementById("m-cancel").addEventListener("click", () => {
      document.getElementById("material-form-panel").classList.add("hidden");
    });
  }

  // Botón de reportes
  const btnRefReportes = document.getElementById("btn-ref-reportes");
  if(btnRefReportes){
    btnRefReportes.addEventListener("click", async () => {
      try {
        const res = await fetch(`${BACKEND}/reportes/general`, { headers: getAuthHeaders() });
        const data = await res.json();
        document.getElementById("reportes-output").textContent = JSON.stringify(data, null, 2);
      } catch(e){ alert("Error"); }
    });
  }

  // Páginas que necesitan datos al cargar
  if(document.getElementById("spas-list")) loadSpas({});
  if(document.getElementById("usuarios-table")) loadUsuarios();
  if(document.getElementById("materiales-list")) loadMateriales();
  if(document.getElementById("mis-resenas")) loadMisResenas();

  // If spa detail page (spa_id provided via template variable)
  const spaDetailRoot = document.getElementById("spa-detail");
  if(spaDetailRoot){
    // spa_id should be in data attribute from template route
    const spaIdFromURL = (window.location.pathname.split("/").pop());
    loadSpaDetail(spaIdFromURL);
  }
});

/* ---------- funciones para consumo del API ---------- */

async function loadSpas(filters = {}) {
  let url = `${BACKEND}/spas`;
  const params = new URLSearchParams();
  if(filters.nombre) params.append("nombre", filters.nombre);
  if(filters.zona) params.append("zona", filters.zona);
  if(params.toString()) url = `${BACKEND}/spas/buscar/?${params.toString()}`;
  try {
    const res = await fetch(url, { headers: getAuthHeaders() });
    const data = await res.json();
    const cont = document.getElementById("spas-list");
    if(!cont) return;
    cont.innerHTML = "";
    if(!Array.isArray(data)) { cont.innerHTML = `<p>No hay spas</p>`; return; }
    data.forEach(spa => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<h3>${spa.nombre}</h3>
                        <p>${spa.direccion}</p>
                        <p>${spa.zona}</p>
                        <a class="btn" href="/spas/${spa.id}">Ver</a>`;
      cont.appendChild(card);
    });
  } catch(err){ console.error(err); }
}

async function loadSpaDetail(spaId) {
  try {
    const res = await fetch(`${BACKEND}/spas/${spaId}`, { headers: getAuthHeaders() });
    const spa = await res.json();
    if(!res.ok) { alert(spa.detail || "No se pudo cargar spa"); return; }
    document.getElementById("spa-name").textContent = spa.nombre;
    document.getElementById("spa-direction").textContent = `Dirección: ${spa.direccion}`;
    document.getElementById("spa-zone").textContent = `Zona: ${spa.zona}`;
    document.getElementById("spa-horario").textContent = `Horario: ${spa.horario}`;
    // cargar reseñas
    const resRes = await fetch(`${BACKEND}/resenas/por_spa/${spaId}`, { headers: getAuthHeaders() });
    const resenas = await resRes.json();
    const cont = document.getElementById("spa-resenas");
    cont.innerHTML = "";
    if(Array.isArray(resenas)){
      resenas.forEach(r => {
        const div = document.createElement("div");
        div.className = "card";
        div.innerHTML = `<strong>${r.calificacion}/5</strong> <p>${r.comentario}</p>`;
        cont.appendChild(div);
      });
    }
    // materiales
    const matRes = await fetch(`${BACKEND}/materiales/por_spa/${spaId}`, { headers: getAuthHeaders() });
    const mat = await matRes.json();
    const matList = document.getElementById("spa-materiales");
    matList.innerHTML = "";
    if(Array.isArray(mat)) {
      mat.forEach(m => {
        const li = document.createElement("li");
        li.textContent = `${m.nombre} (${m.tipo})`;
        matList.appendChild(li);
      });
    }
    // enviar reseña
    const btnEnviar = document.getElementById("btn-enviar-resena");
    if(btnEnviar){
      btnEnviar.onclick = async () => {
        const cal = parseInt(document.getElementById("resena-calificacion").value || 0);
        const com = document.getElementById("resena-comentario").value || "";
        try {
          const res = await fetch(`${BACKEND}/resenas/`, {
            method: "POST",
            headers: { "Content-Type":"application/json", ...getAuthHeaders() },
            body: JSON.stringify({ calificacion: cal, comentario: com, fecha_creacion: new Date().toISOString().split("T")[0], spa_id: parseInt(spaId), usuario_id: 0 })
          });
          const data = await res.json();
          if(!res.ok) alert(data.detail || "Error");
          else { alert("Reseña creada"); loadSpaDetail(spaId); }
        } catch(e){ alert("Error"); }
      };
    }
  } catch(e){ console.error(e); }
}

async function loadUsuarios(){
  try {
    const res = await fetch(`${BACKEND}/usuarios/`, { headers: getAuthHeaders() });
    const data = await res.json();
    const tbody = document.querySelector("#usuarios-table tbody");
    if(!tbody) return;
    tbody.innerHTML = "";
    if(!Array.isArray(data)) return;
    data.forEach(u => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${u.id}</td><td>${u.nombre}</td><td>${u.correo}</td><td>${u.rol}</td><td>${u.activo}</td>
        <td>
          <button class="btn-desactivar" data-id="${u.id}">Desactivar</button>
        </td>`;
      tbody.appendChild(tr);
    });
    document.querySelectorAll(".btn-desactivar").forEach(b => {
      b.addEventListener("click", async (ev) => {
        const id = ev.target.dataset.id;
        if(!confirm("Desactivar usuario?")) return;
        const res = await fetch(`${BACKEND}/usuarios/desactivar/${id}`, {
          method: "PATCH",
          headers: getAuthHeaders()
        });
        const d = await res.json();
        alert(d.message || d.detail || "OK");
        loadUsuarios();
      });
    });
  } catch(e){ console.error(e); }
}

async function loadMateriales(){
  try {
    const res = await fetch(`${BACKEND}/materiales/`, { headers: getAuthHeaders() });
    const data = await res.json();
    const cont = document.getElementById("materiales-list"); if(!cont) return;
    cont.innerHTML = "";
    data.forEach(m => {
      const card = document.createElement("div"); card.className = "card";
      card.innerHTML = `<h4>${m.nombre}</h4><p>${m.tipo}</p>`;
      cont.appendChild(card);
    });
  } catch(e){ console.error(e); }
}

async function loadMisResenas(){
  try {
    const res = await fetch(`${BACKEND}/resenas/mias`, { headers: getAuthHeaders() });
    const data = await res.json();
    const cont = document.getElementById("mis-resenas"); if(!cont) return;
    cont.innerHTML = "";
    data.forEach(r => {
      const card = document.createElement("div"); card.className = "card";
      card.innerHTML = `<strong>${r.calificacion}/5</strong><p>${r.comentario}</p>`;
      cont.appendChild(card);
    });
  } catch(e){ console.error(e); }
}
