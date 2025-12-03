async function cargarUsuarios() {
    const resp = await apiFetch("/usuarios/");
    const usuarios = await resp.json();

    const statsResp = await apiFetch("/usuarios/stats");
    const stats = await statsResp.json();

    document.getElementById("total").textContent = stats.total;
    document.getElementById("activos").textContent = stats.activos;
    document.getElementById("bloqueados").textContent = stats.bloqueados;

    const tabla = document.getElementById("tablaUsuarios");
    tabla.innerHTML = "";

    usuarios.forEach(u => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${u.nombre}</td>
            <td>${u.correo}</td>
            <td>${u.rol}</td>
            <td>${u.activo ? "🟢 Activo" : "🔴 Bloqueado"}</td>
            <td>
                ${
                    u.activo
                    ? `<button class="btn btn-bloquear" data-id="${u.id}" data-action="bloquear">Desactivar</button>`
                    : `<button class="btn btn-activar" data-id="${u.id}" data-action="activar">Activar</button>`
                }
            </td>
        `;
        tabla.appendChild(tr);
    });
}

document.addEventListener("click", async (e) => {
    if (e.target.dataset.action === "bloquear") {
        await apiFetch(`/usuarios/desactivar/${e.target.dataset.id}`, { method: "PATCH" });
    }
    if (e.target.dataset.action === "activar") {
        await apiFetch(`/usuarios/activar/${e.target.dataset.id}`, { method: "PATCH" });
    }

    cargarUsuarios();
});

document.addEventListener("DOMContentLoaded", cargarUsuarios);
