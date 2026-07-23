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
