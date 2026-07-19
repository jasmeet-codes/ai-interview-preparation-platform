/* ================================================================
   main.js - loaded on every page.
   Handles: dark/light theme toggle, toast notifications, a small
   fetch() wrapper (apiRequest) used by every other JS file, and the
   mobile hamburger menu.
   ================================================================ */

// ---------- Theme (dark/light mode), persisted in localStorage ----------
(function initTheme() {
  const saved = localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", saved);
  updateToggleIcon(saved);
})();

function updateToggleIcon(theme) {
  const btn = document.getElementById("themeToggle");
  if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
}

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
      updateToggleIcon(next);
    });
  }

  const hamburger = document.getElementById("hamburger");
  const navLinks = document.getElementById("navLinks");
  if (hamburger && navLinks) {
    hamburger.addEventListener("click", () => navLinks.classList.toggle("open"));
  }
});

// ---------- Toast notifications ----------
let toastTimer = null;
function showToast(message, type = "success") {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = message;
  el.className = `toast visible toast-${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("visible"), 3500);
}

// ---------- Small fetch() wrapper used across all pages ----------
async function apiRequest(url, options = {}) {
  const opts = {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  };
  if (options.body) opts.body = JSON.stringify(options.body);
  if (options.formData) {
    delete opts.headers["Content-Type"]; // let the browser set multipart boundary
    opts.body = options.formData;
  }

  const res = await fetch(url, opts);
  let data = {};
  try { data = await res.json(); } catch (e) { /* no JSON body */ }

  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}
