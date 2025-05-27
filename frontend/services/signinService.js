const secretKey = "JOSUAN"

class SignInService {
  constructor() { }

  async handleSignIn(formData) {
    try {
      const response = await api.post("/auth/sign-in", formData);
      localStorage.setItem("access_token", response.data.payload.access_token);

      return response.data.message;
    } catch (e) {
      console.error("Sign up failed:", error.response?.data || error.message);
      throw error;
    }
  }

  // async handleSignIn(formData) {
  //   try {
  //     const obj = {};
  //     formData.forEach((value, key) => {
  //       obj[key] = value;
  //     });

  //     const jsonStr = JSON.stringify(obj);

  //     const encrypted = CryptoJS.AES.encrypt(jsonStr, secretKey).toString();

  //     const response = await api.post("/auth/sign-in", { encrypted });

  //     if (response.data?.payload?.access_token) {
  //       localStorage.setItem("access_token", response.data.payload.access_token);
  //     }

  //     return response.data.message;
  //   } catch (error) {
  //     console.error("Sign in failed:", error.response?.data || error.message);
  //     throw error;
  //   }
  // }
}

$(document).ready(function () {
  const signInService = new SignInService();

  $("#signinForm").on("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const submitBtn = $(this).find('button[type="submit"]');

    toggleButtonLoading(submitBtn, true, "Logging in...");

    try {
      const message = await signInService.handleSignIn(formData);

      window.alert(message);
      window.location.href = "/";
    } catch (e) {
      window.alert(e);
    } finally {
      toggleButtonLoading(submitBtn, false);
    }
  });
});
