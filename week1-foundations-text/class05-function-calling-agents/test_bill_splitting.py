"""
Self-check for the Bill-Splitting tools 🧾
===========================================

Run this to make sure add_expense and calculate_split work. Pure math, no
internet or API key needed.

HOW TO RUN (from the project's ROOT folder, with (gset-vibes) active):

    python week1-foundations-text/class05-function-calling-agents/test_bill_splitting.py
"""

import os
import json

# The agent file connects to Gemini when it loads, which normally needs your key.
# These tests don't use the AI, so we set a fake key just so the import works.
os.environ.setdefault("GEMINI_API_KEY", "not-needed-for-this-test")

from bill_splitting_agent import add_expense, calculate_split, expenses


def check(name, condition):
    """Print a friendly PASS/FAIL line and remember the result."""
    print(("✅ PASS" if condition else "❌ FAIL"), "-", name)
    return condition


print("\nChecking the bill-splitting tools...\n")

results = []

# 1) Adding an expense should update the running total.
first = json.loads(add_expense("pizza", 20))
print("   add_expense('pizza', 20) ->", first)
results.append(check("add_expense tracks the running total",
                     first["running_total"] == 20 and first["expense_count"] == 1))

# 2) A second expense should add to the running total.
second = json.loads(add_expense("drinks", 15))
print("   add_expense('drinks', 15) ->", second)
results.append(check("add_expense accumulates across calls",
                     second["running_total"] == 35 and second["expense_count"] == 2))

# 3) Splitting with a tip should compute tip, total, and per-person share.
split = json.loads(calculate_split(4, 15))
print("   calculate_split(4, 15) ->", split)
results.append(check("calculate_split adds a 15% tip on $35",
                     split["tip_amount"] == 5.25 and split["total"] == 40.25))
results.append(check("calculate_split divides evenly among 4 people",
                     split["amount_per_person"] == 10.06))

# 4) Splitting with no tip should just divide the subtotal.
expenses.clear()
add_expense("lunch", 30)
no_tip_split = json.loads(calculate_split(3))
print("   calculate_split(3) with no tip ->", no_tip_split)
results.append(check("calculate_split defaults tip_percent to 0",
                     no_tip_split["tip_amount"] == 0
                     and no_tip_split["amount_per_person"] == 10))

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

print(f"\n{sum(results)} / {len(results)} checks passed.\n")
if all(results):
    print("🎉 Your bill-splitting tools work! Now run bill_splitting_agent.py and try it.\n")
else:
    print("Some checks failed — read the ❌ lines above to see what to fix.\n")
