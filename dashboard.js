/* ================================================================
   dashboard.js - fetches /api/analytics and fills in the stat cards
   + recent interviews table on the dashboard page.
   ================================================================ */

function scoreClass(score) {
  if (score >= 7) return "score-high";
  if (score >= 4) return "score-mid";
  return "score-low";
}

function formatDate(isoString) {
  if (!isoString) return "-";
  const d = new Date(isoString.replace(" ", "T") + "Z");
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

async function loadDashboard() {
  try {
    const data = await apiRequest("/api/analytics");

    document.getElementById("statTotal").textContent = data.total_interviews;
    document.getElementById("statAvg").textContent = data.overall_avg || "0";
    document.getElementById("statBest").textContent = data.best_score || "0";

    const oneWeekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    const thisWeek = data.recent.filter(i => {
      const t = new Date((i.created_at || "").replace(" ", "T") + "Z").getTime();
      return t >= oneWeekAgo;
    }).length;
    document.getElementById("statWeek").textContent = thisWeek;

    const tbody = document.getElementById("historyBody");
    if (!data.recent.length) {
      tbody.innerHTML = `<tr><td colspan="6">
        <div class="empty-state">
          <div class="empty-icon">🎤</div>
          <p>No interviews yet. Start your first one to see your history here.</p>
        </div>
      </td></tr>`;
      return;
    }

    tbody.innerHTML = data.recent.map(i => `
      <tr>
        <td>${i.category}</td>
        <td>${i.difficulty}</td>
        <td>${i.role}</td>
        <td>${i.status === "completed"
          ? '<span class="badge badge-success">Completed</span>'
          : '<span class="badge badge-accent">In progress</span>'}</td>
        <td>${i.status === "completed"
          ? `<span class="score-pill ${scoreClass(i.avg_score)}">${i.avg_score.toFixed(1)}</span>`
          : "-"}</td>
        <td class="text-muted">${formatDate(i.created_at)}</td>
      </tr>
    `).join("");
  } catch (err) {
    showToast("Couldn't load dashboard data: " + err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", loadDashboard);
