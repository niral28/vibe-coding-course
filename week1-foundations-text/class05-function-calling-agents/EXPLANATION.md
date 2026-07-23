# 🧮 How Your AI Adaptive Math Tutor Web App Works

Welcome! This document explains how your **AI Math Tutor** web application works under the hood. Whether you're new to coding or looking to understand web development and AI agents, this guide breaks down every piece in plain, easy-to-follow language!

---

## 🌟 1. The Big Picture: How All the Parts Connect

Your project is built using three main components working in harmony:

```
┌─────────────────────────┐         HTTP JSON          ┌─────────────────────────┐
│     BROWSER FRONTEND    │ <========================> │     FLASK WEB SERVER    │
│  (HTML, CSS, JavaScript)│   /api/submit_answer etc.  │        (app.py)         │
└─────────────────────────┘                            └────────────┬────────────┘
                                                                    │ Tool Call
                                                                    ▼
                                                       ┌─────────────────────────┐
                                                       │   GEMINI AI & PYTHON    │
                                                       │ (check_answer & tools)  │
                                                       └─────────────────────────┘
```

1. **The Web Browser (Frontend)**: What you see and interact with! Built with **HTML** (structure), **CSS** (colorful styles & glassmorphism cards), and **JavaScript** (timers, screen switching, and dynamic updates).
2. **The Flask Web Server (Backend - `app.py`)**: A lightweight Python server running locally. It handles requests from the browser, manages session data, generates math problems in Python, and talks to Gemini.
3. **The Gemini AI Agent (`check_answer` & `end_session`)**: The brain powered by Google's `gemini-3.5-flash` model. It calls Python tools to grade answers accurately and delivers warm, encouraging tutor feedback.

---

## 🔐 2. Keeping Your API Key Safe (`.env` and `python-dotenv`)

### Why non-hardcoded keys matter
Never type secret keys directly into code (e.g. `api_key = "AIzaSy..."`). If you share your file or upload it to GitHub, anyone could steal your key!

### How we load it in `app.py`:
```python
from dotenv import load_dotenv
import os

# Read hidden configuration file named .env
load_dotenv()

# Read the environment variable safely
api_key = os.getenv("GEMINI_API_KEY")
```

- **`python-dotenv`** reads the hidden `.env` file sitting in your folder.
- **`os.getenv("GEMINI_API_KEY")`** extracts the key into memory securely.

---

## 🧮 3. Anti-Hallucination: Python Holds the Mathematical Truth

### The Problem with AI Math
Large Language Models (LLMs) predict text—they don't do real calculations in their heads. If an AI tries to calculate `14 x 13` directly, it might hallucinate or make a mistake.

### The Solution: Function Calling (Tools)
In `app.py`, Python creates the math problem **and** computes the exact answer *before* presenting it:

```python
# Python calculates the exact correct answer:
def make_problem(level, topics):
    a, b = 12, 7
    return {"text": "12 × 7", "answer": 84}
```

When you type an answer, the AI is handed a **tool** called `check_answer`:
```python
def check_answer(student_answer, problem, prior_misses=0):
    if student_answer == problem["answer"]:
        return "CORRECT: Praise them!"
    else:
        return "INCORRECT: Give a gentle hint (no answer)."
```

Because **Python grades the student's answer**, the AI never has to guess whether you're right or wrong! The AI simply receives Python's authoritative grading result and turns it into a friendly, encouraging sentence for you.

---

## 🎯 4. The 3 App Screens Explained

### Screen 1: Start Screen
- **Difficulty Selection**: Select starting level (Level 1 to 5, mapping Grade 3 up to Grade 8 multi-step problems) with visible radio buttons.
- **Topics**: Visible emerald-green checkboxes next to each topic choice: Addition, Subtraction, Multiplication, Division, Mixed, Two-Step, Fractions, and Decimals! You can check or uncheck any combination.
- **Session Ending Mode (Either / Or)**:
  - **Option A (Fixed Questions)**: Choose a set number of problems (e.g. 5, 8, 10, 15, or 20 questions) and complete them at your own pace.
  - **Option B (Time Limit Speed Run)**: Set a timer (1, 2, 3, 5, or 10 minutes) and solve as many questions as you can before time expires!

### Screen 2: Quiz Screen
- Displays the current problem in bold typography (`12 + 8 = ?`).
- Features a **live question timer** (showing how many seconds you take per question) and an **overall session timer**.
- Displays an animated AI Tutor card with hints, praise, or encouragement.
- **The Mid-Question Timer Rule**: If the overall time limit expires while you are in the middle of solving a problem, the app displays a gentle notification banner ("Time's up for the overall session! Take your time to finish this current question..."). It lets you complete and submit that question, updates your statistics, and *then* wraps up the session cleanly.

### Screen 3: Summary Screen
- **Accuracy Scorecard**: Displays your percentage, correct vs. incorrect counts, total session duration, and average time per question.
- **AI Wrap-up Message**: Shows Gemini's final encouraging session assessment with celebratory confetti!
- **Breakdown Table**: A detailed table listing every single question answered, your answer, the real answer, result (Correct / Missed), and exact seconds spent.

---

## 🚀 5. How to Run the App

1. Make sure your `.env` file contains your `GEMINI_API_KEY`:
   ```bash
   GEMINI_API_KEY=your_real_gemini_key_here
   ```

2. Start the Flask server from your terminal:
   ```bash
   python app.py
   ```

3. Open your browser and visit:
   ```
   http://127.0.0.1:5000
   ```

Enjoy practicing math with your personal AI agent! 🎓✨
