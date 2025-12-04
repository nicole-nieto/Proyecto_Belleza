// static/js/materiales.js
// Usa window.apiFetch (definido en app.js) y window.getRol()/getToken()

document.addEventListener("DOMContentLoaded", () => {
  // ELEMENTOS
  const tabla = document.getElementById("tablaMateriales");
  const mensajeDiv = document.getElementById("mensaje");
  const accionesAdmin = document.getElementById("acciones-admin");
  const btnMostrarCrear = document.getElementById("btnMostrarCrear");
  const formContainer = document.getElementById("formContainer");
  const form = document.getElementById("formMaterial");
  const btnCancelar = document.getElementById("btnCancelar");
  const tituloForm = document.getElementById("tituloForm");

  // Estado local
  let editando = false;

  // -----------------------
  // Helpers
  // -----------------------
  function showMessage(text, type = "info") {
    mensajeDiv.textContent = text || "";
    mensajeDiv.className = type;
    if (text) {
      // cleanup automático tras 4s
      clearTimeout(showMessage._t);
      showMessage._t = setTimeout(() => {
        mensajeDiv.textContent = "";
        mensajeDiv.className = "";
      }, 4000);
    }
  }

  async function safeApiFetch(path, options = {}) {
    // usa window.apiFetch tal cual lo tienes en app.js
    try {
      const resp = await window.apiFetch(path, options);
      return resp;
    } catch (err) {
      // window.apiFetch ya redirige en 401, pero capturamos el error para UX
      if (String(err).toLowerCase().includes("unauthorized")) {
        showMessage("Necesitas iniciar sesión para ver los materiales.", "error");
        // no redirigimos acá porque app.js ya lo hace si detecta 401
      } else if (String(err).toLowerCase().includes("network")) {
        showMessage("Error de red. Revisa tu conexión.", "error");
      } else {
        showMessage(err.message || "Error en la petición", "error");
      }
      throw err;
    }
  }

  async function apiJSON(path, options = {}) {
    const resp = await safeApiFetch(path, options);
    // si ya fue manejado por safeApiFetch y resp no existe, lanzar
    if (!resp) throw new Error("No response");
    if (!resp.ok) {
      // intentar leer json o texto
      let detail = "Error";
      try {
        const j = await resp.json();
        detail = j.detail || j.message || JSON.stringify(j);
      } catch {
        try { detail = await resp.text(); } catch {}
      }
      throw new Error(detail || `HTTP ${resp.status}`);
    }
    // body
    const contentType = resp.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return resp.json();
    } else {
      return resp.text();
    }
  }

  // -----------------------
  // Render tabla
  // -----------------------
  function renderTabla(materiales) {
    tabla.innerHTML = "";
    if (!Array.isArray(materiales)) return;

    materiales.forEach(m => {
      const tr = document.createElement("tr");

      // NombreSeguro
      const nombre = m.nombre ?? "-";
      const tipo = m.tipo ?? "-";

      // Solo mostrar botones si rol admin (lo determina el servidor, pero aquí UI)
      const rol = window.getRol();
      const esAdmin = (rol === "admin_principal");

      tr.innerHTML = `
        <td>${m.id}</td>
        <td>${escapeHtml(nombre)}</td>
        <td>${escapeHtml(tipo)}</td>
        <td class="col-acciones">${esAdmin ? `<button class="editar" data-id="${m.id}">✏️</button> <button class="eliminar" data-id="${m.id}">🗑️</button>` : ""}</td>
      `;

      tabla.appendChild(tr);
    });

    // Añadir listeners (delegación ligera)
    tabla.querySelectorAll(".editar").forEach(btn => {
      btn.addEventListener("click", () => iniciarEdicion(Number(btn.dataset.id)));
    });
    tabla.querySelectorAll(".eliminar").forEach(btn => {
      btn.addEventListener("click", () => confirmarEliminar(Number(btn.dataset.id)));
    });
  }

  // pequeño escapado para evitar inyección accidental en UI
  function escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str.replace(/[&<>"']/g, (s) => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[s]));
  }

  // -----------------------
  // Cargar
  // -----------------------
async function cargarMateriales() {
    showMessage("Cargando materiales...", "info");

    try {
        const materiales = await apiJSON("/materiales/", { method: "GET" });

        // mostrar tabla
        renderTabla(materiales);

        // mostrar acciones admin solo para admin_principal (CORREGIDO)
        const rol = window.getRol();
        
        if (rol === "admin_principal") { // <--- ✅ AHORA VERIFICAMOS SI ES ADMIN
            // Mostrar tanto el botón de crear como las columnas de acción
            accionesAdmin.style.display = "block"; // 🎯 ESTA ES LA LÍNEA CLAVE
            document.querySelectorAll(".col-acciones").forEach(el => el.style.display = "");
        } else {
            // Si no es admin, ocultamos ambos elementos
            accionesAdmin.style.display = "none";
            document.querySelectorAll(".col-acciones").forEach(el => el.style.display = "none");
        }

        showMessage("", "");
    } catch (err) {
        console.error("cargarMateriales:", err);
    }
}


  // -----------------------
  // Crear / Editar
  // -----------------------
  btnMostrarCrear && btnMostrarCrear.addEventListener("click", () => {
    editando = false;
    form.reset();
    document.getElementById("materialId").value = "";
    tituloForm.innerText = "Crear Material";
    formContainer.style.display = "block";
  });

  btnCancelar && btnCancelar.addEventListener("click", () => {
    formContainer.style.display = "none";
  });

  form && form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("materialId").value;
    const payload = {
      nombre: document.getElementById("nombre").value.trim(),
      tipo: document.getElementById("tipo").value.trim()
    };

    if (!payload.nombre) return showMessage("Nombre requerido", "error");

    try {
      if (editando && id) {
        // PATCH /materiales/{id}
        await apiJSON(`/materiales/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        showMessage("Material actualizado", "exito");
      } else {
        // POST /materiales/
        await apiJSON("/materiales/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        showMessage("Material creado", "exito");
      }

      formContainer.style.display = "none";
      cargarMateriales();
    } catch (err) {
      console.error("guardar material:", err);
      showMessage(err.message || "Error guardando material", "error");
    }
  });

  // -----------------------
  // Iniciar edición
  // -----------------------
  async function iniciarEdicion(id) {
    try {
      // traer lista actual para tomar el objeto (simple)
      const materiales = await apiJSON("/materiales/", { method: "GET" });
      const m = materiales.find(x => Number(x.id) === Number(id));
      if (!m) return showMessage("Material no encontrado", "error");

      editando = true;
      document.getElementById("materialId").value = m.id;
      document.getElementById("nombre").value = m.nombre ?? "";
      document.getElementById("tipo").value = m.tipo ?? "";
      tituloForm.innerText = "Editar Material";
      formContainer.style.display = "block";
    } catch (err) {
      console.error("iniciarEdicion:", err);
      showMessage("Error cargando material", "error");
    }
  }

  // -----------------------
  // Eliminar real
  // -----------------------
  async function confirmarEliminar(id) {
    if (!confirm("¿Eliminar permanentemente este material?")) return;
    try {
      await apiJSON(`/materiales/${id}`, { method: "DELETE" });
      showMessage("Material eliminado", "exito");
      cargarMateriales();
    } catch (err) {
      console.error("eliminar:", err);
      showMessage(err.message || "Error eliminando", "error");
    }
  }

  // -----------------------
  // Inicio
  // -----------------------
  cargarMateriales();
});
