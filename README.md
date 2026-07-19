# InterviewIQ - AI Interview Preparation Platform

A full-stack web app for practicing job interviews with an AI interviewer.
Pick a category (HR, Technical, Aptitude, Coding) and difficulty, answer
questions one at a time, and get an instant score (1-10) with strengths,
weaknesses, and suggestions - plus resume analysis and progress analytics.

Built with **Flask + SQLite** on the backend and plain **HTML/CSS/JavaScript**
on the frontend (no build step required).

---

## Features

- Email/password signup & login (hashed passwords, session-based auth)
- Dashboard with stats, category picker, and recent interview history
- Choose category (HR / Technical / Aptitude / Coding) and difficulty (Easy / Medium / Hard)
- AI interview chat: one question at a time, with score + feedback + strengths + weaknesses + suggestions per answer
- 7 auto-generated questions per interview (configurable, 5-10 range)
- Full interview history and scores stored in SQLite
- Analytics page with score trend, category, and difficulty charts (Chart.js)
- Resume upload (PDF) with AI-driven scoring, strengths, gaps, and suggestions
- Dark / light mode toggle (persisted in the browser)
- Fully responsive, mobile-friendly UI
- **Works with zero setup**: if no AI API key is configured, the app automatically
  uses a realistic built-in mock question bank and feedback engine

---

## Project structure

```
ai-interview-platform/
├── app.py                     # Flask application entry point
├── config.py                  # Central configuration, loads .env
├── database.py                # SQLite connection + schema
├── utils.py                   # login_required decorator etc.
├── requirements.txt
├── .env.example                # Copy to .env and fill in your API key
├── instance/
│   └── interview_prep.db       # SQLite database (auto-created on first run)
├── routes/
│   ├── auth.py                 # signup / login / logout
│   ├── dashboard.py            # dashboard page + analytics API
│   ├── interview.py            # interview setup, chat, scoring
│   └── resume.py                # resume upload + analysis
├── services/
│   ├── ai_service.py            # OpenAI integration + automatic mock fallback
│   └── resume_parser.py         # PDF text extraction
├── static/
│   ├── css/style.css            # design system (light + dark themes)
│   ├── js/                      # main.js, auth.js, dashboard.js,
│   │                             # interview_setup.js, interview_chat.js,
│   │                             # resume.js, analytics.js
│   └── uploads/resumes/         # uploaded resume PDFs are stored here
└── templates/
    ├── base.html, index.html, signup.html, login.html
    ├── dashboard.html, select_interview.html
    ├── interview_chat.html, interview_summary.html
    ├── resume.html, analytics.html, 404.html
```

---

## 1. Installation

**Requirements:** Python 3.9+

```bash
# 1. Clone / unzip the project, then move into it
cd ai-interview-platform

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 2. Configure your environment (and paste your API key here)

```bash
# Copy the example env file
cp .env.example .env      # Windows: copy .env.example .env
```

Open the new **`.env`** file in a text editor. You'll see:

```
SECRET_KEY=change-this-to-a-random-secret-key
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

- **Paste your OpenAI API key** on the `OPENAI_API_KEY=` line, e.g.
  `OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx`
  (Get a key at https://platform.openai.com/api-keys)
- Generate a real `SECRET_KEY` with:
  `python -c "import secrets; print(secrets.token_hex(32))"`
- **No API key? No problem.** Leave `OPENAI_API_KEY` blank and the app
  automatically switches to its built-in mock AI (see `services/ai_service.py`) -
  every feature still works, using a curated bank of realistic questions and a
  heuristic feedback/scoring engine. A small "Running in mock-AI demo mode"
  note appears in the footer when this is active.

All configuration is centralized in **`config.py`**, which reads from `.env`
via `python-dotenv` - the API key is never hardcoded anywhere in the source.

## 3. Run the app

```bash
python app.py
```

The first run automatically creates `instance/interview_prep.db` with all
required tables. Then open:

```
http://127.0.0.1:5000
```

Sign up for an account and start practicing.

---

## How the AI integration works

`services/ai_service.py` is the single place that talks to the AI:

- `generate_questions(category, difficulty, role, count)` - generates interview questions
- `evaluate_answer(question, answer, category, difficulty)` - scores an answer 1-10 with feedback
- `analyze_resume(resume_text, target_role)` - scores/analyzes a resume

Each function tries the real OpenAI API first (if `OPENAI_API_KEY` is set in
`.env`). If the key is missing, or the API call fails for any reason (network
issue, invalid key, rate limit), the function **automatically falls back** to
a local mock implementation so the app never breaks. You can swap in a
different provider (Anthropic, local LLM, etc.) by editing `_call_openai`
and the prompt-building code in that one file - no other file needs to change.

---

## Notes on the mock AI mode

- Questions come from a curated bank of 7 questions per category/difficulty
  combination (`MOCK_QUESTION_BANK` in `services/ai_service.py`) - easy to edit or expand.
  Includes 12 combinations covering all categories x difficulties in the requested 5-10 range.
- Feedback/scoring uses a simple heuristic (answer length + keyword presence)
  so scores feel responsive to what you actually type, without needing a real model.
- Resume analysis in mock mode scans for common resume keywords and gives an
  approximate score - clearly a heuristic, not a substitute for the real API.

---

## Tech stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Backend    | Python, Flask, Flask sessions            |
| Database   | SQLite (raw `sqlite3`, no ORM)           |
| Frontend   | HTML5, CSS3 (custom design system), vanilla JavaScript |
| Charts     | Chart.js (via CDN)                       |
| PDF parsing| pypdf                                    |
| AI         | OpenAI Chat Completions API (optional) with mock fallback |

---

## Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plaintext).
- The API key lives only in `.env`, which should be added to `.gitignore` and never committed.
- Session cookies are signed using `SECRET_KEY` - make sure to set a strong,
  random value in production.
- File uploads are restricted to PDF only and capped at 5MB by default (see `MAX_UPLOAD_MB` in `.env`).

## License

Free to use and modify for learning or personal projects.
