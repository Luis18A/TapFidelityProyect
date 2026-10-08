// Client PWA State
let currentToken = localStorage.getItem("fidelizacion_token") || null;
let currentPin = "";
let cooldownTimerInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  initApp();

  document.getElementById("form-register").addEventListener("submit", handleRegister);
  document.getElementById("btn-add-stamp").addEventListener("click", handleAddStamp);
  document.getElementById("btn-open-redeem").addEventListener("click", openPinModal);
  document.getElementById("btn-change-user").addEventListener("click", handleLogout);
});

async function initApp() {
  if (!currentToken) {
    showSection("section-register");
    return;
  }
  await fetchAccountStatus();
}

function showSection(sectionId) {
  document.getElementById("section-register").style.display = "none";
  document.getElementById("section-card").style.display = "none";
  document.getElementById(sectionId).style.display = "block";
}

async function fetchAccountStatus() {
  try {
    const res = await fetch("/api/client/status", {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    const data = await res.json();

    if (!data.authenticated) {
      localStorage.removeItem("fidelizacion_token");
      currentToken = null;
      showSection("section-register");
      return;
    }

    renderCardDashboard(data);
    showSection("section-card");
  } catch (err) {
    console.error("Error fetching status:", err);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById("input-name").value.trim();
  const whatsapp = document.getElementById("input-whatsapp").value.trim();

  if (!name || !whatsapp) return;

  try {
    const res = await fetch("/api/client/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, whatsapp })
    });
    const data = await res.json();

    if (data.success && data.client) {
      currentToken = data.client.session_token;
      localStorage.setItem("fidelizacion_token", currentToken);
      await fetchAccountStatus();
    }
  } catch (err) {
    alert("Error de conexión al registrar. Inténtalo nuevamente.");
  }
}

function renderCardDashboard(data) {
  const client = data.client;
  const status = data.card_status;

  document.getElementById("user-display-name").textContent = client.name;
  document.getElementById("user-display-phone").textContent = client.whatsapp;
  document.getElementById("reward-display-text").textContent = status.reward_name;

  // Render 5 slots
  const activeStamps = status.active_stamps;
  for (let i = 1; i <= 5; i++) {
    const slot = document.getElementById(`slot-${i}`);
    if (i <= activeStamps) {
      slot.classList.add("active");
    } else {
      slot.classList.remove("active");
    }
  }

  // Redeem button state
  const btnRedeem = document.getElementById("btn-open-redeem");
  const btnStamp = document.getElementById("btn-add-stamp");

  if (status.can_redeem) {
    btnRedeem.style.display = "flex";
  } else {
    btnRedeem.style.display = "none";
  }

  // Cooldown status
  const cooldown = status.cooldown;
  const cooldownBanner = document.getElementById("cooldown-container");
  
  if (!cooldown.is_eligible) {
    btnStamp.disabled = true;
    cooldownBanner.style.display = "flex";
    startCooldownTimer(cooldown.seconds_remaining);
  } else {
    btnStamp.disabled = false;
    cooldownBanner.style.display = "none";
    if (cooldownTimerInterval) clearInterval(cooldownTimerInterval);
  }
}

function startCooldownTimer(initialSeconds) {
  if (cooldownTimerInterval) clearInterval(cooldownTimerInterval);
  let seconds = initialSeconds;

  const updateText = () => {
    if (seconds <= 0) {
      clearInterval(cooldownTimerInterval);
      fetchAccountStatus();
      return;
    }
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    let str = "";
    if (hrs > 0) str += `${hrs}h `;
    str += `${mins}m ${secs}s`;
    
    document.getElementById("cooldown-text").textContent = `Próximo sello disponible en: ${str}`;
    seconds--;
  };

  updateText();
  cooldownTimerInterval = setInterval(updateText, 1000);
}

async function handleAddStamp() {
  if (!currentToken) return;

  try {
    const res = await fetch("/api/client/stamp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_token: currentToken })
    });
    const data = await res.json();

    if (data.success) {
      await fetchAccountStatus();
    } else {
      alert(data.message || "No se pudo agregar el sello.");
    }
  } catch (err) {
    alert("Error de conexión al sumar sello.");
  }
}

// PIN Keypad Modal Logic
function openPinModal() {
  currentPin = "";
  updatePinDots();
  document.getElementById("pin-error-msg").style.display = "none";
  document.getElementById("modal-pin").classList.add("active");
}

function closePinModal() {
  document.getElementById("modal-pin").classList.remove("active");
  currentPin = "";
}

function pressKey(num) {
  if (currentPin.length < 4) {
    currentPin += num;
    updatePinDots();
  }
  if (currentPin.length === 4) {
    submitPin();
  }
}

function clearPin() {
  currentPin = "";
  updatePinDots();
  document.getElementById("pin-error-msg").style.display = "none";
}

function updatePinDots() {
  for (let i = 1; i <= 4; i++) {
    const dot = document.getElementById(`dot-${i}`);
    if (i <= currentPin.length) {
      dot.classList.add("filled");
    } else {
      dot.classList.remove("filled");
    }
  }
}

async function submitPin() {
  try {
    const res = await fetch("/api/client/redeem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_token: currentToken, pin: currentPin })
    });
    const data = await res.json();

    if (data.success) {
      closePinModal();
      document.getElementById("celebration-reward-text").textContent = data.reward_name;
      document.getElementById("modal-celebration").classList.add("active");
      await fetchAccountStatus();
    } else {
      const errBox = document.getElementById("pin-error-msg");
      errBox.textContent = data.message || "PIN Incorrecto";
      errBox.style.display = "block";
      clearPin();
    }
  } catch (err) {
    alert("Error de conexión al canjear el premio.");
    clearPin();
  }
}

function closeCelebration() {
  document.getElementById("modal-celebration").classList.remove("active");
}

function handleLogout() {
  if (confirm("¿Deseas cerrar sesión en este dispositivo?")) {
    localStorage.removeItem("fidelizacion_token");
    currentToken = null;
    showSection("section-register");
  }
}
