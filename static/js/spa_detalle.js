// ================================
// OBTENER ID DESDE LA URL
// ================================
const params = new URLSearchParams(window.location.search);
const spaId = params.get("id");

if (!spaId) {
    alert("No se proporcionó un ID de spa");
    window.location.href = "/spas";
}

// ================================
// CARGAR TODA LA INFO DEL SPA
// ================================
document.addEventListener("DOMContentLoaded", () => {
    cargarSpaCompleto();
    // 🚨 NUEVO: Llamar a la función que configura el formulario de subida
    configurarFormularioSubida(); 
});

// ================================
// CARGA UN SOLO ENDPOINT: /spas/{id}
// ================================
async function cargarSpaCompleto() {
    try {
        const res = await apiFetch(`/spas/${spaId}`);

        if (!res.ok) {
            alert("Este spa no existe o está inactivo");
            return;
        }

        const spa = await res.json();

        // ================================
        // DATOS PRINCIPALES
        // ================================
        document.getElementById("spaNombre").innerText = spa.nombre;
        document.getElementById("spaDireccion").innerText = spa.direccion;
        document.getElementById("spaZona").innerText = spa.zona;
        document.getElementById("spaHorario").innerText = spa.horario ?? "No definido";
        document.getElementById("spaUpdate").innerText = spa.ultima_actualizacion ?? "-";
        document.getElementById("spaCalificacion").innerText = `⭐ ${spa.calificacion_promedio?.toFixed(1) ?? "0.0"} / 5`;

        // 🚨 Configurar el ID del Spa en el campo oculto del formulario de subida
        const spaIdInput = document.getElementById('spa_id_input');
        if (spaIdInput) {
            spaIdInput.value = spaId;
        }
        const rol = window.getRol();
        const seccionSubidaImagen = document.getElementById('seccionSubidaImagen');

        // Asumiendo que getUserId() y getRol() están disponibles globalmente (en app.js o config.js)
        // Y asumiendo que el objeto 'spa' contiene el 'admin_spa_id'
        const esAdminDeEsteSpa = (rol === "admin_spa" && spa.admin_spa_id == window.getUserId());
        const esAdminPrincipal = rol === "admin_principal";
        
        if (seccionSubidaImagen && (esAdminPrincipal || esAdminDeEsteSpa)) {
            // Si es admin principal o admin del spa, muestra la sección.
            seccionSubidaImagen.classList.remove('hidden'); 
        } else if (seccionSubidaImagen) {
            // Si no es admin, asegura que esté oculto.
            seccionSubidaImagen.classList.add('hidden');
        }

        // ================================
        // GALERÍA
        // ================================
        const contGaleria = document.getElementById("galeriaSpa");
        contGaleria.innerHTML = "";

        if (spa.imagenes && spa.imagenes.length > 0) {
            spa.imagenes.forEach(img_obj => { 
                const img = document.createElement("img");
                img.src = img_obj.url;
                img.alt = `Imagen de ${spa.nombre}`;
                img.className = "imagen-galeria-estilo"; 
                contGaleria.appendChild(img);
            });
        } else {
            contGaleria.innerHTML = "<p class='muted'>No hay imágenes disponibles para este Spa.</p>";
        }

        // ================================
        // SERVICIOS
        // ================================
        const contServicios = document.getElementById("listaServicios");
        contServicios.innerHTML = "";

        if (!spa.servicios || spa.servicios.length === 0) {
            contServicios.innerHTML = "<p>Este spa no tiene servicios</p>";
        } else {
            spa.servicios.forEach(s => {
                const div = document.createElement("div");
                div.className = "card-detalle-estilo";
                div.innerHTML = `
                    <h3 class="text-lg font-bold">${s.nombre}</h3>
                    <p><strong>Precio:</strong> $${s.precio}</p>
                    <p>${s.descripcion ?? ""}</p>
                `;
                contServicios.appendChild(div);
            });
        }

        // Botón de asociar servicio (admin)
        if (window.getRol() === "admin_principal") {
            const btnServ = document.createElement("button");
            btnServ.className = "bg-blue-600 text-white px-3 py-1 rounded mt-2";
            btnServ.innerText = "Asociar servicio a este spa";
            btnServ.onclick = () => asociarServicio();
            contServicios.parentElement.appendChild(btnServ);
        }

        // ================================
        // MATERIALES
        // ================================
        const contMateriales = document.getElementById("listaMateriales");
        contMateriales.innerHTML = "";

        if (!spa.materiales || spa.materiales.length === 0) {
            contMateriales.innerHTML = "<p>No hay materiales relacionados</p>";
        } else {
            spa.materiales.forEach(m => {
                const div = document.createElement("div");
                div.className = "card-detalle-estilo";
                div.innerHTML = `
                    <h3 class="text-lg font-bold">${m.nombre}</h3>
                    <p><strong>Tipo:</strong> ${m.tipo}</p>
                `;
                contMateriales.appendChild(div);
            });
        }

        // Botón de asociar material (admin)
        if (window.getRol() === "admin_principal") {
            const btnMat = document.createElement("button");
            btnMat.className = "bg-green-600 text-white px-3 py-1 rounded mt-2";
            btnMat.innerText = "Asociar material a este spa";
            btnMat.onclick = () => asociarMaterial();
            contMateriales.parentElement.appendChild(btnMat);
        }

        // ================================
        // RESEÑAS
        // ================================
        const contResenas = document.getElementById("listaResenas");
        contResenas.innerHTML = "";

        if (!spa.resenas || spa.resenas.length === 0) {
            contResenas.innerHTML = "<p>Este spa no tiene reseñas</p>";
        } else {
            spa.resenas.forEach(r => {
                const div = document.createElement("div");
                div.className = "card-detalle-estilo";
                div.innerHTML = `
                    <p><strong>${r.usuario_nombre}</strong> ⭐ ${r.calificacion}</p>
                    <p>${r.comentario}</p>
                    <p class="text-sm text-gray-600">${r.fecha}</p>
                `;
                contResenas.appendChild(div);
            });
        }

    } catch (err) {
        console.error("Error cargando spa:", err);
    }
}

// =====================================================
// FUNCIONES PARA SUBIR IMAGEN (NUEVO BLOQUE)
// =====================================================
function configurarFormularioSubida() {
    const form = document.getElementById('formSubidaImagen');
    const mensaje = document.getElementById('mensajeSubida');

    if (!form) return; 

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!spaId) {
            alert("Error interno: ID del Spa no disponible.");
            return;
        }

        mensaje.textContent = "Subiendo imagen, por favor espera...";
        mensaje.className = "mt-3 text-sm text-blue-600 font-semibold";
        mensaje.style.display = 'block';

        const formData = new FormData(form);
        const url = `/spas/${spaId}/imagenes`; 

        try {
            const response = await apiFetch(url, {
                method: 'POST',
                body: formData, 
            });

            const data = await response.json();

            if (response.ok) {
                mensaje.textContent = `✅ Imagen subida y registrada con éxito.`;
                mensaje.className = "mt-3 text-sm text-green-600 font-semibold";
                form.reset();
                cargarSpaCompleto(); 
            } else {
                const errorDetail = data.detail || 'Error desconocido del servidor.';
                mensaje.textContent = `❌ Error al subir: ${errorDetail}`;
                mensaje.className = "mt-3 text-sm text-red-600 font-semibold";
            }
        } catch (error) {
            mensaje.textContent = `❌ Error de red: No se pudo contactar al servidor.`;
            mensaje.className = "mt-3 text-sm text-red-600 font-semibold";
            console.error('Error de red:', error);
        }
    });
}

// =====================================================
// FUNCIONES PARA ASOCIAR SERVICIO / MATERIAL
// =====================================================
async function asociarServicio() {
    const servicioId = prompt("ID del servicio a asociar:");
    if (!servicioId) return;

    const precio = prompt("Precio del servicio en este spa:");
    if (!precio) return;

    const duracion = prompt("Duración del servicio (ej: '30 min'):");
    if (!duracion) return;

    try {
        const res = await apiFetch(`/servicios/asociar/${spaId}/${servicioId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ precio: parseFloat(precio), duracion })
        });

        if (!res.ok) {
            const e = await res.text();
            alert("Error: " + e);
            return;
        }

        alert("Servicio asociado correctamente");
        cargarSpaCompleto();
    } catch (err) {
        console.error(err);
    }
}

async function asociarMaterial() {
    const materialId = prompt("ID del material a asociar:");
    if (!materialId) return;

    try {
        const res = await apiFetch(`/materiales/asociar/${spaId}/${materialId}`, {
            method: "POST"
        });

        if (!res.ok) {
            const e = await res.text();
            alert("Error: " + e);
            return;
        }

        alert("Material asociado correctamente");
        cargarSpaCompleto();
    } catch (err) {
        console.error(err);
    }
}
