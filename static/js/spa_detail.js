// static/js/spa_detail.js

async function fetchDetail(id) {
  const possible = [
    `/spa/${id}`,
    `/spas/${id}`,
    `/spa/detail/${id}`
  ];

  for (const p of possible) {
    try {
      const resp = await fetch((location.hostname === 'localhost' ? 'http://localhost:8000' : '') + p);
      if (resp.ok) return await resp.json();
    } catch (err) { /* sigue intentando */ }
  }
  return null;
}

function renderDetail(spa) {
  const el = document.getElementById('detail-content');
  el.classList.remove('hidden');
  el.innerHTML = `
    <h2>${spa.nombre || spa.name}</h2>
    <p class="muted">${spa.zona || spa.direccion || ''}</p>
    <p>${spa.descripcion || ''}</p>

    <h3>Servicios</h3>
    <ul>
      ${(spa.servicios || spa.services || []).map(s => `<li>${s.nombre || s.name} — ${s.precio || ''}</li>`).join('')}
    </ul>

    <h3>Reseñas</h3>
    <div>
      ${(spa.resenas || spa.reviews || []).map(r => `<div class="review"><strong>${r.autor || r.usuario || 'Anónimo'}</strong><p>${r.comentario || r.text}</p></div>`).join('') || '<p>No hay reseñas aún.</p>'}
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', async () => {
  const loading = document.getElementById('loading');
  const data = await fetchDetail(typeof SPA_ID === 'undefined' ? null : SPA_ID);
  if (!data) {
    loading.innerText = 'No se encontró el spa o hubo error de conexión.';
    return;
  }
  loading.remove();
  renderDetail(data);
});
