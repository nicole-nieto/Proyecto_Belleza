// static/js/spas.js

async function cargarSpas(){
    try{
        const rol = window.getRol();
        let url = "/spas/";

        if (rol === "admin_principal") {
            url = "/spas/?incluir_inactivos=true";
        }

        const res = await apiFetch(url, { method: "GET" });

        if(!res.ok){
            document.getElementById("spaList").innerHTML = `<p>Error cargando spas</p>`;
            return;
        }

        const spas = await res.json();
        mostrarSpas(spas);
        checkAdmin();
    } catch (err){
        console.error("Error cargando spas:", err);
    }
}


async function buscarSpas(){
    const q = document.getElementById("inputBuscar").value.trim();
    const zona = document.getElementById("inputZona")?.value.trim() || "";

    if(q.length < 1 && zona.length < 1){
        cargarSpas();
        return;
    }

    const params = new URLSearchParams();
    if(q.length > 0) params.append("nombre", q);
    if(zona.length > 0) params.append("zona", zona);

    try{
        const res = await apiFetch(`/spas/buscar/?${params.toString()}`, { method: "GET" });

        if(!res.ok){
            document.getElementById("spaList").innerHTML = `<p>No se encontraron spas</p>`;
            return;
        }

        const spas = await res.json();
        mostrarSpas(spas);
    } catch (err){
        console.error("Error en búsqueda:", err);
    }
}

function mostrarSpas(spas){
    const contenedor = document.getElementById("spaList");
    contenedor.innerHTML = "";

    if(spas.length === 0){
        contenedor.innerHTML = `<p>No hay spas disponibles</p>`;
        return;
    }

    spas.forEach(spa => {
        const card = document.createElement("div");
        card.className = "bg-white shadow-md p-4 rounded";

        const rol = window.getRol();

        const estadoTexto = (!spa.activo)
            ? ` <span class="text-red-600">(desactivado)</span>`
            : "";

        let botonesAdmin = "";

        if(rol === "admin_principal"){

            if(!spa.activo){
                botonesAdmin = `
                    <button onclick="restaurarSpa(${spa.id})" 
                            class="bg-green-600 text-white px-3 py-1 mt-2 rounded w-full">
                        Restaurar
                    </button>
                `;
            } else {
                botonesAdmin = `
                    <button onclick="editarSpa(${spa.id})" 
                            class="bg-yellow-600 text-white px-3 py-1 mt-2 rounded w-full">
                        Editar
                    </button>
                    <button onclick="desactivarSpa(${spa.id})" 
                            class="bg-red-600 text-white px-3 py-1 mt-2 rounded w-full">
                        Desactivar
                    </button>
                `;
            }
        }

        card.innerHTML = `
            <h3 class="text-xl font-bold">${spa.nombre} ${estadoTexto}</h3>

            <p><strong>Dirección:</strong> ${spa.direccion}</p>
            <p><strong>Zona:</strong> ${spa.zona}</p>
            <p><strong>Horario:</strong> ${spa.horario ?? "No definido"}</p>

            <button onclick="verSpa(${spa.id})" 
                    class="bg-blue-600 text-white px-3 py-1 mt-3 rounded w-full">
                Ver
            </button>

            ${botonesAdmin}
        `;

        contenedor.appendChild(card);
    });
}



function verSpa(id) {
    window.location.href = `/spa_detalle?id=${id}`;
}


// ----------------- ADMIN OPTIONS -------------------

function checkAdmin(){
    const box = document.getElementById("adminActions");
    const rol = window.getRol();

    if(rol === "admin_principal"){
        box.innerHTML = `
            <button onclick="formCrearSpa()" 
                    class="bg-green-600 text-white px-3 py-1 rounded">
                + Crear Spa
            </button>
        `;
    } else {
        box.innerHTML = "";
    }
}


// ---------------- CREAR SPA --------------------

function formCrearSpa(){
    const nombre = prompt("Nombre del Spa:");
    if(!nombre) return;

    const direccion = prompt("Dirección:");
    if(!direccion) return;

    const zona = prompt("Zona:");
    if(!zona) return;

    const horario = prompt("Horario:");

    crearSpa(nombre, direccion, zona, horario);
}

async function crearSpa(nombre, direccion, zona, horario){
    try{
        const res = await apiFetch("/spas/", {
            method: "POST",
            body: JSON.stringify({ nombre, direccion, zona, horario })
        });

        if(res.ok){
            alert("Spa creado correctamente");
            cargarSpas();
        } else {
            const error = await res.json();
            alert("Error: " + error.detail);
        }
    } catch(err){
        console.error("Error creando spa:", err);
    }
}


// ---------------- EDITAR SPA ------------------

async function editarSpa(id){

    let payload = {};
    const nombre = prompt("Nuevo nombre:");
    if(nombre) payload.nombre = nombre;

    const direccion = prompt("Nueva dirección:");
    if(direccion) payload.direccion = direccion;

    const zona = prompt("Nueva zona:");
    if(zona) payload.zona = zona;

    const horario = prompt("Nuevo horario:");
    if(horario) payload.horario = horario;

    if(Object.keys(payload).length === 0){
        alert("No ingresaste ningún cambio");
        return;
    }

    try{
        const res = await apiFetch(`/spas/${id}`, {
            method: "PATCH",
            body: JSON.stringify(payload)
        });

        if(res.ok){
            alert("Spa actualizado");
            cargarSpas();
        } else {
            alert("Error editando spa");
        }

    } catch(err){
        console.error(err);
    }
}


// -------------- DESACTIVAR SPA -----------

async function desactivarSpa(id){
    if(!confirm("¿Seguro que deseas desactivar este spa?")) return;

    try{
        const res = await apiFetch(`/spas/${id}`, {
            method: "DELETE"
        });

        if(res.ok){
            alert("Spa desactivado");
            cargarSpas();
        } else {
            alert("Error al desactivar spa");
        }
    } catch(err){
        console.error(err);
    }
}


// -------------- RESTAURAR SPA ----------

async function restaurarSpa(id){
    if(!confirm("¿Restaurar este spa?")) return;

    try{
        const res = await apiFetch(`/spas/${id}/restore`, {
            method: "PATCH"
        });

        if(res.ok){
            alert("Spa restaurado");
            cargarSpas();
        } else {
            alert("Error restaurando spa");
        }
    } catch(err){
        console.error(err);
    }
}


// ------------------ INIT ---------------------

document.addEventListener("DOMContentLoaded", cargarSpas);
