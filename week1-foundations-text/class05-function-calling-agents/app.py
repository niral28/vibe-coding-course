"""
Flask Web Backend for AI Math Tutor 🧮
=========================================
Reads GEMINI_API_KEY from .env using python-dotenv.
Implements tools (check_answer, end_session) via Gemini OpenAI client compatibility.
"""

import os
import json
import time
import uuid
import random
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment variables securely from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file! Please set it before running app.py.")

app = Flask(__name__)
CORS(app)

MODEL = "gemini-3.5-flash"

# Connect to Gemini via its OpenAI-compatible endpoint
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# In-memory store for active session states
SESSIONS = {}


# ============================================================================
# PROBLEM GENERATOR (Python holds the mathematical truth)
# ============================================================================
def make_problem(level, topics):
    """
    Generates a math problem based on difficulty level (1-5) and selected topics.
    Returns a dict: {"text": str, "answer": int/float/str, "topic": str, "display_text": str}
    """
    if not topics:
        topics = ["addition"]

    # Pick one topic from the user's selected list
    chosen_topic = random.choice(topics)
    if chosen_topic == "mixed":
        chosen_topic = random.choice(["addition", "subtraction", "multiplication", "division"])

    if chosen_topic == "addition":
        if level <= 1:
            a, b = random.randint(2, 9), random.randint(2, 9)
        elif level == 2:
            a, b = random.randint(10, 30), random.randint(5, 20)
        elif level == 3:
            a, b = random.randint(20, 75), random.randint(15, 50)
        elif level == 4:
            a, b = random.randint(50, 150), random.randint(30, 120)
        else:
            a, b = random.randint(100, 500), random.randint(100, 500)
        return {"text": f"{a} + {b}", "answer": a + b, "topic": "Addition", "level": level}

    elif chosen_topic == "subtraction":
        if level <= 1:
            a, b = random.randint(2, 9), random.randint(2, 9)
        elif level == 2:
            a, b = random.randint(10, 30), random.randint(5, 20)
        elif level == 3:
            a, b = random.randint(25, 80), random.randint(10, 45)
        elif level == 4:
            a, b = random.randint(60, 180), random.randint(25, 95)
        else:
            a, b = random.randint(150, 600), random.randint(50, 300)
        if b > a:
            a, b = b, a  # non-negative for friendliness
        return {"text": f"{a} - {b}", "answer": a - b, "topic": "Subtraction", "level": level}

    elif chosen_topic == "multiplication":
        if level <= 1:
            a, b = random.randint(2, 5), random.randint(2, 5)
        elif level == 2:
            a, b = random.randint(2, 9), random.randint(2, 9)
        elif level == 3:
            a, b = random.randint(5, 12), random.randint(4, 12)
        elif level == 4:
            a, b = random.randint(10, 20), random.randint(3, 12)
        else:
            a, b = random.randint(12, 25), random.randint(6, 15)
        return {"text": f"{a} × {b}", "answer": a * b, "topic": "Multiplication", "level": level}

    elif chosen_topic == "division":
        if level <= 1:
            b = random.randint(2, 5)
            ans = random.randint(1, 5)
        elif level == 2:
            b = random.randint(2, 9)
            ans = random.randint(2, 9)
        elif level == 3:
            b = random.randint(3, 12)
            ans = random.randint(3, 12)
        elif level == 4:
            b = random.randint(4, 15)
            ans = random.randint(5, 15)
        else:
            b = random.randint(6, 20)
            ans = random.randint(8, 20)
        a = b * ans
        return {"text": f"{a} ÷ {b}", "answer": ans, "topic": "Division", "level": level}

    elif chosen_topic == "two-step":
        if level <= 2:
            a, b = random.randint(2, 6), random.randint(2, 5)
            c = random.randint(1, 10)
            return {"text": f"{a} × {b} + {c}", "answer": (a * b) + c, "topic": "Two-Step", "level": level}
        elif level == 3:
            a, b = random.randint(3, 9), random.randint(2, 8)
            c = random.randint(2, 15)
            return {"text": f"{a} × {b} - {c}", "answer": (a * b) - c, "topic": "Two-Step", "level": level}
        else:
            a, b = random.randint(4, 12), random.randint(3, 9)
            c, d = random.randint(5, 20), random.randint(2, 6)
            return {"text": f"({a} + {c}) × {d}", "answer": (a + c) * d, "topic": "Two-Step", "level": level}

    elif chosen_topic == "fractions":
        # Common denominator fractions for clarity
        denom = random.choice([3, 4, 5, 6, 8, 10])
        num1 = random.randint(1, denom - 1)
        num2 = random.randint(1, denom - 1)
        op = random.choice(["+", "-"])
        if op == "-":
            if num2 > num1:
                num1, num2 = num2, num1
            ans_num = num1 - num2
        else:
            ans_num = num1 + num2
        text = f"{num1}/{denom} {op} {num2}/{denom}"
        ans_str = f"{ans_num}/{denom}"
        return {"text": text, "answer": ans_str, "topic": "Fractions", "level": level}

    elif chosen_topic == "decimals":
        if level <= 2:
            a = round(random.uniform(1.0, 9.9), 1)
            b = round(random.uniform(1.0, 9.9), 1)
            op = "+"
            ans = round(a + b, 1)
        elif level == 3:
            a = round(random.uniform(5.0, 19.9), 1)
            b = round(random.uniform(1.0, 9.9), 1)
            if b > a:
                a, b = b, a
            op = "-"
            ans = round(a - b, 1)
        else:
            a = round(random.uniform(1.0, 5.0), 1)
            b = random.randint(2, 6)
            op = "×"
            ans = round(a * b, 1)
        return {"text": f"{a} {op} {b}", "answer": ans, "topic": "Decimals", "level": level}

    # Fallback to simple addition
    a, b = random.randint(2, 9), random.randint(2, 9)
    return {"text": f"{a} + {b}", "answer": a + b, "topic": "Addition", "level": level}


# ============================================================================
# TOOL DEFINITIONS & GRADER
# ============================================================================
def check_answer(student_answer, problem, prior_misses=0):
    """
    Grades the student's typed answer against Python's stored correct answer.
    Handles integers, decimals, and fraction formats.
    """
    raw_str = str(student_answer).strip()
    correct = problem["answer"]

    # Check fraction matching e.g. "3/4"
    if "/" in str(correct):
        if raw_str == str(correct):
            return f"CORRECT: {problem['text']} = {correct}. Praise them warmly!"
        else:
            if prior_misses == 0:
                return (f"INCORRECT: Student typed '{raw_str}', but correct is '{correct}'. "
                        f"First try on this problem. Do NOT reveal answer or give detailed hint yet; "
                        f"just encourage them to try again.")
            else:
                return (f"INCORRECT: Student typed '{raw_str}', correct is '{correct}'. "
                        f"Give one encouraging hint on how to add/subtract fractions with matching denominators.")

    # Check decimal / float matching
    if isinstance(correct, float):
        try:
            val = float(raw_str)
            if abs(val - correct) < 0.05:
                return f"CORRECT: {problem['text']} = {correct}. Praise them warmly!"
        except ValueError:
            return "NOT_A_NUMBER: The answer should be a number (like 3.5). Ask gently to re-type."
    else:
        # Check integer matching
        try:
            val = int(raw_str)
            if val == correct:
                return f"CORRECT: {problem['text']} = {correct}. Praise them warmly!"
        except ValueError:
            return "NOT_A_NUMBER: The answer should be a whole number. Ask gently to re-type."

    # If incorrect:
    if prior_misses == 0:
        return (f"INCORRECT: The student typed {raw_str}, but {problem['text']} = {correct}. "
                f"This is their first try on this problem. Do NOT reveal the answer or hint yet. "
                f"Just give one short, warm sentence saying it's not quite right and to try again!")
    else:
        return (f"INCORRECT: The student typed {raw_str}, but {problem['text']} = {correct}. "
                f"Do NOT reveal the answer. Give one short, friendly method hint nudging them to the right path.")


def end_session(reason, correct_count, total):
    """Returns wrap-up sentence from tutor tool."""
    if reason == "FINISHED":
        return f"🎉 Session complete! You got {correct_count} out of {total} right. Great work practicing today!"
    elif reason == "TIME_EXPIRED":
        return f"⏱️ Time's up for today! You solved {correct_count} out of {total} correctly. Excellent effort!"
    elif reason == "QUIT":
        return f"👋 Session stopped early. You got {correct_count} out of {total} correct. See you next time!"
    else:
        return f"Session ended ({reason}). Score: {correct_count}/{total}."


# Gemini Tool schema definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_answer",
            "description": (
                "Check the student's answer against the REAL answer computed in Python. "
                "Call this EVERY TIME the student submits an answer. Never compute arithmetic in your head."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "student_answer": {
                        "type": "string",
                        "description": "What the student typed as their answer",
                    }
                },
                "required": ["student_answer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_session",
            "description": "Call this when the practice session is over.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why the session ended",
                        "enum": ["FINISHED", "TIME_EXPIRED", "QUIT"],
                    },
                },
                "required": ["reason"],
            },
        },
    },
]


SYSTEM_PROMPT = (
    "You are a warm, encouraging math tutor for students in grades 3-8. "
    "VERY IMPORTANT: The web app itself presents each problem. Do NOT state new problems yourself. "
    "For every answer the student submits, you MUST call check_answer to grade it. "
    "Never grade arithmetic in your head — Python is the source of truth. "
    "When check_answer returns CORRECT, give ONE short, enthusiastic line of praise. "
    "When check_answer returns INCORRECT: if first try, give one warm line saying try again; "
    "if second/third try, give ONE short method hint without revealing the answer. "
    "Keep every reply to 1-2 friendly sentences. Call end_session when the session wraps up."
)


# ============================================================================
# FLASK ROUTES
# ============================================================================
@app.route("/")
def index():
    """Renders the main web application."""
    return render_template("index.html")


@app.route("/api/start_session", methods=["POST"])
def api_start_session():
    """Initializes a new practice session with either Fixed Questions mode or Time Limit mode."""
    data = request.json or {}
    level = int(data.get("difficulty", 1))
    topics = data.get("topics", ["addition"])
    mode = data.get("mode", "questions")  # 'questions' or 'time'

    if mode == "time":
        time_limit_minutes = float(data.get("time_limit_minutes", 3))
        time_limit_seconds = time_limit_minutes * 60
        max_questions = 999  # uncapped for time limit mode (solve as many as possible!)
    else:
        max_questions = int(data.get("max_questions", 8))
        time_limit_seconds = None

    session_id = str(uuid.uuid4())
    start_time = time.time()

    first_problem = make_problem(level, topics)

    SESSIONS[session_id] = {
        "session_id": session_id,
        "mode": mode,
        "level": level,
        "topics": topics,
        "max_questions": max_questions,
        "time_limit_seconds": time_limit_seconds,
        "start_time": start_time,
        "streak": 0,
        "correct_count": 0,
        "problems_done": 0,
        "attempts_on_current": 0,
        "MAX_TRIES": 3,
        "current_problem": first_problem,
        "question_start_time": start_time,
        "history": [],
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
        "is_finished": False,
        "finish_reason": None,
    }

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "mode": mode,
        "current_problem": {
            "text": first_problem["text"],
            "topic": first_problem["topic"],
            "level": first_problem["level"],
        },
        "level": level,
        "streak": 0,
        "problems_done": 0,
        "max_questions": max_questions,
        "time_limit_seconds": time_limit_seconds,
    })


@app.route("/api/submit_answer", methods=["POST"])
def api_submit_answer():
    """Submits an answer, grades with Gemini tools, updates time and difficulty."""
    data = request.json or {}
    session_id = data.get("session_id")

    if not session_id or session_id not in SESSIONS:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    session = SESSIONS[session_id]
    if session["is_finished"]:
        return jsonify({"status": "error", "message": "Session is already finished"}), 400

    student_answer = str(data.get("answer", "")).strip()
    now = time.time()
    time_spent_on_question = round(now - session["question_start_time"], 1)

    problem = session["current_problem"]
    attempts = session["attempts_on_current"]

    # 1. Run check_answer python tool directly & get AI message via Gemini
    grader_result = check_answer(student_answer, problem, prior_misses=attempts)

    # 2. Communicate with Gemini model via OpenAI tool execution pattern
    session["messages"].append({"role": "user", "content": f"My answer is: {student_answer}"})

    ai_reply = ""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=session["messages"],
            tools=TOOLS,
        )
        ai_message = response.choices[0].message
        session["messages"].append({
            "role": "assistant",
            "content": ai_message.content or "",
            "tool_calls": ai_message.tool_calls,
        })

        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                if name == "check_answer":
                    session["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": grader_result,
                    })

            # Follow up call for AI's conversational response
            follow_up = client.chat.completions.create(model=MODEL, messages=session["messages"])
            ai_reply = follow_up.choices[0].message.content
            session["messages"].append({"role": "assistant", "content": ai_reply})
        else:
            ai_reply = ai_message.content or "Nice try! Let me know if you want another hint."

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Graceful fallback response if API has a hiccup
        if grader_result.startswith("CORRECT"):
            ai_reply = f"🎉 Spot on! {problem['text']} = {problem['answer']}."
        else:
            ai_reply = f"Not quite right yet! Keep going!"

    # 3. Update session state & metrics
    is_correct = grader_result.startswith("CORRECT")
    is_not_number = grader_result.startswith("NOT_A_NUMBER")

    attempt_revealed_answer = False

    if is_correct:
        session["correct_count"] += 1
        session["problems_done"] += 1
        session["streak"] += 1
        session["attempts_on_current"] = 0

        # Record question in history
        session["history"].append({
            "question_num": session["problems_done"],
            "problem_text": problem["text"],
            "student_answer": student_answer,
            "correct_answer": problem["answer"],
            "is_correct": True,
            "time_spent_seconds": time_spent_on_question,
            "level": problem["level"],
            "topic": problem["topic"],
            "ai_feedback": ai_reply,
        })

        # Adaptive difficulty adjustment: 2 in a row -> level up
        if session["streak"] >= 2 and session["level"] < 5:
            session["level"] += 1
            session["streak"] = 0

        # Generate next problem
        session["current_problem"] = make_problem(session["level"], session["topics"])
        session["question_start_time"] = time.time()

    elif not is_not_number:
        session["streak"] = 0
        session["attempts_on_current"] += 1

        if session["attempts_on_current"] >= session["MAX_TRIES"]:
            # Max attempts reached: reveal answer and move on
            attempt_revealed_answer = True
            session["problems_done"] += 1

            session["history"].append({
                "question_num": session["problems_done"],
                "problem_text": problem["text"],
                "student_answer": student_answer,
                "correct_answer": problem["answer"],
                "is_correct": False,
                "time_spent_seconds": time_spent_on_question,
                "level": problem["level"],
                "topic": problem["topic"],
                "ai_feedback": f"Solution: {problem['answer']}. {ai_reply}",
            })

            # Ease off level on struggle
            if session["level"] > 1:
                session["level"] -= 1

            session["attempts_on_current"] = 0
            session["current_problem"] = make_problem(session["level"], session["topics"])
            session["question_start_time"] = time.time()

    # 4. Check Timer & Max Questions Rule:
    # "if the time limit runs out while I'm in the middle of a question, let me finish that question, then end."
    total_elapsed = now - session["start_time"]
    time_limit_expired = (
        session["time_limit_seconds"] is not None
        and total_elapsed >= session["time_limit_seconds"]
    )
    questions_reached = session["problems_done"] >= session["max_questions"]

    # Wrap up session if time is expired or max questions reached (after question is completed)
    if (time_limit_expired or questions_reached) and (is_correct or attempt_revealed_answer):
        session["is_finished"] = True
        session["finish_reason"] = "TIME_EXPIRED" if time_limit_expired else "FINISHED"

    return jsonify({
        "status": "success",
        "is_correct": is_correct,
        "is_not_number": is_not_number,
        "attempts": session["attempts_on_current"],
        "max_tries": session["MAX_TRIES"],
        "revealed_answer": problem["answer"] if attempt_revealed_answer else None,
        "ai_reply": ai_reply,
        "is_finished": session["is_finished"],
        "finish_reason": session["finish_reason"],
        "level": session["level"],
        "streak": session["streak"],
        "correct_count": session["correct_count"],
        "problems_done": session["problems_done"],
        "max_questions": session["max_questions"],
        "next_problem": {
            "text": session["current_problem"]["text"],
            "topic": session["current_problem"]["topic"],
            "level": session["current_problem"]["level"],
        } if not session["is_finished"] else None,
    })


@app.route("/api/end_session", methods=["POST"])
def api_end_session():
    """Allows user to quit session manually."""
    data = request.json or {}
    session_id = data.get("session_id")

    if not session_id or session_id not in SESSIONS:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    session = SESSIONS[session_id]
    session["is_finished"] = True
    session["finish_reason"] = "QUIT"

    wrap_message = end_session("QUIT", session["correct_count"], session["problems_done"])
    return jsonify({"status": "success", "message": wrap_message})


@app.route("/api/session_summary", methods=["GET"])
def api_session_summary():
    """Fetches summary details for the summary screen."""
    session_id = request.args.get("session_id")

    if not session_id or session_id not in SESSIONS:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    session = SESSIONS[session_id]
    total_time = round(time.time() - session["start_time"], 1)

    # Compute average time per question
    history = session["history"]
    if history:
        avg_time_per_q = round(sum(item["time_spent_seconds"] for item in history) / len(history), 1)
    else:
        avg_time_per_q = 0.0

    accuracy_pct = round((session["correct_count"] / max(1, session["problems_done"])) * 100, 1)

    # Fetch final Gemini summary text using end_session tool format
    reason = session["finish_reason"] or "FINISHED"
    summary_text = end_session(reason, session["correct_count"], session["problems_done"])

    return jsonify({
        "status": "success",
        "correct_count": session["correct_count"],
        "problems_done": session["problems_done"],
        "incorrect_count": session["problems_done"] - session["correct_count"],
        "accuracy_pct": accuracy_pct,
        "total_time_seconds": total_time,
        "avg_time_per_question": avg_time_per_q,
        "history": history,
        "summary_text": summary_text,
        "finish_reason": reason,
    })


if __name__ == "__main__":
    print("🚀 Starting AI Math Tutor Web App on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
