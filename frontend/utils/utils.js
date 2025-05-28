const BACKEND_URL = "https://hulom-sia1-finals.onrender.com/api";

const DEFAULT_PROFILE_IMAGE = "/assets/default-profile-image.png";

function toggleButtonLoading($button, isLoading, loadingText = "Loading") {
  if (!$button.data("original-html")) {
    $button.data("original-html", $button.html());
  }

  $button.fadeOut(200, function () {
    if (isLoading) {
      $button.prop("disabled", true);
      $button.html(
        `<span class="loading loading-spinner"></span> ${loadingText}`
      );
    } else {
      $button.prop("disabled", false);
      $button.html($button.data("original-html"));
    }

    $button.fadeIn(200);
  });
}

function calculateAge(birthdate) {
  const birthDate = new Date(birthdate);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDifference = today.getMonth() - birthDate.getMonth();
  if (
    monthDifference < 0 ||
    (monthDifference === 0 && today.getDate() < birthDate.getDate())
  ) {
    age--;
  }
  return age;
}

function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );

    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error("Invalid JWT", e);
    return null;
  }
}

function isJwtExpired(token) {
  const decoded = parseJwt(token);
  if (!decoded || !decoded.exp) return true;
  const now = Math.floor(Date.now() / 1000);
  return decoded.exp < now;
}

let countdownInterval;

function startTimer({ seconds, hours }) {
  clearInterval(countdownInterval);

  if (
    (seconds != null && hours != null) ||
    (seconds == null && hours == null)
  ) {
    console.error("❌ Please provide either 'seconds' or 'hours', not both.");
    document.getElementById("timer").textContent = "Invalid input";
    return;
  }

  let totalSeconds = seconds != null ? seconds : hours * 3600;

  function updateDisplay() {
    const hrs = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
    const mins = String(Math.floor((totalSeconds % 3600) / 60)).padStart(
      2,
      "0"
    );
    const secs = String(totalSeconds % 60).padStart(2, "0");
    document.getElementById("timer").textContent = `${hrs}:${mins}:${secs}`;
  }

  updateDisplay();

  countdownInterval = setInterval(() => {
    totalSeconds--;
    updateDisplay();

    if (totalSeconds <= 0) {
      clearInterval(countdownInterval);
    }
  }, 1000);
}

function showLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "grid";
}

function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "none";
}

function handleLogout() {
  localStorage.removeItem("access_token");
  window.location.href = "/auth/sign-in";
}

async function checkConnection() {
  try {
    showLoading();
    const response = await api.get("/ping");
    console.log("Connection OK:", response.status);
  } catch (e) {
    console.error("API connection failed:", e.message);
  } finally {
    hideLoading();
  }
}

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  withCredentials: true,
});

$(document).ready(function () {
  const img = document.querySelector(".avatar-img");

  if (img) {
    img.onerror = function () {
      this.src = DEFAULT_PROFILE_IMAGE;
    };

    img.src = DEFAULT_PROFILE_IMAGE;
  }

  $("#avatar").click(function () {
    $("#popover-1").toggle();
  });
});
