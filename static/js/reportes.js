async function cargarDatos() {
    const resenasResp = await apiFetch("/reportes/resenas_por_spa");
    const promedioResp = await apiFetch("/reportes/promedio_por_spa");

    const resenas = await resenasResp.json();   // [{spa: "X", cantidad: 12}, ...]
    const promedios = await promedioResp.json(); // [{spa: "X", promedio: 4.3}, ...]

    generarGraficaResenas(resenas);
    generarGraficaPromedios(promedios);
    generarTop5(promedios);
}

function generarGraficaResenas(data) {
    const ctx = document.getElementById('chartResenasSpa');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(x => x.spa),
            datasets: [{
                label: "Cantidad de reseñas",
                data: data.map(x => x.cantidad),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
            }]
        }
    });
}

function generarGraficaPromedios(data) {
    const ctx = document.getElementById('chartPromedioSpa');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(x => x.spa),
            datasets: [{
                label: "Promedio de calificaciones",
                data: data.map(x => x.promedio),
                backgroundColor: 'rgba(255, 159, 64, 0.6)',
            }]
        }
    });
}

function generarTop5(data) {
    const sorted = [...data]
        .sort((a, b) => b.promedio - a.promedio)
        .slice(0, 3);

    const list = document.getElementById("top5");
    list.innerHTML = "";

    sorted.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.spa} — ${item.promedio}⭐`;
        list.appendChild(li);
    });
}

document.addEventListener("DOMContentLoaded", cargarDatos);
