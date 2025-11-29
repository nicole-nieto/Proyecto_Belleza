// =============================
//    CARGAR MATERIALES
// =============================
document.addEventListener("DOMContentLoaded", () => {
    cargarMateriales();
    checkAdminMaterial();
});

let materialesGlobal = [];

async function cargarMateriales() {
    try {
        const rol = window.getRol();
        let url = "/materiales/";

        // Admin principal puede ver inactivos
        if (rol === "admin_principal") {
            url = "/materiales/?incluir_inactivos=true";
        }

        const res = await apiFetch(url, { method: "GET" });
        if (!res.ok) {
            console.error("Error cargando materiales");
            return;
        }

        materialesGlobal = await res.json();
        mostrarMateriales(materialesGlobal);

    } catch (err) {
        console.error("Error:", err);
    }
}

// =============================
//    MOSTRAR LISTA / TARJETAS
// =============================
function mostrarMateriales(lista) {
    const cont = document.getElementById("materialList");
    cont.innerHTML = "";

    if (lista.length === 0) {
        cont.innerHTML = `<p class="text-gray-600 text-center">No se encontraron materiales</p>`;
        return;
    }

    lista.forEach(mat => {
        
        // Estilo de tu captura (tarjeta rosada)
        const card = document.createElement("div");
        card.className = `
            bg-pink-300 
            p-4 
            rounded-xl 
            shadow 
            text-gray-900
        `;

        card.innerHTML = `
            <p class="font-bold">${mat.nombre}</p>
            <p class="text-sm">Tipo: ${mat.tipo ?? "N/A"}</p>

            ${mat.activo ? "" : `<p class="text-red-700 font-bold mt-1">(Desactivado)</p>`}
        `;

        const rol = window.getRol();
        if (rol === "admin_principal" || rol === "admin_spa") {
            const btns = document.createElement("div");
            btns.className = "mt-3 flex gap-2";

            // Editar
            const btnEditar = document.createElement("button");
            btnEditar.textContent = "Editar";
            btnEditar.className = "px-2 py-1 bg-blue-600 text-white rounded";
            btnEditar.onclick = () => abrirModalEditar(mat);

            // Eliminar / Restaurar
            const btnEliminar = document.createElement("button");
            btnEliminar.textContent = mat.activo ? "Desactivar" : "Restaurar";
            btnEliminar.className = mat.activo ?
                "px-2 py-1 bg-red-600 text-white rounded" :
                "px-2 py-1 bg-green-600 text-white rounded";

            btnEliminar.onclick = () => toggleMaterial(mat.id, mat.activo);

            btns.appendChild(btnEditar);
            btns.appendChild(btnEliminar);
            card.appendChild(btns);
        }

        cont.appendChild(card);
    });
}

// =============================
//     BUSCADOR EN TIEMPO REAL
// =============================
function buscarMateriales() {
    const txt = document.getElementById("inputBuscar").value.toLowerCase();

    const filtrados = materialesGlobal.filter(m =>
        m.nombre.toLowerCase().includes(txt) ||
        (m.tipo && m.tipo.toLowerCase().includes(txt))
    );

    mostrarMateriales(filtrados);
}

// =============================
//      MODAL CREAR / EDITAR
// =============================
let editandoID = null;

function abrirModalCrear() {
    editandoID = null;
    document.getElementById("modalTitulo").innerText = "Crear Material";
    document.getElementById("matNombre").value = "";
    document.getElementById("matTipo").value = "";
    document.getElementById("modalMaterial").classList.remove("hidden");
}

function abrirModalEditar(mat) {
    editandoID = mat.id;
    document.getElementById("modalTitulo").innerText = "Editar Material";
    document.getElementById("matNombre").value = mat.nombre;
    document.getElementById("matTipo").value = mat.tipo;
    document.getElementById("modalMaterial").classList.remove("hidden");
}

function cerrarModal() {
    document.getElementById("modalMaterial").classList.add("hidden");
}

// =============================
//    GUARDAR (Crear / Editar)
// =============================
async function guardarMaterial() {
    const nombre = document.getElementById("matNombre").value.trim();
    const tipo = document.getElementById("matTipo").value.trim();

    if (!nombre) {
        alert("El nombre es obligatorio");
        return;
    }

    const datos = { nombre, tipo };

    let res;

    // EDITAR
    if (editandoID) {
        res = await apiFetch(`/materiales/${editandoID}`, {
            method: "PATCH",
            body: JSON.stringify(datos),
        });
    }
    // CREAR
    else {
        res = await apiFetch("/materiales/", {
            method: "POST",
            body: JSON.stringify(datos),
        });
    }

    if (!res.ok) {
        alert("Error guardando material");
        return;
    }

    cerrarModal();
    cargarMateriales();
}

// =============================
//  DESACTIVAR / RESTAURAR
// =============================
async function toggleMaterial(id, activo) {
    if (activo) {
        // desactivar
        const res = await apiFetch(`/materiales/${id}`, { method: "DELETE" });
        if (!res.ok) return alert("Error desactivando material");
    } else {
        // restaurar
        const res = await apiFetch(`/materiales/${id}`, {
            method: "PATCH",
            body: JSON.stringify({ activo: true, nombre: "placeholder", tipo: "" })
        });
        if (!res.ok) return alert("Error restaurando material");
    }

    cargarMateriales();
}

// =============================
//   MOSTRAR BOTÓN CREAR SOLO ADMIN
// =============================
function checkAdminMaterial() {
    const rol = window.getRol();
    const cont = document.getElementById("adminActions");

    if (rol === "admin_principal" || rol === "admin_spa") {
        cont.innerHTML = `
            <button onclick="abrirModalCrear()"
                    class="px-4 py-2 bg-green-600 text-white rounded">
                + Crear Material
            </button>
        `;
    }
}
