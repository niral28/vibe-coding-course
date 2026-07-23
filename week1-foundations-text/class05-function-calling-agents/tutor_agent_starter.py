"""
GSET Vibe Coding — Class 5 Project: AI Math Tutor 🧮✅  (Option D — my own agent)
================================================================================

WHAT THIS BUILDS
  An AI tutor for grades 3-8 (built for my Think&Thrive students). It shows a
  math problem, the student types an answer, and the AI uses a TOOL to CHECK
  the answer against the real value that PYTHON computed. It keeps going in a
  LOOP: right answers make the next problem harder, wrong answers get a hint
  and stay at the same level, until the student quits or finishes the session.

WHY THIS IS A REAL "AGENT" (the two big ideas from Class 5)
  • FUNCTION CALLING -> the AI calls check_answer(), a Python function that does
    the REAL grading. The AI never grades in its head, so it can't be confidently
    wrong. (Same trick as validate_word in Wordle: Python holds the truth.)
  • AGENTIC LOOP     -> a while-loop where the AI checks, reacts, and the level
    adapts on its own across many problems with no code edits between steps.

HOW TO RUN IT
  1. Put this file in the class05 folder next to your .env (with GEMINI_API_KEY).
  2. From that folder, with (gset-vibes) active:
       python tutor_agent_starter.py
"""

# --- Libraries we use -------------------------------------------------------
import os
import json
import random
from dotenv import load_dotenv     # reads GEMINI_API_KEY from the .env file
from openai import OpenAI          # talk to Gemini via its OpenAI-compatible endpoint

load_dotenv()

MODEL = "gemini-3.5-flash"         # the tutor's brain
PROBLEMS_PER_SESSION = 8           # how many problems before we wrap up


# ============================================================================
# BUILDING BLOCK — connect to Gemini
# ============================================================================
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


# ============================================================================
# BUILDING BLOCK — make a math problem (Python owns the truth)
# The AI never invents a problem or its answer. Python does, so the answer is
# always correct. Level 1-5 roughly maps to grade 3 up to grade 8.
# Returns a dict like {"text": "7 x 8", "answer": 56}.
# ============================================================================
def make_problem(level):
    """Generate a problem at the given difficulty and return its text + real answer."""
    if level <= 1:
        a, b = random.randint(2, 9), random.randint(2, 9)
        op = random.choice(["+", "-"])
    elif level == 2:
        a, b = random.randint(10, 30), random.randint(2, 12)
        op = random.choice(["+", "-", "x"])
    elif level == 3:
        a, b = random.randint(2, 12), random.randint(2, 12)
        op = "x"
    elif level == 4:
        b = random.randint(2, 12)
        answer = random.randint(2, 12)
        a = b * answer            # guarantees a clean division
        op = "÷"
    else:  # level 5 — two-step
        a, b = random.randint(3, 15), random.randint(2, 9)
        c = random.randint(2, 9)
        text = f"{a} x {b} + {c}"
        return {"text": text, "answer": a * b + c}

    if op == "+":
        answer = a + b
    elif op == "-":
        if b > a:
            a, b = b, a           # keep it non-negative for younger kids
        answer = a - b
    elif op == "x":
        answer = a * b
    elif op == "÷":
        answer = a // b

    return {"text": f"{a} {op} {b}", "answer": answer}


# ============================================================================
# BUILDING BLOCK — the grader (the AI will call this as a TOOL)
# Compares the student's answer to the REAL answer Python already computed.
# This is the anti-hallucination core: grading happens in code, not in the AI.
# ============================================================================
def check_answer(student_answer, problem, prior_misses=0):
    """Grade the student's answer against the real answer for this problem.

    prior_misses = how many times they've already missed THIS problem, so we
    can hold hints back on the very first try and give them on later tries.
    """
    try:
        given = int(str(student_answer).strip())
    except ValueError:
        return "NOT_A_NUMBER: The student did not type a whole number. Gently ask them to type just the number."

    correct = problem["answer"]
    if given == correct:
        return f"CORRECT: {problem['text']} = {correct}. Praise them and get ready for a harder one."
    elif prior_misses == 0:
        # First time missing this problem: no hint yet, just gently try again.
        return (f"INCORRECT: The student said {given}, but {problem['text']} = {correct}. "
                f"This is their first try on this problem. Do NOT give a hint and do NOT "
                f"reveal the answer. Just say one short, warm line that it's not quite right "
                f"and to try again.")
    else:
        # Second or third try: now offer a method hint (still no answer).
        return (f"INCORRECT: The student said {given}, but {problem['text']} = {correct}. "
                f"Do NOT reveal the answer. Give one short, encouraging hint about how to "
                f"get there.")


# ============================================================================
# BUILDING BLOCK — end the session (worked-example tool, like end_game)
# ============================================================================
def end_session(reason, correct_count, total):
    """Return a friendly wrap-up message."""
    if reason == "FINISHED":
        return f"🎉 Session complete! You got {correct_count} out of {total} right. Great work today!"
    elif reason == "QUIT":
        return f"👋 No problem, we can stop here. You got {correct_count} out of {total}. See you next time!"
    else:
        return f"Session over ({reason}). Score: {correct_count}/{total}."


# ============================================================================
# BUILDING BLOCK — the menu of tools we hand the AI (function calling)
# ============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_answer",
            # ----------------------------------------------------------------
            # TODO 2 — DONE: a clear description so the AI calls this EVERY time
            #          the student gives a numeric answer, instead of grading it
            #          itself. Good description = the AI uses the tool correctly.
            # ----------------------------------------------------------------
            "description": (
                "Check the student's answer to the CURRENT math problem. Call this "
                "every single time the student responds with an answer. Never grade "
                "the math yourself — always call this tool, because it computes the "
                "real answer in code and tells you if the student was right or wrong."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "student_answer": {
                        "type": "string",
                        "description": "Exactly what the student typed as their answer",
                    }
                },
                "required": ["student_answer"],
            },
        },
    },
    {
        # 👇 Worked example — same shape, filled in for you (mirrors end_game).
        "type": "function",
        "function": {
            "name": "end_session",
            "description": "Call this when the session is over: all problems done, or the student says stop/quit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why the session ended",
                        "enum": ["FINISHED", "QUIT"],
                    },
                },
                "required": ["reason"],
            },
        },
    },
]


# ============================================================================
# THE MAIN EVENT — the agentic loop
# ============================================================================
def run_tutor():
    print("🧮 Hi! I'm your math tutor. Type your answer to each problem.")
    print("   (Type 'quit' any time to stop.)\n")

    level = 1
    streak = 0
    correct_count = 0
    problems_done = 0
    attempts = 0                       # wrong tries on the CURRENT problem
    MAX_TRIES = 3                      # after this many misses, reveal and move on
    current_problem = make_problem(level)

    # ------------------------------------------------------------------------
    # TODO 1 — DONE: the AI's job description. Note the two grounding rules:
    #   it MUST use check_answer, and it must NOT reveal answers when wrong.
    # ------------------------------------------------------------------------
    system_prompt = (
        "You are a warm, encouraging math tutor for students in grades 3-8. "
        "VERY IMPORTANT: The app itself shows each math problem to the student. "
        "You do NOT create, choose, write out, or present problems. Never say things "
        "like 'What is 15 - 8?' or announce the next question. Doing that confuses the "
        "student because it will not match the problem the app is showing. "
        "For every answer the student submits, you MUST call the check_answer tool to "
        "grade it. Never do the arithmetic yourself and never trust your own calculation, "
        "the tool is the source of truth. After the tool replies: if it says CORRECT, give "
        "ONE short upbeat sentence of praise. If it says INCORRECT, give ONE short, kind "
        "hint about the method, and do NOT reveal the answer or the next problem. Keep every "
        "reply to a single friendly sentence, the way you'd talk to a 10-year-old. Call "
        "end_session when the session ends."
    )

    messages = [{"role": "system", "content": system_prompt}]

    game_over = False

    # ---- THE AGENTIC LOOP --------------------------------------------------
    while not game_over and problems_done < PROBLEMS_PER_SESSION:
        # 1) Show the current problem and get the student's typed answer.
        print(f"Problem {problems_done + 1}:  {current_problem['text']} = ?")
        answer = input("Your answer: ").strip()

        # Let the student bail out gracefully.
        if answer.lower() in ("quit", "stop", "exit"):
            print("\n🤖 " + end_session("QUIT", correct_count, problems_done) + "\n")
            break

        messages.append({"role": "user", "content": f"My answer is: {answer}"})

        # --------------------------------------------------------------------
        # TODO 3 — DONE: ask the AI what to do (the model call, with our tools).
        # --------------------------------------------------------------------
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )

        ai_message = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": ai_message.content or "",
            "tool_calls": ai_message.tool_calls,
        })

        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if name == "check_answer":
                    # ------------------------------------------------------------
                    # TODO 4 — DONE: run our grader and hand the result back.
                    #   Python compares against current_problem, so the AI can't
                    #   fake it. Then we adapt difficulty from the real result.
                    # ------------------------------------------------------------
                    result = check_answer(args["student_answer"], current_problem, attempts)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    })

                    # Adapt: only real attempts count; correct answers level up.
                    if result.startswith("CORRECT"):
                        correct_count += 1
                        problems_done += 1
                        streak += 1
                        attempts = 0                 # fresh start on next problem
                        if streak >= 2 and level < 5:
                            level += 1        # two in a row -> harder
                            streak = 0
                        current_problem = make_problem(level)
                    elif result.startswith("INCORRECT"):
                        streak = 0
                        attempts += 1
                        if attempts >= MAX_TRIES:
                            # Out of tries: reveal the answer, count it as done,
                            # and move on to an EASIER problem so they can rebuild.
                            print(f"   (The answer was {current_problem['answer']}. "
                                  f"Let's try an easier one.)")
                            problems_done += 1
                            attempts = 0
                            if level > 1:
                                level -= 1
                            current_problem = make_problem(level)
                        # else: keep the SAME problem so they can retry with the hint.
                    # NOT_A_NUMBER: don't advance; re-ask the same problem.

                elif name == "end_session":
                    result = end_session(args["reason"], correct_count, problems_done)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    })
                    # --------------------------------------------------------
                    # TODO 5 — DONE: session ended, stop the loop.
                    # --------------------------------------------------------
                    game_over = True

            # After the tool runs, get the AI's friendly reply to the student.
            follow_up = client.chat.completions.create(model=MODEL, messages=messages)
            reply = follow_up.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            print(f"\n🤖 {reply}\n")

        else:
            # AI replied with plain text (no tool). Just show it.
            print(f"\n🤖 {ai_message.content}\n")

    # If we ran out of problems without an explicit end, wrap up.
    if not game_over and problems_done >= PROBLEMS_PER_SESSION:
        print("\n🤖 " + end_session("FINISHED", correct_count, problems_done) + "\n")

    print("Thanks for practicing! 🎓")


if __name__ == "__main__":
    run_tutor()