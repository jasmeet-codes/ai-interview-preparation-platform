/* ================================================================
   auth.js - handles the signup and login forms via fetch() calls
   to the JSON API in routes/auth.py
   ================================================================ */

function setFormError(message) {
  const el = document.getElementById("formError");
  if (!el) return;
  if (!message) { el.classList.remove("visible"); el.textContent = ""; return; }
  el.textContent = message;
  el.classList.add("visible");
}

function setButtonLoading(btn, loading, label) {
  btn.disabled = loading;
  btn.innerHTML = loading ? `<span class="spinner"></span> Please wait...` : label;
}

document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      setFormError(null);
      const btn = document.getElementById("submitBtn");
      setButtonLoading(btn, true);

      const payload = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        target_role: document.getElementById("target_role").value,
        password: document.getElementById("password").value,
      };

      try {
        const data = await apiRequest("/api/signup", { method: "POST", body: payload });
        window.location.href = data.redirect || "/dashboard";
      } catch (err) {
        setFormError(err.message);
        setButtonLoading(btn, false, "Create account");
      }
    });
  }

  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      setFormError(null);
      const btn = document.getElementById("submitBtn");
      setButtonLoading(btn, true);

      const payload = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      };

      try {
        const data = await apiRequest("/api/login", { method: "POST", body: payload });
        window.location.href = data.redirect || "/dashboard";
      } catch (err) {
        setFormError(err.message);
        setButtonLoading(btn, false, "Log in");
      }
    });
  }
});
