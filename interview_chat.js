/* ================================================================
   interview_chat.js - drives the interview chat page:
   loads state, submits answers, renders AI feedback, advances
   through questions, and finishes the interview.
   ================================================================ */

const interviewId = document.querySelector(".chat-shell").dataset.interviewId;
let currentQuestion = null;
let totalQuestions = 0;

function scoreColor(score) {
  if (score >= 7) return "var(--success)";
  if (score >= 4) return "var(--accent)";
  return "var(--danger)";
}

function renderAnsweredHistoryItem(record) {
  const div = document.createElement("div");
  div.className = "card chat-history-item";
  div.innerHTML = `
    <div class="flex items-center justify-between mb-16">
      <strong style="font-family:var(--font-mono); font-size:0.8rem; color:var(--text-faint);">
        QUESTION ${record.question_number}
      </strong>
      <span class="score-pill ${record.score >= 7 ? 'score-high' : record.score >= 4 ? 'score-mid' : 'score-low'}">
        ${record.score}/10
      </span>
    </div>
    <p style="font-weight:600; margin-bottom:10px;">${escapeHtml(record.question_text)}</p>
    <p class="text-muted" style="font-size:0.88rem; margin-bottom:14px;">${escapeHtml(record.answer_text)}</p>
    <div class="feedback-block"><h5>Feedback</h5><p>${escapeHtml(record.feedback)}</p></div>
    <div class="feedback-block"><h5>Strengths</h5><p>${escapeHtml(record.strengths)}</p></div>
    <div class="feedback-block"><h5>Weaknesses</h5><p>${escapeHtml(record.weaknesses)}</p></div>
    <div class="feedback-block"><h5>Suggestions</h5><p>${escapeHtml(record.suggestions)}</p></div>
  `;
  return div;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function updateProgress(answeredCount) {
  const pct = Math.round((answeredCount / totalQuestions) * 100);
  document.getElementById("progressFill").style.width = pct + "%";
  document.getElementById("progressLabel").textContent =
    `Question ${Math.min(answeredCount + 1, totalQuestions)} of ${totalQuestions}`;
}

function showQuestion(q) {
  currentQuestion = q;
  document.getElementById("questionNumTag").textContent = `QUESTION ${q.question_number}`;
  document.getElementById("questionText").textContent = q.question_text;
  document.getElementById("questionSpotlight").style.display = "block";
  document.getElementById("answerBox").style.display = "block";
  document.getElementById("answerInput").value = "";
  document.getElementById("answerInput").focus();
  updateWordCounter();
}

function hideQuestionUI() {
  document.getElementById("questionSpotlight").style.display = "none";
  document.getElementById("answerBox").style.display = "none";
}

function updateWordCounter() {
  const text = document.getElementById("answerInput").value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  document.getElementById("wordCounter").textContent = `${words} word${words === 1 ? "" : "s"}`;
}

async function loadState() {
  try {
    const data = await apiRequest(`/api/interview/${interviewId}/state`);
    totalQuestions = data.total;

    const history = document.getElementById("chatHistory");
    history.innerHTML = "";
    data.answered.forEach(r => history.appendChild(renderAnsweredHistoryItem(r)));
    updateProgress(data.answered.length);

    if (data.next_question) {
      showQuestion(data.next_question);
    } else {
      // All questions answered already -> show finish button
      hideQuestionUI();
      document.getElementById("finishContainer").style.display = "block";
    }
  } catch (err) {
    showToast("Couldn't load interview: " + err.message, "error");
  }
}

function renderFeedback(result, questionNumber, questionText, answerText) {
  const container = document.getElementById("feedbackContainer");
  container.innerHTML = `
    <div class="card feedback-card">
      <div class="feedback-score-row">
        <div class="feedback-score-ring" style="border-color:${scoreColor(result.score)}; color:${scoreColor(result.score)};">
          ${result.score}
        </div>
        <div>
          <strong>Score for question ${questionNumber}</strong>
          <p class="text-muted" style="font-size:0.85rem;">out of 10</p>
        </div>
      </div>
      <div class="feedback-block"><h5>Feedback</h5><p>${escapeHtml(result.feedback)}</p></div>
      <div class="feedback-block"><h5>Strengths</h5><p>${escapeHtml(result.strengths)}</p></div>
      <div class="feedback-block"><h5>Weaknesses</h5><p>${escapeHtml(result.weaknesses)}</p></div>
      <div class="feedback-block"><h5>Suggestions</h5><p>${escapeHtml(result.suggestions)}</p></div>
      <button class="btn btn-primary mt-16" id="continueBtn">Continue</button>
    </div>
  `;
  container.scrollIntoView({ behavior: "smooth", block: "center" });
}

document.addEventListener("DOMContentLoaded", () => {
  loadState();

  document.getElementById("answerInput").addEventListener("input", updateWordCounter);

  document.getElementById("submitAnswerBtn").addEventListener("click", async () => {
    const answer = document.getElementById("answerInput").value.trim();
    if (!answer) {
      showToast("Please write an answer before submitting.", "error");
      return;
    }

    const btn = document.getElementById("submitAnswerBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Evaluating...`;

    try {
      const data = await apiRequest(`/api/interview/${interviewId}/answer`, {
        method: "POST",
        body: { answer },
      });

      hideQuestionUI();
      renderFeedback(data.result, data.question_number, currentQuestion.question_text, answer);
      updateProgress(data.question_number);

      document.getElementById("continueBtn").addEventListener("click", () => {
        document.getElementById("feedbackContainer").innerHTML = "";
        if (data.is_last) {
          document.getElementById("finishContainer").style.display = "block";
        } else {
          showQuestion(data.next_question);
        }
      });
    } catch (err) {
      showToast("Couldn't submit answer: " + err.message, "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Submit answer";
    }
  });

  document.getElementById("finishBtn").addEventListener("click", async () => {
    const btn = document.getElementById("finishBtn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Finalizing...`;
    try {
      const data = await apiRequest(`/api/interview/${interviewId}/finish`, { method: "POST" });
      showToast(`Interview complete! Average score: ${data.avg_score}/10`, "success");
      setTimeout(() => window.location.href = `/interview/summary/${interviewId}`, 900);
    } catch (err) {
      showToast("Couldn't finish interview: " + err.message, "error");
      btn.disabled = false;
      btn.textContent = "Finish interview & see results";
    }
  });
});
