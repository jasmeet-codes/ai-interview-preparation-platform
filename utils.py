"""
utils.py
--------
Small shared helpers used across multiple route blueprints.
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify


def login_required(view_func):
    """Redirect to /login (or return 401 for API/JSON calls) if not logged in."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Not authenticated"}), 401
            return redirect(url_for("auth.login_page", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped
