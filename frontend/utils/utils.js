const BACKEND_URL = "http://localhost:5000/api";

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

function getCookie(name) {
  const cookieArr = document.cookie.split("; ");
  for (const cookie of cookieArr) {
    const [key, val] = cookie.split("=");
    if (key === name) return val;
  }
  return null;
}

function decodeJwtPayload(token) {
  if (!token) return null;
  const payloadBase64Url = token.split(".")[1];
  if (!payloadBase64Url) return null;

  const base64 = payloadBase64Url.replace(/-/g, "+").replace(/_/g, "/");

  try {
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  timeout: 10000,
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
