const adminToken = localStorage.getItem("admin_token");

document.addEventListener("DOMContentLoaded", () => {
  if (!adminToken) {
    window.location.href = "/admin";
    return;
  }

  fetchDashboardData();

  document.getElementById("form-update-settings").addEventListener("submit", handleUpdateSettings);
  document.getElementById("btn-admin-logout").addEventListener("click", () => {
    localStorage.removeItem("admin_token");
    window.location.href = "/admin";
  });
});

async function fetchDashboardData() {
  try {
    const res = await fetch("/api/admin/dashboard", {
      headers: { "Authorization": `Bearer ${adminToken}` }
    });
    
    if (res.status === 401) {
      localStorage.removeItem("admin_token");
      window.location.href = "/admin";
      return;
    }

    const data = await res.json();
    if (data.success) {
      renderMetrics(data.metrics);
      renderSettings(data.settings);
      renderClientsTable(data.clients);
    }
  } catch (err) {
    console.error("Error loading dashboard data:", err);
  }
}

function renderMetrics(metrics) {
  document.getElementById("kpi-total-clients").textContent = metrics.total_clients;
  document.getElementById("kpi-visits-today").textContent = metrics.visits_today;
  document.getElementById("kpi-visits-week").textContent = `${metrics.visits_this_week} esta semana`;
  document.getElementById("kpi-total-stamps").textContent = metrics.total_stamps;
  document.getElementById("kpi-total-redemptions").textContent = metrics.total_redemptions;
  document.getElementById("kpi-retention-rate").textContent = `${metrics.retention_rate}%`;
  document.getElementById("kpi-recurrent-clients").textContent = `${metrics.recurrent_clients} clientes recurrentes`;
}

function renderSettings(settings) {
  if (settings.redemption_pin) {
    document.getElementById("setting-pin").value = settings.redemption_pin;
  }
  if (settings.current_reward) {
    document.getElementById("setting-reward").value = settings.current_reward;
  }
  if (settings.cooldown_hours) {
    document.getElementById("setting-cooldown").value = settings.cooldown_hours;
  }
}

function renderClientsTable(clients) {
  const tbody = document.getElementById("tbody-clients");
  tbody.innerHTML = "";

  if (!clients || clients.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #787060;">Aún no hay clientes registrados.</td></tr>`;
    return;
  }

  clients.forEach(c => {
    const tr = document.createElement("tr");
    
    const lastVisit = c.last_visit_at ? new Date(c.last_visit_at).toLocaleString("es-AR") : "Sin visitas";
    const isRecurrent = c.total_stamps >= 2;
    const badgeHtml = isRecurrent 
      ? `<span class="badge badge-gold">Recurrente</span>`
      : `<span class="badge" style="background: #e4dfd3; color: #625c4f;">Nuevo</span>`;

    tr.innerHTML = `
      <td><strong>${escapeHtml(c.name)}</strong></td>
      <td>${escapeHtml(c.whatsapp)}</td>
      <td><strong style="color: #cba152;">${c.total_stamps || 0} sellos</strong></td>
      <td>${c.total_redemptions || 0} canjes</td>
      <td>${lastVisit}</td>
      <td>${badgeHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function handleUpdateSettings(e) {
  e.preventDefault();
  const pin = document.getElementById("setting-pin").value.trim();
  const reward = document.getElementById("setting-reward").value.trim();
  const cooldown = document.getElementById("setting-cooldown").value.trim();

  try {
    const res = await fetch("/api/admin/settings", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${adminToken}`
      },
      body: JSON.stringify({
        redemption_pin: pin,
        current_reward: reward,
        cooldown_hours: cooldown
      })
    });
    const data = await res.json();

    if (data.success) {
      alert("¡Configuración actualizada con éxito!");
      await fetchDashboardData();
    } else {
      alert(data.message || "Error al actualizar la configuración.");
    }
  } catch (err) {
    alert("Error de conexión al actualizar la configuración.");
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
