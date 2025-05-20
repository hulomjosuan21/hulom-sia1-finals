class SignInService {
  constructor() {}

  async handleSignIn(formData) {
    for (const [key, value] of formData.entries()) {
      console.log(`${key}: ${value}`);
    }
  }
}

$(document).ready(function () {
  const signInService = new SignInService();

  $("#signinForm").on("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const submitBtn = $(this).find('button[type="submit"]');

    toggleButtonLoading(submitBtn, true, "Submitting...");

    setTimeout(() => {
      toggleButtonLoading(submitBtn, false);
      this.reset();
    }, 2000);
  });
});
