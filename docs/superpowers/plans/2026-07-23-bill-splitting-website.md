# Bill-Splitting Agent Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the terminal bill-splitting agent into a clean local website that live-streams every Gemini API call and agentic-loop step, adds country-aware tax/tipping via Gemini's own knowledge, and explains the code simply.

**Architecture:** A Flask app (`bill_splitting_web.py`) imports the tools, client, and system prompt from the existing `bill_splitting_agent.py` (single source of truth) and runs the same 6-step agentic loop per chat turn, streaming each step to the browser as server-sent events. The frontend is one self-contained `static/index.html` (vanilla JS, no build step) with a chat panel, a live "Agent Console" timeline, and a "How it works" explainer.

**Tech Stack:** Python 3.10 (conda env `gset-vibes`), Flask, openai SDK pointed at Gemini's OpenAI-compatible endpoint (`gemini-3.5-flash`), vanilla HTML/CSS/JS.

## Global Constraints

- All new files live in `week1-foundations-text/class05-function-calling-agents/`.
- The terminal program `bill_splitting_agent.py` must keep working unchanged in behavior (same tools + agentic loop; only extended, never broken).
- `GEMINI_API_KEY` is read from `.env` server-side only; the browser never sees it.
- No hardcoded country table — country tax/tipping knowledge comes from Gemini itself via the system prompt.
- Tests in `test_bill_splitting.py` / `test_bill_splitting_web.py` must run with **no API key and no network** (they set a fake key before import).
- Dependencies go in the root `requirements.txt` (single source of truth per CLAUDE.md).
- The Flask app runs on port **5001** (macOS AirPlay squats on 5000).
- Run commands from the repo root with the `gset-vibes` conda env active.
- Code style: match the existing files — heavy friendly comments, section banners (`# ====`), emoji in user-facing strings, teaching tone.

---

### Task 1: Extend the tools + system prompt for country tax & tipping

**Files:**
- Modify: `week1-foundations-text/class05-function-calling-agents/bill_splitting_agent.py`
- Test: `week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py`

**Interfaces:**
- Consumes: existing `add_expense(description, amount)`, `calculate_split(num_people, tip_percent=0)`, `expenses` list, `tools` schema list, `client`, `MODEL`.
- Produces (later tasks rely on these exact names):
  - `calculate_split(num_people, tip_percent=0, tax_percent=0) -> str` (JSON string now containing keys `subtotal, tax_percent, tax_amount, tip_percent, tip_amount, total, num_people, amount_per_person`)
  - Module-level constant `SYSTEM_PROMPT: str` (extracted from `run_bill_splitting_agent`, extended with country knowledge instructions)
  - `tools` schema updated with an optional `tax_percent` number parameter on `calculate_split`.

- [ ] **Step 1: Write the failing tests**

Append to the end of `test_bill_splitting.py`, just before the final `print(f"\n{sum(results)}...")` block (move that summary block below these new checks):

```python
# 5) Splitting with tax should add tax on top of the subtotal.
expenses.clear()
add_expense("lunch", 30)
tax_split = json.loads(calculate_split(2, 0, 10))
print("   calculate_split(2, 0, 10) with 10% tax ->", tax_split)
results.append(check("calculate_split adds 10% tax on $30",
                     tax_split["tax_amount"] == 3.0 and tax_split["total"] == 33.0))
results.append(check("calculate_split splits tax-included total among 2 people",
                     tax_split["amount_per_person"] == 16.5))

# 6) Tax and tip together: 10% tax + 20% tip on $30 = $39 total.
tax_tip_split = json.loads(calculate_split(3, 20, 10))
print("   calculate_split(3, 20, 10) ->", tax_tip_split)
results.append(check("calculate_split combines tax and tip",
                     tax_tip_split["total"] == 39.0
                     and tax_tip_split["amount_per_person"] == 13.0))

# 7) The system prompt should exist and teach the country trick.
from bill_splitting_agent import SYSTEM_PROMPT
results.append(check("SYSTEM_PROMPT mentions country tax & tipping",
                     "country" in SYSTEM_PROMPT and "tax_percent" in SYSTEM_PROMPT))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py`
Expected: crashes with `TypeError: calculate_split() takes ... positional arguments but 3 were given` (or an ImportError for `SYSTEM_PROMPT` if reordered) — the new behavior doesn't exist yet.

- [ ] **Step 3: Implement `tax_percent`, `SYSTEM_PROMPT`, and schema in `bill_splitting_agent.py`**

3a. Replace the whole `calculate_split` function (keep its section banner, update the banner text to "split the running total (plus tax and tip) evenly"):

```python
def calculate_split(num_people, tip_percent=0, tax_percent=0):
    """Add tax + tip to the running total and divide evenly among num_people."""
    subtotal = sum(item["amount"] for item in expenses)
    tax = subtotal * (tax_percent / 100)
    tip = subtotal * (tip_percent / 100)
    total = subtotal + tax + tip
    per_person = total / num_people if num_people else 0
    return json.dumps({
        "subtotal": round(subtotal, 2),
        "tax_percent": tax_percent,
        "tax_amount": round(tax, 2),
        "tip_percent": tip_percent,
        "tip_amount": round(tip, 2),
        "total": round(total, 2),
        "num_people": num_people,
        "amount_per_person": round(per_person, 2),
    })
```

3b. In the `tools` schema for `calculate_split`, update the function `description` to:

```
"Add tax and tip to the running total and split the whole bill evenly among a number of people. Call this only after all expenses have been added, once the user asks to split the bill."
```

and add this property after `tip_percent` (leave `required` as `["num_people"]`):

```python
"tax_percent": {
    "type": "number",
    "description": "Sales tax or VAT as a percent, e.g. 8.875 for New York. "
                   "If the user mentioned what country they're in, use your "
                   "knowledge of that country's typical rate. Use 0 otherwise.",
},
```

3c. Extract the system prompt to a module-level constant placed right after the `tools` list, and extend it. Then in `run_bill_splitting_agent`, replace the inline `system_prompt = (...)` assignment with `messages = [{"role": "system", "content": SYSTEM_PROMPT}]`:

```python
# ============================================================================
# The agent's instructions (shared by the terminal and web versions)
# ============================================================================
SYSTEM_PROMPT = (
    "You are a friendly bill-splitting assistant. As the user mentions "
    "expenses, call add_expense once per expense to add it to the running "
    "tab — do not do the math yourself. When the user asks to split the "
    "bill, call calculate_split with the number of people, the tip percent, "
    "and the tax percent. If the user mentions a country they're in, use "
    "your own knowledge of that country: pass its typical sales tax / VAT "
    "rate as tax_percent, suggest a culturally appropriate tip_percent "
    "(for example: tipping isn't customary in Japan, ~5-10% is polite in "
    "Germany, 15-20% is standard in the US), and briefly explain the local "
    "custom in your reply. If no country or tip is mentioned, use 0 for "
    "both. After a tool gives you a result, explain it back to the user in "
    "a short, friendly way — for add_expense, confirm what was added and "
    "the new running total; for calculate_split, clearly state the total "
    "and how much each person owes. Never calculate totals or splits "
    "yourself — always use the tools."
)
```

3d. In the terminal loop's tool dispatch, pass the new argument through:

```python
elif name == "calculate_split":
    result = calculate_split(
        args["num_people"],
        args.get("tip_percent", 0),
        args.get("tax_percent", 0),
    )
```

3e. In the file's top docstring "Try it out" list, add one line after `add $15 for drinks`:

```
       we're in Japan — split between 4 people
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py`
Expected: `9 / 9 checks passed.` and the 🎉 line.

- [ ] **Step 5: Commit**

```bash
git add week1-foundations-text/class05-function-calling-agents/bill_splitting_agent.py \
        week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py
git commit -m "feat: add country-aware tax to bill-splitting tools and prompt"
```

---

### Task 2: Flask backend with SSE-streamed agentic loop

**Files:**
- Create: `week1-foundations-text/class05-function-calling-agents/bill_splitting_web.py`
- Test: `week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py`
- Modify: `requirements.txt` (repo root)

**Interfaces:**
- Consumes (from Task 1): `MODEL`, `SYSTEM_PROMPT`, `add_expense`, `calculate_split`, `client`, `expenses`, `tools` — all imported from `bill_splitting_agent`.
- Produces (Task 3's frontend relies on these exactly):
  - `GET /` → serves `static/index.html`
  - `GET /state` → JSON `{"api_key_present": bool, "model": str|null, "expenses": [...], "running_total": float}`
  - `POST /reset` → JSON `{"ok": true}`, clears expenses and conversation
  - `POST /chat` (body `{"message": str}`) → `text/event-stream` of `data: {...}\n\n` events with `type` one of: `api_call` (`request_number`, `model`), `tool_call` (`name`, `args`), `tool_result` (`name`, `result`, `expenses`, `running_total`), `final_answer` (`content`, `expenses`, `running_total`), `error` (`message`).

- [ ] **Step 1: Add flask to the root `requirements.txt`**

Add a line `flask` to `/Users/justinli/vibe-coding-course/requirements.txt`, then run:

Run: `pip install -r requirements.txt`
Expected: ends with `Successfully installed ...` or `Requirement already satisfied` lines, exit code 0.

- [ ] **Step 2: Write the failing tests**

Create `test_bill_splitting_web.py`:

```python
"""
Self-check for the Bill-Splitting web app 🧾🌐
==============================================

Run this to make sure the Flask routes work. No internet or real API key
needed — the AI chat route itself is exercised in the browser instead.

HOW TO RUN (from the project's ROOT folder, with (gset-vibes) active):

    python week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py
"""

import os

# The agent file connects to Gemini when it loads, which normally needs your
# key. These tests never call the AI, so a fake key is enough for the import.
os.environ.setdefault("GEMINI_API_KEY", "not-needed-for-this-test")

from bill_splitting_web import app, messages
from bill_splitting_agent import add_expense, expenses


def check(name, condition):
    """Print a friendly PASS/FAIL line and remember the result."""
    print(("✅ PASS" if condition else "❌ FAIL"), "-", name)
    return condition


print("\nChecking the bill-splitting web app...\n")

results = []
web = app.test_client()

# 1) The home page should serve the website.
home = web.get("/")
results.append(check("GET / serves the page",
                     home.status_code == 200 and b"Bill-Splitting" in home.data))

# 2) /state should report the key and an empty tab to start.
expenses.clear()
state = web.get("/state").get_json()
print("   GET /state ->", state)
results.append(check("GET /state reports api_key_present and an empty tab",
                     state["api_key_present"] is True
                     and state["expenses"] == []
                     and state["running_total"] == 0))

# 3) /state should reflect expenses added by the tool.
add_expense("pizza", 20)
state = web.get("/state").get_json()
results.append(check("GET /state shows the running tab",
                     state["running_total"] == 20 and len(state["expenses"]) == 1))

# 4) /reset should clear the tab and the conversation (system prompt stays).
messages.append({"role": "user", "content": "hi"})
web.post("/reset")
state = web.get("/state").get_json()
results.append(check("POST /reset clears expenses and conversation",
                     state["expenses"] == [] and len(messages) == 1
                     and messages[0]["role"] == "system"))

print(f"\n{sum(results)} / {len(results)} checks passed.\n")
if all(results):
    print("🎉 The web app's routes work! Now run bill_splitting_web.py and "
          "open http://localhost:5001 in your browser.\n")
else:
    print("Some checks failed — read the ❌ lines above to see what to fix.\n")
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py`
Expected: `ModuleNotFoundError: No module named 'bill_splitting_web'`.

- [ ] **Step 4: Write the backend**

Create `bill_splitting_web.py`:

```python
"""
GSET Vibe Coding — Class 5: Bill-Splitting Agent, WEB EDITION 🧾🌐
==================================================================

Same tools, same agentic loop as bill_splitting_agent.py — but now with a
web page that SHOWS you every Gemini API call and every loop step, live.

HOW TO RUN IT
  1. Make sure .env has your GEMINI_API_KEY.
  2. From the project's ROOT folder, with (gset-vibes) active:

       python week1-foundations-text/class05-function-calling-agents/bill_splitting_web.py

  3. Open http://localhost:5001 and chat away. Try:
       add $20 for pizza
       add $15 for drinks
       we're in Japan — split between 4 people
------------------------------------------------------------------------------
"""

import json
import os

from dotenv import load_dotenv   # reads your GEMINI_API_KEY from the .env file
from flask import Flask, Response, jsonify, request, send_from_directory

load_dotenv()

app = Flask(__name__)

# If the key is missing we still serve the page (it shows a friendly banner),
# but we must not import the agent module — it reads the key at import time.
HAS_KEY = bool(os.environ.get("GEMINI_API_KEY"))

if HAS_KEY:
    from bill_splitting_agent import (
        MODEL,
        SYSTEM_PROMPT,
        add_expense,
        calculate_split,
        client,
        expenses,
        tools,
    )
    # The running conversation — exactly like the terminal version's list.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
else:
    expenses = []
    messages = []


def running_total():
    """Current total of the tab, rounded to cents."""
    return round(sum(item["amount"] for item in expenses), 2)


def sse(data):
    """Format one server-sent event the browser can stream."""
    return f"data: {json.dumps(data)}\n\n"


# ============================================================================
# Plain routes: the page, the current tab, and the reset button
# ============================================================================
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/state")
def state():
    return jsonify({
        "api_key_present": HAS_KEY,
        "model": MODEL if HAS_KEY else None,
        "expenses": expenses,
        "running_total": running_total(),
    })


@app.route("/reset", methods=["POST"])
def reset():
    expenses.clear()
    del messages[1:]  # keep only the system prompt
    return jsonify({"ok": True})


# ============================================================================
# THE AGENTIC LOOP — same 6-step loop as the terminal, but every step is
# streamed to the browser as a server-sent event so you can WATCH it think.
# ============================================================================
@app.route("/chat", methods=["POST"])
def chat():
    if not HAS_KEY:
        return jsonify({"error": "GEMINI_API_KEY is missing"}), 500
    user_message = request.get_json()["message"]

    def stream():
        messages.append({"role": "user", "content": user_message})

        # ---- One user turn can take several agentic steps ------------------
        for step in range(6):
            # 📤 Announce the real API round-trip before we make it.
            yield sse({"type": "api_call",
                       "request_number": step + 1,
                       "model": MODEL})
            try:
                response = client.chat.completions.create(
                    model=MODEL, messages=messages, tools=tools,
                )
            except Exception as exc:
                yield sse({"type": "error", "message": str(exc)})
                return

            ai_message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": ai_message.content or "",
                "tool_calls": ai_message.tool_calls,
            })

            # No tool call -> the AI is giving its final answer for this turn.
            if not ai_message.tool_calls:
                yield sse({
                    "type": "final_answer",
                    "content": ai_message.content,
                    "expenses": expenses,
                    "running_total": running_total(),
                })
                return

            # Otherwise, run whichever tool(s) the AI asked for.
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                yield sse({"type": "tool_call", "name": name, "args": args})

                if name == "add_expense":
                    result = add_expense(args["description"], args["amount"])
                elif name == "calculate_split":
                    result = calculate_split(
                        args["num_people"],
                        args.get("tip_percent", 0),
                        args.get("tax_percent", 0),
                    )
                else:
                    result = json.dumps({"error": f"Unknown tool {name}"})

                yield sse({
                    "type": "tool_result",
                    "name": name,
                    "result": json.loads(result),
                    "expenses": expenses,
                    "running_total": running_total(),
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result,
                })

        yield sse({"type": "error",
                   "message": "Hit the 6-step limit for this turn — try again."})

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    # Port 5001 because macOS AirPlay already sits on port 5000.
    app.run(debug=True, port=5001)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py`
Expected: at this point check #1 FAILS (no `static/index.html` yet → `GET /` is 404) and checks 2-4 PASS: `3 / 4 checks passed.` That is the correct state before Task 3. If checks 2-4 fail, fix the backend now.

Also re-run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py`
Expected: `9 / 9 checks passed.` (backend didn't break the tools).

- [ ] **Step 6: Commit**

```bash
git add requirements.txt \
        week1-foundations-text/class05-function-calling-agents/bill_splitting_web.py \
        week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py
git commit -m "feat: Flask backend streaming the bill-splitting agentic loop via SSE"
```

---

### Task 3: The web page (chat + live Agent Console + explainer)

**Files:**
- Create: `week1-foundations-text/class05-function-calling-agents/static/index.html`

**Interfaces:**
- Consumes (from Task 2, exact shapes): `GET /state`, `POST /reset`, `POST /chat` streaming `data: {...}\n\n` events with `type` ∈ {`api_call`, `tool_call`, `tool_result`, `final_answer`, `error`} and the fields listed in Task 2.
- Produces: the complete user-facing page. No later task consumes code from this one.

- [ ] **Step 1: Create `static/index.html`**

The full file (self-contained HTML + CSS + JS, no external requests):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧾 Bill-Splitting Agent</title>
<style>
  :root {
    --bg: #f6f7fb; --card: #ffffff; --ink: #1c2333; --muted: #6b7280;
    --accent: #4f46e5; --accent-soft: #eef2ff; --green: #059669;
    --console-bg: #101425; --console-ink: #d7ddf3; --red: #dc2626;
    --radius: 14px; --shadow: 0 1px 3px rgba(16,20,37,.08), 0 8px 24px rgba(16,20,37,.06);
  }
  * { box-sizing: border-box; margin: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg); color: var(--ink); line-height: 1.5;
  }
  .wrap { max-width: 1100px; margin: 0 auto; padding: 24px 20px 60px; }

  /* ---------- header ---------- */
  header { text-align: center; margin-bottom: 20px; }
  header h1 { font-size: 1.9rem; letter-spacing: -.02em; }
  header p { color: var(--muted); margin-top: 4px; }
  .model-badge {
    display: inline-block; margin-top: 10px; padding: 4px 12px;
    background: var(--accent-soft); color: var(--accent); border-radius: 999px;
    font-size: .8rem; font-weight: 600;
  }
  .banner {
    background: #fef2f2; border: 1px solid #fecaca; color: #991b1b;
    border-radius: var(--radius); padding: 12px 16px; margin-bottom: 16px;
    display: none;
  }

  /* ---------- layout ---------- */
  .layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 820px) { .layout { grid-template-columns: 1fr; } }
  .panel {
    background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow);
    padding: 16px; display: flex; flex-direction: column;
  }
  .panel h2 { font-size: 1rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }

  /* ---------- running tab ---------- */
  .tab-card {
    background: var(--accent-soft); border-radius: 10px; padding: 10px 12px;
    font-size: .88rem; margin-bottom: 10px;
  }
  .tab-card .total { font-weight: 700; color: var(--accent); }
  .tab-card ul { list-style: none; margin-top: 4px; }
  .tab-card li { display: flex; justify-content: space-between; color: var(--muted); }

  /* ---------- chat ---------- */
  #chat-log { flex: 1; min-height: 320px; max-height: 440px; overflow-y: auto; padding: 4px 2px; }
  .bubble { max-width: 85%; padding: 9px 13px; border-radius: 14px; margin: 6px 0; font-size: .93rem; white-space: pre-wrap; }
  .bubble.user { background: var(--accent); color: #fff; margin-left: auto; border-bottom-right-radius: 4px; }
  .bubble.ai { background: #f1f2f7; border-bottom-left-radius: 4px; }
  .chip {
    display: inline-block; font-size: .74rem; font-family: ui-monospace, monospace;
    background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa;
    border-radius: 999px; padding: 2px 10px; margin: 3px 0;
  }
  form { display: flex; gap: 8px; margin-top: 10px; }
  input[type=text] {
    flex: 1; padding: 10px 14px; border: 1px solid #d9dce6; border-radius: 10px;
    font-size: .95rem; outline: none;
  }
  input[type=text]:focus { border-color: var(--accent); }
  button {
    padding: 10px 18px; border: none; border-radius: 10px; background: var(--accent);
    color: #fff; font-weight: 600; cursor: pointer; font-size: .9rem;
  }
  button:disabled { opacity: .5; cursor: default; }
  .hint { font-size: .8rem; color: var(--muted); margin-top: 8px; }
  .reset { background: transparent; color: var(--muted); font-weight: 500; padding: 6px 0; align-self: flex-start; }

  /* ---------- agent console ---------- */
  .console { background: var(--console-bg); color: var(--console-ink); }
  .console h2 { color: #fff; }
  #console-log {
    flex: 1; min-height: 380px; max-height: 520px; overflow-y: auto;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .8rem;
  }
  .step { padding: 7px 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid transparent; word-break: break-word; }
  .step.api { background: rgba(99,102,241,.16); border-left-color: #818cf8; }
  .step.tool { background: rgba(245,158,11,.12); border-left-color: #f59e0b; }
  .step.result { background: rgba(16,185,129,.10); border-left-color: #10b981; }
  .step.answer { background: rgba(255,255,255,.07); border-left-color: #e5e7eb; }
  .step.error { background: rgba(220,38,38,.15); border-left-color: var(--red); }
  .step.turn { color: #8b93b8; border-left: none; margin-top: 12px; font-size: .74rem; text-transform: uppercase; letter-spacing: .06em; }
  .pulse {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: #818cf8; margin-right: 6px; animation: pulse 1s infinite;
  }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .25; } }
  .console-empty { color: #8b93b8; padding: 20px 10px; }

  /* ---------- how it works ---------- */
  .how { margin-top: 28px; }
  .how h2 { text-align: center; font-size: 1.3rem; margin-bottom: 14px; }
  .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  @media (max-width: 820px) { .cards { grid-template-columns: 1fr; } }
  .card { background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow); padding: 16px; font-size: .88rem; }
  .card h3 { font-size: .95rem; margin-bottom: 6px; }
  .card p { color: var(--muted); margin-bottom: 8px; }
  .card pre {
    background: var(--console-bg); color: var(--console-ink); border-radius: 8px;
    padding: 10px; font-size: .72rem; overflow-x: auto; line-height: 1.45;
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🧾 Bill-Splitting Agent</h1>
    <p>An AI agent that never does math itself — it calls real Python tools, and you can watch every step.</p>
    <span class="model-badge" id="model-badge">Powered by the Gemini API</span>
  </header>

  <div class="banner" id="key-banner">
    ⚠️ <strong>No GEMINI_API_KEY found.</strong> Copy <code>shared/.env.example</code> to
    <code>.env</code>, add your key, then restart <code>bill_splitting_web.py</code>.
  </div>

  <div class="layout">
    <!-- ================= chat panel ================= -->
    <section class="panel">
      <h2>💬 Chat</h2>
      <div class="tab-card" id="tab-card">🧾 Running tab: <span class="total">$0.00</span> — nothing yet, add an expense!</div>
      <div id="chat-log"></div>
      <form id="chat-form">
        <input type="text" id="chat-input" placeholder='Try: "add $20 for pizza"' autocomplete="off">
        <button type="submit" id="send-btn">Send</button>
      </form>
      <div class="hint">💡 Tip: mention a country — <em>“we're in Japan — split between 4 people”</em> — and the AI applies local tax &amp; tipping customs.</div>
      <button class="reset" id="reset-btn">↺ Reset tab &amp; conversation</button>
    </section>

    <!-- ================= agent console ================= -->
    <aside class="panel console">
      <h2>🛰️ Agent Console <span style="font-weight:400;font-size:.75rem;color:#8b93b8">— live view of the agentic loop</span></h2>
      <div id="console-log"><div class="console-empty">Waiting for your first message… every Gemini API call and tool call will appear here as it happens.</div></div>
    </aside>
  </div>

  <!-- ================= how it works ================= -->
  <section class="how">
    <h2>How the code works</h2>
    <div class="cards">
      <div class="card">
        <h3>① Function calling</h3>
        <p>The AI is told about two Python functions. Instead of doing math (which LLMs are bad at), it replies with <em>“please run this tool with these arguments”</em> — and our Python actually runs it.</p>
        <pre>add_expense(description, amount)
  → adds to the tab, returns total

calculate_split(num_people,
                tip_percent,
                tax_percent)
  → tax + tip, split per person</pre>
      </div>
      <div class="card">
        <h3>② The agentic loop</h3>
        <p>One message from you can take several API round-trips. The server keeps calling Gemini until it stops asking for tools and answers you — that's the loop in the console.</p>
        <pre>for step in range(6):
    response = gemini(messages, tools)
    if no tool_calls:
        show final answer; break
    run the tool
    send result back to Gemini</pre>
      </div>
      <div class="card">
        <h3>③ Country smarts</h3>
        <p>There's no country database here. The system prompt tells Gemini: if the user names a country, use <em>your own knowledge</em> of its tax rate and tipping culture, and pass those numbers to the tool.</p>
        <pre>"we're in Japan" →
  Gemini knows: 10% tax,
  tipping isn't customary
  → calculate_split(4, 0, 10)</pre>
      </div>
    </div>
  </section>
</div>

<script>
  const chatLog = document.getElementById("chat-log");
  const consoleLog = document.getElementById("console-log");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  let turnCount = 0;

  const esc = (s) => String(s).replace(/[&<>"']/g,
    (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

  // ---------- rendering helpers ----------
  function bubble(role, text) {
    const div = document.createElement("div");
    div.className = "bubble " + role;
    div.textContent = text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function chip(text) {
    const div = document.createElement("div");
    div.innerHTML = `<span class="chip">🔧 ${esc(text)}</span>`;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function consoleStep(cls, html) {
    const empty = consoleLog.querySelector(".console-empty");
    if (empty) empty.remove();
    // Freeze any previous pulsing dot — that request has moved on.
    consoleLog.querySelectorAll(".pulse").forEach(p => p.classList.remove("pulse"));
    const div = document.createElement("div");
    div.className = "step " + cls;
    div.innerHTML = html;
    consoleLog.appendChild(div);
    consoleLog.scrollTop = consoleLog.scrollHeight;
    return div;
  }

  function renderTab(expenses, total) {
    const card = document.getElementById("tab-card");
    if (!expenses || expenses.length === 0) {
      card.innerHTML = '🧾 Running tab: <span class="total">$0.00</span> — nothing yet, add an expense!';
      return;
    }
    const items = expenses.map(e =>
      `<li><span>${esc(e.description)}</span><span>$${e.amount.toFixed(2)}</span></li>`).join("");
    card.innerHTML = `🧾 Running tab: <span class="total">$${total.toFixed(2)}</span><ul>${items}</ul>`;
  }

  // ---------- one streamed event from the agentic loop ----------
  function handleEvent(ev) {
    if (ev.type === "api_call") {
      consoleStep("api",
        `<span class="pulse"></span>📤 Calling Gemini API — request #${ev.request_number} <em>(${esc(ev.model)})</em>`);
    } else if (ev.type === "tool_call") {
      consoleStep("tool", `🔧 Gemini asked for tool: <strong>${esc(ev.name)}</strong>(${esc(JSON.stringify(ev.args))})`);
      chip(`${ev.name}(${JSON.stringify(ev.args)})`);
    } else if (ev.type === "tool_result") {
      consoleStep("result", `📥 Python ran <strong>${esc(ev.name)}</strong> → ${esc(JSON.stringify(ev.result))}`);
      renderTab(ev.expenses, ev.running_total);
    } else if (ev.type === "final_answer") {
      consoleStep("answer", "💬 Final answer — no more tool calls, the loop ends.");
      bubble("ai", ev.content);
      renderTab(ev.expenses, ev.running_total);
    } else if (ev.type === "error") {
      consoleStep("error", `❌ ${esc(ev.message)}`);
      bubble("ai", "⚠️ Something went wrong: " + ev.message);
    }
  }

  // ---------- send a message and stream the loop ----------
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message || sendBtn.disabled) return;
    input.value = "";
    sendBtn.disabled = true;
    bubble("user", message);
    turnCount += 1;
    consoleStep("turn", `— turn ${turnCount}: “${esc(message)}” —`);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
          const chunk = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          if (chunk.startsWith("data: ")) handleEvent(JSON.parse(chunk.slice(6)));
        }
      }
    } catch (err) {
      handleEvent({ type: "error", message: err.message });
    }
    consoleLog.querySelectorAll(".pulse").forEach(p => p.classList.remove("pulse"));
    sendBtn.disabled = false;
    input.focus();
  });

  // ---------- reset ----------
  document.getElementById("reset-btn").addEventListener("click", async () => {
    await fetch("/reset", { method: "POST" });
    chatLog.innerHTML = "";
    consoleLog.innerHTML = '<div class="console-empty">Tab reset — waiting for your next message…</div>';
    turnCount = 0;
    renderTab([], 0);
  });

  // ---------- initial load ----------
  (async () => {
    const state = await (await fetch("/state")).json();
    if (!state.api_key_present) {
      document.getElementById("key-banner").style.display = "block";
      input.disabled = true;
      sendBtn.disabled = true;
      return;
    }
    document.getElementById("model-badge").textContent =
      "Powered by the Gemini API — " + state.model;
    renderTab(state.expenses, state.running_total);
  })();
</script>
</body>
</html>
```

- [ ] **Step 2: Run the web tests to verify the page is served**

Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py`
Expected: `4 / 4 checks passed.` and the 🎉 line (check #1 now passes because `static/index.html` exists).

- [ ] **Step 3: Smoke-run the server**

Run (background): `python week1-foundations-text/class05-function-calling-agents/bill_splitting_web.py`
Then: `curl -s http://localhost:5001/ | head -5` → expect the `<!DOCTYPE html>` opening; `curl -s http://localhost:5001/state` → expect JSON with `"api_key_present": true`. Stop the server after checking.

- [ ] **Step 4: Commit**

```bash
git add week1-foundations-text/class05-function-calling-agents/static/index.html
git commit -m "feat: bill-splitting web page with live agent console and explainer"
```

---

### Task 4: End-to-end verification in the browser

**Files:**
- No new files. Fix anything the e2e run uncovers (any file from Tasks 1-3).

**Interfaces:**
- Consumes: the full running app from Tasks 1-3 with a real `GEMINI_API_KEY` in `.env`.
- Produces: verified working demo (and fixes, if needed).

- [ ] **Step 1: Start the server**

Run in background: `python week1-foundations-text/class05-function-calling-agents/bill_splitting_web.py`
Expected: Flask banner with `Running on http://127.0.0.1:5001`.

- [ ] **Step 2: Exercise the demo script in a real browser**

Open `http://localhost:5001` (use claude-in-chrome browser tools if available, otherwise ask the user to click through) and verify each item:

1. Page loads clean; model badge reads "Powered by the Gemini API — gemini-3.5-flash"; no key banner.
2. Send `add $20 for pizza` → console shows, in order: turn separator → `📤 request #1` (pulsing while waiting) → `🔧 add_expense` → `📥 result` → `📤 request #2` → `💬 Final answer`; chat shows a 🔧 chip + AI bubble; running tab shows pizza $20.00.
3. Send `add $15 for drinks` → tab shows both items, total $35.00.
4. Send `we're in Japan — split between 4 people` → console shows `calculate_split` called with `tax_percent` ≈ 10 and `tip_percent` 0; AI reply mentions Japanese tipping culture.
5. Click "↺ Reset tab & conversation" → tab and chat clear; send `split between 2 people` → per-person $0.00 (empty tab), proving reset worked.
6. Nothing in the browser network tab ever contains the API key (spot-check the `/chat` request/response).

- [ ] **Step 3: Fix anything that failed, re-verify, and re-run both test files**

Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py` → `9 / 9 checks passed.`
Run: `python week1-foundations-text/class05-function-calling-agents/test_bill_splitting_web.py` → `4 / 4 checks passed.`

- [ ] **Step 4: Commit any fixes**

```bash
git add -A week1-foundations-text/class05-function-calling-agents/
git commit -m "fix: polish from end-to-end browser verification"
```

(Skip the commit if the e2e run needed no changes.)
