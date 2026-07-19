/* ================================================================
   interview_setup.js - handles the category/difficulty pill selection
   and kicks off a new interview via /api/interview/start
   ================================================================ */

let selectedCategory = null;
let selectedDifficulty = null;

function wireOptionGroup(containerId, onSelect) {
  const container = document.getElementById(containerId);
  container.querySelectorAll(".option-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      container.querySelectorAll(".option-pill").forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      onSelect(btn.dataset.value);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireOptionGroup("categoryOptions", (val) => selectedCategory = val);
  wireOptionGroup("difficultyOptions", (val) => selectedDifficulty = val);

  // Pre-select category from ?category= query param (linked from dashboard cards)
  const params = new URLSearchParams(window.location.search);
  const preselect = params.get("category");
  if (preselect) {
    const btn = document.querySelector(`#categoryOptions .option-pill[data-value="${preselect}"]`);
    if (btn) btn.click();
  }

  document.getElementById("startBtn").addEventListener("click", async () => {
    const errorEl = document.getElementById("formError");
    errorEl.classList.remove("visible");

    if (!selectedCategory || !selectedDifficulty) {
      errorEl.textContent = "Please choose a category and difficulty to continue.";
      errorEl.classList.add("visible");
      return;
    }

    const role = document.getElementById("role").value.trim() || "Software Engineer";
    const btn = document.getElementById("startBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Generating questions...`;

    try {
      const data = await apiRequest("/api/interview/start", {
        method: "POST",
        body: { category: selectedCategory, difficulty: selectedDifficulty, role },
      });
      window.location.href = data.redirect;
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.classList.add("visible");
      btn.disabled = false;
      btn.textContent = "Generate questions & start";
    }
  });
});
