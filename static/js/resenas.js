// static/js/resenas.js
// Depende de: /static/js/app.js (apiFetch, getToken, getRol, saveSession)

(function () {
  const spaSelect = document.getElementById('spa-select');
  const spaFilter = document.getElementById('spa-filter');
  const form = document.getElementById('form-resena');
  const resenasList = document.getElementById('resenas-list');
  const misResenasList = document.getElementById('mis-resenas-list');
  const sinSesionMsg = document.getElementById('sin-sesion-msg');
  const btnCargar = document.getElementById('btn-cargar');

  // Inicializar
  document.addEventListener('DOMContentLoaded', init);

  async function init() {
    try {
      await cargarSpas();
      actualizarUIParaSesion();
      bindEvents();
      // Si existe token y hay un spa seleccionado por defecto, cargar sus reseñas
      if (spaFilter.value) await cargarResenasPorSpa(spaFilter.value);
      await cargarMisResenas();
    } catch (err) {
      console.error('init error', err);
    }
  }

  function actualizarUIParaSesion() {
    const token = window.getToken();
    const rol = window.getRol();
    if (!token || rol !== 'usuario') {
      sinSesionMsg.classList.remove('hidden');
      form.querySelectorAll('input,textarea,select,button').forEach(el => el.disabled = true);
    } else {
      sinSesionMsg.classList.add('hidden');
      form.querySelectorAll('input,textarea,select,button').forEach(el => el.disabled = false);
    }
  }

  function bindEvents() {
    form.addEventListener('submit', handleCrearResena);
    btnCargar.addEventListener('click', async (e) => {
      e.preventDefault();
      const spaId = spaFilter.value;
      if (!spaId) return alert('Selecciona un spa para cargar reseñas');
      await cargarResenasPorSpa(spaId);
    });
  }

  // Carga la lista de spas para los selects
  async function cargarSpas() {
    try {
        const res = await apiFetch("/spas/", { method: "GET" });

        if (!res.ok) {
            console.error("Error cargando spas:", res.status);
            return;
        }

        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const text = await res.text();
            console.error("Respuesta NO JSON del servidor:", text);
            return;
        }

const spas = await res.json();


      // limpiar y agregar
      spaSelect.innerHTML = '<option value="">-- Selecciona un spa --</option>';
      spaFilter.innerHTML = '<option value="">-- Selecciona un spa --</option>';

      spas.forEach(s => {
        if (!s.activo) return; // mostrar solo activos
        const opt1 = document.createElement('option');
        opt1.value = s.id;
        opt1.textContent = `${s.nombre} — ${s.zona || ''}`;
        spaSelect.appendChild(opt1);

        const opt2 = opt1.cloneNode(true);
        spaFilter.appendChild(opt2);
      });

    } catch (err) {
      console.error('cargarSpas', err);
      spaSelect.innerHTML = '<option value="">Error cargando spas</option>';
      spaFilter.innerHTML = '<option value="">Error cargando spas</option>';
    }
  }

  // Cargar reseñas por spa (visibles al público)
  async function cargarResenasPorSpa(spaId) {
    resenasList.innerHTML = '<p>Cargando reseñas...</p>';
    try {
      const resp = await apiFetch(`/resenas/por_spa/${spaId}`);
      if (!resp.ok) {
        if (resp.status === 404) resenasList.innerHTML = '<p>Spa no encontrado o inactivo.</p>';
        else throw new Error('Error al cargar reseñas');
        return;
      }
      const resenas = await resp.json();
      renderResenas(resenas, resenasList, { allowEdit: false });
    } catch (err) {
      console.error('cargarResenasPorSpa', err);
      resenasList.innerHTML = '<p>Error cargando reseñas.</p>';
    }
  }

  // Cargar mis reseñas (el usuario autenticado)
  async function cargarMisResenas() {
    misResenasList.innerHTML = '<p>Cargando mis reseñas...</p>';
    // solo si hay token
    if (!window.getToken()) {
      misResenasList.innerHTML = '<p>Inicia sesión para ver tus reseñas.</p>';
      return;
    }
    try {
      const resp = await apiFetch('/resenas/mias');
      if (!resp.ok) {
        if (resp.status === 401) misResenasList.innerHTML = '<p>No autorizado. Inicia sesión.</p>';
        else throw new Error('Error al cargar mis reseñas');
        return;
      }
      const resenas = await resp.json();
      if (!resenas.length) misResenasList.innerHTML = '<p>No tienes reseñas publicadas.</p>';
      else renderResenas(resenas, misResenasList, { allowEdit: true });
    } catch (err) {
      console.error('cargarMisResenas', err);
      misResenasList.innerHTML = '<p>Error cargando tus reseñas.</p>';
    }
  }

  // Render general de reseñas dentro de un contenedor
  function renderResenas(resenas, container, opts = { allowEdit: false }) {
    container.innerHTML = '';
    resenas.forEach(r => {
      const card = document.createElement('article');
      card.className = 'resena-card';
      card.dataset.id = r.id;

      const header = document.createElement('div');
      header.className = 'resena-header';
      header.innerHTML = `<strong>${r.spa_nombre || ''}</strong> — <span class="small">${formatDate(r.fecha_creacion)}</span>`;

      const score = document.createElement('div');
      score.className = 'resena-score';
      score.textContent = `${r.calificacion} / 5`;

      const body = document.createElement('p');
      body.className = 'resena-text';
      body.textContent = r.comentario;

      const byline = document.createElement('div');
      byline.className = 'resena-user';
      byline.textContent = r.usuario_nombre ? `Por: ${r.usuario_nombre}` : '';

      const actions = document.createElement('div');
      actions.className = 'resena-actions';
      // Si es usuario normal y dueño de la reseña → puede editar/eliminar
      if (opts.allowEdit) {
        const btnEdit = document.createElement('button');
        btnEdit.textContent = 'Editar';
        btnEdit.addEventListener('click', () => abrirEditorEnLinea(r, card));
        
        const btnDelete = document.createElement('button');
        btnDelete.textContent = 'Eliminar';
        btnDelete.addEventListener('click', () => eliminarResena(r.id, card));

        actions.appendChild(btnEdit);
        actions.appendChild(btnDelete);
        }
        // Si es admin principal → puede eliminar cualquier reseña
        if (window.getRol() === "admin_principal") {
            const btnDeleteAdmin = document.createElement('button');
            btnDeleteAdmin.textContent = 'Eliminar (Admin)';
            btnDeleteAdmin.classList.add('btn-eliminar-resena-admin');
            btnDeleteAdmin.dataset.id = r.id;
            actions.appendChild(btnDeleteAdmin);
        }

      card.appendChild(header);
      card.appendChild(score);
      card.appendChild(body);
      card.appendChild(byline);
      card.appendChild(actions);

      container.appendChild(card);
    });
  }

  // Formatear fecha AAAA-MM-DD -> DD/MM/YYYY
  function formatDate(d) {
    try {
      const date = new Date(d);
      return `${date.getDate().toString().padStart(2,'0')}/${(date.getMonth()+1).toString().padStart(2,'0')}/${date.getFullYear()}`;
    } catch (e) { return d; }
  }

  // Crear reseña
  async function handleCrearResena(e) {
    e.preventDefault();
    const spaId = spaSelect.value;
    const calificacion = Number(document.getElementById('calificacion').value);
    const comentario = document.getElementById('comentario').value.trim();

    if (!spaId) return alert('Selecciona un spa');
    if (!calificacion || calificacion < 1 || calificacion > 5) return alert('Selecciona una calificación válida');
    if (!comentario) return alert('Escribe un comentario');

    const payload = { calificacion, comentario, spa_id: Number(spaId) };

    try {
      const resp = await apiFetch('/resenas/', { method: 'POST', body: JSON.stringify(payload) });
      if (!resp.ok) {
        const err = await resp.json().catch(()=>null);
        alert(err?.detail || 'Error creando reseña');
        return;
      }
      const nueva = await resp.json();
      alert('Reseña publicada');
      form.reset();
      // refrescar vistas
      if (spaFilter.value == spaId) await cargarResenasPorSpa(spaId);
      await cargarMisResenas();
    } catch (err) {
      console.error('handleCrearResena', err);
      alert('Error de red al crear reseña');
    }
  }

  // Abrir editor en linea dentro de la tarjeta
  function abrirEditorEnLinea(resena, card) {
    // reemplazar contenido por un pequeño formulario
    card.innerHTML = '';

    const formEdit = document.createElement('form');
    formEdit.className = 'resena-edit-form';

    const scoreLabel = document.createElement('label');
    scoreLabel.textContent = 'Calificación';
    const scoreSel = document.createElement('select');
    [5,4,3,2,1].forEach(n => {
      const o = document.createElement('option'); o.value = n; o.textContent = n; if (n===resena.calificacion) o.selected = true; scoreSel.appendChild(o);
    });

    const txtLabel = document.createElement('label'); txtLabel.textContent = 'Comentario';
    const textarea = document.createElement('textarea'); textarea.rows = 4; textarea.value = resena.comentario;

    const spaLabel = document.createElement('label'); spaLabel.textContent = 'Spa (id)';
    const spaInput = document.createElement('input'); spaInput.type='number'; spaInput.value = resena.spa_id;

    const btnSave = document.createElement('button'); btnSave.type='submit'; btnSave.textContent='Guardar';
    const btnCancel = document.createElement('button'); btnCancel.type='button'; btnCancel.textContent='Cancelar';

    formEdit.appendChild(scoreLabel); formEdit.appendChild(scoreSel);
    formEdit.appendChild(txtLabel); formEdit.appendChild(textarea);
    formEdit.appendChild(spaLabel); formEdit.appendChild(spaInput);
    formEdit.appendChild(btnSave); formEdit.appendChild(btnCancel);

    btnCancel.addEventListener('click', () => { cargarMisResenas(); });

    formEdit.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const data = {
        calificacion: Number(scoreSel.value),
        comentario: textarea.value.trim(),
        spa_id: Number(spaInput.value)
      };
      if (!data.comentario) return alert('Comentario vacío');
      try {
        const resp = await apiFetch(`/resenas/${resena.id}`, { method: 'PATCH', body: JSON.stringify(data) });
        if (!resp.ok) {
          const err = await resp.json().catch(()=>null);
          alert(err?.detail || 'Error al actualizar');
          return;
        }
        alert('Reseña actualizada');
        await cargarMisResenas();
        if (spaFilter.value) await cargarResenasPorSpa(spaFilter.value);
      } catch (err) {
        console.error('editar', err);
        alert('Error de red al actualizar reseña');
      }
    });

    card.appendChild(formEdit);
  }

  // Eliminar reseña (lógico)
  async function eliminarResena(id, card) {
    if (!confirm('¿Eliminar esta reseña? Esto la desactivará (no se eliminará permanentemente).')) return;
    try {
      const resp = await apiFetch(`/resenas/${id}`, { method: 'DELETE' });
      if (!resp.ok) {
        const err = await resp.json().catch(()=>null);
        alert(err?.detail || 'Error al eliminar');
        return;
      }
      alert('Reseña desactivada');
      // refrescar mis reseñas y la vista por spa
      await cargarMisResenas();
      if (spaFilter.value) await cargarResenasPorSpa(spaFilter.value);
    } catch (err) {
      console.error('eliminarResena', err);
      alert('Error de red al eliminar');
    }
  }

  document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("btn-eliminar-resena-admin")) {
        const id = e.target.dataset.id;
        if (!confirm("¿Eliminar definitivamente esta reseña?")) return;

        try {
            const res = await apiFetch(`/resenas/${id}`, { method: "DELETE" });

            if (res.ok) {
                alert("Reseña eliminada por administrador principal");
                if (spaFilter.value) await cargarResenasPorSpa(spaFilter.value);
                await cargarMisResenas();
            } else {
                alert("No se pudo eliminar la reseña");
            }
        } catch (err) {
            console.error("Error eliminando como admin:", err);
        }
    }
});

})();
