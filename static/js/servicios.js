// static/js/servicios.js
document.addEventListener('DOMContentLoaded', () => {

  // ELEMENTOS
  const tablaServicios = document.getElementById("tablaServicios");
  const formContainer = document.getElementById("formContainer");
  const accionesAdmin = document.getElementById("acciones-admin");
  const btnMostrarCrear = document.getElementById("btnMostrarCrear");
  const btnCancelar = document.getElementById("btnCancelar");
  const form = document.getElementById("formServicio");

  let editando = false;

  // ==================================
  // CARGAR SERVICIOS
  // ==================================
  async function cargarServicios() {
    try {
      const resp = await window.apiFetch("/servicios/", { method: "GET" });
      if (!resp.ok) throw new Error("Error cargando servicios");

      const servicios = await resp.json();
      renderTabla(servicios);

      const rol = window.getRol();
      const esAdmin = (rol === "admin_principal");

      accionesAdmin.style.display = esAdmin ? "block" : "none";

      ajustarVisibilidadColumnas();

    } catch (err) {
      console.error("cargarServicios:", err);
      alert("No se pudieron cargar los servicios.");
    }
  }

  // ==================================
  // OCULTAR COLUMNAS SEGÚN ROL
  // ==================================
  function ajustarVisibilidadColumnas() {
    const thAcciones = document.getElementById("th-acciones");
    const rol = window.getRol();
    const esAdmin = (rol === "admin_principal");

    thAcciones.style.display = esAdmin ? "" : "none";
  }

  // ==================================
  // RENDER TABLA
  // ==================================
  function renderTabla(servicios) {
    tablaServicios.innerHTML = "";
    if (!Array.isArray(servicios)) return;

    const rol = window.getRol();
    const esAdmin = (rol === "admin_principal");

    servicios.forEach(s => {
      const fila = document.createElement("tr");

      const descripcion = s.descripcion ?? "-";
      const duracion = s.duracion_ref ?? "-";
      const precio = (s.precio_ref === null || s.precio_ref === undefined)
        ? "-"
        : Number(s.precio_ref).toFixed(2);

      const acciones = esAdmin
        ? `
            <button data-id="${s.id}" class="btn-editar">✏️</button>
            <button data-id="${s.id}" class="btn-eliminar">🗑️</button>
          `
        : "";

      fila.innerHTML = `
        <td>${s.id}</td>
        <td>${s.nombre}</td>
        <td>${descripcion}</td>
        <td>${duracion}</td>
        <td>${precio}</td>
        ${esAdmin ? `<td>${acciones}</td>` : ""}
      `;

      tablaServicios.appendChild(fila);
    });

    // Eventos SOLO si es admin
    if (esAdmin) {
      tablaServicios.querySelectorAll(".btn-editar").forEach(btn => {
        btn.addEventListener("click", (e) => {
          const id = Number(e.currentTarget.dataset.id);
          iniciarEdicion(id);
        });
      });

      tablaServicios.querySelectorAll(".btn-eliminar").forEach(btn => {
        btn.addEventListener("click", (e) => {
          const id = Number(e.currentTarget.dataset.id);
          confirmarEliminar(id);
        });
      });
    }
  }

  // ==================================
  // MOSTRAR FORMULARIO CREAR
  // ==================================
  btnMostrarCrear.addEventListener("click", () => {
    editando = false;
    form.reset();
    document.getElementById("servicioId").value = "";
    document.getElementById("tituloForm").innerText = "Crear Servicio";
    formContainer.style.display = "block";
  });

  // ==================================
  // CANCELAR
  // ==================================
  btnCancelar.addEventListener("click", () => {
    formContainer.style.display = "none";
  });

  // ==================================
  // GUARDAR (CREAR / EDITAR)
  // ==================================
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("servicioId").value;

    const payload = {
      nombre: document.getElementById("nombre").value.trim(),
      descripcion: document.getElementById("descripcion").value.trim() || undefined,
      duracion_ref: document.getElementById("duracion_ref").value.trim() || undefined,
    };

    const precioRaw = document.getElementById("precio_ref").value;
    if (precioRaw !== "") {
      const precioNum = Number(precioRaw);
      if (Number.isNaN(precioNum) || precioNum <= 0) {
        return alert("El precio debe ser un número mayor que 0.");
      }
      payload.precio_ref = precioNum;
    }

    try {
      let path = "/servicios/";
      let method = "POST";

      if (editando && id) {
        path = `/servicios/${id}`;
        method = "PATCH";
      }

      const resp = await window.apiFetch(path, {
        method,
        body: JSON.stringify(payload)
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: "Error" }));
        throw new Error(err.detail);
      }

      alert(editando ? "Servicio actualizado" : "Servicio creado");
      formContainer.style.display = "none";
      cargarServicios();

    } catch (err) {
      console.error("guardar:", err);
      alert(err.message || "Error al guardar.");
    }
  });

  // ==================================
  // INICIAR EDICIÓN
  // ==================================
  async function iniciarEdicion(id) {
    try {
      const resp = await window.apiFetch("/servicios/", { method: "GET" });
      if (!resp.ok) throw new Error("Error al obtener servicios");

      const servicios = await resp.json();
      const s = servicios.find(x => Number(x.id) === Number(id));
      if (!s) return alert("Servicio no encontrado");

      editando = true;

      document.getElementById("servicioId").value = s.id;
      document.getElementById("nombre").value = s.nombre ?? "";
      document.getElementById("descripcion").value = s.descripcion ?? "";
      document.getElementById("duracion_ref").value = s.duracion_ref ?? "";
      document.getElementById("precio_ref").value =
        (s.precio_ref === null || s.precio_ref === undefined) ? "" : s.precio_ref;

      document.getElementById("tituloForm").innerText = "Editar Servicio";
      formContainer.style.display = "block";

    } catch (err) {
      console.error("iniciarEdicion:", err);
      alert("Error al cargar servicio para edición.");
    }
  }

  // ==================================
  // ELIMINAR (REAL)
  // ==================================
  async function confirmarEliminar(id) {
    if (!confirm("¿Eliminar permanentemente este servicio?")) return;

    try {
      const resp = await window.apiFetch(`/servicios/${id}`, { method: "DELETE" });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: "Error" }));
        throw new Error(err.detail);
      }

      alert("Servicio eliminado.");
      cargarServicios();

    } catch (err) {
      console.error("eliminar:", err);
      alert(err.message || "Error eliminando servicio.");
    }
  }

  // ==================================
  // INICIALIZAR
  // ==================================
  cargarServicios();

});
