"""
routes/interview.py
--------------------
Handles the full interview lifecycle:
  1. GET  /interview/setup        -> page to choose category/difficulty/role
  2. POST /api/interview/start    -> generates questions (AI or mock), creates DB rows
  3. GET  /interview/chat/<id>    -> the chat page itself
  4. GET  /api/interview/<id>/state   -> current question + progress (for page refresh)
  5. POST /api/interview/<id>/answer  -> submit an answer, get AI feedback + score
  6. POST /api/interview/<id>/finish  -> mark interview completed, compute avg score
"""

from flask import Blueprint, render_template, request, jsonify, session
from database import get_db
from utils import login_required
from services import ai_service
from config import CATEGORIES, DIFFICULTIES, QUESTIONS_PER_INTERVIEW

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/interview/setup")
@login_required
def setup_page():
    return render_template("select_interview.html", categories=CATEGORIES, difficulties=DIFFICULTIES)


@interview_bp.route("/api/interview/start", methods=["POST"])
@login_required
def api_start_interview():
    data = request.get_json(silent=True) or {}
    category = data.get("category")
    difficulty = data.get("difficulty")
    role = (data.get("role") or "Software Engineer").strip()

    if category not in CATEGORIES or difficulty not in DIFFICULTIES:
        return jsonify({"error": "Please choose a valid category and difficulty."}), 400

    questions = ai_service.generate_questions(category, difficulty, role, QUESTIONS_PER_INTERVIEW)

    db = get_db()
    cur = db.execute(
        """INSERT INTO interviews (user_id, category, difficulty, role, total_questions)
           VALUES (?, ?, ?, ?, ?)""",
        (session["user_id"], category, difficulty, role, len(questions)),
    )
    interview_id = cur.lastrowid

    for idx, q in enumerate(questions, start=1):
        db.execute(
            """INSERT INTO qa_records (interview_id, question_number, question_text)
               VALUES (?, ?, ?)""",
            (interview_id, idx, q),
        )
    db.commit()

    return jsonify({"interview_id": interview_id, "redirect": f"/interview/chat/{interview_id}"})


@interview_bp.route("/interview/chat/<int:interview_id>")
@login_required
def chat_page(interview_id):
    db = get_db()
    interview = db.execute(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?", (interview_id, session["user_id"])
    ).fetchone()
    if not interview:
        return render_template("404.html"), 404
    return render_template("interview_chat.html", interview=interview)


def _get_owned_interview(db, interview_id):
    return db.execute(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, session["user_id"]),
    ).fetchone()


@interview_bp.route("/api/interview/<int:interview_id>/state")
@login_required
def api_interview_state(interview_id):
    db = get_db()
    interview = _get_owned_interview(db, interview_id)
    if not interview:
        return jsonify({"error": "Interview not found."}), 404

    records = db.execute(
        "SELECT * FROM qa_records WHERE interview_id = ? ORDER BY question_number ASC",
        (interview_id,),
    ).fetchall()

    answered = [dict(r) for r in records if r["answer_text"] is not None]
    next_q = next((dict(r) for r in records if r["answer_text"] is None), None)

    return jsonify({
        "interview": dict(interview),
        "answered": answered,
        "next_question": next_q,
        "total": len(records),
    })


@interview_bp.route("/api/interview/<int:interview_id>/answer", methods=["POST"])
@login_required
def api_submit_answer(interview_id):
    data = request.get_json(silent=True) or {}
    answer_text = (data.get("answer") or "").strip()

    db = get_db()
    interview = _get_owned_interview(db, interview_id)
    if not interview:
        return jsonify({"error": "Interview not found."}), 404

    record = db.execute(
        """SELECT * FROM qa_records WHERE interview_id = ? AND answer_text IS NULL
           ORDER BY question_number ASC LIMIT 1""",
        (interview_id,),
    ).fetchone()
    if not record:
        return jsonify({"error": "No pending question for this interview."}), 400

    result = ai_service.evaluate_answer(
        record["question_text"], answer_text, interview["category"], interview["difficulty"]
    )

    db.execute(
        """UPDATE qa_records SET answer_text = ?, score = ?, feedback = ?, strengths = ?,
           weaknesses = ?, suggestions = ?, answered_at = datetime('now') WHERE id = ?""",
        (
            answer_text, result["score"], result["feedback"], result["strengths"],
            result["weaknesses"], result["suggestions"], record["id"],
        ),
    )
    db.commit()

    next_q = db.execute(
        """SELECT * FROM qa_records WHERE interview_id = ? AND answer_text IS NULL
           ORDER BY question_number ASC LIMIT 1""",
        (interview_id,),
    ).fetchone()

    return jsonify({
        "result": result,
        "question_number": record["question_number"],
        "next_question": dict(next_q) if next_q else None,
        "is_last": next_q is None,
    })


@interview_bp.route("/api/interview/<int:interview_id>/finish", methods=["POST"])
@login_required
def api_finish_interview(interview_id):
    db = get_db()
    interview = _get_owned_interview(db, interview_id)
    if not interview:
        return jsonify({"error": "Interview not found."}), 404

    scores = db.execute(
        "SELECT score FROM qa_records WHERE interview_id = ? AND score IS NOT NULL",
        (interview_id,),
    ).fetchall()
    avg_score = round(sum(r["score"] for r in scores) / len(scores), 2) if scores else 0

    db.execute(
        """UPDATE interviews SET status = 'completed', avg_score = ?, completed_at = datetime('now')
           WHERE id = ?""",
        (avg_score, interview_id),
    )
    db.commit()

    return jsonify({"message": "Interview completed.", "avg_score": avg_score, "redirect": "/analytics"})


@interview_bp.route("/interview/summary/<int:interview_id>")
@login_required
def summary_page(interview_id):
    db = get_db()
    interview = _get_owned_interview(db, interview_id)
    if not interview:
        return render_template("404.html"), 404
    records = db.execute(
        "SELECT * FROM qa_records WHERE interview_id = ? ORDER BY question_number ASC",
        (interview_id,),
    ).fetchall()
    return render_template("interview_summary.html", interview=interview, records=records)
