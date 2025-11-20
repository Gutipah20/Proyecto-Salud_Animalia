const API_BASE = '';

async function apiRequest(path, method = 'GET', data = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (data) opts.body = JSON.stringify(data);

  try {
    const res = await fetch(API_BASE + path, opts);
    return await res.json();
  } catch (error) {
    console.error('API Request Error:', error);
    return { ok: false, error: 'Error de conexión' };
  }
}

async function crearReserva(e) {
  e.preventDefault();

  const user = JSON.parse(localStorage.getItem('user'));
  if (!user) {
    alert('Inicia sesión primero');
    window.location.href = '/login';
    return;
  }

  const mascota = document.getElementById('res-mascota').value.trim();
  const motivo = document.getElementById('res-motivo').value.trim();
  const fechaInput = document.getElementById('res-fecha').value;

  if (!mascota || !motivo || !fechaInput) {
    alert('Por favor completa todos los campos obligatorios');
    return;
  }

  const fecha = new Date(fechaInput).toISOString();

  const submitBtn = e.target.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Agendando...';

  try {
    const res = await apiRequest('/api/reservas', 'POST', {
      user_id: user.id,
      mascota: mascota,
      motivo: motivo,
      fecha: fecha,
    });

    if (res.ok) {
      alert('¡Cita agendada exitosamente!');
      document.getElementById('form-reserva').reset();

      if (typeof cargarMisReservas === 'function') {
        await cargarMisReservas();
      }
      if (typeof cargarReservas === 'function') {
        await cargarReservas();
      }
    } else {
      alert(res.error || 'No se pudo crear la reserva');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error al crear la reserva');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Agendar Cita';
  }
}

async function cargarMisReservas() {
  const user = JSON.parse(localStorage.getItem('user'));
  if (!user) return;

  const container = document.getElementById('mis-reservas');
  if (!container) return;

  try {
    const res = await apiRequest(`/api/reservas?user_id=${user.id}`, 'GET');

    if (res.ok && res.reservas && res.reservas.length > 0) {
      container.innerHTML = res.reservas
        .map((r) => {
          const fecha = new Date(r.fecha);
          const fechaFormateada = fecha.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          });

          return `
            <div class="card" style="padding: 12px; margin-bottom: 10px; background: #f9f9f9;">
              <h4 style="margin: 0 0 8px 0; color: var(--brand);">🐾 ${r.mascota}</h4>
              <p style="margin: 4px 0; font-size: 0.9rem;"><strong>Motivo:</strong> ${r.motivo}</p>
              <p style="margin: 4px 0; font-size: 0.9rem;"><strong>Fecha:</strong> ${fechaFormateada}</p>
              <button class="btn" onclick="eliminarReserva(${r.id})" 
                      style="margin-top: 8px; padding: 6px 12px; font-size: 0.85rem; background: #dc3545;">
                Cancelar Cita
              </button>
            </div>
          `;
        })
        .join('');
    } else {
      container.innerHTML = '<p class="help">No tienes reservas agendadas.</p>';
    }
  } catch (error) {
    console.error('Error al cargar reservas:', error);
    container.innerHTML = '<p class="help">Error al cargar las reservas.</p>';
  }
}

async function cargarReservas() {
  const user = JSON.parse(localStorage.getItem('user'));
  if (!user) return;

  const tbody = document.getElementById('tabla-reservas');
  if (!tbody) return;

  const admin = user.role === 'admin';
  const url = admin
    ? '/api/reservas/admin'
    : `/api/reservas?user_id=${user.id}`;

  tbody.innerHTML =
    '<tr><td colspan="7" style="text-align:center;padding:2rem;">Cargando...</td></tr>';

  try {
    const res = await apiRequest(url, 'GET');

    if (res.ok && res.reservas && res.reservas.length) {
      tbody.innerHTML = '';

      res.reservas.forEach((r) => {
        const tr = document.createElement('tr');
        const fecha = new Date(r.fecha).toLocaleString('es-ES');

        tr.innerHTML = `
          <td style="padding:8px;border:1px solid #ddd;">${r.id}</td>
          ${
            admin
              ? `<td style="padding:8px;border:1px solid #ddd;">${
                  r.user_name || 'N/A'
                }</td>`
              : ''
          }
          <td style="padding:8px;border:1px solid #ddd;">${r.mascota}</td>
          <td style="padding:8px;border:1px solid #ddd;">${r.motivo}</td>
          <td style="padding:8px;border:1px solid #ddd;">${fecha}</td>
          <td style="padding:8px;border:1px solid #ddd;">
            <button onclick="eliminarReserva(${r.id})">Eliminar</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      const colspan = admin ? '6' : '5';
      tbody.innerHTML = `<tr><td colspan='${colspan}' style='padding:8px;border:1px solid #ddd;text-align:center;'>No hay reservas</td></tr>`;
    }
  } catch (error) {
    console.error('Error:', error);
    tbody.innerHTML =
      '<tr><td colspan="7" style="text-align:center;padding:2rem;color:red;">Error al cargar reservas</td></tr>';
  }
}

async function eliminarReserva(id) {
  if (!confirm('¿Estás seguro de cancelar esta cita?')) return;

  try {
    const res = await apiRequest(`/api/reservas/${id}`, 'DELETE');

    if (res.ok) {
      alert('✅ Cita cancelada exitosamente');

      if (document.getElementById('mis-reservas')) {
        await cargarMisReservas();
      }
      if (document.getElementById('tabla-reservas')) {
        await cargarReservas();
      }
    } else {
      alert('❌ ' + (res.error || 'No se pudo cancelar la cita'));
    }
  } catch (error) {
    console.error('Error:', error);
    alert('❌ Error al cancelar la cita');
  }
}

function isAdmin() {
  try {
    const u = JSON.parse(localStorage.getItem('user') || 'null');
    return u && u.role === 'admin';
  } catch (e) {
    return false;
  }
}

function cerrarSesion() {
  if (confirm('¿Cerrar sesión?')) {
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('tabla-reservas')) {
    cargarReservas();
  }

  if (document.getElementById('mis-reservas')) {
    cargarMisReservas();
  }
});
