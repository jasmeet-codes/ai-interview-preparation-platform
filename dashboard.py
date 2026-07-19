"""
routes/dashboard.py
--------------------
Renders the dashboard page and exposes a JSON analytics endpoint that the
frontend charts (Chart.js) pull data from.
"""

from flask import Blueprint, render_template, session, jsonify
from database import get_db
from utils import login_required
from config import CATEGORIES, DIFFICULTIES

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    return render_template(
        "dashboard.html",
        categories=CATEGORIES,
        difficulties=DIFFICULTIES,
        user_name=session.get("user_name"),
    )


@dashboard_bp.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html", user_name=session.get("user_name"))


@dashboard_bp.route("/api/analytics")
@login_required
def api_analytics():
    """Aggregate the logged-in user's interview history for charts + stats cards."""
    db = get_db()
    user_id = session["user_id"]

    interviews = db.execute(
        """SELECT id, category, difficulty, role, avg_score, status, created_at, completed_at
           FROM interviews WHERE user_id = ? ORDER BY created_at ASC""",
        (user_id,),
    ).fetchall()

    completed = [i for i in interviews if i["status"] == "completed"]

    # ---- summary stats ----
    total_interviews = len(completed)
    overall_avg = (
        round(sum(i["avg_score"] for i in completed) / total_interviews, 1)
        if total_interviews else 0
    )
    best_score = round(max((i["avg_score"] for i in completed), default=0), 1)

    # ---- score trend over time (line chart) ----
    trend = [{"label": f"#{idx + 1}", "score": round(i["avg_score"], 1)} for idx, i in enumerate(completed)]

    # ---- average score per category (bar chart) ----
    by_category = {}
    for i in completed:
        by_category.setdefault(i["category"], []).append(i["avg_score"])
    category_averages = [
        {"category": cat, "avg": round(sum(scores) / len(scores), 1)}
        for cat, scores in by_category.items()
    ]

    # ---- count per difficulty (doughnut chart) ----
    by_difficulty = {}
    for i in completed:
        by_difficulty[i["difficulty"]] = by_difficulty.get(i["difficulty"], 0) + 1

    # ---- recent history table ----
    recent = [dict(i) for i in reversed(interviews[-10:])]

    return jsonify({
        "total_interviews": total_interviews,
        "overall_avg": overall_avg,
        "best_score": best_score,
        "trend": trend,
        "category_averages": category_averages,
        "difficulty_counts": by_difficulty,
        "recent": recent,
    })
