class SignUpService {
  constructor() {}

  async handleSignUp(formData) {
    for (const [key, value] of formData.entries()) {
      console.log(`${key}: ${value}`);
    }

    try {
      const response = await api.post("/auth/sign-up", formData);
      console.log("Account id", response.data.payload.account_id);
      this.access_token = response.data.payload.access_token;
      this.account_id = parseJwt(response.data.payload.access_token).sub;
      return response.data.message;
    } catch (error) {
      console.error("Sign up failed:", error.response?.data || error.message);
      throw error;
    }
  }

  async handleVerify(verifyCode) {
    try {
      const response = await api.put("/auth/verify-account", {
        account_id: this.account_id,
        verification_token: verifyCode,
      });
      localStorage.setItem("access_token", response.data.payload.access_token);

      return response.data.message;
    } catch (error) {
      console.error("Sign up failed:", error.response?.data || error.message);
      throw error;
    }
  }

  get geParseAccessToken() {
    return parseJwt(this.access_token);
  }

  get isJwtNotExpired() {
    return !isJwtExpired(this.access_token);
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
      startTimer({ hours: 1 });
      $("#verifyModal")[0].showModal();
    } catch (e) {
      window.alert(e);
    } finally {
      toggleButtonLoading(submitBtn, false);
    }
  });

  $("#verifyBtn").click(async function () {
    const verificationCode = $("#verificationInput").val();
    const $btn = $(this);

    toggleButtonLoading($btn, true, "Verifying...");

    try {
      if (signUpService.isJwtNotExpired) {
        const verifyCode = signUpService.geParseAccessToken.verification_token;
        if (verificationCode === verifyCode) {
          const message = await signUpService.handleVerify(verificationCode);

          window.alert(message);
        } else {
          throw new Error("Error Code");
        }
      } else {
        throw new Error("Token is expired!");
      }
    } catch (e) {
      window.alert(e);
    } finally {
      toggleButtonLoading($btn, false);
    }
  });
});
