/* ================================================================
   analytics.js - fetches /api/analytics and renders 3 Chart.js
   visualizations: score trend (line), difficulty split (doughnut),
   and average score per category (bar).
   ================================================================ */

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

async function loadAnalytics() {
  try {
    const data = await apiRequest("/api/analytics");

    document.getElementById("statTotal").textContent = data.total_interviews;
    document.getElementById("statAvg").textContent = data.overall_avg || "0";
    document.getElementById("statBest").textContent = data.best_score || "0";

    if (!data.total_interviews) {
      document.getElementById("emptyState").innerHTML = `
        <div class="card empty-state">
          <div class="empty-icon">📈</div>
          <p>Complete an interview to start seeing your analytics here.</p>
          <a href="/interview/setup" class="btn btn-accent mt-16">Start an interview</a>
        </div>`;
      return;
    }

    const accent = cssVar("--accent");
    const primary = cssVar("--primary");
    const success = cssVar("--success");
    const danger = cssVar("--danger");
    const textMuted = cssVar("--text-muted");
    const border = cssVar("--border");

    Chart.defaults.color = textMuted;
    Chart.defaults.borderColor = border;
    Chart.defaults.font.family = "Inter";

    // ---- Trend line chart ----
    new Chart(document.getElementById("trendChart"), {
      type: "line",
      data: {
        labels: data.trend.map(t => t.label),
        datasets: [{
          label: "Average score",
          data: data.trend.map(t => t.score),
          borderColor: accent,
          backgroundColor: accent + "33",
          tension: 0.35,
          fill: true,
          pointBackgroundColor: accent,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { min: 0, max: 10 } },
      },
    });

    // ---- Difficulty doughnut chart ----
    const diffLabels = Object.keys(data.difficulty_counts);
    new Chart(document.getElementById("difficultyChart"), {
      type: "doughnut",
      data: {
        labels: diffLabels,
        datasets: [{
          data: diffLabels.map(l => data.difficulty_counts[l]),
          backgroundColor: [success, accent, danger],
          borderWidth: 0,
        }],
      },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } },
    });

    // ---- Category bar chart ----
    new Chart(document.getElementById("categoryChart"), {
      type: "bar",
      data: {
        labels: data.category_averages.map(c => c.category),
        datasets: [{
          label: "Average score",
          data: data.category_averages.map(c => c.avg),
          backgroundColor: primary,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { min: 0, max: 10 } },
      },
    });
  } catch (err) {
    showToast("Couldn't load analytics: " + err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", loadAnalytics);
