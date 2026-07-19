"""
routes/resume.py
-----------------
Lets a user upload a PDF resume, extracts its text, and runs it through the
AI service (or mock analyzer) for a score + strengths/gaps/suggestions.
"""

import os
import json
import uuid
from flask import Blueprint, render_template, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from database import get_db
from utils import login_required
from services.resume_parser import extract_text_from_pdf
from services import ai_service

resume_bp = Blueprint("resume", __name__)


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_RESUME_EXTENSIONS"]


@resume_bp.route("/resume")
@login_required
def resume_page():
    db = get_db()
    history = db.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC",
        (session["user_id"],),
    ).fetchall()
    return render_template("resume.html", history=history)


@resume_bp.route("/api/resume/upload", methods=["POST"])
@login_required
def api_upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file was uploaded."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file was selected."}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported."}), 400

    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    safe_name = f"{session['user_id']}_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    if not text:
        return jsonify({
            "error": "Couldn't extract text from this PDF. It may be a scanned image - "
                     "try a text-based PDF export instead."
        }), 422

    db = get_db()
    user = db.execute("SELECT target_role FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    target_role = user["target_role"] if user else "Software Engineer"

    analysis = ai_service.analyze_resume(text, target_role)

    db.execute(
        "INSERT INTO resumes (user_id, filename, analysis) VALUES (?, ?, ?)",
        (session["user_id"], file.filename, json.dumps(analysis)),
    )
    db.commit()

    return jsonify({"analysis": analysis, "filename": file.filename})
