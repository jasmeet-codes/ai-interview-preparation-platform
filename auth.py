"""
routes/auth.py
---------------
Handles signup, login, and logout using Flask sessions + salted password
hashes (werkzeug.security). No JWT/OAuth needed for this project's scope.
"""

import re
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- Page routes (render the HTML forms) ----------
@auth_bp.route("/signup", methods=["GET"])
def signup_page():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard_page"))
    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard_page"))
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_page"))


# ---------- JSON API routes (called via fetch() from JS) ----------
@auth_bp.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    target_role = (data.get("target_role") or "Software Engineer").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are all required."}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        return jsonify({"error": "An account with that email already exists."}), 409

    password_hash = generate_password_hash(password)
    cursor = db.execute(
        "INSERT INTO users (name, email, password_hash, target_role) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, target_role),
    )
    db.commit()

    session.permanent = True
    session["user_id"] = cursor.lastrowid
    session["user_name"] = name
    return jsonify({"message": "Account created successfully.", "redirect": url_for("dashboard.dashboard_page")})


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify({"message": "Logged in successfully.", "redirect": url_for("dashboard.dashboard_page")})
