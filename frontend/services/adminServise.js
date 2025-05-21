$(document).ready(function () {
  const authUserClass = new AuthUser();

  try {
    authUserClass.checkAuth();
  } catch (e) {
    window.alert(e);
  }
});
