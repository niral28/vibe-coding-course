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

                # 🛡️ Gemini can send malformed args (e.g. amount as a string),
                # and our own tool functions can raise too. If either blows up
                # here, we must NOT let the exception kill the generator — that
                # would leave this assistant message's tool_calls unanswered,
                # and every future turn would then error out at the API until
                # the tab is reset. So we catch it, hand the error back to
                # Gemini as if it were a tool result (same pattern as the
                # "Unknown tool" branch below), and let the loop continue —
                # the AI gets a chance to apologize or try again.
                try:
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
                except Exception as exc:
                    result = json.dumps({"error": f"Tool {name} failed: {exc}"})
                    yield sse({"type": "error",
                               "message": f"Tool {name} failed: {exc}"})

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
