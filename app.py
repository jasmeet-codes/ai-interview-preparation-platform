"""
app.py
------
Application entry point. Run with:  python app.py
"""

from flask import Flask, render_template, session, redirect, url_for
from config import Config
from database import close_db, init_db
from auth import auth_bp
from dashboard import dashboard_bp
from interview import interview_bp
from resume import resume_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register the DB teardown handler + create tables on first run.
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db(app)

    # Register all route blueprints.
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(resume_bp)

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard.dashboard_page"))
        return render_template("index.html")

    @app.context_processor
    def inject_globals():
        """Make a few things available to every template automatically."""
        return {
            "is_logged_in": "user_id" in session,
            "current_user_name": session.get("user_name"),
            "ai_mock_mode": app.config["AI_MOCK_MODE"],
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=5000)
