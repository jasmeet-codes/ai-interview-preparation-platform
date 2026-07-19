"""
services/ai_service.py
-----------------------
Single point of contact between the Flask routes and "the AI".

Every function below has two code paths:
    1. REAL MODE  - if config.AI_MOCK_MODE is False, we call the OpenAI
                    Chat Completions API (see _call_openai).
    2. MOCK MODE  - if no API key is configured, we generate believable
                    questions/feedback locally so the whole app keeps
                    working with zero setup and zero cost.

This means routes never need to know or care whether a real key is present.
"""

import json
import random
import re
import requests
from flask import current_app

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


# ============================================================
# Low level helper for calling OpenAI (used by all "real mode" functions)
# ============================================================
def _call_openai(system_prompt, user_prompt, expect_json=True):
    api_key = current_app.config["OPENAI_API_KEY"]
    model = current_app.config["OPENAI_MODEL"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }
    if expect_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content) if expect_json else content
    except Exception as exc:  # network error, bad key, rate limit, parse error...
        current_app.logger.warning(f"OpenAI call failed, falling back to mock: {exc}")
        return None  # signals caller to use the mock path


# ============================================================
# MOCK DATA BANK - used automatically when no API key is configured
# ============================================================
MOCK_QUESTION_BANK = {
    "HR": {
        "Easy": [
            "Tell me about yourself.",
            "Why do you want to work at our company?",
            "What are your strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Why should we hire you?",
            "What motivates you at work?",
            "Describe your ideal work environment.",
        ],
        "Medium": [
            "Tell me about a time you handled conflict with a coworker.",
            "Describe a situation where you failed and what you learned.",
            "How do you prioritize tasks when everything feels urgent?",
            "Tell me about a time you had to persuade someone.",
            "How do you handle constructive criticism?",
            "Describe a time you went above and beyond your job duties.",
            "How do you stay productive while working remotely?",
        ],
        "Hard": [
            "Tell me about the most difficult decision you've had to make at work.",
            "Describe a time you disagreed with your manager's decision. What did you do?",
            "How would you handle leading a team through a layoff?",
            "Tell me about a time you had to deliver bad news to a stakeholder.",
            "Describe a situation where you had to make an ethical judgment call.",
            "How do you handle being wrong in front of your entire team?",
            "Tell me about a time you had to manage conflicting priorities from two leaders.",
        ],
    },
    "Technical": {
        "Easy": [
            "What is the difference between a process and a thread?",
            "Explain the difference between SQL and NoSQL databases.",
            "What is the purpose of version control systems like Git?",
            "What is an API and why is it useful?",
            "Explain the difference between GET and POST HTTP methods.",
            "What is object-oriented programming?",
            "What is the difference between synchronous and asynchronous code?",
        ],
        "Medium": [
            "Explain how a REST API differs from GraphQL.",
            "What is database indexing and why does it matter?",
            "Explain the CAP theorem in distributed systems.",
            "How would you design a rate limiter for an API?",
            "What is the difference between horizontal and vertical scaling?",
            "Explain caching strategies and when you'd use them.",
            "What is dependency injection and why is it useful?",
        ],
        "Hard": [
            "Design a URL shortening service like bit.ly. What are the key components?",
            "How would you design a system to handle 1 million concurrent users?",
            "Explain how you would debug a memory leak in a production service.",
            "Design a notification system that supports email, SMS, and push.",
            "How would you design a distributed cache?",
            "Explain trade-offs between microservices and a monolith at scale.",
            "How would you design a real-time chat application?",
        ],
    },
    "Aptitude": {
        "Easy": [
            "If a train travels 60 km in 1.5 hours, what is its average speed?",
            "A shopkeeper marks up an item by 20% then gives a 10% discount. What is the net profit percentage?",
            "What comes next in the series: 2, 4, 8, 16, ?",
            "If 5 workers can build a wall in 10 days, how many days for 10 workers?",
            "A is twice as old as B. In 10 years, A will be 1.5 times as old as B. Find their current ages.",
            "What is 15% of 480?",
            "If the ratio of boys to girls in a class is 3:2 and there are 30 students, how many girls are there?",
        ],
        "Medium": [
            "A boat travels 20 km upstream in 4 hours and 20 km downstream in 2 hours. Find the speed of the boat in still water.",
            "In how many ways can 5 people be seated in a row such that 2 specific people are always together?",
            "The average of 5 numbers is 20. If one number is excluded, the average becomes 22. Find the excluded number.",
            "A can complete a task in 12 days, B in 15 days. How long will they take working together?",
            "Find the probability of getting exactly 2 heads in 3 coin tosses.",
            "A sum of money doubles itself in 8 years at simple interest. Find the rate of interest.",
            "If the perimeter of a rectangle is 60 cm and its length is twice its width, find its area.",
        ],
        "Hard": [
            "Three pipes A, B and C can fill a tank in 12, 15 and 20 hours respectively. If all three are opened together but C is closed after 4 hours, how long to fill the tank?",
            "A sum of money becomes 3 times itself in 10 years at compound interest. In how many years will it become 9 times itself?",
            "In a group of 100 people, 60 like tea, 50 like coffee, and 20 like neither. How many like both?",
            "A train crosses a platform of length 300m in 30 seconds and a pole in 15 seconds. Find the length and speed of the train.",
            "Find the number of ways to arrange the letters of 'MISSISSIPPI'.",
            "A alone can do a piece of work in 6 days and B alone in 8 days. With help of C they finish in 3 days. How long would C alone take?",
            "Two trains start from stations 300 km apart and move towards each other. Find their meeting time given speeds of 40 km/h and 60 km/h.",
        ],
    },
    "Coding": {
        "Easy": [
            "Write a function to check if a given string is a palindrome.",
            "Write a function to find the maximum element in an array.",
            "Write a function to reverse a linked list.",
            "Write a function to check if two strings are anagrams.",
            "Write a function to find the factorial of a number using recursion.",
            "Write a function to remove duplicates from an array.",
            "Write a function to count the vowels in a string.",
        ],
        "Medium": [
            "Given an array of integers, find two numbers that add up to a target sum (Two Sum problem). Explain your approach.",
            "Write a function to find the first non-repeating character in a string.",
            "Explain and implement a binary search algorithm.",
            "Write a function to detect a cycle in a linked list.",
            "Given a string, find the length of the longest substring without repeating characters.",
            "Write a function to merge two sorted arrays into one sorted array.",
            "Implement a function to check if a binary tree is balanced.",
        ],
        "Hard": [
            "Design and explain an algorithm to find the median of two sorted arrays in O(log(min(m,n))) time.",
            "Given a matrix, write an algorithm to rotate it 90 degrees in place.",
            "Explain how you would implement an LRU (Least Recently Used) cache.",
            "Write an algorithm to find the shortest path in a weighted graph (Dijkstra's algorithm) and explain its complexity.",
            "Given a set of intervals, merge all overlapping intervals. Explain your approach and complexity.",
            "Design an algorithm to serialize and deserialize a binary tree.",
            "Explain how you would solve the 'N-Queens' problem using backtracking.",
        ],
    },
}


def generate_questions(category, difficulty, role, count):
    """
    Return a list of `count` interview question strings for the given
    category/difficulty/role. Tries the real AI first, falls back to the
    mock question bank automatically.
    """
    if not current_app.config["AI_MOCK_MODE"]:
        system = (
            "You are an expert technical interviewer. Generate realistic, "
            "specific interview questions. Respond ONLY with JSON in the "
            'form {"questions": ["...", "..."]}.'
        )
        user = (
            f"Generate {count} unique {difficulty.lower()}-difficulty {category} "
            f"interview questions for a candidate applying for the role: '{role}'. "
            "Questions should be one sentence each, no numbering, no answers."
        )
        result = _call_openai(system, user, expect_json=True)
        if result and isinstance(result.get("questions"), list) and len(result["questions"]) >= count:
            return result["questions"][:count]

    # ---- MOCK fallback ----
    bank = MOCK_QUESTION_BANK.get(category, MOCK_QUESTION_BANK["HR"]).get(
        difficulty, MOCK_QUESTION_BANK["HR"]["Easy"]
    )
    questions = bank.copy()
    random.shuffle(questions)
    # If more questions are requested than the bank holds, cycle through again.
    while len(questions) < count:
        questions += random.sample(bank, min(len(bank), count - len(questions)))
    return questions[:count]


def _mock_evaluate(question, answer, category, difficulty):
    """A lightweight, deterministic heuristic scorer used when no AI key is set.
    Not a real NLP model - just enough signal to make the demo feel alive."""
    answer = (answer or "").strip()
    word_count = len(answer.split())

    # Very small, very naive heuristics just to vary the score sensibly.
    length_score = min(5, word_count // 15)              # up to 5 pts for depth
    keyword_bonus = 1 if re.search(r"\b(because|example|result|I|team)\b", answer, re.I) else 0
    base = 3 if word_count > 0 else 0
    score = max(1, min(10, base + length_score + keyword_bonus + random.randint(0, 1)))

    if word_count == 0:
        feedback = "No answer was provided, so it's impossible to evaluate content or delivery."
        strengths = "N/A"
        weaknesses = "The question was left unanswered."
        suggestions = "Try to always give at least a brief attempt, even if you're unsure - partial credit beats a blank."
    elif word_count < 15:
        feedback = "Your answer is quite brief. Interviewers usually expect a structured response with context, action, and outcome."
        strengths = "Concise and to the point."
        weaknesses = "Lacks detail, examples, and depth to fully demonstrate your understanding."
        suggestions = "Expand your answer using a structure like Situation -> Action -> Result, and include a concrete example."
    elif score >= 8:
        feedback = "Strong, detailed answer that addresses the question directly and shows good communication."
        strengths = "Clear structure, relevant detail, and confident tone."
        weaknesses = "Could tighten the answer slightly to stay within a typical 60-90 second spoken response."
        suggestions = "Keep practicing timing your answers aloud so they stay sharp under interview pressure."
    else:
        feedback = "A solid attempt that covers the basics but could go deeper with specific examples or reasoning."
        strengths = "Shows understanding of the core concept."
        weaknesses = "Missing specific examples, metrics, or deeper reasoning to fully convince an interviewer."
        suggestions = f"For {category} questions at {difficulty} level, back up claims with a specific example or number."

    return {
        "score": score,
        "feedback": feedback,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
    }


def evaluate_answer(question, answer, category, difficulty):
    """
    Return dict: {score (1-10), feedback, strengths, weaknesses, suggestions}
    Tries real AI first, falls back to the mock heuristic evaluator.
    """
    if not current_app.config["AI_MOCK_MODE"]:
        system = (
            "You are an expert interview coach. Evaluate the candidate's answer "
            "honestly and constructively. Respond ONLY with JSON in the form: "
            '{"score": <integer 1-10>, "feedback": "...", "strengths": "...", '
            '"weaknesses": "...", "suggestions": "..."}'
        )
        user = (
            f"Category: {category}\nDifficulty: {difficulty}\n"
            f"Question: {question}\nCandidate's answer: {answer}\n\n"
            "Score the answer from 1 (poor) to 10 (excellent) and give concise, "
            "specific feedback, strengths, weaknesses, and improvement suggestions."
        )
        result = _call_openai(system, user, expect_json=True)
        if result and "score" in result:
            try:
                result["score"] = max(1, min(10, int(result["score"])))
                return result
            except (ValueError, TypeError):
                pass

    return _mock_evaluate(question, answer, category, difficulty)


def analyze_resume(resume_text, target_role="Software Engineer"):
    """
    Return dict: {overall_score, strengths, gaps, suggestions, keywords_found}
    """
    if not current_app.config["AI_MOCK_MODE"]:
        system = (
            "You are an expert resume reviewer and career coach. Respond ONLY "
            "with JSON in the form: {\"overall_score\": <1-10>, \"strengths\": "
            '"...", "gaps": "...", "suggestions": "...", "keywords_found": ["...", "..."]}'
        )
        user = (
            f"Target role: {target_role}\n\nResume text:\n{resume_text[:6000]}\n\n"
            "Analyze this resume for the target role."
        )
        result = _call_openai(system, user, expect_json=True)
        if result and "overall_score" in result:
            return result

    # ---- MOCK fallback: simple keyword-based heuristic analysis ----
    text_lower = resume_text.lower()
    keyword_pool = [
        "python", "java", "javascript", "sql", "react", "flask", "django",
        "project", "team", "led", "developed", "designed", "api", "cloud",
        "aws", "git", "agile", "testing", "communication", "leadership",
    ]
    found = [kw for kw in keyword_pool if kw in text_lower]
    word_count = len(resume_text.split())

    score = min(10, max(3, len(found) // 2 + (2 if word_count > 200 else 0)))

    return {
        "overall_score": score,
        "strengths": (
            f"Resume includes {len(found)} relevant keywords "
            f"({', '.join(found[:8]) if found else 'general terms'}) and has a "
            f"reasonable length of about {word_count} words."
        ),
        "gaps": (
            "Could not detect quantified achievements (numbers/metrics) or a clear "
            "skills section in some resumes - make sure impact is measurable."
            if word_count > 0 else "No readable text was found in the uploaded PDF."
        ),
        "suggestions": (
            f"Tailor the resume more closely to the target role of '{target_role}' by mirroring "
            "keywords from the job description, and quantify achievements "
            "(e.g. 'improved performance by 30%')."
        ),
        "keywords_found": found,
    }
