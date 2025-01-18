document.addEventListener("DOMContentLoaded", () => {
  const googleLoginBtn = document.querySelector(".google-login-btn");
  googleLoginBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("/auth/google_auth_url");
      if (!response.ok) {
        throw new Error(
          `Failed to get Google login URL (status: ${response.status})`
        );
      }
      const data = await response.json();
      if (!data.authorization_url) {
        throw new Error("No authorization_url in response");
      }
      window.location.href = data.authorization_url;
    } catch (error) {
      console.error(error);
      alert("Failed to initiate Google login. Please try again.");
    }
  });
});
