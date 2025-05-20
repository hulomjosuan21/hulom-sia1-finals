function getCookie(name) {
  const cookieArr = document.cookie.split("; ");
  for (const cookie of cookieArr) {
    const [key, val] = cookie.split("=");
    if (key === name) return val;
  }
  return null;
}

function decodeJwtPayload(token) {
  if (!token || typeof token !== "string") return null;

  const parts = token.split(".");
  if (parts.length !== 3) return null;

  const payloadBase64Url = parts[1];
  const base64 = payloadBase64Url.replace(/-/g, "+").replace(/_/g, "/");

  try {
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (err) {
    console.error("Failed to decode JWT payload:", err);
    return null;
  }
}

class SignUpService {
  constructor() {}

  async handleSignUp(formData) {
    for (const [key, value] of formData.entries()) {
      console.log(`${key}: ${value}`);
    }

    try {
      const response = await api.post("/auth/sign-up", formData);
      console.log("Account id", response.data.payload.account_id);
      this.account_id = response.data.payload.account_id;
      return response.data;
    } catch (error) {
      console.error("Sign up failed:", error.response?.data || error.message);
      throw error;
    }
  }

  async handleVerify(formData) {
    for (const [key, value] of formData.entries()) {
      console.log(`${key}: ${value}`);
    }
  }

  getDecodedAccessToken() {
    const token = getCookie("access_token_cookie");
    return decodeJwtPayload(token);
  }

  get getAccountId() {
    return this.account_id;
  }
}

$(document).ready(function () {
  const signUpService = new SignUpService();

  $("#signupForm").on("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    const submitBtn = $(this).find('button[type="submit"]');

    toggleButtonLoading(submitBtn, true, "Submitting...");

    try {
      const data = await signUpService.handleSignUp(formData);

      console.log(data.message);
      $("#verifyModal")[0].showModal();
    } catch (e) {
      console.log(e);
    } finally {
      toggleButtonLoading(submitBtn, false);
    }
  });

  $("#verifyBtn").click(async function () {
    const verificationCode = $("#verificationInput").val();
    const token = signUpService.getDecodedAccessToken();

    if (verificationCode) {
      console.log("Token: ", token);
    } else {
      window.alert("Enter verification code!");
    }
  });
});
