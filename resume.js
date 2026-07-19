/* ================================================================
   resume.js - handles drag/drop or click-to-upload PDF resume,
   sends it to /api/resume/upload, and renders the AI analysis.
   ================================================================ */

function renderAnalysis(analysis, filename) {
  const scoreColor = analysis.overall_score >= 7 ? "var(--success)"
    : analysis.overall_score >= 4 ? "var(--accent)" : "var(--danger)";

  const keywords = (analysis.keywords_found || [])
    .map(k => `<span class="keyword-chip">${k}</span>`).join("") || "<span class='text-muted'>None detected</span>";

  document.getElementById("analysisResult").innerHTML = `
    <div class="card">
      <p class="text-center text-muted mb-16" style="font-size:0.85rem;">Analysis for <strong>${filename}</strong></p>
      <div class="resume-score-badge" style="border-color:${scoreColor}; color:${scoreColor};">
        ${analysis.overall_score}
      </div>
      <p class="text-center text-muted mb-24">Overall resume score / 10</p>

      <div class="feedback-block"><h5>Strengths</h5><p>${analysis.strengths}</p></div>
      <div class="feedback-block"><h5>Gaps to address</h5><p>${analysis.gaps}</p></div>
      <div class="feedback-block"><h5>Suggestions</h5><p>${analysis.suggestions}</p></div>
      <div class="feedback-block">
        <h5>Keywords found</h5>
        <div>${keywords}</div>
      </div>
    </div>
  `;
}

async function handleFile(file) {
  if (!file) return;
  if (file.type !== "application/pdf") {
    showToast("Only PDF files are supported.", "error");
    return;
  }

  document.getElementById("fileNameLabel").textContent = `Analyzing "${file.name}"...`;
  document.getElementById("analysisResult").innerHTML = `
    <div class="card text-center"><span class="spinner" style="border-top-color:var(--primary); border-color:var(--border);"></span>
    <p class="mt-16 text-muted">Reading and analyzing your resume...</p></div>`;

  const formData = new FormData();
  formData.append("resume", file);

  try {
    const data = await apiRequest("/api/resume/upload", { method: "POST", formData });
    document.getElementById("fileNameLabel").textContent = `Last analyzed: ${file.name}`;
    renderAnalysis(data.analysis, data.filename);
    showToast("Resume analyzed successfully.", "success");
  } catch (err) {
    document.getElementById("analysisResult").innerHTML = "";
    document.getElementById("fileNameLabel").textContent = "";
    showToast(err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const zone = document.getElementById("uploadZone");
  const input = document.getElementById("resumeInput");

  zone.addEventListener("click", () => input.click());
  input.addEventListener("change", () => handleFile(input.files[0]));

  ["dragenter", "dragover"].forEach(evt =>
    zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.add("dragover"); })
  );
  ["dragleave", "drop"].forEach(evt =>
    zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.remove("dragover"); })
  );
  zone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    handleFile(file);
  });
});
