class AuthUser {
  constructor() {
    this.getToken();
  }

  async fetchUserObj() {
    try {
      const { data } = await api.get(
        `/user/get-single-obj?account_id=${this.account_id}`
      );
      this.authUser = data.payload;
      console.log(JSON.stringify(this.authUser, null, 2));
    } catch (error) {
      console.error("Sign up failed:", error.response?.data || error.message);
      throw error;
    }
  }

  async checkAuth() {
    showLoading();

    if (!this.account_id) {
      hideLoading();
      window.location.href = "/auth/sign-in";
      return;
    }

    await this.fetchUserObj();
    const authUser = this.authUser;
    const currentPath = window.location.pathname;

    if (!authUser) {
      hideLoading();
      if (!currentPath.includes("/auth")) {
        window.location.href = "/auth/sign-in";
      }
      return;
    }

    if (authUser.role === "Admin") {
      if (!currentPath.startsWith("/admin")) {
        window.location.href = "/admin/dashboard";
        return;
      }
    } else if (authUser.role === "Student") {
      if (currentPath.startsWith("/admin")) {
        alert("Access denied: Admins only.");
        window.location.href = "/";
        return;
      }

      if (currentPath === "/auth/sign-in" || currentPath.startsWith("/admin")) {
        hideLoading();
        window.location.href = "/";
        return;
      }
    } else {
      hideLoading();
      window.location.href = "/auth/sign-in";
      return;
    }

    hideLoading();
  }

  getToken() {
    try {
      const token = localStorage.getItem("access_token");

      if (isJwtExpired(token)) {
        return null;
      } else if (!token) {
        window.location.href = "/auth/sign-in";
      } else {
        const obj = parseJwt(token);
        this.account_id = obj.sub;
      }
    } catch {}
  }
}
